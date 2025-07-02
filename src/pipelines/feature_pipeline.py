
from zenml.pipelines import pipeline
from pipelines.steps import load_data_step, create_features_step, create_preprocessor_step
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

# Cache set to false
@pipeline(enable_cache=False)
def feature_engineering_pipeline(
    input_path: str = str(PROJECT_ROOT / "data" / "processed" / "cleaned_house_data.csv"),
    output_path: str = str(PROJECT_ROOT / "data" / "processed" / "house_data_featured.csv"),
    preprocessor_path: str = str(PROJECT_ROOT / "models" / "preprocessor.joblib")
):
    """Pipeline to add features and preprocess data."""
    df = load_data_step(input_path)
    df_featured = create_features_step(df)
    create_preprocessor_step(df_featured, preprocessor_path)
    # df_transformed = run_preprocessing_step(input_path, output_path, preprocessor_path)
   