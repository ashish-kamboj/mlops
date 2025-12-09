"""
Step 2: Preprocess Data
Preprocesses features for model training.

Parameters:
- normalize: Whether to normalize features (StandardScaler)
- data_dir: Directory containing input data
- output_dir: Directory to save outputs
"""

import pandas as pd
import os
import json
import pickle
from sklearn.preprocessing import StandardScaler
import sys

# ==============================================================================
# PARAMETERS (modify these or pass as arguments)
# ==============================================================================
normalize = True
data_dir = 'outputs/data'
output_dir = 'outputs'

# Allow command-line override
if len(sys.argv) > 1:
    normalize = sys.argv[1].lower() == 'true'
if len(sys.argv) > 2:
    data_dir = sys.argv[2]
if len(sys.argv) > 3:
    output_dir = sys.argv[3]

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

print("=" * 70)
print("STEP 2: PREPROCESS DATA")
print("=" * 70)

print("\nPreprocessing data with parameters:")
print(f"  - normalize: {normalize}")
print(f"  - data_dir: {data_dir}")
print(f"  - output_dir: {output_dir}")

# Load data from previous step
print("\nLoading data from Step 1...")
X_train = pd.read_csv(os.path.join(data_dir, 'X_train.csv'))
X_test = pd.read_csv(os.path.join(data_dir, 'X_test.csv'))
y_train = pd.read_csv(os.path.join(data_dir, 'y_train.csv')).values.ravel()
y_test = pd.read_csv(os.path.join(data_dir, 'y_test.csv')).values.ravel()

print("Data loaded successfully")
print(f"X_train shape: {X_train.shape}")
print(f"X_test shape: {X_test.shape}")

# Check for missing values
print("\n" + "-" * 70)
print("Checking for missing values...")
print("-" * 70)
print(f"Missing values in X_train: {X_train.isnull().sum().sum()}")
print(f"Missing values in X_test: {X_test.isnull().sum().sum()}")
print(f"Missing values in y_train: {pd.Series(y_train).isnull().sum()}")
print(f"Missing values in y_test: {pd.Series(y_test).isnull().sum()}")

# Normalize features if enabled
print("\n" + "-" * 70)
if normalize:
    print("Applying StandardScaler normalization...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"X_train mean after scaling: {X_train_scaled.mean(axis=0)[:3]}...")
    print(f"X_train std after scaling: {X_train_scaled.std(axis=0)[:3]}...")
else:
    print("Skipping normalization")
    X_train_scaled = X_train.values
    X_test_scaled = X_test.values
    scaler = None

# Convert back to DataFrame
X_train_processed = pd.DataFrame(X_train_scaled, columns=X_train.columns)
X_test_processed = pd.DataFrame(X_test_scaled, columns=X_test.columns)

print("-" * 70)

# Save preprocessed data
print("\nSaving preprocessed data...")
processed_dir = os.path.join(output_dir, 'processed')
os.makedirs(processed_dir, exist_ok=True)

X_train_processed.to_csv(os.path.join(processed_dir, 'X_train_processed.csv'), index=False)
X_test_processed.to_csv(os.path.join(processed_dir, 'X_test_processed.csv'), index=False)
y_train_df = pd.DataFrame({'target': y_train})
y_test_df = pd.DataFrame({'target': y_test})
y_train_df.to_csv(os.path.join(processed_dir, 'y_train.csv'), index=False)
y_test_df.to_csv(os.path.join(processed_dir, 'y_test.csv'), index=False)

# Save scaler if used
if scaler is not None:
    with open(os.path.join(processed_dir, 'scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)

# Save preprocessing metadata
preprocess_metadata = {
    'normalize': normalize,
    'scaler_used': scaler is not None,
    'scaler_type': 'StandardScaler' if scaler else None
}

with open(os.path.join(processed_dir, 'preprocessing_metadata.json'), 'w') as f:
    json.dump(preprocess_metadata, f, indent=2)

print("Preprocessed data saved to", processed_dir)
print("Files created:")
print("  - X_train_processed.csv")
print("  - X_test_processed.csv")
print("  - y_train.csv")
print("  - y_test.csv")
if scaler is not None:
    print("  - scaler.pkl")
print("  - preprocessing_metadata.json")

print("\n" + "=" * 70)
print("STEP 2 COMPLETED SUCCESSFULLY")
print("=" * 70)
