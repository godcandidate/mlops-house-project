import pandas as pd
import json
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

def main():
    # Load the training data
    reference_data = pd.read_csv("data/trained_data.csv")
    
    # Load and process inference logs
    with open("logs/inference.json", 'r') as f:
        logs = json.load(f)
    
    # Extract input features from the nested structure
    current_data = pd.json_normalize([log['input_data'] for log in logs])
    
    # Ensure consistent case for categorical columns
    if 'location' in current_data.columns:
        current_data['location'] = current_data['location'].str.title()
    if 'condition' in current_data.columns:
        current_data['condition'] = current_data['condition'].str.title()
    
    # Select only the columns that exist in both datasets
    common_columns = list(set(reference_data.columns) & set(current_data.columns))
    print("Common columns:", common_columns)
    print("Reference columns:", reference_data.columns.tolist())
    print("Current columns:", current_data.columns.tolist())
    print("Reference missing values:", reference_data[common_columns].isna().sum())
    print("Current missing values:", current_data[common_columns].isna().sum())
    
    # Align data types
    for col in common_columns:
        if reference_data[col].dtype != current_data[col].dtype:
            try:
                current_data[col] = current_data[col].astype(reference_data[col].dtype)
                print(f"Converted {col} to {reference_data[col].dtype}")
            except Exception as e:
                print(f"Type conversion failed for {col}: {e}")
    
    # Select only common columns
    reference_data = reference_data[common_columns]
    current_data = current_data[common_columns]
    
    # Create a data drift report
    report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset()
    ])
    
    # Run the report
    report.run(
        reference_data=reference_data,
        current_data=current_data
    )
    
    # Save HTML report
    report.save_html("reports/data_drift_report-1.html")
    print("✅ Data drift report generated at reports/data_drift_report.html")
    
if __name__ == "__main__":
    main()