from zenml.pipelines import pipeline
from pipelines.steps import load_data_step, clean_data_step, save_data_step
from pathlib import Path

# Get the project root path (src/zenml_pipelines/../../)
# zenml login --local --docker
PROJECT_ROOT = Path(__file__).parent.parent.parent

@pipeline(enable_cache=False)
def data_processing_pipeline(
    input_path = str(PROJECT_ROOT / "data" / "raw" / "house_data.csv"),
    output_path = str(PROJECT_ROOT / "data" / "processed" / "cleaned_house_data.csv")
):
    """Modular data processing pipeline."""
    raw_df = load_data_step(input_path)
    cleaned_df = clean_data_step(raw_df)
    save_data_step(cleaned_df, output_path)