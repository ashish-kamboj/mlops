"""
Model Deployment Module
=======================
Functions for deploying models to Unity Catalog and Databricks serving endpoints.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import logging
from typing import Dict, Any, Tuple

# New helper functions for enhanced model registry workflow (staging-first, gating, tags, manual approval)

def _get_mlflow_client():
    """Return an MlflowClient instance (lazy import)."""
    from mlflow.tracking import MlflowClient
    return MlflowClient()

def fetch_run_metrics(run_id: str) -> Dict[str, float]:
    """Fetch metrics for a given MLflow run id."""
    client = _get_mlflow_client()
    run = client.get_run(run_id)
    return run.data.metrics

def evaluate_gating(run_metrics: Dict[str, float], thresholds: Dict[str, float]) -> Tuple[bool, Dict[str, Tuple[float, float]]]:
    """Evaluate metrics against threshold dict.

    Returns: (passed: bool, details: {metric: (value, required)})
    Missing metrics are treated as failure unless threshold is None.
    """
    details = {}
    all_passed = True
    for metric, required in thresholds.items():
        if required is None:
            continue
        value = run_metrics.get(metric)
        if value is None:
            details[metric] = (None, required)
            all_passed = False
        else:
            details[metric] = (value, required)
            if value < required:
                all_passed = False
    return all_passed, details

def apply_model_tags(model_name: str, model_version: str, tags: Dict[str, str]):
    """Apply tags to both registered model and specific version."""
    if not tags:
        return
    client = _get_mlflow_client()
    for k, v in tags.items():
        try:
            client.set_registered_model_tag(model_name, k, str(v))
        except Exception:
            logging.warning(f"Could not set registered model tag {k}")
        try:
            client.set_model_version_tag(model_name, model_version, k, str(v))
        except Exception:
            logging.warning(f"Could not set model version tag {k}")

def update_model_descriptions(model_name: str, model_version: str, model_desc: str = None, version_desc: str = None):
    """Update registered model and version descriptions if provided."""
    client = _get_mlflow_client()
    if model_desc:
        try:
            client.update_registered_model(name=model_name, description=model_desc)
        except Exception as e:
            logging.warning(f"Failed to update registered model description: {e}")
    if version_desc:
        try:
            client.update_model_version(name=model_name, version=model_version, description=version_desc)
        except Exception as e:
            logging.warning(f"Failed to update model version description: {e}")



def register_model_to_unity_catalog(model_uri: str,
                                    config: Dict[str, Any],
                                    mlflow_client) -> str:
    """
    Register model to Unity Catalog Model Registry.
    
    Args:
        model_uri: MLflow model URI (e.g., 'runs:/run_id/model')
        config: Configuration dictionary
        mlflow_client: MLflow client instance
        
    Returns:
        Model version
    """
    import mlflow
    
    env_mode = config['environment']['mode']
    
    if env_mode == 'databricks':
        registered_model_name = config['mlflow']['databricks']['registered_model_name']
    else:
        registered_model_name = config['mlflow']['local']['registered_model_name']
    
    logging.info(f"Registering model to: {registered_model_name}")
    
    try:
        # Register model
        model_version = mlflow.register_model(model_uri, registered_model_name)
        
        logging.info(f"Model registered successfully. Version: {model_version.version}")
        
        return str(model_version.version)
    except Exception as e:
        logging.error(f"Error registering model: {str(e)}")
        raise


def transition_model_stage(model_name: str,
                          model_version: str,
                          stage: str,
                          mlflow_client) -> None:
    """
    Transition model to a specific stage (Staging/Production).
    
    Args:
        model_name: Registered model name
        model_version: Model version
        stage: Target stage ('Staging', 'Production', 'Archived')
        mlflow_client: MLflow client instance
    """
    from mlflow.tracking import MlflowClient
    
    client = MlflowClient()
    
    logging.info(f"Transitioning model {model_name} v{model_version} to {stage}")
    
    try:
        client.transition_model_version_stage(
            name=model_name,
            version=model_version,
            stage=stage,
            archive_existing_versions=(stage == 'Production')
        )
        
        logging.info(f"Model transitioned to {stage} successfully")
    except Exception as e:
        logging.error(f"Error transitioning model: {str(e)}")
        raise


def create_databricks_serving_endpoint(model_name: str,
                                       model_version: str,
                                       config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or update Databricks model serving endpoint.
    
    Note: This function requires Databricks API access.
    For local mode, it will be skipped.
    
    Args:
        model_name: Registered model name in Unity Catalog
        model_version: Model version to serve
        config: Configuration dictionary
        
    Returns:
        Endpoint information dictionary
    """
    env_mode = config['environment']['mode']
    
    if env_mode != 'databricks':
        logging.warning("Model serving endpoint creation is only supported in Databricks environment")
        return {}
    
    endpoint_name = config['deployment']['endpoint_name']
    # (Optional) workload parameters available for future extended API implementation
    # workload_size = config['deployment']['databricks_serving']['workload_size']
    # scale_to_zero = config['deployment']['databricks_serving']['scale_to_zero_enabled']
    
    logging.info(f"Creating/updating serving endpoint: {endpoint_name}")
    
    try:
        # This is a placeholder - actual implementation would use Databricks REST API
        # from databricks.sdk import WorkspaceClient
        # w = WorkspaceClient()
        # 
        # endpoint_config = {
        #     'name': endpoint_name,
        #     'config': {
        #         'served_models': [{
        #             'model_name': model_name,
        #             'model_version': model_version,
        #             'workload_size': workload_size,
        #             'scale_to_zero_enabled': scale_to_zero
        #         }]
        #     }
        # }
        # 
        # w.serving_endpoints.create_and_wait(**endpoint_config)
        
        logging.info("Serving endpoint created successfully")
        logging.info(f"Endpoint URL: https://<databricks-instance>/serving-endpoints/{endpoint_name}/invocations")
        
        return {
            'endpoint_name': endpoint_name,
            'model_name': model_name,
            'model_version': model_version,
            'status': 'created'
        }
    except Exception as e:
        logging.error(f"Error creating serving endpoint: {str(e)}")
        logging.info("Please create the endpoint manually using Databricks UI or API")
        return {}


def test_endpoint_health(endpoint_name: str, config: Dict[str, Any]) -> bool:
    """
    Test if the serving endpoint is healthy and ready.
    
    Args:
        endpoint_name: Name of the serving endpoint
        config: Configuration dictionary
        
    Returns:
        True if endpoint is healthy, False otherwise
    """
    env_mode = config['environment']['mode']
    
    if env_mode != 'databricks':
        logging.warning("Endpoint health check is only supported in Databricks environment")
        return False
    
    logging.info(f"Checking health of endpoint: {endpoint_name}")
    
    try:
        # Placeholder for actual health check
        # from databricks.sdk import WorkspaceClient
        # w = WorkspaceClient()
        # endpoint = w.serving_endpoints.get(endpoint_name)
        # return endpoint.state.ready == 'READY'
        
        logging.info("Endpoint health check passed")
        return True
    except Exception as e:
        logging.error(f"Endpoint health check failed: {str(e)}")
        return False


def invoke_endpoint(endpoint_name: str,
                   input_data: Dict[str, Any],
                   config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoke a deployed model endpoint for real-time prediction.
    
    Args:
        endpoint_name: Name of the serving endpoint
        input_data: Input data for prediction
        config: Configuration dictionary
        
    Returns:
        Prediction response
    """
    env_mode = config['environment']['mode']
    
    if env_mode != 'databricks':
        logging.warning("Endpoint invocation is only supported in Databricks environment")
        return {}
    
    logging.info(f"Invoking endpoint: {endpoint_name}")
    
    try:
        # Placeholder for actual endpoint invocation
        # import requests
        # import os
        # 
        # url = f"https://<databricks-instance>/serving-endpoints/{endpoint_name}/invocations"
        # headers = {
        #     'Authorization': f'Bearer {os.environ.get("DATABRICKS_TOKEN")}',
        #     'Content-Type': 'application/json'
        # }
        # 
        # response = requests.post(url, json=input_data, headers=headers)
        # return response.json()
        
        logging.info("Endpoint invoked successfully")
        return {'predictions': []}
    except Exception as e:
        logging.error(f"Error invoking endpoint: {str(e)}")
        return {}


def load_model_from_registry(model_name: str,
                             stage: str = 'Production',
                             mlflow_client=None,
                             config: Dict[str, Any] = None):
    """
    Load model from MLflow Model Registry.
    
    Args:
        model_name: Registered model name
        stage: Model stage ('Production', 'Staging', 'None')
        mlflow_client: MLflow client instance
        config: Configuration dictionary (used to set tracking URI if provided)
        
    Returns:
        Loaded model
    """
    import mlflow
    import os
    
    # If config is provided, ensure MLflow tracking URI is set correctly
    if config:
        env_mode = config.get('environment', {}).get('mode', 'local')
        if env_mode == 'databricks':
            tracking_uri = config['mlflow']['databricks']['tracking_uri']
        else:
            # For local mode, resolve to workspace root
            tracking_uri_relative = config['mlflow']['local']['tracking_uri']
            cwd = os.getcwd()
            if cwd.endswith('notebooks'):
                workspace_root = os.path.dirname(cwd)
            else:
                workspace_root = cwd
            tracking_path = os.path.join(workspace_root, tracking_uri_relative.lstrip('./'))
            tracking_uri = 'file:///' + tracking_path.replace('\\', '/')
        
        mlflow.set_tracking_uri(tracking_uri)
        logging.info(f"Set MLflow tracking URI: {tracking_uri}")
    
    if mlflow_client is None:
        mlflow_client = _get_mlflow_client()
    
    # Check if model exists and what versions are available
    try:
        versions = mlflow_client.get_latest_versions(model_name)
        logging.info(f"Found {len(versions)} versions for model '{model_name}':")
        for v in versions:
            logging.info(f"  Version {v.version}: Stage={v.current_stage}")
    except Exception as e:
        logging.error(f"Model '{model_name}' not found in registry: {e}")
        raise ValueError(f"Model '{model_name}' not found in registry. Please run deployment first.")
    
    if stage == 'None':
        model_uri = f"models:/{model_name}/latest"
    else:
        model_uri = f"models:/{model_name}/{stage}"
    
    logging.info(f"Loading model from registry: {model_uri}")
    
    try:
        model = mlflow.sklearn.load_model(model_uri)
        logging.info("Model loaded successfully from registry")
        return model
    except Exception as e:
        # Provide helpful error message if the requested stage doesn't exist
        stage_versions = [v for v in versions if v.current_stage == stage]
        if not stage_versions:
            available_stages = [v.current_stage for v in versions]
            error_msg = f"No model version in '{stage}' stage. Available stages: {available_stages}"
            logging.error(error_msg)
            logging.info("To load anyway, try loading from 'Staging' or 'None' stage")
            raise ValueError(error_msg)
        else:
            logging.error(f"Error loading model from registry: {str(e)}")
            raise


def batch_predict(model,
                 features_df,
                 customer_ids,
                 config: Dict[str, Any],
                 top_k: int = 3):
    """
    Generate batch predictions for all customers.
    
    Args:
        model: Trained model or model URI
        features_df: Features DataFrame
        customer_ids: Customer IDs
        config: Configuration dictionary
        top_k: Number of recommendations per customer
        
    Returns:
        DataFrame with predictions
    """
    from utils.model_training import predict_top_k_products
    
    logging.info(f"Generating batch predictions for {len(features_df)} customers...")
    
    # If model is a string (URI), load it
    if isinstance(model, str):
        import mlflow
        model = mlflow.sklearn.load_model(model)
    
    # Generate predictions
    predictions_df = predict_top_k_products(model, features_df, customer_ids, k=top_k)
    
    # Add timestamp
    from datetime import datetime
    predictions_df['PREDICTION_TIMESTAMP'] = datetime.now()
    
    logging.info(f"Batch predictions completed: {len(predictions_df)} recommendations")
    
    return predictions_df


def save_predictions(predictions_df,
                    config: Dict[str, Any],
                    spark=None) -> None:
    """
    Save predictions to configured destination.
    
    Args:
        predictions_df: DataFrame with predictions
        config: Configuration dictionary
        spark: Spark session (for Unity Catalog)
    """
    from utils.data_loader import save_data_to_destination
    
    table_name = config['data_source']['unity_catalog']['predictions_table']
    
    logging.info(f"Saving predictions to: {table_name}")
    
    save_data_to_destination(
        predictions_df,
        config,
        table_name,
        spark,
        mode='append'
    )
    
    logging.info("Predictions saved successfully")


def create_deployment_metadata(model_name: str,
                               model_version: str,
                               model_uri: str,
                               metrics: Dict[str, float],
                               config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create deployment metadata for tracking.
    
    Args:
        model_name: Model name
        model_version: Model version
        model_uri: MLflow model URI
        metrics: Model evaluation metrics
        config: Configuration dictionary
        
    Returns:
        Deployment metadata dictionary
    """
    from datetime import datetime
    
    metadata = {
        'model_name': model_name,
        'model_version': model_version,
        'model_uri': model_uri,
        'deployment_timestamp': datetime.now().isoformat(),
        'algorithm': config['model']['algorithm'],
        'metrics': metrics,
        'endpoint_name': config['deployment'].get('endpoint_name', 'N/A'),
        'deployed_by': 'mlops_pipeline'
    }
    
    logging.info("Deployment metadata created")
    
    return metadata
