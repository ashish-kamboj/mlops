"""
Common Utilities Module
=======================
Shared utility functions for the MLOps pipeline.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json


def load_config(config_path: str = "./config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration parameters
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info(f"Configuration loaded successfully from {config_path}")
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        raise


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_format = config.get('logging', {}).get('format', 
                                                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    log_file_path = config.get('logging', {}).get('file_path', './outputs/logs/pipeline.log')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )


def get_environment_mode(config: Dict[str, Any]) -> str:
    """
    Get the current environment mode (local or databricks).
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Environment mode string
    """
    return config.get('environment', {}).get('mode', 'local')


def is_databricks_environment() -> bool:
    """
    Check if code is running in Databricks environment.
    
    Returns:
        True if running in Databricks, False otherwise
    """
    return 'DATABRICKS_RUNTIME_VERSION' in os.environ


def get_timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    """
    Get current timestamp as formatted string.
    
    Args:
        format: Datetime format string
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format)


def create_directory(directory_path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)
    logging.debug(f"Directory ensured: {directory_path}")


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Save dictionary as JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Output file path
    """
    create_directory(os.path.dirname(file_path))
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, default=str)
    logging.info(f"JSON saved to {file_path}")


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file as dictionary.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary from JSON file
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    logging.info(f"JSON loaded from {file_path}")
    return data


def get_spark_session(config: Dict[str, Any]):
    """
    Get or create Spark session based on environment.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Spark session object
    """
    try:
        from pyspark.sql import SparkSession
        
        if is_databricks_environment():
            # In Databricks, use the existing Spark session
            spark = SparkSession.builder.getOrCreate()
            logging.info("Using existing Databricks Spark session")
        else:
            # For local development, create a new Spark session
            spark = SparkSession.builder \
                .appName("NextBestProductLocal") \
                .master("local[*]") \
                .config("spark.sql.warehouse.dir", "./spark-warehouse") \
                .getOrCreate()
            logging.info("Created local Spark session")
        
        return spark
    except Exception as e:
        logging.error(f"Error creating Spark session: {str(e)}")
        raise


def get_mlflow_client(config: Dict[str, Any]):
    """
    Initialize MLflow client based on environment.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        MLflow client object
    """
    import mlflow
    
    env_mode = get_environment_mode(config)
    
    if env_mode == 'databricks':
        mlflow_config = config['mlflow']['databricks']
        mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        mlflow.set_registry_uri(mlflow_config['model_registry_uri'])
        experiment_name = mlflow_config['experiment_name']
    else:
        mlflow_config = config['mlflow']['local']
        tracking_uri_relative = mlflow_config['tracking_uri']
        
        # Resolve to workspace root from current working directory
        # When running from notebooks/, we need to go up one level
        cwd = os.getcwd()
        print(f"🔍 DEBUG: Current working directory: {cwd}")
        
        if cwd.endswith('notebooks'):
            workspace_root = os.path.dirname(cwd)
            print(f"🔍 DEBUG: Detected notebooks directory, going up to workspace root: {workspace_root}")
        else:
            workspace_root = cwd
            print(f"🔍 DEBUG: Using current directory as workspace root: {workspace_root}")
        
        tracking_path = os.path.join(workspace_root, tracking_uri_relative.lstrip('./'))
        print(f"🔍 DEBUG: Final MLflow tracking path: {tracking_path}")
        
        create_directory(tracking_path)
        
        # Use file:/// URI format for Windows compatibility
        mlflow_tracking_uri = 'file:///' + tracking_path.replace('\\', '/')
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        
        logging.info(f"MLflow tracking URI set to: {mlflow_tracking_uri}")
        logging.info(f"MLflow tracking path: {tracking_path}")
        
        experiment_name = mlflow_config['experiment_name']
    
    # Set or create experiment
    try:
        mlflow.set_experiment(experiment_name)
        logging.info(f"MLflow experiment set: {experiment_name}")
    except Exception as e:
        logging.warning(f"Could not set experiment: {str(e)}")
    
    return mlflow


def format_table_name(config: Dict[str, Any], table_key: str) -> str:
    """
    Format table name based on data source type.
    
    Args:
        config: Configuration dictionary
        table_key: Key for the table in config
        
    Returns:
        Formatted table name/path
    """
    data_source_type = config['data_source']['type']
    
    if data_source_type == 'unity_catalog':
        uc_config = config['data_source']['unity_catalog']
        catalog = uc_config['catalog']
        schema = uc_config['schema']
        table_name = uc_config['tables'][table_key]
        return f"{catalog}.{schema}.{table_name}"
    else:
        csv_config = config['data_source']['csv']
        input_path = csv_config['input_path']
        file_name = csv_config['tables'][table_key]
        return os.path.join(input_path, file_name)


def get_feature_store_client(config: Dict[str, Any]):
    """
    Get Feature Store client if in Databricks environment.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Feature Store client or None
    """
    if not config['feature_store']['enabled']:
        logging.info("Feature Store is disabled in config")
        return None
    
    try:
        from databricks.feature_store import FeatureStoreClient
        fs = FeatureStoreClient()
        logging.info("Feature Store client initialized")
        return fs
    except ImportError:
        logging.warning("Databricks Feature Store not available. Running without Feature Store.")
        return None
    except Exception as e:
        logging.error(f"Error initializing Feature Store: {str(e)}")
        return None


class Timer:
    """Context manager for timing code execution."""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        logging.info(f"Starting {self.name}...")
        return self
        
    def __exit__(self, *args):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logging.info(f"{self.name} completed in {elapsed:.2f} seconds")


def print_section_header(title: str, width: int = 80) -> None:
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        width: Width of the header
    """
    print("\n" + "=" * width)
    print(f"{title.center(width)}")
    print("=" * width + "\n")
