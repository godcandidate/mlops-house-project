import argparse
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
import xgboost as xgb
import yaml
import logging
from mlflow.tracking import MlflowClient
import platform
import sklearn

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# Load model from config
# -----------------------------
def get_model_instance(name, params):
    model_map = {
        'LinearRegression': LinearRegression,
        'RandomForest': RandomForestRegressor,
        'GradientBoosting': GradientBoostingRegressor,
        'XGBoost': xgb.XGBRegressor
    }
    if name not in model_map:
        raise ValueError(f"Unsupported model: {name}")
    return model_map[name](**params)

# -----------------------------
# Step 1: Load Config
# -----------------------------
def load_config(config_path: str) -> dict:
    """Load YAML config."""
    logger.info(f"Loading config from {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

# -----------------------------
# Step 2: Load Data
# -----------------------------
def load_data(data_path: str) -> pd.DataFrame:
    """Load dataset."""
    logger.info(f"Loading data from {data_path}")
    return pd.read_csv(data_path)

# -----------------------------
# Step 3: Train Model
# -----------------------------
def train_model(config: dict, data: pd.DataFrame) -> object:
    """Train model using config and data."""
    model_cfg = config["model"]
    target = model_cfg['target_variable']

    X = data.drop(columns=[target])
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logger.info(f"Training model: {model_cfg['best_model']}")
    model = get_model_instance(model_cfg['best_model'], model_cfg['parameters'])
    model.fit(X_train, y_train)

    return model

# -----------------------------
# Step 4: Evaluate Model
# -----------------------------
def evaluate_model(model, data: pd.DataFrame) -> dict:
    """Evaluate model performance."""
    X = data.drop(columns=['price'])  # or use target var from config
    y = data['price']
    y_pred = model.predict(X)

    mae = float(mean_absolute_error(y, y_pred))
    r2 = float(r2_score(y, y_pred))

    logger.info(f"Evaluation complete. MAE: {mae:.2f}, R²: {r2:.4f}")
    return {"mae": mae, "r2": r2}

# -----------------------------
# Step 5: Log to MLflow
# -----------------------------
def log_to_mlflow(model, metrics: dict, config: dict, model_name: str):
    """Log model + metrics to MLflow and register model."""
    model_cfg = config["model"]
    target = model_cfg['target_variable']

    mlflow.set_experiment(model_name)

    with mlflow.start_run(run_name="final_training") as run:
        mlflow.log_params(model.get_params())
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, "tuned_model")
        model_uri = f"runs:/{run.info.run_id}/tuned_model"

        client = MlflowClient()
        try:
            client.create_registered_model(model_name)
        except Exception:
            pass  # Already exists

        model_version = client.create_model_version(
            name=model_name,
            source=model_uri,
            run_id=run.info.run_id
        )

        client.transition_model_version_stage(
            name=model_name,
            version=model_version.version,
            stage="Staging"
        )

        description = (
            f"Model for predicting house prices.\n"
            f"Algorithm: {model_cfg['best_model']}\n"
            f"Hyperparameters: {model_cfg['parameters']}\n"
            f"Target variable: {target}\n"
            f"Performance metrics:\n"
            f"  - MAE: {metrics['mae']:.2f}\n"
            f"  - R²: {metrics['r2']:.4f}"
        )
        client.update_registered_model(model_name, description)

        deps = {
            "python_version": platform.python_version(),
            "scikit_learn_version": sklearn.__version__,
            "xgboost_version": xgb.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
        }
        for k, v in deps.items():
            client.set_registered_model_tag(model_name, k, v)

        logger.info(f"Registered model '{model_name}' with version {model_version.version}")

# -----------------------------
# Main function (for standalone run)
# -----------------------------
def main(config_path: str, data_path: str, models_dir: str, model_name: str, mlflow_tracking_uri: str = None):
    if mlflow_tracking_uri:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
    config = load_config(config_path)
    data = load_data(data_path)
    model = train_model(config, data)
    metrics = evaluate_model(model, data)
    log_to_mlflow(model, metrics, config, model_name)

# -----------------------------
# CLI Entry Point
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and register final model from config.")
    parser.add_argument("--config", type=str, required=True, help="Path to model_config.yaml")
    parser.add_argument("--data", type=str, required=True, help="Path to processed CSV dataset")
    parser.add_argument("--models-dir", type=str, required=True, help="Directory to save trained model")
    parser.add_argument("--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI")
    parser.add_argument("--model-name", type=str, default="house_price_model", help="Name of the registered model")

    args = parser.parse_args()

    main(
        config_path=args.config,
        data_path=args.data,
        models_dir=args.models_dir,
        model_name=args.model_name,
        mlflow_tracking_uri=args.mlflow_tracking_uri
    )