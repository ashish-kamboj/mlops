"""
Drift Detector Module
Core module for detecting data drift using Evidently AI library.
Supports multiple statistical tests for numerical and categorical columns.
"""

import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from evidently.legacy.pipeline.column_mapping import ColumnMapping
from evidently import Report
from evidently.presets import DataDriftPreset

class DriftDetector:
    """
    Detects data drift between two datasets using Evidently AI.
    
    This class handles the core drift detection logic, including:
    - Column type identification
    - Statistical test configuration
    - Drift report generation
    - Result extraction and formatting
    """
    
    def __init__(self, config_manager):
        """
        Initialize DriftDetector with configuration.
        
        Args:
            config_manager: ConfigManager instance with loaded configuration
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.drift_config = self.config.get_drift_detection_config()
    
    def detect_drift(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        table_name: str,
        columns: Optional[List[str]] = None
    ) -> Tuple[Report, Dict[str, Any]]:
        """
        Detect data drift between reference and current datasets.
        
        Args:
            reference_data (pd.DataFrame): Reference dataset (previous version)
            current_data (pd.DataFrame): Current dataset (latest version)
            table_name (str): Name of the table being analyzed
            columns (Optional[List[str]]): Specific columns to analyze (None = all)
            
        Returns:
            Tuple[Report, Dict[str, Any]]: Evidently Report object and drift summary
            
        Raises:
            ValueError: If datasets are invalid or incompatible
        """
        self.logger.info(f"Starting drift detection for table: {table_name}")
        
        # Validate datasets
        self._validate_datasets(reference_data, current_data, table_name)
        
        # Prepare data
        ref_data, cur_data = self._prepare_data(
            reference_data, current_data, columns
        )
        
        # Identify column types
        numerical_cols, categorical_cols = self._identify_column_types(ref_data)
        
        self.logger.info(f"Detected {len(numerical_cols)} numerical and "
                        f"{len(categorical_cols)} categorical columns")
        
        # Configure column mapping for Evidently
        column_mapping = self._create_column_mapping(numerical_cols, categorical_cols)
        
        # Create and run drift report
        # report = self._create_drift_report(
        #     ref_data, cur_data, column_mapping
        # )

        report = self._create_drift_report(
            ref_data, cur_data
        )
        
        # Extract drift summary
        drift_summary = self._extract_drift_summary(
            report, table_name, numerical_cols, categorical_cols
        )
        
        self.logger.info(f"Drift detection completed for {table_name}. "
                        f"Drifted columns: {drift_summary['num_drifted_columns']}")
        
        return report, drift_summary
    
    def _validate_datasets(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        table_name: str
    ) -> None:
        """
        Validate that datasets meet requirements for drift detection.
        
        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            table_name: Table name for error messages
            
        Raises:
            ValueError: If datasets are invalid
        """
        min_sample_size = self.drift_config.get('min_sample_size', 100)
        
        # Check if datasets are empty
        if reference_data.empty:
            raise ValueError(f"Reference dataset for {table_name} is empty")
        if current_data.empty:
            raise ValueError(f"Current dataset for {table_name} is empty")
        
        # Check minimum sample size
        if len(reference_data) < min_sample_size:
            self.logger.warning(
                f"Reference data size ({len(reference_data)}) is below "
                f"minimum sample size ({min_sample_size})"
            )
        if len(current_data) < min_sample_size:
            self.logger.warning(
                f"Current data size ({len(current_data)}) is below "
                f"minimum sample size ({min_sample_size})"
            )
        
        # Check column compatibility
        ref_cols = set(reference_data.columns)
        cur_cols = set(current_data.columns)
        
        if ref_cols != cur_cols:
            missing_in_current = ref_cols - cur_cols
            missing_in_reference = cur_cols - ref_cols
            
            if missing_in_current:
                self.logger.warning(
                    f"Columns in reference but not in current: {missing_in_current}"
                )
            if missing_in_reference:
                self.logger.warning(
                    f"Columns in current but not in reference: {missing_in_reference}"
                )
    
    def _prepare_data(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        columns: Optional[List[str]]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Prepare datasets for drift detection.
        
        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            columns: Specific columns to include (None = all)
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Prepared reference and current datasets
        """
        # Get common columns
        common_cols = list(set(reference_data.columns) & set(current_data.columns))
        
        # Filter to specified columns if provided
        if columns and columns != 'all':
            common_cols = [col for col in common_cols if col in columns]
        
        # No explicit ID exclusion; all selected columns are analyzed
        
        # Handle missing values based on strategy
        strategy = self.drift_config.get('missing_values_strategy', 'keep')
        
        ref_data = reference_data[common_cols].copy()
        cur_data = current_data[common_cols].copy()
        
        if strategy == 'drop':
            ref_data = ref_data.dropna()
            cur_data = cur_data.dropna()
            self.logger.info(f"Dropped missing values. Ref size: {len(ref_data)}, "
                           f"Cur size: {len(cur_data)}")
        elif strategy == 'fill':
            # Fill numeric columns with median, categorical with mode
            for col in ref_data.columns:
                if pd.api.types.is_numeric_dtype(ref_data[col]):
                    ref_median = ref_data[col].median()
                    ref_data[col].fillna(ref_median, inplace=True)
                    cur_data[col].fillna(ref_median, inplace=True)
                else:
                    ref_mode = ref_data[col].mode()[0] if not ref_data[col].mode().empty else 'Unknown'
                    ref_data[col].fillna(ref_mode, inplace=True)
                    cur_data[col].fillna(ref_mode, inplace=True)
        
        return ref_data, cur_data
    
    def _identify_column_types(
        self,
        data: pd.DataFrame
    ) -> Tuple[List[str], List[str]]:
        """
        Identify numerical and categorical columns.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Tuple[List[str], List[str]]: Lists of numerical and categorical column names
        """
        numerical_cols = []
        categorical_cols = []
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                # Check if it's actually categorical (e.g., few unique values)
                unique_ratio = data[col].nunique() / len(data)
                if unique_ratio < 0.05 and data[col].nunique() < 20:
                    categorical_cols.append(col)
                else:
                    numerical_cols.append(col)
            else:
                categorical_cols.append(col)
        
        return numerical_cols, categorical_cols
    
    def _create_column_mapping(
        self,
        numerical_cols: List[str],
        categorical_cols: List[str]
    ) -> ColumnMapping:
        """
        Create Evidently column mapping.
        
        Args:
            numerical_cols: List of numerical column names
            categorical_cols: List of categorical column names
            
        Returns:
            ColumnMapping: Evidently column mapping object
        """
        return ColumnMapping(
            numerical_features=numerical_cols,
            categorical_features=categorical_cols
        )
    
    def _create_drift_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        #column_mapping: ColumnMapping
    ) -> Report:
        """
        Create and generate Evidently drift report using DataDriftPreset.
        
        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            column_mapping: Column mapping for Evidently
        Returns:
            Report: Generated Evidently report
        """
        # Use DataDriftPreset for drift detection
        report = Report([DataDriftPreset()])
        self.logger.info("Generating Evidently report...")
        generate_report = report.run(
            reference_data=reference_data,
            current_data=current_data
            #column_mapping=column_mapping
        )
        return generate_report
    
    def _extract_drift_summary(
        self,
        report: Report,
        table_name: str,
        numerical_cols: List[str],
        categorical_cols: List[str]
    ) -> Dict[str, Any]:
        """
        Extract drift detection summary from Evidently report.
        
        Args:
            report: Evidently Report object
            table_name: Name of the table
            numerical_cols: List of numerical columns
            categorical_cols: List of categorical columns
        Returns:
            Dict[str, Any]: Drift summary with key metrics
        """

        report_json_str = report.json()  # Returns JSON string
        report_dict = json.loads(report_json_str)

        drift_info = {
            'table_name': table_name,
            'timestamp': datetime.now().isoformat(),
            'num_columns': len(numerical_cols) + len(categorical_cols),
            'num_numerical_columns': len(numerical_cols),
            'num_categorical_columns': len(categorical_cols),
            'numerical_columns': numerical_cols,
            'categorical_columns': categorical_cols,
            'drifted_columns': [],
            'num_drifted_columns': 0,
            'drift_share': 0.0,
            'dataset_drift': False,
            'column_drift_details': {}
        }
        try:
            metrics = report_dict.get('metrics', [])
            drifted_columns_count = None
            drift_share = None
            for metric in metrics:
                config = metric.get('config', {})
                value = metric.get('value', None)
                # Drifted columns count and share
                if config.get('type') == 'evidently:metric_v2:DriftedColumnsCount':
                    drifted_columns_count = value.get('count', 0) if isinstance(value, dict) else 0
                    drift_share = value.get('share', 0.0) if isinstance(value, dict) else 0.0
                # Per-column drift metrics
                if config.get('type') == 'evidently:metric_v2:ValueDrift':
                    col_name = config.get('column')
                    method = config.get('method')
                    threshold = config.get('threshold')
                    drift_score = value
                    is_drifted = False
                    if drift_score is not None and threshold is not None:
                        is_drifted = drift_score >= threshold
                    if is_drifted:
                        drift_info['drifted_columns'].append(col_name)
                    drift_info['column_drift_details'][col_name] = {
                        'drift_detected': is_drifted,
                        'drift_score': drift_score,
                        'method': method,
                        'threshold': threshold
                    }
            drift_info['num_drifted_columns'] = len(drift_info['drifted_columns'])
            drift_info['drift_share'] = drift_share if drift_share is not None else 0.0
            threshold = self.drift_config.get('column_drift_threshold', 0.3)
            if drift_info['drift_share'] >= threshold:
                drift_info['dataset_drift'] = True
            # Fallback: if drift_share not available, use ratio
            if drift_share is None and drift_info['num_columns'] > 0:
                drift_ratio = drift_info['num_drifted_columns'] / drift_info['num_columns']
                drift_info['drift_share'] = drift_ratio
                if drift_ratio >= threshold:
                    drift_info['dataset_drift'] = True
        except Exception as e:
            self.logger.error(f"Error extracting drift summary: {e}")
        return drift_info
    
    def apply_sampling(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply sampling to dataset if configured.
        
        Args:
            data: Input DataFrame
        Returns:
            pd.DataFrame: Sampled DataFrame (or original if sampling disabled)
        """
        sampling_config = self.config.get_sampling_config()
        if not sampling_config.get('enabled', False):
            return data
        method = sampling_config.get('method', 'fraction')
        random_seed = sampling_config.get('random_seed', 42)
        if method == 'fraction':
            fraction = sampling_config.get('fraction', 0.1)
            sampled = data.sample(frac=fraction, random_state=random_seed)
            self.logger.info(f"Sampled {len(sampled)} rows using fraction {fraction}")
        else:  # fixed size
            fixed_size = sampling_config.get('fixed_size', 10000)
            sample_size = min(fixed_size, len(data))
            sampled = data.sample(n=sample_size, random_state=random_seed)
            self.logger.info(f"Sampled {len(sampled)} rows using fixed size")
        return sampled