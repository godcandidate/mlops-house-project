from zenml.pipelines import pipeline
import mlflow
from pipelines.steps import (
    load_config_step,
    load_data_step,
    train_model_step,
    evaluate_model_step,
    log_to_mlflow_step
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

@pipeline(enable_cache=False)
def model_training_pipeline(
    #config_path: str = str(PROJECT_ROOT / "configs" / "model_config.yaml"),
    config_path: str = "/home/edward/Desktop/Personal projects/mlops-house-project/configs/model_config.yaml",
    data_path: str = str(PROJECT_ROOT / "data" / "processed" / "featured_house_data.csv"),
    model_name: str = "house_price_model",
    mlflow_tracking_uri: str = "http://localhost:5555"
):
    # Set mlflow tracking uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    config = load_config_step(config_path)
    data = load_data_step(data_path)
    model = train_model_step(config=config, data=data)
    metrics = evaluate_model_step(model=model, data=data)
    log_to_mlflow_step(model=model, metrics=metrics, config=config, model_name=model_name)