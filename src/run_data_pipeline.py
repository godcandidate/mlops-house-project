from pipelines.data_pipeline import data_processing_pipeline
from zenml.client import Client

if __name__ == "__main__":
    # Get the registered GitHub code repository
    repo = Client().get_code_repository("mlops-house-project")

    # Run the pipeline with the associated code repository
    data_processing_pipeline().run(code_repository=repo)