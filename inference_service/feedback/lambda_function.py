import json
import os
from decimal import Decimal 
import boto3

dynamodb = boto3.resource("dynamodb")
FEEDBACK_DYNAMODB_TABLE = os.environ.get("FEEDBACK_DYNAMODB_TABLE")

def lambda_handler(event, context):
    """
    AWS Lambda handler function for saving user feedback.
    Expects event['body'] to be a JSON string like:
    {"prediction_id": "...", "user_feedback": "...", "expected_price": 123.45}
    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The runtime information of the Lambda function.
    Returns:
        dict: The response object (statusCode, headers, body).
    """
    print("Feedback Lambda handler invoked.")

    try:
        # --- 1. Parse Input Data ---
        if "body" not in event or not event["body"]:
            raise ValueError("Invalid event structure: Missing or empty 'body' field.")

        try:
            body = json.loads(event["body"])
            print(f"Parsed feedback input: {body}")
        except json.JSONDecodeError as je:
            raise ValueError(f"Invalid JSON in request body: {je}")

        # --- 2. Validate Required Fields ---
        required_fields = ["prediction_id", "user_feedback"]
        for field in required_fields:
            if field not in body or not body[field]:
                 raise ValueError(f"Missing required field in request body: '{field}'")

        # --- 3. Prepare Log Entry for DynamoDB ---
        log_entry = {
            "prediction_id": body["prediction_id"],
            "user_feedback": body["user_feedback"],
            
        }
        if "expected_price" in body and body["expected_price"] is not None:
            # Convert float to Decimal for DynamoDB
            log_entry["expected_price"] = Decimal(str(body["expected_price"]))

      

        # --- 4. Save to DynamoDB ---
        table = dynamodb.Table(FEEDBACK_DYNAMODB_TABLE) 
        table.put_item(Item=log_entry)
        print(f"Successfully saved feedback for prediction ID {body['prediction_id']}.")

        # --- 5. Return Success Response ---
        return {
            "statusCode": 200,
            "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "POST,OPTIONS",
        },
            "body": json.dumps({"message": "Feedback saved successfully"})
        }

    except ValueError as ve: 
        print(f"Client Error (Bad Request): {ve}")
        return {
            "statusCode": 400, 
            "body": json.dumps({"error": f"Invalid input data: {str(ve)}"})
        }
    except Exception as e: 
        print(f"Internal Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An error occurred while saving feedback: {str(e)}"})
        }
