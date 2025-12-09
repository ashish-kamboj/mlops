"""
Step 3: Train Model
Trains a regression model using preprocessed data.

Parameters:
- model_type: Type of model (linear_regression, ridge, lasso)
- alpha: Regularization parameter (for ridge and lasso)
- fit_intercept: Whether to fit intercept
- data_dir: Directory containing processed data
- output_dir: Directory to save outputs
"""

import pandas as pd
import numpy as np
import os
import json
import pickle
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import time
import sys

# ==============================================================================
# PARAMETERS (modify these or pass as arguments)
# ==============================================================================
model_type = 'linear_regression'
alpha = 1.0
fit_intercept = True
data_dir = 'outputs/processed'
output_dir = 'outputs'

# Allow command-line override
if len(sys.argv) > 1:
    model_type = sys.argv[1]
if len(sys.argv) > 2:
    alpha = float(sys.argv[2])
if len(sys.argv) > 3:
    fit_intercept = sys.argv[3].lower() == 'true'
if len(sys.argv) > 4:
    data_dir = sys.argv[4]
if len(sys.argv) > 5:
    output_dir = sys.argv[5]

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

print("=" * 70)
print("STEP 3: TRAIN MODEL")
print("=" * 70)

print("\nTraining model with parameters:")
print(f"  - model_type: {model_type}")
print(f"  - alpha: {alpha}")
print(f"  - fit_intercept: {fit_intercept}")

# Load preprocessed data
print("\nLoading preprocessed data from Step 2...")
X_train = pd.read_csv(os.path.join(data_dir, 'X_train_processed.csv'))
X_test = pd.read_csv(os.path.join(data_dir, 'X_test_processed.csv'))
y_train = pd.read_csv(os.path.join(data_dir, 'y_train.csv')).values.ravel()
y_test = pd.read_csv(os.path.join(data_dir, 'y_test.csv')).values.ravel()

print("Data loaded successfully")
print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")

# Initialize and train model
print("\n" + "-" * 70)
print(f"Initializing {model_type}...")
print("-" * 70)

if model_type == 'linear_regression':
    model = LinearRegression(fit_intercept=fit_intercept)
elif model_type == 'ridge':
    model = Ridge(alpha=alpha, fit_intercept=fit_intercept, random_state=42)
elif model_type == 'lasso':
    model = Lasso(alpha=alpha, fit_intercept=fit_intercept, random_state=42)
else:
    raise ValueError(f"Unknown model_type: {model_type}")

print(f"Model initialized: {model}")

# Train the model
print("\nTraining model...")
start_time = time.time()

model.fit(X_train, y_train)

train_time = time.time() - start_time
print(f"Training completed in {train_time:.4f} seconds")

# Make predictions
print("\n" + "-" * 70)
print("Making predictions...")
print("-" * 70)
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# Calculate metrics
train_mse = mean_squared_error(y_train, y_train_pred)
train_rmse = np.sqrt(train_mse)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_r2 = r2_score(y_train, y_train_pred)

test_mse = mean_squared_error(y_test, y_test_pred)
test_rmse = np.sqrt(test_mse)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_r2 = r2_score(y_test, y_test_pred)

print("\nTraining Metrics:")
print(f"  - MSE: {train_mse:.4f}")
print(f"  - RMSE: {train_rmse:.4f}")
print(f"  - MAE: {train_mae:.4f}")
print(f"  - R²: {train_r2:.4f}")

print("\nTest Metrics:")
print(f"  - MSE: {test_mse:.4f}")
print(f"  - RMSE: {test_rmse:.4f}")
print(f"  - MAE: {test_mae:.4f}")
print(f"  - R²: {test_r2:.4f}")

# Save model and metrics
print("\n" + "-" * 70)
print("Saving model and metrics...")
print("-" * 70)

model_dir = os.path.join(output_dir, 'models')
os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(model_dir, f'{model_type}_model.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

# Save predictions
predictions_dir = os.path.join(output_dir, 'predictions')
os.makedirs(predictions_dir, exist_ok=True)

pd.DataFrame({'actual': y_train, 'predicted': y_train_pred}).to_csv(
    os.path.join(predictions_dir, f'{model_type}_train_predictions.csv'), index=False
)
pd.DataFrame({'actual': y_test, 'predicted': y_test_pred}).to_csv(
    os.path.join(predictions_dir, f'{model_type}_test_predictions.csv'), index=False
)

# Save metrics
metrics = {
    'model_type': model_type,
    'alpha': alpha,
    'fit_intercept': fit_intercept,
    'training_time_seconds': train_time,
    'train_metrics': {
        'mse': float(train_mse),
        'rmse': float(train_rmse),
        'mae': float(train_mae),
        'r2': float(train_r2)
    },
    'test_metrics': {
        'mse': float(test_mse),
        'rmse': float(test_rmse),
        'mae': float(test_mae),
        'r2': float(test_r2)
    },
    'coefficients': model.coef_.tolist() if hasattr(model, 'coef_') else None,
    'intercept': float(model.intercept_) if hasattr(model, 'intercept_') else None
}

metrics_path = os.path.join(model_dir, f'{model_type}_metrics.json')
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"Model saved to {model_path}")
print(f"Metrics saved to {metrics_path}")
print("Files created:")
print(f"  - {model_type}_model.pkl")
print(f"  - {model_type}_metrics.json")
print(f"  - {model_type}_train_predictions.csv")
print(f"  - {model_type}_test_predictions.csv")

print("\n" + "=" * 70)
print("STEP 3 COMPLETED SUCCESSFULLY")
print("=" * 70)
