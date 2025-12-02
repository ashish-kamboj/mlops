"""
Data Loading and Processing Module
===================================
Functions for loading data from various sources (Unity Catalog, CSV)
and basic data processing operations.

Author: Home Credit Data Science Team
Date: 2025-11-11
"""

import os
import logging
from typing import Dict, Any, Optional, List
import pandas as pd


def load_data_from_source(config: Dict[str, Any], table_key: str, spark=None) -> pd.DataFrame:
    """
    Load data from configured source (Unity Catalog or CSV).
    
    Args:
        config: Configuration dictionary
        table_key: Key for the table in config (e.g., 'customer', 'transaction')
        spark: Spark session (required for Unity Catalog)
        
    Returns:
        pandas DataFrame with loaded data
    """
    data_source_type = config['data_source']['type']
    
    if data_source_type == 'unity_catalog':
        return load_from_unity_catalog(config, table_key, spark)
    else:
        return load_from_csv(config, table_key)


def load_from_unity_catalog(config: Dict[str, Any], table_key: str, spark) -> pd.DataFrame:
    """
    Load data from Unity Catalog table.
    
    Args:
        config: Configuration dictionary
        table_key: Key for the table in config
        spark: Spark session
        
    Returns:
        pandas DataFrame
    """
    if spark is None:
        raise ValueError("Spark session is required for Unity Catalog")
    
    uc_config = config['data_source']['unity_catalog']
    catalog = uc_config['catalog']
    schema = uc_config['schema']
    table_name = uc_config['tables'][table_key]
    
    full_table_name = f"{catalog}.{schema}.{table_name}"
    
    logging.info(f"Loading data from Unity Catalog: {full_table_name}")
    
    try:
        df_spark = spark.table(full_table_name)
        df = df_spark.toPandas()
        logging.info(f"Loaded {len(df)} rows from {full_table_name}")
        return df
    except Exception as e:
        logging.error(f"Error loading from Unity Catalog: {str(e)}")
        raise


def load_from_csv(config: Dict[str, Any], table_key: str) -> pd.DataFrame:
    """
    Load data from CSV file.
    
    Args:
        config: Configuration dictionary
        table_key: Key for the table in config
        
    Returns:
        pandas DataFrame
    """
    csv_config = config['data_source']['csv']
    input_path = csv_config['input_path']
    file_name = csv_config['tables'][table_key]
    
    file_path = os.path.join(input_path, file_name)
    
    logging.info(f"Loading data from CSV: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except FileNotFoundError:
        logging.error(f"CSV file not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading CSV: {str(e)}")
        raise


def load_all_tables(config: Dict[str, Any], spark=None) -> Dict[str, pd.DataFrame]:
    """
    Load all tables defined in configuration.
    
    Args:
        config: Configuration dictionary
        spark: Spark session (required for Unity Catalog)
        
    Returns:
        Dictionary with table names as keys and DataFrames as values
    """
    data_source_type = config['data_source']['type']
    
    if data_source_type == 'unity_catalog':
        table_config = config['data_source']['unity_catalog']['tables']
    else:
        table_config = config['data_source']['csv']['tables']
    
    tables = {}
    
    for table_key in table_config.keys():
        try:
            tables[table_key] = load_data_from_source(config, table_key, spark)
        except Exception as e:
            logging.warning(f"Could not load table {table_key}: {str(e)}")
            tables[table_key] = None
    
    logging.info(f"Successfully loaded {sum(1 for v in tables.values() if v is not None)} tables")
    return tables


def save_data_to_destination(df: pd.DataFrame, 
                             config: Dict[str, Any], 
                             table_name: str,
                             spark=None,
                             mode: str = "overwrite",
                             output_path: str = None) -> None:
    """
    Save DataFrame to configured destination (Unity Catalog or CSV).
    
    Args:
        df: DataFrame to save
        config: Configuration dictionary
        table_name: Name of the table/file
        spark: Spark session (required for Unity Catalog)
        mode: Write mode ('overwrite', 'append')
        output_path: Optional custom output path (for CSV only)
    """
    data_source_type = config['data_source']['type']
    
    if data_source_type == 'unity_catalog':
        save_to_unity_catalog(df, config, table_name, spark, mode)
    else:
        save_to_csv(df, config, table_name, output_path)


def save_to_unity_catalog(df: pd.DataFrame,
                          config: Dict[str, Any],
                          table_name: str,
                          spark,
                          mode: str = "overwrite") -> None:
    """
    Save DataFrame to Unity Catalog.
    
    Args:
        df: DataFrame to save
        config: Configuration dictionary
        table_name: Table name
        spark: Spark session
        mode: Write mode
    """
    if spark is None:
        raise ValueError("Spark session is required for Unity Catalog")
    
    uc_config = config['data_source']['unity_catalog']
    catalog = uc_config['catalog']
    output_schema = uc_config['output_schema']
    
    full_table_name = f"{catalog}.{output_schema}.{table_name}"
    
    logging.info(f"Saving data to Unity Catalog: {full_table_name}")
    
    try:
        df_spark = spark.createDataFrame(df)
        df_spark.write.mode(mode).saveAsTable(full_table_name)
        logging.info(f"Saved {len(df)} rows to {full_table_name}")
    except Exception as e:
        logging.error(f"Error saving to Unity Catalog: {str(e)}")
        raise


def save_to_csv(df: pd.DataFrame,
                config: Dict[str, Any],
                table_name: str,
                custom_output_path: str = None) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        config: Configuration dictionary
        table_name: File name (without .csv extension)
        custom_output_path: Optional custom output path (overrides config)
    """
    csv_config = config['data_source']['csv']
    
    # Use custom path if provided, otherwise use path from config
    if custom_output_path:
        output_path = custom_output_path
    else:
        output_path = csv_config['output_path']
    
    os.makedirs(output_path, exist_ok=True)
    file_path = os.path.join(output_path, f"{table_name}.csv")
    
    logging.info(f"Saving data to CSV: {file_path}")
    
    try:
        df.to_csv(file_path, index=False)
        logging.info(f"Saved {len(df)} rows to {file_path}")
    except Exception as e:
        logging.error(f"Error saving CSV: {str(e)}")
        raise


def validate_dataframe(df: pd.DataFrame, 
                       required_columns: Optional[List[str]] = None,
                       min_rows: int = 1) -> bool:
    """
    Validate DataFrame has required columns and minimum rows.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        min_rows: Minimum number of rows required
        
    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        logging.error("DataFrame is None or empty")
        return False
    
    if len(df) < min_rows:
        logging.error(f"DataFrame has {len(df)} rows, minimum {min_rows} required")
        return False
    
    if required_columns:
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            return False
    
    logging.debug(f"DataFrame validation passed: {len(df)} rows, {len(df.columns)} columns")
    return True


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get summary statistics for a DataFrame.
    
    Args:
        df: DataFrame to summarize
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'num_rows': len(df),
        'num_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
    }
    
    return summary


def merge_tables(left_df: pd.DataFrame,
                right_df: pd.DataFrame,
                left_on: str,
                right_on: str,
                how: str = 'left') -> pd.DataFrame:
    """
    Merge two DataFrames with logging.
    
    Args:
        left_df: Left DataFrame
        right_df: Right DataFrame
        left_on: Column name in left DataFrame
        right_on: Column name in right DataFrame
        how: Type of merge ('left', 'right', 'inner', 'outer')
        
    Returns:
        Merged DataFrame
    """
    logging.info(f"Merging tables on {left_on}={right_on}, how={how}")
    logging.info(f"Left: {len(left_df)} rows, Right: {len(right_df)} rows")
    
    merged_df = left_df.merge(right_df, left_on=left_on, right_on=right_on, how=how)
    
    logging.info(f"Merged result: {len(merged_df)} rows")
    
    return merged_df


def filter_dataframe_by_date(df: pd.DataFrame,
                             date_column: str,
                             start_date: Optional[str] = None,
                             end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: DataFrame to filter
        date_column: Name of the date column
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])
    
    original_count = len(df)
    
    if start_date:
        df = df[df[date_column] >= pd.to_datetime(start_date)]
        logging.info(f"Filtered by start_date {start_date}: {len(df)} rows remaining")
    
    if end_date:
        df = df[df[date_column] <= pd.to_datetime(end_date)]
        logging.info(f"Filtered by end_date {end_date}: {len(df)} rows remaining")
    
    logging.info(f"Date filtering: {original_count} -> {len(df)} rows")
    
    return df
