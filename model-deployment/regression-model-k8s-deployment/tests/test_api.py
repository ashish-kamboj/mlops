#!/usr/bin/env python
"""
Test client for the model inference API.
"""

import requests
import json
import argparse
from typing import Dict, List, Any
import numpy as np


class InferenceAPIClient:
    """Client for model inference API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of inference server
        """
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        response = requests.get(f"{self.base_url}/api/v1/info")
        response.raise_for_status()
        return response.json()
    
    def predict_single(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Make single prediction.
        
        Args:
            features: Dictionary of feature values
        
        Returns:
            Prediction response
        """
        payload = {"features": features}
        response = requests.post(
            f"{self.base_url}/api/v1/predict",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def predict_batch(self, features_list: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Make batch predictions.
        
        Args:
            features_list: List of feature dictionaries
        
        Returns:
            Batch prediction response
        """
        payload = {"features": features_list}
        response = requests.post(
            f"{self.base_url}/api/v1/predict_batch",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def predict_dataframe(self, data: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Make predictions from DataFrame format.
        
        Args:
            data: Dictionary with feature names as keys and lists of values
        
        Returns:
            Prediction response
        """
        payload = {"data": data}
        response = requests.post(
            f"{self.base_url}/api/v1/predict_dataframe",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()


def test_health(client: InferenceAPIClient):
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = client.health_check()
        print(f"✓ Health check passed: {response['status']}")
        print(f"  Model loaded: {response['model_loaded']}")
        print(f"  Features: {response['features_count']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


def test_model_info(client: InferenceAPIClient):
    """Test model info endpoint."""
    print("\nTesting model info endpoint...")
    try:
        response = client.get_model_info()
        print(f"✓ Model info retrieved")
        print(f"  Model type: {response['model_type']}")
        print(f"  Features count: {response['features_count']}")
        print(f"  Features: {response['features'][:3]}... (showing first 3)")
        return True
    except Exception as e:
        print(f"✗ Model info failed: {str(e)}")
        return False


def test_single_prediction(client: InferenceAPIClient, num_features: int = 10):
    """Test single prediction."""
    print("\nTesting single prediction endpoint...")
    try:
        # Create sample features
        features = {f"feature_{i+1}": float(np.random.uniform(0, 10)) for i in range(num_features)}
        
        response = client.predict_single(features)
        print(f"✓ Single prediction successful")
        print(f"  Prediction: {response['prediction']:.4f}")
        print(f"  Status: {response['status']}")
        return True
    except Exception as e:
        print(f"✗ Single prediction failed: {str(e)}")
        return False


def test_batch_prediction(client: InferenceAPIClient, batch_size: int = 5, num_features: int = 10):
    """Test batch prediction."""
    print(f"\nTesting batch prediction endpoint ({batch_size} samples)...")
    try:
        # Create sample batch
        features_list = []
        for _ in range(batch_size):
            features = {f"feature_{i+1}": float(np.random.uniform(0, 10)) for i in range(num_features)}
            features_list.append(features)
        
        response = client.predict_batch(features_list)
        print(f"✓ Batch prediction successful")
        print(f"  Samples: {response['count']}")
        print(f"  Predictions: {response['predictions'][:3]}... (showing first 3)")
        return True
    except Exception as e:
        print(f"✗ Batch prediction failed: {str(e)}")
        return False


def test_dataframe_prediction(client: InferenceAPIClient, num_samples: int = 5, num_features: int = 10):
    """Test DataFrame prediction."""
    print(f"\nTesting DataFrame prediction endpoint ({num_samples} samples)...")
    try:
        # Create sample DataFrame format data
        data = {}
        for i in range(num_features):
            feature_name = f"feature_{i+1}"
            data[feature_name] = [float(np.random.uniform(0, 10)) for _ in range(num_samples)]
        
        response = client.predict_dataframe(data)
        print(f"✓ DataFrame prediction successful")
        print(f"  Samples: {response['count']}")
        print(f"  Predictions: {response['predictions']}")
        return True
    except Exception as e:
        print(f"✗ DataFrame prediction failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    parser = argparse.ArgumentParser(description="Test inference API")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:5000",
        help="Base URL of inference server"
    )
    parser.add_argument(
        "--features",
        type=int,
        default=10,
        help="Number of features"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ML Model Inference API Test Client")
    print("=" * 60)
    print(f"Target URL: {args.url}\n")
    
    client = InferenceAPIClient(base_url=args.url)
    
    results = {}
    results['health'] = test_health(client)
    results['info'] = test_model_info(client)
    results['single'] = test_single_prediction(client, num_features=args.features)
    results['batch'] = test_batch_prediction(client, batch_size=5, num_features=args.features)
    results['dataframe'] = test_dataframe_prediction(client, num_samples=5, num_features=args.features)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())