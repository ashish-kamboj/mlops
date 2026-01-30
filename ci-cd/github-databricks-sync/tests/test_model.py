"""
Unit tests for ML model utilities and training pipeline
"""

import pytest
import numpy as np
import pandas as pd
import tempfile
import json
import os
from unittest.mock import patch
from src.utils import (
    load_config,
    save_metrics,
    evaluate_model,
    prepare_features,
    validate_input
)


class TestConfigLoading:
    """Tests for configuration loading"""
    
    def test_load_config_valid(self):
        """Test loading valid configuration"""
        config = load_config('config/model_config.yaml')
        assert config is not None
        assert 'model_config' in config
        assert config['model_config']['name'] == 'Housing Price Prediction'
        
    def test_load_config_has_required_keys(self):
        """Test config has all required keys"""
        config = load_config('config/model_config.yaml')
        assert 'model_config' in config
        assert 'model' in config['model_config']
        assert 'data' in config['model_config']


class TestMetricsHandling:
    """Tests for metrics saving and evaluation"""
    
    def test_save_metrics(self):
        """Test saving metrics to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = {'mse': 0.5, 'rmse': 0.707, 'r2': 0.95}
            output_path = os.path.join(tmpdir, 'metrics.json')
            
            save_metrics(metrics, output_path)
            
            assert os.path.exists(output_path)
            with open(output_path) as f:
                loaded = json.load(f)
            assert loaded == metrics
    
    def test_evaluate_model_perfect_predictions(self):
        """Test evaluation with perfect predictions"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1, 2, 3, 4, 5])
        
        metrics = evaluate_model(y_true, y_pred)
        
        assert metrics['mse'] == 0.0
        assert metrics['r2_score'] == 1.0
        assert metrics['mae'] == 0.0
    
    def test_evaluate_model_with_error(self):
        """Test evaluation with prediction errors"""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1.1, 2.1, 2.9, 4.1, 4.9])
        
        metrics = evaluate_model(y_true, y_pred)
        
        assert metrics['mse'] > 0
        assert metrics['rmse'] > 0
        assert metrics['mae'] > 0
        assert 0 < metrics['r2_score'] < 1


class TestFeaturePreparation:
    """Tests for feature preparation"""
    
    def test_prepare_features_valid(self):
        """Test preparing valid features"""
        df = pd.DataFrame({
            'feature1': [1, 2, 3],
            'feature2': [4, 5, 6],
            'target': [7, 8, 9]
        })
        
        features, cols = prepare_features(df, ['feature1', 'feature2'])
        
        assert features.shape == (3, 2)
        assert cols == ['feature1', 'feature2']
        assert np.array_equal(features, np.array([[1, 4], [2, 5], [3, 6]]))
    
    def test_prepare_features_single_column(self):
        """Test preparing single feature column"""
        df = pd.DataFrame({'feature': [1, 2, 3]})
        
        features, cols = prepare_features(df, ['feature'])
        
        assert features.shape == (3, 1)
        assert cols == ['feature']


class TestInputValidation:
    """Tests for input validation"""
    
    def test_validate_input_valid(self):
        """Test validation with valid input"""
        X = np.array([[1, 2], [3, 4]])
        y = np.array([1, 2])
        
        result = validate_input(X, y)
        assert result is True
    
    def test_validate_input_mismatched_length(self):
        """Test validation with mismatched lengths"""
        X = np.array([[1, 2], [3, 4]])
        y = np.array([1])
        
        with pytest.raises(ValueError):
            validate_input(X, y)
    
    def test_validate_input_empty_arrays(self):
        """Test validation with empty arrays"""
        X = np.array([])
        y = np.array([])
        
        with pytest.raises(ValueError):
            validate_input(X, y)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
