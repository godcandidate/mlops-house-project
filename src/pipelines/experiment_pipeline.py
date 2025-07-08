from zenml.pipelines import pipeline
from pipelines.steps import (
    load_data_step,
    load_and_select_step,
    train_models_step,
    save_best_model_step
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

@pipeline(enable_cache=False)
def experiment_pipeline(
):
    """Optimized pipeline for experimentation."""
    # Step 1: Load data and select features
    df_featured = load_data_step(data_path="processed/featured_house_data.csv")
    X_train_sel, X_test_sel, y_train, y_test, selected_features = load_and_select_step(df_featured)

    # Step 2: Train and evaluate models
    results = train_models_step(
        X_train=X_train_sel,
        y_train=y_train,
        X_test=X_test_sel,
        y_test=y_test
    )

    # Step 3: Finalize and save config
    save_best_model_step(
        results=results,
        selected_features=selected_features,
    )

