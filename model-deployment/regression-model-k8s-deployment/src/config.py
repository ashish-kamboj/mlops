"""
Configuration loader module for ML model pipeline.
Handles YAML configuration loading and provides centralized config access.
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Load and manage configuration from YAML file."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    @staticmethod
    def get_config_path():
        """Get the path to the config file."""
        # Try multiple locations
        possible_paths = [
            Path("./config/model_config.yaml"),
            Path("../config/model_config.yaml"),
            Path("../../config/model_config.yaml"),
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Default path
        return Path("./config/model_config.yaml")
    
    def load_config(self):
        """Load configuration from YAML file."""
        config_path = self.get_config_path()
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        print(f"Configuration loaded from: {config_path}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path (e.g., 'databricks.catalog')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_dict(self, section: str) -> Dict[str, Any]:
        """Get entire section as dictionary."""
        return self._config.get(section, {})
    
    def get_section(self, *args) -> Dict[str, Any]:
        """Get nested section."""
        value = self._config
        for key in args:
            if isinstance(value, dict):
                value = value.get(key, {})
            else:
                return {}
        return value if isinstance(value, dict) else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Get entire configuration as dictionary."""
        return self._config


class ECRConfig:
    """AWS ECR configuration helper."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('ecr')
    
    def is_enabled(self) -> bool:
        return bool(self.config.get('enabled', False))
    
    def get_registry(self) -> str:
        return self.config.get('registry', '')
    
    def get_repository(self) -> str:
        return self.config.get('repository', 'ml-models/regression-model')
    
    def get_region(self) -> str:
        return self.config.get('region', 'us-east-1')
    
    def get_account_id(self) -> str:
        return self.config.get('account_id', '')
    
    def get_full_image_uri(self, image_name: str, tag: str) -> str:
        registry = self.get_registry()
        if registry:
            return f"{registry}/{image_name}:{tag}"
        return f"{image_name}:{tag}"


class K8sConfig:
    """Kubernetes (Minikube) deployment configuration."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('kubernetes')
    
    def get_namespace(self) -> str:
        return self.config.get('namespace', 'default')
    
    def get_service_type(self) -> str:
        return self.config.get('service_type', 'NodePort')
    
    def get_container_port(self) -> int:
        return int(self.config.get('container_port', 5000))
    
    def get_node_port(self) -> int:
        return int(self.config.get('node_port', 30080))
    
    def get_image_pull_policy(self) -> str:
        return self.config.get('image_pull_policy', 'IfNotPresent')


class DataConfig:
    """Data generation configuration."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('data_generation')
    
    def get_num_samples(self) -> int:
        return self.config.get('num_samples', 5000)
    
    def get_num_features(self) -> int:
        return self.config.get('num_features', 10)
    
    def get_random_seed(self) -> int:
        return self.config.get('random_seed', 42)
    
    def get_test_size(self) -> float:
        return self.config.get('test_size', 0.2)
    
    def get_val_size(self) -> float:
        return self.config.get('val_size', 0.1)
    
    def get_table_name(self) -> str:
        return self.config.get('table_name', 'training_data')
    
    def get_noise_level(self) -> float:
        return self.config.get('noise_level', 0.1)


class ModelConfig:
    """Model training configuration."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('model_training')
    
    def get_algorithm(self) -> str:
        return self.config.get('algorithm', 'random_forest')
    
    def get_hyperparameters(self) -> Dict[str, Any]:
        """Get hyperparameters for the selected algorithm."""
        algorithm = self.get_algorithm()
        hp_section = self.config.get('hyperparameters', {})
        return hp_section.get(algorithm, {})
    
    def get_test_size(self) -> float:
        return self.config.get('test_size', 0.2)
    
    def get_mlflow_config(self) -> Dict[str, Any]:
        return self.config.get('mlflow', {})
    
    def get_experiment_name(self) -> str:
        mlflow_config = self.get_mlflow_config()
        return mlflow_config.get('experiment_name', 'ml_regression_experiment')
    
    def get_run_name(self) -> str:
        mlflow_config = self.get_mlflow_config()
        return mlflow_config.get('run_name', 'regression_model_run')


class FeatureConfig:
    """Feature engineering configuration."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('feature_engineering')
    
    def is_enabled(self) -> bool:
        return self.config.get('enabled', True)
    
    def get_scaling_method(self) -> str:
        return self.config.get('scaling_method', 'standard')
    
    def get_feature_selection_config(self) -> Dict[str, Any]:
        return self.config.get('feature_selection', {})
    
    def is_feature_selection_enabled(self) -> bool:
        fs_config = self.get_feature_selection_config()
        return fs_config.get('enabled', True)
    
    def get_n_features(self) -> int:
        fs_config = self.get_feature_selection_config()
        return fs_config.get('n_features', 8)


class DockerConfig:
    """Docker deployment configuration."""
    
    def __init__(self):
        self.config = ConfigLoader().get_section('docker')
    
    def get_image_name(self) -> str:
        return self.config.get('image_name', 'regression-model-inference')
    
    def get_image_tag(self) -> str:
        return self.config.get('image_tag', 'latest')
    
    def get_full_image_name(self) -> str:
        """Get full image name with registry."""
        registry = self.config.get('registry', '')
        image_name = self.get_image_name()
        tag = self.get_image_tag()
        
        if registry:
            return f"{registry}/{image_name}:{tag}"
        return f"{image_name}:{tag}"
    
    def get_port(self) -> int:
        return self.config.get('port', 5000)
    
    def get_base_image(self) -> str:
        return self.config.get('base_image', 'python:3.9-slim')


def get_config() -> ConfigLoader:
    """Get singleton ConfigLoader instance."""
    return ConfigLoader()