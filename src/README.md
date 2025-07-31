# Source Code

Core ML pipeline implementation for house price prediction.

## 📁 Structure

```
src/
├── data/               # Data processing scripts
├── features/           # Feature engineering pipeline
├── models/             # Model training and evaluation
├── pipelines/          # ZenML pipeline definitions
├── run_data_pipeline.py
├── run_feature_pipeline.py
└── run_model_pipeline.py
```

## 🚀 Usage

### Run Individual Pipelines

```bash
# Data processing
python run_data_pipeline.py

# Feature engineering
python run_feature_pipeline.py

# Model training
python run_model_pipeline.py
```



## 📦 Components

- **data/**: Raw data cleaning and preprocessing
- **features/**: Feature transformation and engineering
- **models/**: Model training, evaluation, and saving
- **pipelines/**: ZenML orchestrated workflows
- **api/**: FastAPI service for local testing