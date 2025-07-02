import pandas as pd
import numpy as np
import joblib
import yaml
import os
import logging
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_selection import RFE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data_exp(data_path: str):
    """Load and split dataset."""
    logger.info(f"Loading data from {data_path}")
    data = pd.read_csv(data_path)
    X = data.drop('price', axis=1)
    y = data['price']
    return train_test_split(X, y, test_size=0.2, random_state=42)


def select_features_with_rfe(X_train, y_train, n_features=10):
    """Use Recursive Feature Elimination with XGBoost."""
    logger.info("Selecting features using RFE")
    selector = RFE(estimator=XGBRegressor(objective='reg:squarederror'), n_features_to_select=n_features)
    selector.fit(X_train, y_train)
    selected_features = X_train.columns[selector.support_]
    ignored_features = X_train.columns[~selector.support_]

    print("Top 10 Selected Features by RFE:")
    for f in selected_features:
        print(f" - {f}")

    print("Features Ignored by RFE:")
    for f in ignored_features:
        print(f" - {f}")

    return selected_features, ignored_features

def train_and_evaluate_models(X_train, y_train, X_test, y_test):
    """Train and evaluate multiple models with optional hyperparameter tuning."""
    logger.info("Training and evaluating models")

    models = {
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(),
        'GradientBoosting': GradientBoostingRegressor(),
        'XGBoost': XGBRegressor(objective='reg:squarederror')
    }

    grids = {
        'LinearRegression': {},
        'RandomForest': {'n_estimators': [100, 150], 'max_depth': [None, 10, 20]},
        'GradientBoosting': {'n_estimators': [100, 250], 'learning_rate': [0.1, 0.05], 'max_depth': [3, 10]},
        'XGBoost': {'n_estimators': [100, 150], 'learning_rate': [0.1, 0.05], 'max_depth': [3, 10]}
    }

    results = {}

    for name, model in models.items():
        logger.info(f"Training {name}...")
        grid = grids[name]

        if grid:
            clf = GridSearchCV(model, grid, cv=3, scoring='r2', n_jobs=-1)
            clf.fit(X_train, y_train)
            best_model = clf.best_estimator_
            best_params = clf.best_params_
        else:
            model.fit(X_train, y_train)
            best_model = model
            best_params = model.get_params()

        y_pred = best_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        results[name] = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2),
            'model': best_model,
            'params': best_params
        }

        logger.info(f"{name}: R²={r2:.4f}, RMSE={rmse:.2f}")

    return results

def find_best_model(results):
    """Find the model with highest R² score."""
    best_name = max(results, key=lambda x: results[x]['r2'])
    best_result = results[best_name]
    logger.info(f"🏆 Best Model: {best_name}")
    logger.info(f"   R² Score: {best_result['r2']:.4f}")
    logger.info(f"   MAE: {best_result['mae']:.2f}")
    logger.info(f"   RMSE: {best_result['rmse']:.2f}")
    return best_name, best_result

def save_model_config(best_name, best_result, selected_features, output_path):
    """Save the best model config to YAML."""
    logger.info(f"Saving model config to {output_path}")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    model_config = {
        'model': {
            'name': 'house_price_model',
            'best_model': best_name,
            'target_variable': 'price',
            'parameters': best_result['params'],
            'r2_score': best_result['r2'],
            'mae': best_result['mae'],
            'feature_sets': {
                'rfe': list(selected_features)
            }
        }
    }

    with open(output_path, 'w') as f:
        yaml.dump(model_config, f)

    return model_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run model experiments and generate config.")
    parser.add_argument("--data", type=str, default="../data/processed/featured_house_data.csv")
    parser.add_argument("--config", type=str, default="../configs/model_config.yaml")
    args = parser.parse_args()

    # Step 1: Load data
    X_train, X_test, y_train, y_test = load_data_exp(args.data)

    # Step 2: Select features
    selected_features, ignored_features = select_features_with_rfe(X_train, y_train)

    # Step 3: Train and evaluate models
    results = train_and_evaluate_models(X_train[selected_features], y_train, X_test[selected_features], y_test)

    # Step 4: Find best model
    best_name, best_result = find_best_model(results)

    # Step 5: Save config
    save_model_config(best_name, best_result, selected_features, args.config)