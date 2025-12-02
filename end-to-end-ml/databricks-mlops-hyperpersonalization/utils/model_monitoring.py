"""
Model Monitoring Module
=======================
Functions for monitoring model performance and detecting drift.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import logging
from typing import Dict, Any
import pandas as pd
import numpy as np
from scipy import stats


def calculate_prediction_distribution(predictions_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate distribution of predictions.
    
    Args:
        predictions_df: DataFrame with predictions
        
    Returns:
        Dictionary with distribution statistics
    """
    logging.info("Calculating prediction distribution...")
    
    # Count predictions by product
    pred_col = 'PREDICTED_PRODUCT_ID'
    distribution = predictions_df[pred_col].value_counts().to_dict()
    
    # Calculate percentages
    total = len(predictions_df)
    distribution_pct = {k: v/total*100 for k, v in distribution.items()}
    
    # Calculate entropy (measure of prediction diversity)
    probs = predictions_df[pred_col].value_counts(normalize=True).values
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    
    result = {
        'distribution': distribution,
        'distribution_pct': distribution_pct,
        'total_predictions': total,
        'unique_products': len(distribution),
        'entropy': float(entropy)
    }
    
    logging.info(f"Prediction distribution calculated: {len(distribution)} unique products")
    
    return result


def detect_feature_drift(reference_df: pd.DataFrame,
                        current_df: pd.DataFrame,
                        threshold: float = 0.1) -> Dict[str, Any]:
    """
    Detect feature drift using Kolmogorov-Smirnov test.
    
    Args:
        reference_df: Reference (training) data
        current_df: Current (production) data
        threshold: Drift detection threshold
        
    Returns:
        Dictionary with drift statistics
    """
    logging.info("Detecting feature drift...")
    
    drift_results = {}
    drifted_features = []
    
    # Get common numeric columns
    numeric_cols = reference_df.select_dtypes(include=[np.number]).columns
    common_cols = set(numeric_cols) & set(current_df.columns)
    
    for col in common_cols:
        try:
            # Kolmogorov-Smirnov test
            ref_values = reference_df[col].dropna()
            curr_values = current_df[col].dropna()
            
            if len(ref_values) > 0 and len(curr_values) > 0:
                ks_statistic, p_value = stats.ks_2samp(ref_values, curr_values)
                
                drift_detected = ks_statistic > threshold
                
                drift_results[col] = {
                    'ks_statistic': float(ks_statistic),
                    'p_value': float(p_value),
                    'drift_detected': drift_detected,
                    'ref_mean': float(ref_values.mean()),
                    'curr_mean': float(curr_values.mean()),
                    'mean_change_pct': float((curr_values.mean() - ref_values.mean()) / ref_values.mean() * 100)
                }
                
                if drift_detected:
                    drifted_features.append(col)
        except Exception as e:
            logging.warning(f"Could not calculate drift for {col}: {str(e)}")
    
    summary = {
        'total_features_checked': len(drift_results),
        'drifted_features_count': len(drifted_features),
        'drifted_features': drifted_features,
        'drift_threshold': threshold,
        'feature_drift_details': drift_results
    }
    
    logging.info(f"Drift detection completed: {len(drifted_features)}/{len(drift_results)} features drifted")
    
    return summary


def calculate_data_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate data quality metrics.
    
    Args:
        df: DataFrame to assess
        
    Returns:
        Dictionary with data quality metrics
    """
    logging.info("Calculating data quality metrics...")
    
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Missing values per column
    missing_per_col = df.isnull().sum().to_dict()
    
    # Columns with high missing rate (>20%)
    high_missing_cols = [col for col, count in missing_per_col.items() 
                         if count / len(df) > 0.2]
    
    # Duplicate rows
    duplicate_count = df.duplicated().sum()
    duplicate_pct = (duplicate_count / len(df) * 100) if len(df) > 0 else 0
    
    # Data quality score (0-1, higher is better)
    quality_score = 1.0 - (missing_pct / 100) - (duplicate_pct / 100)
    quality_score = max(0.0, min(1.0, quality_score))
    
    metrics = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_cells': int(missing_cells),
        'missing_percentage': float(missing_pct),
        'high_missing_columns': high_missing_cols,
        'duplicate_rows': int(duplicate_count),
        'duplicate_percentage': float(duplicate_pct),
        'quality_score': float(quality_score)
    }
    
    logging.info(f"Data quality score: {quality_score:.2f}")
    
    return metrics


def compare_model_performance(current_metrics: Dict[str, float],
                             baseline_metrics: Dict[str, float],
                             threshold: float = 0.05) -> Dict[str, Any]:
    """
    Compare current model performance with baseline.
    
    Args:
        current_metrics: Current model metrics
        baseline_metrics: Baseline model metrics
        threshold: Performance degradation threshold
        
    Returns:
        Comparison results
    """
    logging.info("Comparing model performance...")
    
    comparison = {}
    degraded_metrics = []
    
    for metric_name in baseline_metrics.keys():
        if metric_name in current_metrics and current_metrics[metric_name] is not None:
            baseline_value = baseline_metrics[metric_name]
            current_value = current_metrics[metric_name]
            
            change = current_value - baseline_value
            change_pct = (change / baseline_value * 100) if baseline_value != 0 else 0
            
            degraded = change < -threshold
            
            comparison[metric_name] = {
                'baseline': float(baseline_value),
                'current': float(current_value),
                'change': float(change),
                'change_percentage': float(change_pct),
                'degraded': degraded
            }
            
            if degraded:
                degraded_metrics.append(metric_name)
    
    summary = {
        'metrics_compared': len(comparison),
        'degraded_metrics_count': len(degraded_metrics),
        'degraded_metrics': degraded_metrics,
        'threshold': threshold,
        'metric_comparisons': comparison
    }
    
    logging.info(f"Performance comparison: {len(degraded_metrics)} metrics degraded")
    
    return summary


def generate_monitoring_report(prediction_distribution: Dict[str, Any],
                               drift_results: Dict[str, Any],
                               data_quality: Dict[str, Any],
                               performance_comparison: Dict[str, Any],
                               config: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate comprehensive monitoring report.
    
    Args:
        prediction_distribution: Prediction distribution metrics
        drift_results: Drift detection results
        data_quality: Data quality metrics
        performance_comparison: Performance comparison results
        config: Configuration dictionary
        
    Returns:
        DataFrame with monitoring summary
    """
    from datetime import datetime
    
    logging.info("Generating monitoring report...")
    
    # Determine overall status
    alerts = []
    
    # Check drift
    if drift_results['drifted_features_count'] > 0:
        alerts.append(f"Feature drift detected in {drift_results['drifted_features_count']} features")
    
    # Check data quality
    if data_quality['quality_score'] < config['monitoring']['drift_thresholds']['data_quality_score']:
        alerts.append(f"Data quality score below threshold: {data_quality['quality_score']:.2f}")
    
    # Check performance
    if performance_comparison.get('degraded_metrics_count', 0) > 0:
        alerts.append(f"Performance degradation in {performance_comparison['degraded_metrics_count']} metrics")
    
    overall_status = 'ALERT' if alerts else 'HEALTHY'
    
    # Create summary report
    report_data = {
        'monitoring_timestamp': [datetime.now()],
        'overall_status': [overall_status],
        'alerts': ['; '.join(alerts) if alerts else 'None'],
        'prediction_entropy': [prediction_distribution.get('entropy', 0)],
        'unique_products_predicted': [prediction_distribution.get('unique_products', 0)],
        'total_predictions': [prediction_distribution.get('total_predictions', 0)],
        'drifted_features_count': [drift_results['drifted_features_count']],
        'data_quality_score': [data_quality['quality_score']],
        'missing_percentage': [data_quality['missing_percentage']],
        'degraded_metrics_count': [performance_comparison.get('degraded_metrics_count', 0)]
    }
    
    report_df = pd.DataFrame(report_data)
    
    logging.info(f"Monitoring report generated. Status: {overall_status}")
    
    return report_df


def save_monitoring_results(report_df: pd.DataFrame,
                           detailed_results: Dict[str, Any],
                           config: Dict[str, Any],
                           output_path: str = None) -> None:
    """
    Save monitoring results to configured destination (CSV, JSON, HTML).
    
    Args:
        report_df: Summary report DataFrame
        detailed_results: Detailed monitoring results
        config: Configuration dictionary
        output_path: Optional output path for local saving
    """
    import os
    import json
    from datetime import datetime
    
    if output_path is None:
        output_path = config['monitoring']['output_path']
    
    # Resolve path relative to workspace root (not notebooks folder)
    if not os.path.isabs(output_path):
        # Get workspace root (go up from utils/ to project root)
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(utils_dir)
        output_path = os.path.join(workspace_root, output_path.lstrip('./'))
    
    os.makedirs(output_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save summary report (CSV)
    report_path = os.path.join(output_path, f"monitoring_report_{timestamp}.csv")
    report_df.to_csv(report_path, index=False)
    logging.info(f"Monitoring report saved to {report_path}")
    
    # Save detailed results (JSON)
    details_path = os.path.join(output_path, f"monitoring_details_{timestamp}.json")
    with open(details_path, 'w') as f:
        json.dump(detailed_results, f, indent=4, default=str)
    logging.info(f"Detailed results saved to {details_path}")
    
    # Save HTML report
    html_path = os.path.join(output_path, f"monitoring_report_{timestamp}.html")
    _generate_html_report(report_df, detailed_results, html_path, timestamp)
    logging.info(f"HTML report saved to {html_path}")


def _generate_html_report(report_df: pd.DataFrame, 
                         detailed_results: Dict[str, Any],
                         html_path: str,
                         timestamp: str) -> None:
    """
    Generate HTML report for monitoring results.
    
    Args:
        report_df: Summary report DataFrame
        detailed_results: Detailed monitoring results
        html_path: Path to save HTML file
        timestamp: Timestamp for report
    """
    from datetime import datetime
    
    # Extract key metrics
    status = report_df['overall_status'].values[0] if len(report_df) > 0 else 'UNKNOWN'
    alerts = report_df['alerts'].values[0] if len(report_df) > 0 else 'N/A'
    
    pred_dist = detailed_results.get('prediction_distribution', {})
    drift = detailed_results.get('drift_results', {})
    quality = detailed_results.get('data_quality', {})
    performance = detailed_results.get('performance_comparison', {})
    
    # Build HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Model Monitoring Report - {timestamp}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        .metric-box {{
            display: inline-block;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 10px 10px 0;
            min-width: 200px;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
            font-size: 14px;
        }}
        .metric-value {{
            font-size: 24px;
            color: #333;
            margin-top: 5px;
        }}
        .status-ok {{
            color: #4CAF50;
        }}
        .status-warning {{
            color: #FF9800;
        }}
        .status-critical {{
            color: #F44336;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Model Monitoring Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <h2>📊 Overall Status</h2>
        <div class="metric-box">
            <div class="metric-label">Overall Status</div>
            <div class="metric-value status-{'ok' if status == 'HEALTHY' else 'warning' if status == 'WARNING' else 'critical'}">{status}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Alerts</div>
            <div class="metric-value">{alerts}</div>
        </div>
        
        <h2>🎯 Prediction Distribution</h2>
        <div class="metric-box">
            <div class="metric-label">Total Predictions</div>
            <div class="metric-value">{pred_dist.get('total_predictions', 0)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Unique Products</div>
            <div class="metric-value">{pred_dist.get('unique_products', 0)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Entropy (Diversity)</div>
            <div class="metric-value">{pred_dist.get('entropy', 0):.4f}</div>
        </div>
        
        <h2>📉 Feature Drift Detection</h2>
        <div class="metric-box">
            <div class="metric-label">Features Checked</div>
            <div class="metric-value">{drift.get('total_features_checked', 0)}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Drifted Features</div>
            <div class="metric-value status-{'ok' if drift.get('drifted_features_count', 0) == 0 else 'warning'}">{drift.get('drifted_features_count', 0)}</div>
        </div>
        
        {_build_drifted_features_table(drift) if drift.get('drifted_features') else '<p><em>No drifted features detected.</em></p>'}
        
        <h2>✅ Data Quality</h2>
        <div class="metric-box">
            <div class="metric-label">Quality Score</div>
            <div class="metric-value status-{'ok' if quality.get('quality_score', 0) >= 0.8 else 'warning'}">{quality.get('quality_score', 0):.2f}</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Missing Data %</div>
            <div class="metric-value">{quality.get('missing_percentage', 0):.2f}%</div>
        </div>
        <div class="metric-box">
            <div class="metric-label">Duplicate Rows</div>
            <div class="metric-value">{quality.get('duplicate_rows', 0)}</div>
        </div>
        
        <h2>⚡ Model Performance</h2>
        <div class="metric-box">
            <div class="metric-label">Degraded Metrics</div>
            <div class="metric-value status-{'ok' if performance.get('degraded_metrics_count', 0) == 0 else 'warning'}">{performance.get('degraded_metrics_count', 0)}</div>
        </div>
        
        {_build_performance_table(performance) if performance.get('metric_comparisons') else '<p><em>No performance comparison available.</em></p>'}
        
        <div class="footer">
            <p>Home Credit Model Monitoring System | Report ID: {timestamp}</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _build_drifted_features_table(drift: Dict[str, Any]) -> str:
    """Build HTML table for drifted features."""
    if not drift.get('drifted_features'):
        return ''
    
    rows = []
    for feature in drift['drifted_features'][:10]:  # Top 10
        details = drift.get('feature_drift_details', {}).get(feature, {})
        ks_stat = details.get('ks_statistic', 0)
        rows.append(f"<tr><td>{feature}</td><td>{ks_stat:.4f}</td></tr>")
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>Feature Name</th>
                <th>KS Statistic</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def _build_performance_table(performance: Dict[str, Any]) -> str:
    """Build HTML table for performance metrics."""
    if not performance.get('metric_comparisons'):
        return ''
    
    rows = []
    for metric, comparison in performance['metric_comparisons'].items():
        # Parse comparison string like "accuracy: 0.72 vs 0.75 (degraded by 4.00%)"
        rows.append(f"<tr><td>{comparison}</td></tr>")
    
    return f"""
    <table>
        <thead>
            <tr>
                <th>Metric Comparison</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def create_monitoring_dashboard_data(report_df: pd.DataFrame,
                                     drift_results: Dict[str, Any],
                                     prediction_distribution: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for monitoring dashboard visualization.
    
    Args:
        report_df: Monitoring report DataFrame
        drift_results: Drift detection results
        prediction_distribution: Prediction distribution metrics
        
    Returns:
        Dictionary with dashboard data
    """
    dashboard_data = {
        'summary': report_df.to_dict('records')[0],
        'drift': {
            'drifted_features': drift_results['drifted_features'],
            'top_drifted': sorted(
                [(k, v['ks_statistic']) for k, v in drift_results['feature_drift_details'].items()
                 if v['drift_detected']],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        },
        'predictions': {
            'distribution': prediction_distribution['distribution_pct'],
            'entropy': prediction_distribution['entropy']
        }
    }
    
    return dashboard_data


def generate_evidently_reports(reference_data: pd.DataFrame,
                               current_data: pd.DataFrame,
                               target_data: pd.DataFrame = None,
                               predictions_df: pd.DataFrame = None,
                               target_col: str = None,
                               prediction_col: str = None,
                               output_path: str = None) -> Dict[str, str]:
    """
    Generate Evidently AI reports for data drift and classification performance.
    
    Args:
        reference_data: Reference (training) features dataset
        current_data: Current (production) features dataset
        target_data: DataFrame with actual target values (CUSTOMERID, NEXT_PRODUCT_ID)
        predictions_df: DataFrame with predictions (CUSTOMERID, PREDICTED_PRODUCT_ID)
        target_col: Name of target column (default: 'target')
        prediction_col: Name of prediction column (default: 'prediction')
        output_path: Directory to save HTML reports
        
    Returns:
        Dictionary with paths to generated reports
    """
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset, ClassificationPreset
    except ImportError as e:
        logging.warning(f"Evidently AI not installed or import failed: {e}")
        logging.warning("Install with: pip install evidently")
        return {}
    
    import os
    from datetime import datetime
    
    if output_path is None:
        output_path = './outputs/monitoring'
    
    # Resolve to absolute path
    if not os.path.isabs(output_path):
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(utils_dir)
        output_path = os.path.join(workspace_root, output_path.lstrip('./'))
    
    os.makedirs(output_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_paths = {}
    
    # 1. Data Drift Report - compare reference vs current feature distributions
    logging.info("Generating Evidently Data Drift report...")
    try:
        # Select only numeric columns for drift analysis
        numeric_cols = reference_data.select_dtypes(include=['number']).columns.tolist()
        # Remove ID columns
        numeric_cols = [col for col in numeric_cols if 'ID' not in col.upper()]
        
        if len(numeric_cols) > 0:
            ref_numeric = reference_data[numeric_cols].copy()
            curr_numeric = current_data[numeric_cols].copy()
            
            data_drift_report = Report(metrics=[DataDriftPreset()])
            data_drift_report.run(reference_data=ref_numeric, current_data=curr_numeric)

            drift_report_path = os.path.join(output_path, f"evidently_data_drift_{timestamp}.html")
            _safe_save_evidently_html(data_drift_report, drift_report_path, title="Data Drift Report")
            report_paths['data_drift'] = drift_report_path
            logging.info(f"✅ Data Drift report exported (HTML placeholder if full export unsupported): {os.path.basename(drift_report_path)}")
        else:
            logging.warning("No numeric columns found for drift analysis")
    except Exception as e:
        logging.error(f"Failed to generate Data Drift report: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
    
    # 2. Classification Report - requires targets and predictions
    if predictions_df is not None and target_data is not None:
        logging.info("Generating Evidently Classification report...")
        try:
            # Merge predictions with actual targets
            # Evidently expects DataFrame with 'target' and 'prediction' columns
            classification_data = predictions_df[['CUSTOMERID', prediction_col or 'PREDICTED_PRODUCT_ID']].merge(
                target_data[['CUSTOMERID', target_col or 'NEXT_PRODUCT_ID']],
                on='CUSTOMERID',
                how='inner'
            )
            
            # Filter to rows where we have actual targets (not null)
            classification_data = classification_data[
                classification_data[target_col or 'NEXT_PRODUCT_ID'].notna()
            ].copy()
            
            if len(classification_data) == 0:
                logging.warning("No customers with both predictions and targets for classification report")
            else:
                # Rename columns to what Evidently expects
                classification_data = classification_data.rename(columns={
                    target_col or 'NEXT_PRODUCT_ID': 'target',
                    prediction_col or 'PREDICTED_PRODUCT_ID': 'prediction'
                })
                
                # Split into reference (first half) and current (second half) for comparison
                split_idx = len(classification_data) // 2
                ref_class = classification_data.iloc[:split_idx].copy()
                curr_class = classification_data.iloc[split_idx:].copy()
                
                classification_report = Report(metrics=[ClassificationPreset()])
                classification_report.run(reference_data=ref_class, current_data=curr_class)

                classification_report_path = os.path.join(output_path, f"evidently_classification_{timestamp}.html")
                _safe_save_evidently_html(classification_report, classification_report_path, title="Classification Report")
                report_paths['classification'] = classification_report_path
                logging.info(f"✅ Classification report exported (HTML placeholder if full export unsupported): {os.path.basename(classification_report_path)}")
        except Exception as e:
            logging.error(f"Failed to generate Classification report: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
    
    return report_paths


def generate_evidently_dashboard(reference_data: pd.DataFrame,
                                 current_data: pd.DataFrame,
                                 target_data: pd.DataFrame = None,
                                 predictions_df: pd.DataFrame = None,
                                 target_col: str = None,
                                 prediction_col: str = None,
                                 output_path: str = None) -> str:
    """
    Generate a combined Evidently dashboard with Data Drift, Data Quality, and Classification presets.
    
    Args:
        reference_data: Reference (training) features dataset
        current_data: Current (production) features dataset
        target_data: DataFrame with actual target values (CUSTOMERID, NEXT_PRODUCT_ID)
        predictions_df: DataFrame with predictions (CUSTOMERID, PREDICTED_PRODUCT_ID)
        target_col: Name of target column (default: 'target')
        prediction_col: Name of prediction column (default: 'prediction')
        output_path: Directory to save dashboard
        
    Returns:
        Path to generated dashboard HTML file
    """
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset, DataSummaryPreset, ClassificationPreset
    except ImportError as e:
        logging.warning(f"Evidently AI not installed or import failed: {e}")
        logging.warning("Install with: pip install evidently")
        return None
    
    import os
    from datetime import datetime
    
    if output_path is None:
        output_path = './outputs/monitoring'
    
    # Resolve to absolute path
    if not os.path.isabs(output_path):
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.dirname(utils_dir)
        output_path = os.path.join(workspace_root, output_path.lstrip('./'))
    
    os.makedirs(output_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logging.info("Generating comprehensive Evidently dashboard...")
    
    try:
        # Select only numeric columns for drift/quality analysis
        numeric_cols = reference_data.select_dtypes(include=['number']).columns.tolist()
        ref_numeric = reference_data[numeric_cols].copy()
        curr_numeric = current_data[numeric_cols].copy()
        
        # Create comprehensive report with multiple presets
        metrics = [
            DataDriftPreset(),
            DataSummaryPreset()
        ]
        
        # Prepare classification data if available
        classification_data_ref = None
        classification_data_curr = None
        
        if predictions_df is not None and target_data is not None:
            try:
                # Merge predictions with actual targets
                classification_data = predictions_df[['CUSTOMERID', prediction_col or 'PREDICTED_PRODUCT_ID']].merge(
                    target_data[['CUSTOMERID', target_col or 'NEXT_PRODUCT_ID']],
                    on='CUSTOMERID',
                    how='inner'
                )
                
                # Filter to rows where we have actual targets
                classification_data = classification_data[
                    classification_data[target_col or 'NEXT_PRODUCT_ID'].notna()
                ].copy()
                
                if len(classification_data) > 0:
                    # Rename columns for Evidently
                    classification_data = classification_data.rename(columns={
                        target_col or 'NEXT_PRODUCT_ID': 'target',
                        prediction_col or 'PREDICTED_PRODUCT_ID': 'prediction'
                    })
                    
                    # Split into reference and current for comparison
                    split_idx = len(classification_data) // 2
                    classification_data_ref = classification_data.iloc[:split_idx].copy()
                    classification_data_curr = classification_data.iloc[split_idx:].copy()
                    
                    # Add classification preset
                    metrics.append(ClassificationPreset())
                    
                    logging.info(f"Classification data prepared: {len(classification_data_ref)} ref, {len(classification_data_curr)} curr")
            except Exception as e:
                logging.warning(f"Could not prepare classification data: {str(e)}")
        
        # Create dashboard report
        dashboard_report = Report(metrics=metrics)
        
        # Run report with appropriate data
        if classification_data_ref is not None and classification_data_curr is not None:
            # Merge numeric features with classification columns
            ref_with_class = ref_numeric.copy()
            curr_with_class = curr_numeric.copy()
            
            # Add target and prediction columns if they exist
            if 'target' in classification_data_ref.columns:
                ref_with_class['target'] = classification_data_ref['target'].values[:len(ref_with_class)]
                ref_with_class['prediction'] = classification_data_ref['prediction'].values[:len(ref_with_class)]
                curr_with_class['target'] = classification_data_curr['target'].values[:len(curr_with_class)]
                curr_with_class['prediction'] = classification_data_curr['prediction'].values[:len(curr_with_class)]
            
            dashboard_report.run(reference_data=ref_with_class, current_data=curr_with_class)
        else:
            # Only drift and quality, no classification
            dashboard_report.run(reference_data=ref_numeric, current_data=curr_numeric)
        
        # Save dashboard
        dashboard_path = os.path.join(output_path, f"evidently_dashboard_{timestamp}.html")
        _safe_save_evidently_html(dashboard_report, dashboard_path, title="Evidently Dashboard")
        logging.info(f"✅ Evidently dashboard exported (HTML placeholder if full export unsupported): {os.path.basename(dashboard_path)}")
        return dashboard_path
    
    except Exception as e:
        logging.error(f"Failed to generate Evidently dashboard: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return None


def _safe_save_evidently_html(report_obj: Any, html_path: str, title: str = "Evidently Report") -> None:
    """Safely persist Evidently report HTML.

    New Evidently versions (>=0.7) removed the save_html()/get_html() helpers from Report.
    This function attempts common methods; if unavailable, writes a minimal placeholder
    with guidance on how to obtain full interactive dashboards (pin earlier version or use new UI service).
    """
    try:
        # Try legacy method if present
        if hasattr(report_obj, 'save_html') and callable(getattr(report_obj, 'save_html')):
            report_obj.save_html(html_path)
            return
        # Try get_html / as_html variants
        for meth_name in ('get_html', 'as_html', 'html'):
            meth = getattr(report_obj, meth_name, None)
            if callable(meth):
                html = meth()
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                return
        # Fallback: create placeholder summarizing available metrics
        metrics_list = []
        try:
            metrics_attr = getattr(report_obj, 'metrics', [])
            metrics_list = [type(m).__name__ for m in metrics_attr] if metrics_attr else []
        except Exception:
            pass
        placeholder = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title>
        <style>body{{font-family:Arial,sans-serif;margin:40px;background:#fafafa}}code{{background:#eee;padding:2px 4px;border-radius:3px}}</style></head>
        <body><h1>{title}</h1>
        <p><strong>Notice:</strong> This Evidently version does not expose a direct HTML export API via <code>Report.save_html()</code>.
        A minimal placeholder is shown instead.</p>
        <h2>Included Metrics</h2>
        <ul>{''.join(f'<li>{m}</li>' for m in metrics_list) if metrics_list else '<li>No metrics discovered</li>'}</ul>
        <h2>How to get full interactive dashboards</h2>
        <ol>
           <li>Pin Evidently to an earlier version (e.g. <code>pip install evidently==0.6.0</code>) that supports <code>save_html</code>.</li>
           <li>Or integrate the new UI service components (e.g. <code>evidently.ui</code> dashboard manager) for richer visualization.</li>
        </ol>
        <p>File generated at: {html_path}</p>
        </body></html>"""
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(placeholder)
    except Exception as e:
        import logging
        logging.error(f"Failed to persist Evidently HTML placeholder: {e}")
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(f"Error writing HTML placeholder: {e}")
        except Exception:
            pass
