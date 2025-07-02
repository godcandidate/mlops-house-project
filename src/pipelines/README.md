# House Price Prediction MLOps Pipeline

This project implements a modular MLOps workflow for house price prediction using [ZenML](https://zenml.io/) and [MLflow](https://www.mlflow.org/). The pipeline is structured to handle data processing, feature engineering, model experimentation, and production-ready model training. ZenML and MLflow are set up using a Docker Compose file for consistent environments.

## Project Structure

The pipelines are organized under the `pipelines` directory:

```
├── pipelines
│   ├── data_pipeline.py        # Cleans raw data
│   ├── experiment_pipeline.py  # Experiments with feature selection and models
│   ├── feature_pipeline.py     # Creates features and preprocesses data
│   ├── model_pipeline.py       # Trains and logs the final model
│   └── steps.py                # Shared pipeline steps
```

## Pipelines Overview

### 🧹 Data Processing Pipeline (`data_pipeline.py`)

- **Purpose**: Loads raw data, cleans it, and saves the cleaned dataset.
- **Input**: `data/raw/house_data.csv`
- **Output**: `data/processed/cleaned_house_data.csv`

---

### 🔧 Feature Engineering Pipeline (`feature_pipeline.py`)

- **Purpose**: Applies feature engineering and preprocessing to cleaned data.
- **Input**: `data/processed/cleaned_house_data.csv`
- **Outputs**:
  - Featured data: `data/processed/house_data_featured.csv`
  - Preprocessor: `models/preprocessor.joblib`

---

### 🧪 Experiment Pipeline (`experiment_pipeline.py`)

- **Purpose**: Experiments with feature selection and model training to identify the best model.
- **Inputs**:
  - `data/processed/house_data_featured.csv`
  - `configs/model_config.yaml`
- **Output**: Best model configuration and results.

---

### 🏋️ Model Training Pipeline (`model_pipeline.py`)

- **Purpose**: Trains the final model, evaluates it, and logs results to MLflow.
- **Inputs**:
  - `data/processed/house_data_featured.csv`
  - `configs/model_config.yaml`
- **Output**: Trained model and metrics logged to MLflow at:  
  [http://localhost:5555](http://localhost:5555)

---

## Directory Layout

| Path              | Description                                           |
| ----------------- | ----------------------------------------------------- |
| `data/raw/`       | Raw input data (e.g., `house_data.csv`)               |
| `data/processed/` | Processed and featured data                           |
| `models/`         | Trained models and preprocessors                      |
| `configs/`        | Model configuration files (e.g., `model_config.yaml`) |

---

## Development and Production

- **Development**: Use `data_pipeline.py`, `feature_pipeline.py`, `experiment_pipeline.py` for feature and model experimentation.
- **Production**: Use `data_processing_pipeline.py` and `model_training_pipeline.py` for end-to-end data processing and model training.

---
