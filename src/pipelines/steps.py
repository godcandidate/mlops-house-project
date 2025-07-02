from zenml import step
import pandas as pd
from data.run_processing import load_data, clean_data
from features.engineer import create_features, create_and_save_preprocessor, run_feature_engineering
from sklearn.compose import ColumnTransformer
from typing import Dict, Any
from sklearn.base import BaseEstimator
from models.train_model import load_config, train_model, evaluate_model, log_to_mlflow
from experimentation.experiment import load_data_exp, select_features_with_rfe, train_and_evaluate_models, find_best_model, save_model_config
from typing import Tuple
from typing import Annotated

# DATA PROCESSING STEPS
@step
def load_data_step(input_path: str) -> pd.DataFrame:
    return load_data(input_path)

@step
def clean_data_step(df: pd.DataFrame) -> pd.DataFrame:
    return clean_data(df)

@step
def save_data_step(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, index=False)


# FEATURE ENGINEERING STEPS
@step
def create_features_step(df: pd.DataFrame) -> pd.DataFrame:
    return create_features(df)

@step
def create_preprocessor_step(df: pd.DataFrame, preprocessor_path: str):
    """Step to create, fit, and save the preprocessor."""
    return create_and_save_preprocessor(df, preprocessor_path)

@step
def run_preprocessing_step(
    input_file: str,
    output_file: str,
    preprocessor_file: str
):
    return run_feature_engineering(input_file, output_file, preprocessor_file)

# EXPERIMENTATION STEPS
# @step
# def load_data_exp_step(data_path: str) -> Tuple[
#     Annotated[pd.DataFrame, "X_train"],
#     Annotated[pd.DataFrame, "X_test"],
#     Annotated[pd.Series, "y_train"],
#     Annotated[pd.Series, "y_test"]
# ]:
#     """Step to load and split dataset."""
#     X_train, X_test, y_train, y_test = load_data_exp(data_path)
#     return X_train, X_test, y_train, y_test

# @step
# def select_features_step(X_train: pd.DataFrame, y_train: pd.Series) -> pd.Index:
#     """Select top features using RFE."""
#     selected_features, _ = select_features_with_rfe(X_train, y_train)
#     return selected_features

# @step
# def train_models_step(
#     X_train: pd.DataFrame,
#     y_train: pd.Series,
#     X_test: pd.DataFrame,
#     y_test: pd.Series
# ) -> Dict[str, Any]:
#     """Train and evaluate multiple models."""
#     return train_and_evaluate_models(X_train, y_train, X_test, y_test)

# @step
# def find_best_model_step(results: dict) -> Tuple[str, dict]:
#     """Find the best model based on R² score."""
#     return find_best_model(results)

# @step
# def save_model_config_step(
#     best_name: str,
#     best_result: dict,
#     selected_features: pd.Index,
#     config_path: str
# ):
#     """Save the best model config to disk."""
#     save_model_config(best_name, best_result, selected_features, config_path)

# Step 1: Load Data + Select Features
@step
def load_and_select_step(data_path: str) -> Tuple[
    Annotated[pd.DataFrame, "X_train_selected"],
    Annotated[pd.DataFrame, "X_test_selected"],
    Annotated[pd.Series, "y_train"],
    Annotated[pd.Series, "y_test"],
    Annotated[pd.Index, "selected_features"]
]:
    """Load dataset and perform feature selection using RFE."""
    X_train, X_test, y_train, y_test = load_data_exp(data_path)
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
@step(enable_cache=False)
def get_best_model_step(
    results: Dict[str, Any],
    selected_features: pd.Index,
    config_path: str
) -> Tuple[
    Annotated[str, "best_model_name"],
    Annotated[Dict[str, Any], "best_model_result"]
]:
    """Find best model and save config file."""
    best_name, best_result = find_best_model(results)
    save_model_config(best_name, best_result, selected_features, config_path)
    return best_name, best_result

# MODEL TRAINING STEPS
@step
def load_config_step(config_path: str) -> Dict[str, Any]:
    return load_config(config_path)

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