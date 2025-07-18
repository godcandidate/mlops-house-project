import pandas as pd
import json
from evidently.report import Report
from evidently.metric_preset import TargetDriftPreset
from evidently.pipeline.column_mapping import ColumnMapping

def main():
    try:
        # Load reference data (from training)
        reference_data = pd.read_csv("data/trained_data.csv")
        print("Reference data columns:", reference_data.columns.tolist())

        # Validate presence of 'price' in reference_data
        if 'price' not in reference_data.columns:
            raise ValueError("Column 'price' missing in reference_data")
        # Add mock predictions (simulating predictions as price for reference)
        reference_data['predicted_price'] = reference_data['price']

        # Load current data from inference logs
        with open("logs/inference.json", 'r') as f:
            logs = json.load(f)

        # Extract input features and predicted_price from each log
        input_features = []
        predictions = []

        for log in logs:
            if 'input_data' not in log or 'predicted_price' not in log:
                raise ValueError("Log entry missing 'input_data' or 'predicted_price'")
            input_features.append(log['input_data'])
            predictions.append(log['predicted_price'])

        # Create current_data DataFrame
        current_data = pd.json_normalize(input_features)
        current_data['predicted_price'] = predictions
        print("Current data columns:", current_data.columns.tolist())

        # Rename 'predicted_price' to 'price' in current_data to align with reference_data target
        current_data = current_data.rename(columns={'predicted_price': 'price'})

        # Ensure correct data types
        try:
            reference_data['price'] = reference_data['price'].astype(float)
            current_data['price'] = current_data['price'].astype(float)
            # Convert numerical features to consistent types
            for col in ['sqft', 'bedrooms', 'bathrooms', 'year_built']:
                if col in reference_data.columns and col in current_data.columns:
                    reference_data[col] = pd.to_numeric(reference_data[col], errors='coerce')
                    current_data[col] = pd.to_numeric(current_data[col], errors='coerce')
        except ValueError as e:
            raise ValueError("Failed to convert columns to numeric: " + str(e))

        # Define column mapping
        column_mapping = ColumnMapping(
            target='price',  # Both datasets now use 'price' as the target column
            prediction=None,  # No predictions needed for TargetDriftPreset
            numerical_features=['sqft', 'bedrooms', 'bathrooms', 'year_built'],
            categorical_features=['location', 'condition']
        )

        # Build the report with TargetDriftPreset
        report = Report(metrics=[TargetDriftPreset()])

        # Run the report
        report.run(
            reference_data=reference_data,
            current_data=current_data,
            column_mapping=column_mapping
        )

        # Save the report
        report.save_html("reports/prediction_target_drift_report.html")
        print("✅ Drift report generated at reports/prediction_target_drift_report.html")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()