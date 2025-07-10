from pipelines.data_pipeline import data_processing_pipeline
from zenml.code_repositories import get_code_repository

if __name__ == "__main__":
    # Link to the registered GitHub repository
    repo = get_code_repository("mlops-house-project")

    # Run the pipeline with the code repository attached
    data_processing_pipeline().run(code_repository=repo)