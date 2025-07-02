from zenml.pipelines import pipeline
from pipelines.steps import (
    load_and_select_step,
    train_models_step,
    get_best_model_step
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

@pipeline(enable_cache=False)
def experiment_pipeline(
    data_path: str = str(PROJECT_ROOT / "data" / "processed" / "featured_house_data.csv"),
    config_path: str = str(PROJECT_ROOT / "configs" / "model_config.yaml")
):
    """Optimized pipeline for experimentation."""
    # Step 1: Load data and select features
    X_train_sel, X_test_sel, y_train, y_test, selected_features = load_and_select_step(data_path=data_path)

    # Step 2: Train and evaluate models
    results = train_models_step(
        X_train=X_train_sel,
        y_train=y_train,
        X_test=X_test_sel,
        y_test=y_test
    )

    # Step 3: Finalize and save config
    best_name, best_result = get_best_model_step(
        results=results,
        selected_features=selected_features,
        config_path=config_path
    )

