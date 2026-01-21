"""
Configuration Manager Module
Handles loading and validation of YAML configuration files for data drift detection.
"""

import os
import yaml
import logging
from typing import Dict, Any, List


class ConfigManager:
    """
    Manages configuration loading and validation for data drift detection.
    
    This class provides methods to load YAML configuration files, validate settings,
    and provide easy access to configuration parameters throughout the application.
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the ConfigManager with a configuration file path.
        
        Args:
            config_path (str): Path to the YAML configuration file
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML file is malformed
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
        self.logger.info(f"Configuration loaded successfully from {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file with environment variable substitution.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Substitute environment variables
            config = self._substitute_env_vars(config)
            return config
        
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.
        Variables should be in format ${VAR_NAME}.
        
        Args:
            config: Configuration value (can be dict, list, or string)
            
        Returns:
            Configuration with environment variables substituted
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable value
            if config.startswith('${') and config.endswith('}'):
                var_name = config[2:-1]
                return os.getenv(var_name, config)  # Return original if not found
        return config
    
    def _validate_config(self) -> None:
        """
        Validate that required configuration sections and parameters exist.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        required_sections = ['general', 'databricks', 'statistical_tests', 'output']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Required configuration section '{section}' is missing")
        
        # Validate tables configuration
        if 'tables' not in self.config['databricks'] or not self.config['databricks']['tables']:
            raise ValueError("At least one table must be configured in databricks.tables")
        
        # Validate statistical tests
        if 'numerical' not in self.config['statistical_tests']:
            raise ValueError("Numerical statistical tests configuration is required")
        if 'categorical' not in self.config['statistical_tests']:
            raise ValueError("Categorical statistical tests configuration is required")
        
        # Validate output formats
        if 'formats' not in self.config['output'] or not self.config['output']['formats']:
            raise ValueError("At least one output format must be specified")
        
        valid_formats = ['html', 'json']
        for fmt in self.config['output']['formats']:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid output format: {fmt}. Must be one of {valid_formats}")
        
        self.logger.info("Configuration validation passed")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path (str): Dot-separated path to configuration key (e.g., 'databricks.catalog')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
            
        Example:
            >>> config.get('databricks.catalog')
            'main'
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """
        Get list of tables configured for drift detection.
        
        Returns:
            List[Dict[str, Any]]: List of table configurations
        """
        return self.config['databricks']['tables']
    
    def get_statistical_tests(self, column_type: str) -> List[str]:
        """
        Get configured statistical tests for a specific column type.
        
        Args:
            column_type (str): Type of column ('numerical' or 'categorical')
            
        Returns:
            List[str]: List of statistical test names
            
        Raises:
            ValueError: If column_type is invalid
        """
        if column_type not in ['numerical', 'categorical']:
            raise ValueError(f"Invalid column type: {column_type}")
        
        return self.config['statistical_tests'][column_type].get('tests', [])
    
    def get_test_threshold(self, column_type: str) -> float:
        """
        Get drift detection threshold for a specific column type.
        
        Args:
            column_type (str): Type of column ('numerical' or 'categorical')
            
        Returns:
            float: Threshold value
        """
        return self.config['statistical_tests'][column_type].get('threshold', 0.05)
    
    def get_output_formats(self) -> List[str]:
        """
        Get configured output report formats.
        
        Returns:
            List[str]: List of output formats ('html', 'json')
        """
        return self.config['output']['formats']
    
    def is_local_output_enabled(self) -> bool:
        """
        Check if local output is enabled.
        
        Returns:
            bool: True if local output is enabled. Safe when 'local' missing.
        """
        return self.config.get('output', {}).get('local', {}).get('enabled', False)
    
    def is_adls_output_enabled(self) -> bool:
        """
        Check if ADLS output is enabled.
        
        Returns:
            bool: True if ADLS output is enabled
        """
        return self.config['output']['adls'].get('enabled', False)
    
    def get_local_output_path(self) -> str:
        """
        Get local output base path.
        
        Returns:
            str: Local output path (default 'reports'). Safe when 'local' missing.
        """
        return self.config.get('output', {}).get('local', {}).get('base_path', 'reports')
    
    def get_adls_config(self) -> Dict[str, Any]:
        """
        Get ADLS configuration.
        
        Returns:
            Dict[str, Any]: ADLS configuration dictionary
        """
        return self.config['output']['adls']
    
    def get_catalog_name(self) -> str:
        """
        Get Unity Catalog name.
        
        Returns:
            str: Catalog name
        """
        return self.config['databricks']['catalog']
    
    def get_schema_name(self) -> str:
        """
        Get schema/database name.
        
        Returns:
            str: Schema name
        """
        return self.config['databricks']['schema']
    
    def get_version_config(self) -> Dict[str, Any]:
        """
        Deprecated: Versioning is handled via Unity Catalog history.
        Kept for backward compatibility if referenced elsewhere.
        """
        return {}
    
    def get_drift_detection_config(self) -> Dict[str, Any]:
        """
        Get drift detection settings.
        
        Returns:
            Dict[str, Any]: Drift detection configuration
        """
        return self.config.get('drift_detection', {
            'confidence_level': 0.95,
            'min_sample_size': 100,
            'missing_values_strategy': 'keep',
            'column_drift_threshold': 0.3
        })
    
    def get_sampling_config(self) -> Dict[str, Any]:
        """
        Get data sampling configuration.
        
        Returns:
            Dict[str, Any]: Sampling configuration
        """
        return self.config.get('sampling', {
            'enabled': False,
            'method': 'fraction',
            'fraction': 0.1,
            'fixed_size': 10000,
            'random_seed': 42
        })
    
    def get_log_level(self) -> str:
        """
        Get configured log level.
        
        Returns:
            str: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        return self.config['general'].get('log_level', 'INFO')
    
    def __repr__(self) -> str:
        """String representation of ConfigManager."""
        return f"ConfigManager(config_path='{self.config_path}')"