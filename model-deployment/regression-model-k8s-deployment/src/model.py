"""
Model training and management utilities.
Handles model creation, training, and MLflow integration.
"""

import joblib
import json
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import mlflow
import mlflow.sklearn

from config import ModelConfig


class ModelManager:
    """Manage model lifecycle: training, evaluation, and registration."""
    
    def __init__(self):
        self.model_config = ModelConfig()
        self.model = None
        self.scaler = None
    
    def build_model(self) -> Any:
        """
        Build model based on configuration.
        
        Returns:
            Unfitted model object
        """
        algorithm = self.model_config.get_algorithm()
        hyperparameters = self.model_config.get_hyperparameters()
        
        if algorithm == 'random_forest':
            self.model = RandomForestRegressor(**hyperparameters)
        elif algorithm == 'linear_regression':
            self.model = LinearRegression(**hyperparameters)
        elif algorithm == 'gradient_boosting':
            self.model = GradientBoostingRegressor(**hyperparameters)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return self.model
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training target
        
        Returns:
            Trained model
        """
        if self.model is None:
            self.build_model()
        
        self.model.fit(X_train, y_train)
        return self.model
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions.
        
        Args:
            X: Features
        
        Returns:
            Predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        return self.model.predict(X)
    
    def save_model(self, path: str):
        """
        Save model to disk.
        
        Args:
            path: File path to save model
        """
        if self.model is None:
            raise ValueError("Model not trained. Train model first.")
        
        joblib.dump(self.model, path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """
        Load model from disk.
        
        Args:
            path: File path to load model from
        """
        self.model = joblib.load(path)
        print(f"Model loaded from {path}")
    
    @staticmethod
    def get_feature_importance(model: Any, feature_names: list) -> Dict[str, float]:
        """
        Get feature importance for tree-based models.
        
        Args:
            model: Trained model
            feature_names: List of feature names
        
        Returns:
            Dictionary of feature importances
        """
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return {name: float(imp) for name, imp in zip(feature_names, importances)}
        return {}


class MLflowManager:
    """Manage MLflow experiment tracking and model registration."""
    
    def __init__(self):
        self.model_config = ModelConfig()
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Setup MLflow configuration."""
        mlflow_config = self.model_config.get_mlflow_config()
        tracking_uri = mlflow_config.get('tracking_uri', 'file:./mlruns')
        # Ensure local mlruns directory exists when using file store
        if tracking_uri.startswith('file:'):
            import os
            from pathlib import Path
            Path(tracking_uri.replace('file:', '')).mkdir(parents=True, exist_ok=True)
        mlflow.set_tracking_uri(tracking_uri)
        experiment_name = mlflow_config.get('experiment_name', 'ml_regression_experiment')
        
        # Set experiment
        mlflow.set_experiment(experiment_name)
        print(f"MLflow tracking: {tracking_uri} | experiment: {experiment_name}")
    
    def log_params(self, params: Dict[str, Any]):
        """
        Log parameters to MLflow.
        
        Args:
            params: Dictionary of parameters
        """
        for key, value in params.items():
            mlflow.log_param(key, value)
    
    def log_metrics(self, metrics: Dict[str, float]):
        """
        Log metrics to MLflow.
        
        Args:
            metrics: Dictionary of metrics
        """
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, value)
    
    def log_model(self, model: Any, artifact_path: str = "model"):
        """
        Log model to MLflow.
        
        Args:
            model: Model object
            artifact_path: Artifact path in MLflow
        """
        mlflow.sklearn.log_model(model, artifact_path)
    
    def log_artifact(self, local_path: str, artifact_path: str = None):
        """
        Log artifact to MLflow.
        
        Args:
            local_path: Local file path
            artifact_path: Remote artifact path
        """
        mlflow.log_artifact(local_path, artifact_path)
    
    def log_dict(self, data: Dict[str, Any], filename: str):
        """
        Log dictionary as JSON artifact.
        
        Args:
            data: Dictionary to log
            filename: Filename to save
        """
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            temp_path = f.name
        
        mlflow.log_artifact(temp_path, artifact_path=None)
    
    def start_run(self, run_name: str = None) -> str:
        """
        Start MLflow run.
        
        Args:
            run_name: Name for the run
        
        Returns:
            Run ID
        """
        if run_name is None:
            run_name = self.model_config.get_run_name()
        
        run = mlflow.start_run(run_name=run_name)
        
        # Log tags
        mlflow_config = self.model_config.get_mlflow_config()
        tags = mlflow_config.get('tags', {})
        for key, value in tags.items():
            mlflow.set_tag(key, value)
        
        return run.info.run_id
    
    def end_run(self, status: str = "FINISHED"):
        """
        End MLflow run.
        
        Args:
            status: Run status (FINISHED, FAILED)
        """
        mlflow.end_run()
    
    def log_training_run(self, model: Any, metrics: Dict[str, float], 
                         params: Dict[str, Any], feature_importance: Dict[str, float] = None):
        """
        Log complete training run to MLflow.
        
        Args:
            model: Trained model
            metrics: Evaluation metrics
            params: Model parameters
            feature_importance: Feature importance dictionary
        """
        self.log_params(params)
        self.log_metrics(metrics)
        
        if feature_importance:
            self.log_dict(feature_importance, "feature_importance.json")
        
        self.log_model(model)


def get_model_manager() -> ModelManager:
    """Get ModelManager instance."""
    return ModelManager()


def get_mlflow_manager() -> MLflowManager:
    """Get MLflowManager instance."""
    return MLflowManager()