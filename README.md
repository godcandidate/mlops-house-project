#  MLOps House Price Prediction Project

End-to-end MLOps pipeline for house price prediction with monitoring, inference, and automated workflows.

<p align="center"> <img src="infra.png" alt="MLOP AWS Architecture" width="800"> </p>

## 🏗️ Architecture

- **ML Pipeline**: Data processing → Feature engineering → Model training
- **Experiment Tracking**: MLflow for model versioning and metrics
- **Inference**: AWS Lambda functions for predictions and feedback
- **Monitoring**: Streamlit dashboard with Evidently for model drift detection
- **Orchestration**: ZenML pipelines with automated workflows

## 📁 Project Structure

```
mlops-house-project/
├── data                # Raw and processed datasets
├── inference           # Serverless inference endpoints
├── monitoring          # Model monitoring and drift detection
├── notebooks           # Jupyter notebooks for exploration
├── src                 # Core ML pipeline code
└── .github/workflows/  # CI/CD automation
```



## 🔧 Key Components

- **ZenML Pipelines**: Orchestrated ML workflows
- **MLflow**: Experiment tracking and model registry
- **Evidently**: Data drift and model performance monitoring
- **AWS Lambda**: Serverless inference endpoints
- **Streamlit**: Interactive monitoring dashboard
- **FastAPI**: Local development API

## 📊 Monitoring

The monitoring dashboard provides:
- Model performance metrics
- Data drift detection
- A/B testing results
- Real-time inference logs