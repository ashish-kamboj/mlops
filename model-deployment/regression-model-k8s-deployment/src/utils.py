"""
Utility functions for ML pipeline.
Provides common functions for logging, data handling, and model operations.
"""

import logging
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.model_selection import train_test_split
from pathlib import Path

from config import ConfigLoader


# Configure logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    config = ConfigLoader()
    log_level = config.get('logging.level', log_level)
    
    logger = logging.getLogger('ml_pipeline')
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, log_level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(ch)
    
    return logger


logger = setup_logging()


def split_data(X: pd.DataFrame, y: pd.Series, 
               test_size: float = 0.2, 
               val_size: float = 0.1,
               random_seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, 
                                               pd.Series, pd.Series, pd.Series]:
    """
    Split data into train, validation, and test sets.
    
    Args:
        X: Feature dataframe
        y: Target series
        test_size: Test set fraction
        val_size: Validation set fraction
        random_seed: Random seed
    
    Returns:
        Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
    """
    # First split: train+val vs test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed
    )
    
    # Second split: train vs val
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio, random_state=random_seed
    )
    
    logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def scale_features(X_train: pd.DataFrame, X_val: pd.DataFrame, X_test: pd.DataFrame,
                  method: str = 'standard') -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Any]:
    """
    Scale features using specified method.
    
    Args:
        X_train: Training features
        X_val: Validation features
        X_test: Test features
        method: Scaling method (standard, minmax, robust)
    
    Returns:
        Tuple of (scaled X_train, scaled X_val, scaled X_test, scaler object)
    """
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    elif method == 'robust':
        scaler = RobustScaler()
    else:
        raise ValueError(f"Unknown scaling method: {method}")
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_val_scaled = pd.DataFrame(X_val_scaled, columns=X_val.columns, index=X_val.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    
    logger.info(f"Features scaled using {method} method")
    
    return X_train_scaled, X_val_scaled, X_test_scaled, scaler


def save_to_parquet(df: pd.DataFrame, path: str):
    """Save DataFrame to local Parquet file."""
    ensure_directory_exists(str(Path(path).parent))
    df.to_parquet(path, index=False)
    logger.info(f"Saved {len(df)} rows to {path}")


def load_from_parquet(path: str) -> pd.DataFrame:
    """Load DataFrame from local Parquet file."""
    df = pd.read_parquet(path)
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate regression metrics.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary of metrics
    """
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r2_score': r2
    }
    
    logger.info(f"Metrics - MSE: {mse:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
    
    return metrics


def log_metrics_to_dict(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calculate and return metrics as dictionary (for MLflow logging)."""
    return calculate_regression_metrics(y_true, y_pred)


def create_feature_interactions(df: pd.DataFrame, degree: int = 2) -> pd.DataFrame:
    """
    Create polynomial features.
    
    Args:
        df: Input dataframe
        degree: Polynomial degree
    
    Returns:
        DataFrame with additional interaction features
    """
    from sklearn.preprocessing import PolynomialFeatures
    
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    poly_features = poly.fit_transform(df)
    feature_names = poly.get_feature_names_out(df.columns)
    
    return pd.DataFrame(poly_features, columns=feature_names, index=df.index)


def ensure_directory_exists(path: str):
    """Ensure directory exists, create if not."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parent.parent