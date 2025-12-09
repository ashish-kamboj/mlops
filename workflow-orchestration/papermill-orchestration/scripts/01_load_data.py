"""
Step 1: Load Data
Loads or generates regression dataset for the ML pipeline.

Parameters:
- test_size: Train-test split ratio
- random_state: Random seed for reproducibility
- dataset: Type of dataset (synthetic or csv_path)
- output_dir: Directory to save outputs
"""

import numpy as np
import pandas as pd
import os
import json
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
import sys

# ==============================================================================
# PARAMETERS (modify these or pass as arguments)
# ==============================================================================
test_size = 0.2
random_state = 42
dataset = 'synthetic'
output_dir = 'outputs'

# Allow command-line override
if len(sys.argv) > 1:
    test_size = float(sys.argv[1])
if len(sys.argv) > 2:
    random_state = int(sys.argv[2])
if len(sys.argv) > 3:
    dataset = sys.argv[3]
if len(sys.argv) > 4:
    output_dir = sys.argv[4]

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

print("=" * 70)
print("STEP 1: LOAD DATA")
print("=" * 70)

print(f"\nLoading data with parameters:")
print(f"  - dataset: {dataset}")
print(f"  - test_size: {test_size}")
print(f"  - random_state: {random_state}")
print(f"  - output_dir: {output_dir}")

# Generate synthetic regression data
print(f"\nGenerating synthetic regression dataset...")
n_samples = 500
n_features = 10

X, y = make_regression(
    n_samples=n_samples,
    n_features=n_features,
    noise=20,
    random_state=random_state
)

# Create DataFrame
feature_names = [f'feature_{i}' for i in range(n_features)]
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

print(f"\nDataset shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nBasic statistics:")
print(df.describe())

# Split data into train and test sets
print(f"\n" + "-" * 70)
print("Splitting data into train and test sets...")
print("-" * 70)

X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=test_size,
    random_state=random_state
)

print(f"Train set shape: {X_train.shape}")
print(f"Test set shape: {X_test.shape}")
print(f"Train target shape: {y_train.shape}")
print(f"Test target shape: {y_test.shape}")

# Save data for next steps
print(f"\n" + "-" * 70)
print("Saving data...")
print("-" * 70)

os.makedirs(output_dir, exist_ok=True)

data_dir = os.path.join(output_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

# Save as CSV
X_train.to_csv(os.path.join(data_dir, 'X_train.csv'), index=False)
X_test.to_csv(os.path.join(data_dir, 'X_test.csv'), index=False)
y_train.to_csv(os.path.join(data_dir, 'y_train.csv'), index=False, header=['target'])
y_test.to_csv(os.path.join(data_dir, 'y_test.csv'), index=False, header=['target'])

# Save metadata
metadata = {
    'n_samples': n_samples,
    'n_features': n_features,
    'n_train': len(X_train),
    'n_test': len(X_test),
    'feature_names': feature_names,
    'test_size': test_size,
    'random_state': random_state
}

with open(os.path.join(data_dir, 'metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\nData saved to {data_dir}")
print(f"Files created:")
print(f"  - X_train.csv ({X_train.shape[0]} rows, {X_train.shape[1]} columns)")
print(f"  - X_test.csv ({X_test.shape[0]} rows, {X_test.shape[1]} columns)")
print(f"  - y_train.csv ({y_train.shape[0]} rows)")
print(f"  - y_test.csv ({y_test.shape[0]} rows)")
print(f"  - metadata.json")

print(f"\n" + "=" * 70)
print("STEP 1 COMPLETED SUCCESSFULLY")
print("=" * 70)
