import pandas as pd
import json
from datetime import datetime
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import RegressionPreset

def main():
    try:
        # Load training data (reference data)
        reference_data = pd.read_csv("data/trained_data-gradient.csv")  # Contains: price, predicted_price, features...
        
        # Rename 'price' to 'true_price' for consistency
        reference_data = reference_data.rename(columns={'price': 'true_price'})
        
        print("Reference data columns:", reference_data.columns.tolist())
        print("Reference data shape:", reference_data.shape)

        # Current data for linear regression
        current_data = pd.read_csv("data/trained_data-regressor.csv")
        current_data = current_data.rename(columns={'price': 'true_price'})
        
        print("Current data columns:", current_data.columns.tolist())
        print("Current data shape:", current_data.shape)

        # # Load inference logs
        # with open("logs/inference.json", 'r') as f:
        #     inference_logs = json.load(f)

        # # Load feedback logs
        # with open("logs/feedback.json", 'r') as f:
        #     feedback_logs = json.load(f)

        # # Create DataFrame from inference logs
        # inference_data = []
        # for log in inference_logs:
        #     if 'prediction_id' not in log or 'input_data' not in log or 'predicted_price' not in log:
        #         raise ValueError("Inference log missing required fields")
        #     row = log['input_data'].copy()
        #     row['prediction_id'] = log['prediction_id']
        #     row['predicted_price'] = log['predicted_price']
        #     inference_data.append(row)
        # inference_df = pd.json_normalize(inference_data)

        # # Create DataFrame from feedback logs
        # feedback_df = pd.DataFrame(feedback_logs)[['prediction_id', 'user_feedback', 'expected_price']]

        # # Merge inference and feedback DataFrames
        # current_data = inference_df.merge(feedback_df, on='prediction_id', how='left')
        # print("Current data columns after merge:", current_data.columns.tolist())

        # # Create true_price based on feedback
        # current_data['true_price'] = current_data.apply(
        #     lambda row: row['predicted_price'] if row['user_feedback'] == 'positive'
        #     else row['expected_price'] if row['user_feedback'] == 'negative'
        #     else pd.NA, axis=1
        # )

        # # Drop rows with missing true_price (no feedback)
        # initial_count = len(current_data)
        # current_data = current_data.dropna(subset=['true_price'])
        # final_count = len(current_data)

        # if final_count == 0:
        #     raise ValueError("No valid data after merging; all records lack feedback")
        # print(f"Removed {initial_count - final_count} rows due to missing true_price.")

        # # Ensure numeric data types
        # current_data['true_price'] = pd.to_numeric(current_data['true_price'], errors='coerce')
        # current_data['predicted_price'] = pd.to_numeric(current_data['predicted_price'], errors='coerce')
        
        # # Convert all feature columns to numeric where possible
        # feature_columns = ['sqft', 'bedrooms', 'bathrooms', 'year_built', 'house_age', 'bed_bath_ratio', 'price_per_sqft']
        # for col in feature_columns:
        #     if col in current_data.columns:
        #         current_data[col] = pd.to_numeric(current_data[col], errors='coerce')

        print("Current data shape after processing:", current_data.shape)
        print("Reference data shape:", reference_data.shape)

        # Define column mapping
        column_mapping = ColumnMapping()
        column_mapping.target = 'true_price'
        column_mapping.prediction = 'predicted_price'
        column_mapping.numerical_features = ['sqft', 'bedrooms', 'bathrooms', 'year_built']
        column_mapping.categorical_features = ['location', 'condition']

        # Generate regression performance report
        report = Report(metrics=[RegressionPreset()])
        report.run(
            reference_data=reference_data,  # Your training data
            current_data=current_data,      # Your inference + feedback data
            column_mapping=column_mapping
        )

        # Save report
        report_path = "reports/model_performance_report-1.html"
        report.save_html(report_path)
        print(f"✅ Performance report generated at {report_path}")

       
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()