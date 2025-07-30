import joblib
import pandas as pd
from datetime import datetime
from schemas import HousePredictionRequest, PredictionResponse, FeedbackRequest
import uuid
import json
import os
from datetime import datetime
from utils import ModelConfig
import threading

# Load model and preprocessor
PREPROCESSOR_PATH = "../../models/testing/preprocessor.pkl"

INFERENCE_LOG_PATH = "../../logs/inference.log"
FEEDBACK_LOG_PATH = "../../logs/feedback.log"

# Load models conditionally
MODEL_DIR = "../../models/testing"

# Load models based on config
print(ModelConfig.MODE)
if ModelConfig.MODE == "default":
    model = joblib.load(os.path.join(MODEL_DIR, "gradient-boost-v1.0.pkl"))
    MODEL_VERSION = "v1.0"
elif ModelConfig.MODE == "ab":
    model_v1 = joblib.load(os.path.join(MODEL_DIR, "regressor-v1.0.pkl"))
    model_v2 = joblib.load(os.path.join(MODEL_DIR, "regressor-v2.0.pkl"))
    MODEL_VERSION = "ab"
else:
    raise ValueError(f"Unsupported MODEL_MODE: {ModelConfig.MODE}")

# RoundRobinBalancer
class RoundRobinBalancer:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

    def get_version(self, versions=["v1", "v2"]):
        with self.lock:
            self.counter += 1
            return versions[self.counter % len(versions)]

# Instantiate the balancer
rr_balancer = RoundRobinBalancer()

def get_model():
    selected = rr_balancer.get_version()
    return (model_v1, "v1.0") if selected == "v1" else (model_v2, "v2.0")

try:
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    MODEL_NAME = "house_price_regressor"

except Exception as e:
    raise RuntimeError(f"Error loading model or preprocessor: {str(e)}")


def log_prediction(input_data: dict, predicted_price: float, model_name: str, model_version: str):
    """
    Logs prediction data to a JSON file.
    """
    prediction_id = str(uuid.uuid4())
    log_entry = {
        "prediction_id": prediction_id,
        "model_name": model_name,
        "model_version": model_version,
        "input_data": input_data,
        "predicted_price": predicted_price,
        "prediction_time": datetime.now().isoformat()
    }

    # Ensure log directory exists
    os.makedirs(os.path.dirname(INFERENCE_LOG_PATH), exist_ok=True)

    # Append log entry to file
    with open(INFERENCE_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return prediction_id



def predict_price(request: HousePredictionRequest) -> PredictionResponse:
    """
    Predict house price based on input features.
    """
    # Prepare input data
    input_data = pd.DataFrame([request.dict()])
    input_data['house_age'] = datetime.now().year - input_data['year_built']
    input_data['bed_bath_ratio'] = input_data['bedrooms'] / input_data['bathrooms']
    input_data['price_per_sqft'] = 0  # Dummy value for compatibility

    # Preprocess input data
    processed_features = preprocessor.transform(input_data)
    processed_df = pd.DataFrame(processed_features, columns=[str(i) for i in range(processed_features.shape[1])])

    # Get model
    # Get model
    if ModelConfig.MODE == "default":
        current_model = model  # global variable from top of file
        current_model_version = MODEL_VERSION  # from top of file
    elif ModelConfig.MODE == "ab":
        current_model, current_model_version = get_model()
    else:
        raise ValueError(f"Unsupported MODEL_MODE: {ModelConfig.MODE}")
   
    predicted_price = current_model.predict(processed_df)[0]

    # Convert numpy.float32 to Python float and round to 2 decimal places
    predicted_price = round(abs(float(predicted_price)), 2)

    # Confidence interval (10% range)
    confidence_interval = [abs(predicted_price * 0.9), abs(predicted_price * 1.1)]

    # Convert confidence interval values to Python float and round to 2 decimal places
    confidence_interval = [round(float(value), 2) for value in confidence_interval]

    # Log prediction
    prediction_id = log_prediction(
        input_data=input_data.to_dict(orient="records")[0],
        predicted_price=predicted_price,
        model_name=MODEL_NAME,
        model_version=current_model_version
    )


    return PredictionResponse(
        predicted_price=predicted_price,
        confidence_interval=confidence_interval,
        prediction_id=prediction_id
    )

def batch_predict(requests: list[HousePredictionRequest]) -> list[float]:
    """
    Perform batch predictions.
    """
    input_data = pd.DataFrame([req.dict() for req in requests])
    input_data['house_age'] = datetime.now().year - input_data['year_built']
    input_data['bed_bath_ratio'] = input_data['bedrooms'] / input_data['bathrooms']
    input_data['price_per_sqft'] = 0  # Dummy value for compatibility

    # Preprocess input data
    processed_features = preprocessor.transform(input_data)

    # Make predictions
    predictions = model.predict(processed_features)
    return predictions.tolist()


def save_feedback(feedback: FeedbackRequest):
    """
    Logs user feedback for a prediction.
    """
    log_entry = {
        "prediction_id": feedback.prediction_id,
        "user_feedback": feedback.user_feedback,
        "expected_price": feedback.expected_price
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(FEEDBACK_LOG_PATH), exist_ok=True)

    # Append feedback to log file
    with open(FEEDBACK_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return "Feedback saved successfully"