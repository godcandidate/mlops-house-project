import joblib
import pandas as pd
from datetime import datetime

MODEL_PATH = "../../models/trained/house_price_model.pkl"
PREPROCESSOR_PATH = "../../models/trained/preprocessor.pkl"

# Load model and preprocessor
try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model or preprocessor: {str(e)}")

# Helper function to get feature names from preprocessor
def get_feature_names(column_transformer):
    feature_names = []
    for name, transformer, columns in column_transformer.transformers_:
        if transformer == 'drop':
            continue
        if transformer == 'passthrough':
            if isinstance(columns, list):
                feature_names.extend(columns)
            else:
                feature_names.append(columns)
        else:
            if hasattr(transformer, 'get_feature_names_out'):
                try:
                    names = transformer.get_feature_names_out(columns)
                    feature_names.extend(names)
                except Exception:
                    if isinstance(columns, list):
                        feature_names.extend(columns)
                    else:
                        feature_names.append(columns)
            else:
                if isinstance(columns, list):
                    feature_names.extend(columns)
                else:
                    feature_names.append(columns)
    return feature_names

# Sample input dictionary
sample_input_dict = {
    'year_built': 1950,
    'bedrooms': 3,
    'bathrooms': 2,
    'sqft': 1500,
    'location': 'New York',
    'condition': 'Good',
}

# Create DataFrame from input dict
input_df = pd.DataFrame([sample_input_dict])

# Add engineered features as expected by the preprocessor/model
input_df['house_age'] = datetime.now().year - input_df['year_built']
input_df['bed_bath_ratio'] = input_df['bedrooms'] / input_df['bathrooms']
input_df['price_per_sqft'] = 1  # Dummy value for compatibility

# Preprocess the input data
processed_features = preprocessor.transform(input_df)

# Get feature names from preprocessor
feature_names = get_feature_names(preprocessor)

# Build DataFrame with processed features and names for inspection
processed_df = pd.DataFrame(processed_features, columns=feature_names)

print("Processed features with names:")
print(processed_df)

# Make prediction
predicted_price = model.predict(processed_features)[0]
print(f"\nPredicted price: {predicted_price:.2f}")
