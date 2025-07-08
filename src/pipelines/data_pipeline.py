from zenml.pipelines import pipeline
from pipelines.steps import load_data_step, clean_data_step, save_data_step
from pathlib import Path

# Get the project root path (src/zenml_pipelines/../../)
# zenml login --local --docker
PROJECT_ROOT = Path(__file__).parent.parent.parent


@pipeline(enable_cache=False)
def data_processing_pipeline(
):
    """Modular data processing pipeline."""
    raw_df = load_data_step(data_path="dev/raw/house_data.csv")
    cleaned_df = clean_data_step(raw_df)
    save_data_step(data_path="dev/processed/cleaned_house_data.csv", df=cleaned_df)