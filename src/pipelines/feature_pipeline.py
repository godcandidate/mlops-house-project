
from zenml.pipelines import pipeline
from pipelines.steps import load_data_step, create_features_step, save_preprocessor_step
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Cache set to false
@pipeline(enable_cache=False)
def feature_engineering_pipeline(
    output_path: str = str(PROJECT_ROOT / "data" / "processed" / "house_data_featured.csv"),
    preprocessor_path: str = str(PROJECT_ROOT / "models" / "preprocessor.joblib")
):
    """Pipeline to add features and preprocess data."""
    df = load_data_step(data_path="raw/house_data.csv")
    df_featured = create_features_step(df)
    save_preprocessor_step(df_featured)
    # df_transformed = run_preprocessing_step(input_path, output_path, preprocessor_path)
   