from evidently.report import Report
from evidently.metrics import PredictionDriftMetric
import pandas as pd

# Load reference predictions (e.g., from training or baseline period)
# Option 1: If you have stored predictions from training
reference_predictions = pd.read_csv("data/train_predictions.csv")  # shape: (n_samples, 1)

# Option 2: If you don't have stored predictions, make predictions on training data now
# reference_predictions = model.predict(preprocessor.transform(reference_data))

from io import StringIO

# Load current predictions from inference logs
with open("logs/inference.json", 'r') as f:
    inference_logs = pd.read_json(StringIO('\n'.join(f.readlines())), lines=True)
    
current_predictions = inference_logs[["predicted_price"]]

# Run prediction drift report
report = Report(metrics=[PredictionDriftMetric()])
report.run(
    reference_data=reference_predictions,
    current_data=current_predictions,
    column_mapping={"prediction": "predicted_price"}
)

# Save HTML report
report.save_html("reports/prediction_drift_report.html")