"""
Model Training Module
=====================
Reusable functions for training, evaluating, and logging ML models.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import logging
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import joblib


def prepare_training_data(features_df: pd.DataFrame,
                         target_df: pd.DataFrame,
                         config: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare data for model training (train-test split).
    
    Args:
        features_df: DataFrame with features
        target_df: DataFrame with target variable
        config: Configuration dictionary
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    logging.info("Preparing training data...")
    
    # Merge features with target
    df = features_df.merge(target_df, on='CUSTOMERID', how='inner')
    
    # Remove customers without target (didn't purchase next product)
    df = df[df['NEXT_PRODUCT_ID'].notna()].copy()
    
    logging.info(f"Training dataset: {len(df)} samples with target")
    
    # Separate features and target
    target_col = config['model']['target_variable']
    df[target_col] = df['NEXT_PRODUCT_ID']
    
    # Identify feature columns (exclude ID and target columns)
    id_cols = ['CUSTOMERID', 'PARTYID', 'NEXT_PRODUCT_ID', target_col]
    feature_cols = [col for col in df.columns if col not in id_cols]
    
    # Handle categorical columns (one-hot encoding)
    categorical_cols = df[feature_cols].select_dtypes(include=['object', 'category']).columns.tolist()
    
    # if categorical_cols:
    #     logging.info(f"Encoding {len(categorical_cols)} categorical columns")
    #     df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
        
    #     # Update feature columns after encoding
    #     id_cols_set = set(id_cols)
    #     feature_cols = [col for col in df.columns if col not in id_cols_set]

    # Convert interest rate columns to numeric (they should not be one-hot encoded)
    interest_rate_cols = [col for col in categorical_cols if 'INTEREST_RATE' in col]
    if interest_rate_cols:
        logging.info(f"Converting {len(interest_rate_cols)} interest rate columns to numeric: {interest_rate_cols}")
        for col in interest_rate_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove from categorical list
        categorical_cols = [col for col in categorical_cols if col not in interest_rate_cols]

    if categorical_cols:
        logging.info(f"Encoding {len(categorical_cols)} categorical columns: {categorical_cols}")
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    X = df[feature_cols]
    y = df[target_col]
    
    # Train-test split
    split_config = config['model']['train_test_split']
    test_size = split_config['test_size']
    random_state = split_config['random_state']
    stratify = y if split_config['stratify'] else None
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    
    logging.info(f"Train set: {len(X_train)} samples")
    logging.info(f"Test set: {len(X_test)} samples")
    logging.info(f"Number of features: {X_train.shape[1]}")
    logging.info(f"Number of classes: {y.nunique()}")
    
    return X_train, X_test, y_train, y_test


def get_model(config: Dict[str, Any]):
    """
    Initialize model based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Initialized sklearn model
    """
    algorithm = config['model']['algorithm']
    hyperparams = config['model']['hyperparameters'].get(algorithm, {})
    
    logging.info(f"Initializing {algorithm} model with params: {hyperparams}")
    
    if algorithm == 'random_forest':
        model = RandomForestClassifier(**hyperparams)
    elif algorithm == 'logistic_regression':
        model = LogisticRegression(**hyperparams)
    elif algorithm == 'xgboost':
        model = XGBClassifier(**hyperparams)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    return model


def train_model(model, X_train: pd.DataFrame, y_train: pd.Series):
    """
    Train the model.
    
    Args:
        model: Sklearn model instance
        X_train: Training features
        y_train: Training target
        
    Returns:
        Trained model (with label_encoder_ attribute if XGBoost)
    """
    logging.info("Training model...")
    
    # XGBoost requires 0-indexed class labels
    if isinstance(model, XGBClassifier):
        # Create label encoder and fit on training labels
        label_encoder = LabelEncoder()
        y_train_encoded = label_encoder.fit_transform(y_train)
        
        # Store encoder in model for later use during prediction
        model.label_encoder_ = label_encoder
        
        logging.info(f"XGBoost: Encoded labels from {label_encoder.classes_} to {list(range(len(label_encoder.classes_)))}")
        model.fit(X_train, y_train_encoded)
    else:
        model.fit(X_train, y_train)
    
    logging.info("Model training completed")
    
    return model


def evaluate_model(model, 
                   X_test: pd.DataFrame, 
                   y_test: pd.Series,
                   config: Dict[str, Any]) -> Dict[str, float]:
    """
    Evaluate model and return metrics.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test target
        config: Configuration dictionary
        
    Returns:
        Dictionary of evaluation metrics
    """
    logging.info("Evaluating model...")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # For XGBoost, decode predictions back to original labels
    if isinstance(model, XGBClassifier) and hasattr(model, 'label_encoder_'):
        y_test_encoded = model.label_encoder_.transform(y_test)
        y_pred_decoded = model.label_encoder_.inverse_transform(y_pred)
        y_pred = y_pred_decoded
        # For metrics calculation, use encoded values
        y_test_for_metrics = y_test
    else:
        y_test_for_metrics = y_test
    
    y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test_for_metrics, y_pred),
        'precision_weighted': precision_score(y_test_for_metrics, y_pred, average='weighted', zero_division=0),
        'recall_weighted': recall_score(y_test_for_metrics, y_pred, average='weighted', zero_division=0),
        'f1_weighted': f1_score(y_test_for_metrics, y_pred, average='weighted', zero_division=0)
    }
    
    # ROC AUC for multi-class (one-vs-rest)
    if y_pred_proba is not None and len(np.unique(y_test)) > 2:
        try:
            metrics['roc_auc_ovr'] = roc_auc_score(y_test_for_metrics, y_pred_proba, multi_class='ovr', average='weighted')
        except Exception as e:
            logging.warning(f"Could not calculate ROC AUC: {str(e)}")
            metrics['roc_auc_ovr'] = None
    
    # Calculate Top-K Accuracy (for recommendation systems)
    if y_pred_proba is not None:
        metrics['top_1_accuracy'] = top_k_accuracy(y_test_for_metrics, y_pred_proba, k=1)
        metrics['top_3_accuracy'] = top_k_accuracy(y_test_for_metrics, y_pred_proba, k=3)
        metrics['top_5_accuracy'] = top_k_accuracy(y_test_for_metrics, y_pred_proba, k=5)
        
        logging.info("Top-K Accuracy Metrics:")
        logging.info(f"  Top-1 Accuracy: {metrics['top_1_accuracy']:.4f}")
        logging.info(f"  Top-3 Accuracy: {metrics['top_3_accuracy']:.4f}")
        logging.info(f"  Top-5 Accuracy: {metrics['top_5_accuracy']:.4f}")
    
    # Log metrics
    logging.info("Model Evaluation Metrics:")
    for metric_name, value in metrics.items():
        if value is not None:
            logging.info(f"  {metric_name}: {value:.4f}")
    
    return metrics


def top_k_accuracy(y_true: pd.Series, y_pred_proba: np.ndarray, k: int = 3) -> float:
    """
    Calculate Top-K accuracy for recommendation systems.
    
    Measures if the true label is within the top-K predictions.
    This is more relevant for recommendation systems where we show
    multiple options to customers.
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities (n_samples, n_classes)
        k: Number of top predictions to consider
        
    Returns:
        Top-K accuracy score (0.0 to 1.0)
    
    Example:
        If k=3 and top_3_accuracy=0.92, it means the true product
        is in the top-3 recommendations 92% of the time.
    """
    # Get top-K predictions for each sample
    top_k_preds = np.argsort(y_pred_proba, axis=1)[:, -k:]
    
    # Convert y_true to numpy array
    y_true_array = np.array(y_true)
    
    # Check if true label is in top-K predictions
    correct = 0
    for i, true_label in enumerate(y_true_array):
        if true_label in top_k_preds[i]:
            correct += 1
    
    return correct / len(y_true_array)


def get_feature_importance(model, feature_names: List[str], top_n: int = 20) -> pd.DataFrame:
    """
    Get feature importance from trained model.
    
    Args:
        model: Trained model
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        DataFrame with feature importance
    """
    if not hasattr(model, 'feature_importances_'):
        logging.warning("Model does not have feature_importances_ attribute")
        return pd.DataFrame()
    
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False).head(top_n)
    
    logging.info(f"Top {top_n} most important features:")
    for idx, row in importance_df.iterrows():
        logging.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    return importance_df


def plot_feature_importance(importance_df: pd.DataFrame, 
                           output_path: str,
                           top_n: int = 20,
                           algorithm: str = 'model') -> None:
    """
    Plot and save feature importance as PNG image.
    
    Args:
        importance_df: DataFrame with feature importance (from get_feature_importance)
        output_path: Path to save the plot (e.g., 'outputs/models/feature_importance.png')
        top_n: Number of top features to plot
        algorithm: Algorithm name for plot title
    """
    if importance_df.empty:
        logging.warning("Empty feature importance DataFrame. Skipping plot.")
        return
    
    # Take top N features
    plot_df = importance_df.head(top_n)
    
    # Create horizontal bar plot
    plt.figure(figsize=(10, 8))
    plt.barh(range(len(plot_df)), plot_df['importance'], color='steelblue')
    plt.yticks(range(len(plot_df)), plot_df['feature'])
    plt.xlabel('Importance', fontsize=12)
    plt.ylabel('Features', fontsize=12)
    plt.title(f'Top {top_n} Feature Importance - {algorithm.upper()}', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()  # Highest importance at top
    plt.tight_layout()
    
    # Save plot
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logging.info(f"Feature importance plot saved to: {output_path}")


def log_model_to_mlflow(model,
                       X_train: pd.DataFrame,
                       metrics: Dict[str, float],
                       feature_importance: pd.DataFrame,
                       config: Dict[str, Any],
                       mlflow_client) -> str:
    """
    Log model and artifacts to MLflow.
    
    Args:
        model: Trained model
        X_train: Training features (for input example)
        metrics: Evaluation metrics dictionary
        feature_importance: Feature importance DataFrame
        config: Configuration dictionary
        mlflow_client: MLflow client instance
        
    Returns:
        Run ID
    """
    import mlflow.sklearn
    from mlflow.models.signature import infer_signature
    
    logging.info("Logging model to MLflow...")
    
    # Generate run name
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    algorithm = config['model']['algorithm']
    run_name = f"{config['mlflow']['run_name_prefix']}_{algorithm}_{timestamp}"
    
    # Start MLflow run
    with mlflow_client.start_run(run_name=run_name) as run:
        run_id = run.info.run_id
        
        # Log parameters
        mlflow_client.log_params({
            'algorithm': algorithm,
            'test_size': config['model']['train_test_split']['test_size'],
            'random_state': config['model']['train_test_split']['random_state'],
            **config['model']['hyperparameters'].get(algorithm, {})
        })
        
        # Log metrics
        valid_metrics = {k: v for k, v in metrics.items() if v is not None}
        mlflow_client.log_metrics(valid_metrics)
        
        # Log tags
        tags = config['mlflow'].get('tags', {})
        mlflow_client.set_tags(tags)
        
        # Infer model signature (inputs -> predicted labels)
        try:
            example_X = X_train.head(5)
            example_y_pred = model.predict(example_X)
            signature = infer_signature(example_X, example_y_pred)
        except Exception as e:
            logging.warning(f"Could not infer signature: {e}")
            signature = None

        # Log model with signature & input example (improves serving schema enforcement)
        mlflow.sklearn.log_model(
            model,
            "model",
            input_example=example_X,
            signature=signature
        )

        # Log feature column list artifact for downstream inference alignment
        try:
            feature_cols = list(X_train.columns)
            mlflow_client.log_dict({"feature_columns": feature_cols}, "feature_columns.json")
        except Exception as e:
            logging.warning(f"Failed to log feature_columns.json artifact: {e}")
        
        # Log feature importance as artifact
        if not feature_importance.empty:
            # Get workspace root by going up from current working directory if in notebooks folder
            import os
            cwd = os.getcwd()
            
            # If running from notebooks folder, go up one level to workspace root
            if cwd.endswith('notebooks'):
                workspace_root = os.path.dirname(cwd)
            else:
                # Otherwise, use utils parent directory
                workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            output_dir = os.path.join(workspace_root, 'outputs', 'models')
            os.makedirs(output_dir, exist_ok=True)
            
            feature_importance_path = os.path.join(output_dir, 'feature_importance.csv')
            feature_importance.to_csv(feature_importance_path, index=False)
            
            logging.info(f"Feature importance saved to {feature_importance_path}")
            print(f"📊 Feature importance saved to: {feature_importance_path}")
            
            # Log to MLflow from this path
            mlflow_client.log_artifact(feature_importance_path, "feature_importance")
        
        logging.info(f"Model logged to MLflow with run_id: {run_id}")
    
    return run_id


def save_model_locally(model, 
                      feature_names: List[str],
                      output_path: str = "./outputs/models") -> str:
    """
    Save model to local file system.
    
    Args:
        model: Trained model
        feature_names: List of feature names
        output_path: Output directory path
        
    Returns:
        Path to saved model
    """
    import os
    from datetime import datetime
    
    os.makedirs(output_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_filename = f"model_{timestamp}.pkl"
    model_path = os.path.join(output_path, model_filename)
    
    # Save model and feature names
    model_artifact = {
        'model': model,
        'feature_names': feature_names
    }
    
    joblib.dump(model_artifact, model_path)
    
    logging.info(f"Model saved locally to {model_path}")
    
    return model_path


def load_model_from_file(model_path: str) -> Tuple:
    """
    Load model from local file.
    
    Args:
        model_path: Path to model file
        
    Returns:
        Tuple of (model, feature_names)
    """
    model_artifact = joblib.load(model_path)
    
    model = model_artifact['model']
    feature_names = model_artifact['feature_names']
    
    logging.info(f"Model loaded from {model_path}")
    
    return model, feature_names


def predict_top_k_products(model,
                          X: pd.DataFrame,
                          customer_ids: pd.Series,
                          k: int = 3) -> pd.DataFrame:
    """
    Predict top-k products for each customer.
    
    Args:
        model: Trained model
        X: Features DataFrame
        customer_ids: Customer IDs corresponding to X
        k: Number of top products to recommend
        
    Returns:
        DataFrame with customer ID and top-k product recommendations with probabilities
    """
    logging.info(f"Generating top-{k} product recommendations...")
    
    # Get prediction probabilities
    y_pred_proba = model.predict_proba(X)
    
    # Get class labels
    classes = model.classes_
    
    # Create results list
    results = []
    
    for idx, customer_id in enumerate(customer_ids):
        # Get probabilities for this customer
        probs = y_pred_proba[idx]
        
        # Get top-k indices
        top_k_indices = np.argsort(probs)[-k:][::-1]
        
        # Get top-k products and probabilities
        for rank, class_idx in enumerate(top_k_indices, 1):
            results.append({
                'CUSTOMERID': customer_id,
                'RANK': rank,
                'PREDICTED_PRODUCT_ID': classes[class_idx],
                'PROBABILITY': probs[class_idx]
            })
    
    results_df = pd.DataFrame(results)
    
    logging.info(f"Generated {len(results_df)} recommendations for {len(customer_ids)} customers")
    
    return results_df
