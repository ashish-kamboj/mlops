"""
Step 4: Evaluate Model
Evaluates trained model and generates visualizations.

Parameters:
- model_type: Type of model to evaluate
- data_dir: Directory containing processed data
- model_dir: Directory containing trained models
- output_dir: Directory to save outputs
- generate_plots: Whether to generate visualization plots
"""

import pandas as pd
import numpy as np
import os
import json
import pickle
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# ==============================================================================
# PARAMETERS (modify these or pass as arguments)
# ==============================================================================
model_type = 'linear_regression'
data_dir = 'outputs/processed'
model_dir = 'outputs/models'
output_dir = 'outputs'
generate_plots = True

# Allow command-line override
if len(sys.argv) > 1:
    model_type = sys.argv[1]
if len(sys.argv) > 2:
    data_dir = sys.argv[2]
if len(sys.argv) > 3:
    model_dir = sys.argv[3]
if len(sys.argv) > 4:
    output_dir = sys.argv[4]
if len(sys.argv) > 5:
    generate_plots = sys.argv[5].lower() == 'true'

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

print("=" * 70)
print("STEP 4: EVALUATE MODEL")
print("=" * 70)

print("\nEvaluating model with parameters:")
print(f"  - model_type: {model_type}")
print(f"  - generate_plots: {generate_plots}")

# Load data and model
print("\nLoading data and trained model...")
X_test = pd.read_csv(os.path.join(data_dir, 'X_test_processed.csv'))
y_test = pd.read_csv(os.path.join(data_dir, 'y_test.csv')).values.ravel()

model_path = os.path.join(model_dir, f'{model_type}_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Load predictions
predictions_path = os.path.join(output_dir, 'predictions', f'{model_type}_test_predictions.csv')
predictions_df = pd.read_csv(predictions_path)
y_test_pred = predictions_df['predicted'].values

print("Data and model loaded successfully")
print(f"X_test shape: {X_test.shape}")
print(f"y_test shape: {y_test.shape}")

# Calculate detailed evaluation metrics
print("\n" + "-" * 70)
print("Calculating evaluation metrics...")
print("-" * 70)

mse = mean_squared_error(y_test, y_test_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_test_pred)
r2 = r2_score(y_test, y_test_pred)

# Additional metrics
residuals = y_test - y_test_pred
residuals_mean = np.mean(residuals)
residuals_std = np.std(residuals)
residuals_min = np.min(residuals)
residuals_max = np.max(residuals)

# MAPE (Mean Absolute Percentage Error) - avoid division by zero
mape = np.mean(np.abs((y_test - y_test_pred) / y_test)) * 100 if np.all(y_test != 0) else np.nan

print(f"\nModel Performance Metrics:")
print(f"  - MSE: {mse:.4f}")
print(f"  - RMSE: {rmse:.4f}")
print(f"  - MAE: {mae:.4f}")
print(f"  - R² Score: {r2:.4f}")
if not np.isnan(mape):
    print(f"  - MAPE: {mape:.4f}%")

print(f"\nResidual Statistics:")
print(f"  - Mean: {residuals_mean:.4f}")
print(f"  - Std Dev: {residuals_std:.4f}")
print(f"  - Min: {residuals_min:.4f}")
print(f"  - Max: {residuals_max:.4f}")

# Generate visualization plots
if generate_plots:
    print("\n" + "-" * 70)
    print("Generating visualization plots...")
    print("-" * 70)
    
    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    
    # Plot 1: Actual vs Predicted
    print("  Creating: actual_vs_predicted.png")
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_test_pred, alpha=0.6, edgecolors='k')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2, label='Perfect Prediction')
    plt.xlabel('Actual Values', fontsize=12)
    plt.ylabel('Predicted Values', fontsize=12)
    plt.title(f'Actual vs Predicted Values ({model_type})', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'{model_type}_actual_vs_predicted.png'), dpi=100)
    plt.close()
    
    # Plot 2: Residuals
    print("  Creating: residuals.png")
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test_pred, residuals, alpha=0.6, edgecolors='k')
    plt.axhline(y=0, color='r', linestyle='--', lw=2)
    plt.xlabel('Predicted Values', fontsize=12)
    plt.ylabel('Residuals', fontsize=12)
    plt.title(f'Residual Plot ({model_type})', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'{model_type}_residuals.png'), dpi=100)
    plt.close()
    
    # Plot 3: Residuals Distribution
    print("  Creating: residuals_distribution.png")
    plt.figure(figsize=(10, 6))
    plt.hist(residuals, bins=20, edgecolor='black', alpha=0.7)
    plt.xlabel('Residuals', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Distribution of Residuals ({model_type})', fontsize=14, fontweight='bold')
    plt.axvline(x=0, color='r', linestyle='--', lw=2)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'{model_type}_residuals_distribution.png'), dpi=100)
    plt.close()
    
    # Plot 4: Prediction Error Distribution
    print("  Creating: prediction_errors.png")
    errors = np.abs(y_test - y_test_pred)
    plt.figure(figsize=(10, 6))
    plt.hist(errors, bins=20, edgecolor='black', alpha=0.7, color='orange')
    plt.xlabel('Absolute Error', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Distribution of Prediction Errors ({model_type})', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, f'{model_type}_prediction_errors.png'), dpi=100)
    plt.close()
    
    print("  All plots generated successfully")

# Save evaluation summary
print("\n" + "-" * 70)
print("Saving evaluation summary...")
print("-" * 70)

evaluation = {
    'model_type': model_type,
    'test_set_size': len(y_test),
    'metrics': {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'r2': float(r2),
        'mape': float(mape) if not np.isnan(mape) else None
    },
    'residual_statistics': {
        'mean': float(residuals_mean),
        'std': float(residuals_std),
        'min': float(residuals_min),
        'max': float(residuals_max)
    },
    'prediction_samples': {
        'actual': y_test[:5].tolist(),
        'predicted': y_test_pred[:5].tolist(),
        'errors': (y_test[:5] - y_test_pred[:5]).tolist()
    }
}

eval_path = os.path.join(model_dir, f'{model_type}_evaluation.json')
with open(eval_path, 'w') as f:
    json.dump(evaluation, f, indent=2)

print(f"Evaluation summary saved to {eval_path}")
print("Files created:")
if generate_plots:
    print(f"  - {model_type}_actual_vs_predicted.png")
    print(f"  - {model_type}_residuals.png")
    print(f"  - {model_type}_residuals_distribution.png")
    print(f"  - {model_type}_prediction_errors.png")
print(f"  - {model_type}_evaluation.json")

print("\n" + "=" * 70)
print("STEP 4 COMPLETED SUCCESSFULLY")
print("=" * 70)
