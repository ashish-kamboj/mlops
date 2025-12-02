"""
Utils Package for Next Best Product Recommendation MLOps Pipeline
==================================================================

This package contains reusable utility modules for the end-to-end ML pipeline.

Modules:
--------
- common_utils: Common helper functions (config loading, logging, etc.)
- data_loader: Data loading and saving utilities
- feature_engineering: Feature creation and transformation
- model_training: Model training and evaluation
- model_deployment: Model deployment utilities
- model_monitoring: Model monitoring and drift detection
- eda_utils: Exploratory data analysis utilities

Author: Home Credit Data Science Team
Date: 2025-11-11
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Home Credit Data Science Team"

# Import key functions for easy access
from .common_utils import load_config, setup_logging, get_spark_session
from .data_loader import load_data_from_source, save_data_to_destination
from .feature_engineering import (
    create_customer_demographic_features,
    create_account_features,
    create_transaction_features,
    merge_all_features,
    create_target_variable
)
from .model_training import (
    prepare_training_data,
    get_model,
    train_model,
    evaluate_model,
    predict_top_k_products
)

__all__ = [
    # Common utilities
    'load_config',
    'setup_logging',
    'get_spark_session',
    
    # Data operations
    'load_data_from_source',
    'save_data_to_destination',
    
    # Feature engineering
    'create_customer_demographic_features',
    'create_account_features',
    'create_transaction_features',
    'merge_all_features',
    'create_target_variable',
    
    # Model operations
    'prepare_training_data',
    'get_model',
    'train_model',
    'evaluate_model',
    'predict_top_k_products',
]
