"""
Data Loader Module
Handles loading data from Databricks Unity Catalog using table version history.
"""

import logging
from typing import Tuple
import pandas as pd


class DataLoader:
    """
    Loads data from Databricks Unity Catalog and fetches latest vs previous table versions via UC History.
    
    This class handles:
    - Loading data from Unity Catalog tables
    - Identifying and comparing different versions
    - Converting between Spark and Pandas DataFrames
    """
    
    def __init__(self, config_manager, spark=None):
        """
        Initialize DataLoader with configuration and Spark session.
        
        Args:
            config_manager: ConfigManager instance with loaded configuration
            spark: Spark session (optional, required for PySpark operations)
        """
        self.config = config_manager
        self.spark = spark
        self.logger = logging.getLogger(__name__)
        # Versioning is handled via Unity Catalog DESCRIBE HISTORY
    
    def set_spark_session(self, spark):
        """
        Set or update the Spark session.
        
        Args:
            spark: Spark session object
        """
        self.spark = spark
        self.logger.info("Spark session set for DataLoader")
    
    def load_table_versions(
        self,
        table_name: str,
        use_spark: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load reference (previous) and current (latest) versions of a table using Unity Catalog History.
        
        Args:
            table_name (str): Name of the table to load
            use_spark (bool): Must be True. Spark is required in Databricks.
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Reference and current data as pandas DataFrames
            
        Raises:
            ValueError: If versions cannot be identified or loaded
        """
        self.logger.info(f"Loading latest two versions for table: {table_name}")
        
        catalog = self.config.get_catalog_name()
        schema = self.config.get_schema_name()
        full_table_name = f"{catalog}.{schema}.{table_name}"
        
        if not use_spark:
            raise RuntimeError("Spark is required for Unity Catalog history-based loading")
        if not self.spark:
            raise RuntimeError("Spark session not available. Set spark session first.")

        # Get latest two versions from UC History
        hist_df = self.spark.sql(f"DESCRIBE HISTORY {full_table_name}")
        versions = (
            hist_df.select('version')
                   .orderBy('version', ascending=False)
                   .limit(2)
                   .toPandas()['version']
                   .tolist()
        )
        if len(versions) < 2:
            raise ValueError(f"Need at least 2 versions in history for {full_table_name}; found {len(versions)}")

        current_version = int(versions[0])
        reference_version = int(versions[1])
        self.logger.info(f"Comparing UC versions: {reference_version} (reference) vs {current_version} (current)")
        print(f"Comparing UC versions: {reference_version} (reference) vs {current_version} (current)")

        # Read specific versions via SQL VERSION AS OF
        ref_spark_df = self.spark.sql(
            f"SELECT * FROM {full_table_name} VERSION AS OF {reference_version}"
        )
        cur_spark_df = self.spark.sql(
            f"SELECT * FROM {full_table_name} VERSION AS OF {current_version}"
        )

        # Convert to Pandas for Evidently
        reference_data = ref_spark_df.toPandas()
        current_data = cur_spark_df.toPandas()

        return reference_data, current_data
    
    # Deprecated: pandas/local loaders removed; Spark is required in Databricks
    
    # Deprecated helpers removed: version columns are no longer used
    
    # Removed: _get_latest_two_versions
    
    # Removed: _get_specific_versions
    
    def load_table_direct(
        self,
        table_name: str,
        use_spark: bool = False
    ) -> pd.DataFrame:
        """
        Load entire table without version splitting (for testing).
        
        Args:
            table_name: Name of the table
            use_spark: Whether to use Spark
            
        Returns:
            pd.DataFrame: Full table data
        """
        catalog = self.config.get_catalog_name()
        schema = self.config.get_schema_name()
        full_table_name = f"{catalog}.{schema}.{table_name}"
        
        self.logger.info(f"Loading full table: {full_table_name}")
        
        if not use_spark:
            raise RuntimeError("Spark is required for direct table loading in Databricks context")
        if not self.spark:
            raise RuntimeError("Spark session not available")
        spark_df = self.spark.table(full_table_name)
        return spark_df.toPandas()