"""
Utility functions for ML model training and evaluation
"""

import json
import os
import yaml
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Dictionary containing configuration
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_metrics(metrics: Dict[str, float], output_path: str) -> None:
    """
    Save metrics to JSON file
    
    Args:
        metrics: Dictionary of metrics
        output_path: Path to save metrics JSON
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {output_path}")


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Evaluate model performance
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Dictionary containing evaluation metrics
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        "mse": float(mse),
        "rmse": float(rmse),
        "mae": float(mae),
        "r2_score": float(r2)
    }
    
    return metrics


def prepare_features(df: pd.DataFrame, feature_columns: list) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare features from dataframe
    
    Args:
        df: Input dataframe
        feature_columns: List of feature column names
        
    Returns:
        Tuple of (features_array, column_names)
    """
    features = df[feature_columns].values
    return features, feature_columns


def validate_input(X: np.ndarray, y: np.ndarray) -> bool:
    """
    Validate input data
    
    Args:
        X: Feature matrix
        y: Target vector
        
    Returns:
        True if valid, raises exception otherwise
    """
    if len(X) != len(y):
        raise ValueError("X and y must have same number of samples")
    if X.size == 0 or y.size == 0:
        raise ValueError("X and y cannot be empty")
    return True
