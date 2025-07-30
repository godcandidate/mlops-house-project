import pandas as pd
import json
from datetime import datetime
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import RegressionPreset
import os

def main():
    try:
        # Load training data (reference data) - gradient boosting model
        reference_data = pd.read_csv("data/trained_data-gradient.csv")  # Contains: price, predicted_price, features...
        
        # Rename 'price' to 'true_price' for consistency
        reference_data = reference_data.rename(columns={'price': 'true_price'})
    

        # Current data for linear regression
        current_data = pd.read_csv("data/trained_data-regressor.csv")
        current_data = current_data.rename(columns={'price': 'true_price'})
        

        # Define column mapping
        column_mapping = ColumnMapping()
        column_mapping.target = 'true_price'
        column_mapping.prediction = 'predicted_price'
        column_mapping.numerical_features = ['sqft', 'bedrooms', 'bathrooms', 'year_built']
        column_mapping.categorical_features = ['location', 'condition']

        # Generate regression performance report
        report = Report(metrics=[RegressionPreset()])
        report.run(
            reference_data=reference_data,
            current_data=current_data,      
            column_mapping=column_mapping
        )

        # Ensure the 'reports' directory exists
        os.makedirs("reports", exist_ok=True)

         # Save report
        report_path = "reports/model_performance_report.html"
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