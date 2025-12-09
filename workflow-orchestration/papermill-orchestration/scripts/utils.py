"""
Utility functions for notebook orchestration.
Handles configuration management, logging, and helper functions.
"""

import json
import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing configuration parameters
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def save_config(config: Dict[str, Any], output_path: str) -> None:
    """
    Save configuration to a file for record-keeping.
    
    Args:
        config: Configuration dictionary
        output_path: Path to save the configuration
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def setup_logging(log_file: str, level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger = logging.getLogger("OrchestrationLogger")
    logger.setLevel(getattr(logging, level))
    
    # File handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(getattr(logging, level))
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


def get_timestamp() -> str:
    """Get current timestamp for unique file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_output_dir(base_dir: str) -> str:
    """
    Create a unique output directory with timestamp.
    
    Args:
        base_dir: Base output directory
        
    Returns:
        Path to the created directory
    """
    timestamp = get_timestamp()
    output_dir = os.path.join(base_dir, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def resolve_path(path: str, relative_to: Optional[str] = None) -> str:
    """
    Resolve relative paths to absolute paths.
    
    Args:
        path: Path to resolve
        relative_to: Base directory for relative paths
        
    Returns:
        Absolute path
    """
    if os.path.isabs(path):
        return path
    if relative_to:
        return os.path.abspath(os.path.join(relative_to, path))
    return os.path.abspath(path)


def ensure_file_exists(file_path: str) -> bool:
    """Check if file exists, raise error if not."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return True


def merge_configs(base_config: Dict[str, Any], 
                 override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries (override_config takes precedence).
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override with
        
    Returns:
        Merged configuration dictionary
    """
    merged = base_config.copy()
    merged.update(override_config)
    return merged
