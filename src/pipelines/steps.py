from zenml import step
import pandas as pd
from data.run_processing import load_data, clean_data
from features.engineer import create_features, create_and_save_preprocessor, save_features_data, run_feature_engineering
from sklearn.compose import ColumnTransformer
from typing import Dict, Any
from sklearn.base import BaseEstimator
from models.train_model import load_config, train_model, evaluate_model, log_to_mlflow
from experimentation.experiment import select_features_with_rfe, train_and_evaluate_models, find_best_model, save_best_model
from typing import Tuple
from typing import Annotated
from zenml.integrations.s3.artifact_stores import S3ArtifactStore
from zenml.client import Client
from botocore.errorfactory import ClientError
from zenml.materializers.materializer_registry import materializer_registry
import pandas as pd
from .materializers.parquet_materializer import ParquetDataFrameMaterializer
import joblib
import yaml
from sklearn.model_selection import train_test_split


# Register globally
materializer_registry.register_and_overwrite_type(
    key=pd.DataFrame,
    type_=ParquetDataFrameMaterializer
)
# materializer_registry.register_and_overwrite_type(
#     key=pd.Series,
#     type_=ParquetSeriesMaterializer
# )

# materializer_registry.register_and_overwrite_type(
#     key=pd.Index,
#     type_=ParquetIndexMaterializer
# )

# DATA PROCESSING STEPS

# def load_data_step(input_path: str) -> pd.DataFrame:
#     return load_data(input_path)

@step
def load_data_step(data_path: str) -> pd.DataFrame:
    """Load data from S3 using the artifact store's authenticated filesystem."""
    artifact_store = Client().active_stack.artifact_store

    if not isinstance(artifact_store, S3ArtifactStore):
        raise ValueError("Active artifact store must be of type S3ArtifactStore")
    # input_path = f"{artifact_store.path.rstrip('/')}/{data_path}"
    input_path = f"s3://mlops-house-project/data/{data_path}"
    fs = artifact_store.filesystem  # already authenticated via service connector

    with fs.open(input_path, mode="rb") as f:
        return pd.read_csv(f)
        
@step
def clean_data_step(df: pd.DataFrame) -> pd.DataFrame:
    return clean_data(df)

@step
def save_data_step(data_path: str, df: pd.DataFrame):
    """Save DataFrame to S3 using the artifact store's authenticated filesystem."""
    # Get the active artifact store
    artifact_store = Client().active_stack.artifact_store
    if not isinstance(artifact_store, S3ArtifactStore):
        raise ValueError("Active artifact store must be of type S3ArtifactStore")

    # Use the artifact store's underlying filesystem
    fs = artifact_store.filesystem

    # Construct the full S3 path
   # output_path = f"{artifact_store.path.rstrip('/')}/{data_path}"
    output_path = f"s3://mlops-house-project/data/{data_path}"


    # Write CSV using the authenticated filesystem
    with fs.open(output_path, mode="w") as f:
        df.to_csv(f, index=False)


# FEATURE ENGINEERING STEPS
@step
def create_features_step(df: pd.DataFrame) -> pd.DataFrame:
    return create_features(df)

@step
def save_preprocessor_step(df_featured: pd.DataFrame):
    """Step to save the preprocessor and save featured data."""
    preprocessor = create_and_save_preprocessor(df_featured)
    featured_data = save_features_data(df_featured, preprocessor)

    artifact_store = Client().active_stack.artifact_store
    if not isinstance(artifact_store, S3ArtifactStore):
        raise ValueError("Active artifact store must be of type S3ArtifactStore")
    fs = artifact_store.filesystem

    output_path = f"s3://mlops-house-project/models/preprocessor.pkl"
    featured_data_path = f"s3://mlops-house-project/data/processed/featured_house_data.csv"

    with fs.open(output_path, mode="wb") as f:
        joblib.dump(preprocessor, f)
    with fs.open(featured_data_path, mode="wb") as f:
        featured_data.to_csv(f, index=False)


# EXPERIMENTATION STEPS

# Step 1: Load Data + Select Features
@step
def load_and_select_step(df: pd.DataFrame) -> Tuple[
    Annotated[pd.DataFrame, "X_train_selected"],
    Annotated[pd.DataFrame, "X_test_selected"],
    Annotated[pd.Series, "y_train"],
    Annotated[pd.Series, "y_test"],
    Annotated[pd.Index, "selected_features"]
]:
    """Load dataset and perform feature selection using RFE."""
    X = df.drop('price', axis=1)
    y = df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    selected_features, _ = select_features_with_rfe(X_train, y_train)
    
    return (
        X_train[selected_features],
        X_test[selected_features],
        y_train,
        y_test,
        selected_features
    )


# Step 2: Train Models
@step
def train_models_step(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Annotated[Dict[str, Any], "results"]:
    """Train multiple models and return evaluation results."""
    return train_and_evaluate_models(X_train, y_train, X_test, y_test)


# Step 3: Find Best Model + Save Config
@step
def save_best_model_step(
    results: Dict[str, Any],
    selected_features: pd.Index,
) -> Annotated[Dict[str, Any], "model_config"]:
    """Find best model and save config file."""
    best_name, best_result = find_best_model(results)
    model_config = save_best_model(best_name, best_result, selected_features)

    artifact_store = Client().active_stack.artifact_store
    if not isinstance(artifact_store, S3ArtifactStore):
        raise ValueError("Active artifact store must be of type S3ArtifactStore")
    fs = artifact_store.filesystem

    output_path = f"s3://mlops-house-project/configs/model_config.yaml"
    with fs.open(output_path, mode="w") as f:
        yaml.dump(model_config, f)
    return model_config

# MODEL TRAINING STEPS
@step
def load_config_step(config_path: str) -> Dict[str, Any]:
    """Load model configuration from YAML file."""
    artifact_store = Client().active_stack.artifact_store
    if not isinstance(artifact_store, S3ArtifactStore):
        raise ValueError("Active artifact store must be of type S3ArtifactStore")
    fs = artifact_store.filesystem
    input_path = f"s3://mlops-house-project/configs/{config_path}"
    with fs.open(input_path, mode="r") as f:
        return yaml.safe_load(f)



@step
def train_model_step(config: Dict[str, Any], data: pd.DataFrame) -> BaseEstimator:
    return train_model(config, data)

@step
def evaluate_model_step(model: BaseEstimator, data: pd.DataFrame) -> Dict[str, float]:
    return evaluate_model(model, data)

@step(enable_cache=False)
def log_to_mlflow_step(
    model: BaseEstimator,
    metrics: Dict[str, float],
    config: Dict[str, Any],
    model_name: str
):
    log_to_mlflow(model, metrics, config, model_name)