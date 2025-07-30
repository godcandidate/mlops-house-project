# lambda_function.py

import os
import json
import uuid
import boto3
from datetime import datetime
import joblib
import pandas as pd
from io import BytesIO
# Import Decimal for DynamoDB compatibility
from decimal import Decimal

# --- Environment Variables ---
S3_BUCKET = os.environ.get("S3_BUCKET")
MODEL_MODE = os.environ.get("MODEL_MODE", "default")  # "default" or "ab"
PREPROCESSOR_PATH = os.environ.get("PREPROCESSOR_PATH")
DEFAULT_MODEL_PATH = os.environ.get("DEFAULT_MODEL_PATH")
MODEL_V1_PATH = os.environ.get("MODEL_V1_PATH")
MODEL_V2_PATH = os.environ.get("MODEL_V2_PATH")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")

# --- AWS Clients ---
s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# --- Global Model Variables (Initialized on Cold Start) ---
preprocessor = None
model = None
model_v1 = None
model_v2 = None

# --- Round Robin Balancer for A/B Testing ---
class RoundRobinBalancer:
    def __init__(self):
        self.counter = 0

    def get_version(self, versions=["v1", "v2"]):
        self.counter += 1
        # Ensure counter doesn't grow indefinitely
        self.counter = self.counter % len(versions)
        return versions[self.counter]

rr_balancer = RoundRobinBalancer()

# --- Model Loading from S3 ---
def load_model_from_s3(key):
    """
    Loads a joblib model from S3.
    Args:
        key (str): The S3 object key for the model file.
    Returns:
        The loaded model object.
    Raises:
        RuntimeError: If loading fails.
    """
    try:
        print(f"Attempting to load model from s3://{S3_BUCKET}/{key}")
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        buffer = BytesIO(response["Body"].read())
        model_obj = joblib.load(buffer)
        print(f"Successfully loaded model from {key}")
        return model_obj
    except Exception as e:
        error_msg = f"Failed to load model from s3://{S3_BUCKET}/{key}: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

# --- Cold Start Initialization ---
def initialize_models():
    """
    Initializes global model variables by loading them from S3.
    This should only run once per Lambda execution environment (cold start).
    """
    global preprocessor, model, model_v1, model_v2
    print("Initializing models (cold start)...")
    
    try:
        preprocessor = load_model_from_s3(PREPROCESSOR_PATH)

        if MODEL_MODE == "default":
            model = load_model_from_s3(DEFAULT_MODEL_PATH)
        elif MODEL_MODE == "ab":
            model_v1 = load_model_from_s3(MODEL_V1_PATH)
            model_v2 = load_model_from_s3(MODEL_V2_PATH)
        else:
            raise ValueError(f"Unsupported MODEL_MODE: {MODEL_MODE}")
        
        print("All models initialized successfully.")
    except Exception as e:
        # Log the error during initialization
        print(f"Error during model initialization: {e}")
        # Re-raise to fail the Lambda invocation if models can't load
        raise 

# --- Logging to DynamoDB ---
def log_to_dynamodb(log_entry):
    """
    Logs a prediction entry to the specified DynamoDB table.
    Args:
        log_entry (dict): The dictionary containing log data.
    """
    try:
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item=log_entry)
        print(f"Successfully logged prediction ID {log_entry.get('prediction_id')} to DynamoDB.")
    except Exception as e:
        # Log the error but don't fail the prediction
        print(f"Warning: Failed to log to DynamoDB: {e}")

# --- Core Prediction Logic ---
def predict_price(event):
    """
    Processes the event, makes a prediction, and logs the result.
    Args:
        event (dict): The Lambda event object containing the request.
    Returns:
        dict: The Lambda response object (statusCode, headers, body).
    """
    global preprocessor, model, model_v1, model_v2 # Access global models

    # --- 1. Parse Input Data ---
    # Ensure 'body' exists and is valid JSON
    if "body" not in event or not event["body"]:
         raise ValueError("Invalid event structure: Missing or empty 'body' field.")

    try:
        body = json.loads(event["body"])
        print(f"Parsed input data: {body}")
    except json.JSONDecodeError as je:
        raise ValueError(f"Invalid JSON in request body: {je}")

    # --- 2. Data Preparation ---
    input_data = pd.DataFrame([body])
    # Calculate derived features
    current_year = datetime.now().year
    input_data['house_age'] = current_year - input_data['year_built']
    input_data['bed_bath_ratio'] = input_data['bedrooms'] / input_data['bathrooms']
    # Dummy value for pipeline compatibility (if needed by preprocessor)
    input_data['price_per_sqft'] = 1  

    # --- 3. Data Preprocessing ---
    try:
        processed_features = preprocessor.transform(input_data)
        # Create DataFrame with generic column names if needed by the model
        processed_df = pd.DataFrame(
            processed_features, 
            columns=[str(i) for i in range(processed_features.shape[1])]
        )
        print("Data preprocessing completed.")
    except Exception as e:
        raise RuntimeError(f"Error during data preprocessing: {e}")

    # --- 4. Model Selection ---
    if MODEL_MODE == "default":
        current_model = model
        current_version = "default"
    elif MODEL_MODE == "ab":
        selected_version_key = rr_balancer.get_version()
        if selected_version_key == "v1":
            current_model = model_v1
            current_version = "v1.0"
        else: # selected_version_key == "v2"
            current_model = model_v2
            current_version = "v2.0"
        print(f"A/B Testing: Selected model version {current_version}")
    else:
        raise ValueError(f"Unsupported MODEL_MODE: {MODEL_MODE}")

    # --- 5. Prediction ---
    try:
        raw_prediction = current_model.predict(processed_df)[0]
        predicted_price_float = round(abs(float(raw_prediction)), 2)
        print(f"Raw prediction: {raw_prediction}, Rounded price: {predicted_price_float}")
    except Exception as e:
        raise RuntimeError(f"Error during model prediction: {e}")

    # --- 6. Post-Prediction Processing ---
    # Calculate confidence interval using float
    confidence_interval_floats = [
        round(predicted_price_float * 0.9, 2), 
        round(predicted_price_float * 1.1, 2)
    ]
    prediction_id = str(uuid.uuid4())

    # --- 7. Logging to DynamoDB (using Decimal for numerics) ---
    # Convert floats to Decimals for DynamoDB
    predicted_price_decimal = Decimal(str(predicted_price_float))
    confidence_interval_decimals = [Decimal(str(val)) for val in confidence_interval_floats]
    
    log_entry = {
        "prediction_id": prediction_id,
        "model_name": "house_price_regressor",
        "model_version": current_version,
        "input_data": json.dumps(body), # Store original input as string
        "predicted_price": predicted_price_decimal, # Use Decimal
        "confidence_interval": confidence_interval_decimals, # Use list of Decimals
        "prediction_time": datetime.now().isoformat() # ISO format string
    }
    # Log asynchronously or handle potential logging errors gracefully
    log_to_dynamodb(log_entry)

    # --- 8. Format Response ---
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
        "body": json.dumps({
            "predicted_price": predicted_price_float, # Return as standard float for JSON
            "confidence_interval": confidence_interval_floats, # Return as list of floats
            "prediction_id": prediction_id,
            "model_version": current_version # Optional: inform client of version used
        })
    }

# --- Main Lambda Handler ---
def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The runtime information of the Lambda function.
    Returns:
        dict: The response object.
    """
    print("Lambda handler invoked.")
    # Print event for debugging (be cautious with sensitive data in production)
    # print("DEBUG: Received event:", json.dumps(event))

    try:
        # --- Cold Start Check and Model Initialization ---
        # Check if models are already loaded (warm start) or need loading (cold start)
        if preprocessor is None:
            print("Models not found in memory. Triggering initialization...")
            initialize_models()
        else:
             print("Using models from warm execution environment.")

        # --- Perform Prediction ---
        response = predict_price(event)
        print("Prediction completed successfully.")
        return response

    except ValueError as ve: # Specific handling for client input/data errors
        print(f"Client Error: {ve}")
        return {
            "statusCode": 400, # Bad Request
            "body": json.dumps({"error": f"Invalid input data: {str(ve)}"})
        }
    except RuntimeError as re: # Specific handling for internal processing errors
         print(f"Runtime Error: {re}")
         return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Processing failed: {str(re)}"})
        }
    except Exception as e: # Catch-all for unexpected errors
        print(f"Unexpected Error: {e}")
        # Include traceback info for debugging (remove in production if sensitive)
        # import traceback
        # traceback.print_exc() 
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An internal error occurred: {str(e)}"} )
        }
