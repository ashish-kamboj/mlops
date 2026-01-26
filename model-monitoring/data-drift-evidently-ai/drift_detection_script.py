"""
Data Drift Detection - Standalone Script Version

This script performs data drift detection using Evidently AI.
It can be run as a standalone Python script or scheduled as a job.

Usage:
    python drift_detection_script.py --config config/drift_config.yaml
    
    # Or with specific tables
    python drift_detection_script.py --config config/drift_config.yaml --tables customer_data,product_sales
    
    # Dry run (no report saving)
    python drift_detection_script.py --config config/drift_config.yaml --dry-run
"""

import sys
import argparse
from typing import List
import warnings
warnings.filterwarnings('ignore')

# Import utilities
from utils import (
    ConfigManager, 
    DriftDetector, 
    ReportManager, 
    DataLoader, 
    setup_logger,
    get_logger
)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Data Drift Detection using Evidently AI'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/drift_config.yaml',
        help='Path to configuration file (default: config/drift_config.yaml)'
    )
    
    parser.add_argument(
        '--tables',
        type=str,
        help='Comma-separated list of tables to process (default: all from config)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run detection without saving reports'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--use-spark',
        action='store_true',
        default=True,
        help='Use PySpark for data loading (default: True)'
    )
    
    return parser.parse_args()


def initialize_components(config_path: str, verbose: bool = False):
    """
    Initialize all components needed for drift detection.
    
    Args:
        config_path: Path to configuration file
        verbose: Enable verbose logging
        
    Returns:
        tuple: (config, drift_detector, report_manager, data_loader, logger)
    """
    # Load configuration
    config = ConfigManager(config_path)
    
    # Setup logging
    log_level = 'DEBUG' if verbose else config.get_log_level()
    # Configure logger: console + ADLS (if enabled)
    logger = setup_logger(
        log_level=log_level,
        logger_name='drift_detection_script',
        adls_config=config.get_adls_config() if config.is_adls_output_enabled() else None,
    )
    
    logger.info("="*80)
    logger.info("Data Drift Detection Script")
    logger.info("="*80)
    logger.info(f"Configuration: {config_path}")
    logger.info(f"Catalog: {config.get_catalog_name()}.{config.get_schema_name()}")
    
    # Initialize components
    drift_detector = DriftDetector(config)
    report_manager = ReportManager(config)
    
    # Initialize data loader (Spark session will be added if available)
    from pyspark.sql import SparkSession
    spark = SparkSession.getActiveSession()
    if not spark:
        # In Databricks this should always be available
        spark = SparkSession.builder.getOrCreate()
    data_loader = DataLoader(config, spark=spark)
    logger.info("Using PySpark for data loading via Unity Catalog history")
    
    logger.info("All components initialized successfully")
    
    return config, drift_detector, report_manager, data_loader, logger


def process_table(
    table_config: dict,
    drift_detector: DriftDetector,
    report_manager: ReportManager,
    data_loader: DataLoader,
    logger,
    use_spark: bool = True,
    dry_run: bool = False
) -> dict:
    """
    Process a single table for drift detection.
    
    Args:
        table_config: Table configuration dictionary
        drift_detector: DriftDetector instance
        report_manager: ReportManager instance
        data_loader: DataLoader instance
        logger: Logger instance
        use_spark: Use Spark for data loading
        dry_run: Skip report saving if True
        
    Returns:
        dict: Processing result with drift summary
    """
    table_name = table_config['name']
    columns = table_config.get('columns', 'all')
    # id_column deprecated; analyze selected columns directly
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Processing table: {table_name}")
    logger.info(f"{'='*80}")
    
    try:
        # Load data versions
        logger.info(f"Loading data for table: {table_name}")
        reference_data, current_data = data_loader.load_table_versions(
            table_name=table_name,
            use_spark=use_spark
        )
        
        logger.info(f"Data loaded - Reference: {len(reference_data)} rows, "
                   f"Current: {len(current_data)} rows")
        
        # Apply sampling if configured
        reference_data = drift_detector.apply_sampling(reference_data)
        current_data = drift_detector.apply_sampling(current_data)
        
        # Detect drift
        logger.info("Running drift detection...")
        report, drift_summary = drift_detector.detect_drift(
            reference_data=reference_data,
            current_data=current_data,
            table_name=table_name,
            columns=columns if columns != 'all' else None,
        )
        
        # Log results
        if drift_summary['dataset_drift']:
            logger.warning(f"⚠️  DRIFT DETECTED in {table_name}")
            logger.warning(f"   Drifted columns: {drift_summary['drifted_columns']}")
        else:
            logger.info(f"✓ No significant drift detected in {table_name}")
        
        logger.info(f"   Total columns: {drift_summary['num_columns']}")
        logger.info(f"   Drifted columns: {drift_summary['num_drifted_columns']}")
        logger.info(f"   Drift share: {drift_summary['drift_share']:.2%}")
        
        # Save reports (unless dry run)
        saved_paths = {}
        if not dry_run:
            logger.info(f"Saving reports for {table_name}...")
            saved_paths = report_manager.save_reports(
                report=report,
                drift_summary=drift_summary,
                table_name=table_name
            )
            
            for report_type, path in saved_paths.items():
                logger.info(f"   {report_type}: {path}")
        else:
            logger.info("Dry run mode - skipping report saving")
        
        return {
            'table_name': table_name,
            'success': True,
            'drift_summary': drift_summary,
            'report_paths': saved_paths
        }
    
    except Exception as e:
        logger.error(f"✗ Error processing table {table_name}: {e}", exc_info=True)
        return {
            'table_name': table_name,
            'success': False,
            'error': str(e)
        }


def print_summary(results: List[dict], logger):
    """
    Print summary of drift detection results.
    
    Args:
        results: List of processing results
        logger: Logger instance
    """
    logger.info("\n" + "="*80)
    logger.info("DRIFT DETECTION SUMMARY")
    logger.info("="*80)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    if failed:
        logger.warning(f"\n⚠️  {len(failed)} table(s) failed:")
        for result in failed:
            logger.warning(f"  - {result['table_name']}: {result.get('error', 'Unknown error')}")
    
    if successful:
        logger.info(f"\n✓ Successfully processed {len(successful)} table(s):")
        
        drifted_tables = []
        ok_tables = []
        
        for result in successful:
            summary = result['drift_summary']
            if summary['dataset_drift']:
                drifted_tables.append(result)
            else:
                ok_tables.append(result)
        
        # Print tables with drift
        if drifted_tables:
            logger.warning(f"\n⚠️  Tables with drift: {len(drifted_tables)}")
            for result in drifted_tables:
                summary = result['drift_summary']
                logger.warning(
                    f"  - {summary['table_name']}: "
                    f"{summary['num_drifted_columns']}/{summary['num_columns']} columns "
                    f"({summary['drift_share']:.2%})"
                )
        
        # Print tables without drift
        if ok_tables:
            logger.info(f"\n✓ Tables without drift: {len(ok_tables)}")
            for result in ok_tables:
                logger.info(f"  - {result['table_name']}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Total: {len(results)} | Success: {len(successful)} | Failed: {len(failed)}")
    logger.info("="*80)


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Initialize components
        config, drift_detector, report_manager, data_loader, logger = \
            initialize_components(args.config, args.verbose)
        
        # Get tables to process
        all_tables = config.get_tables()
        
        if args.tables:
            # Filter to specific tables
            table_names = [t.strip() for t in args.tables.split(',')]
            tables = [t for t in all_tables if t['name'] in table_names]
            logger.info(f"Processing {len(tables)} specified table(s): {table_names}")
        else:
            # Process all tables
            tables = all_tables
            logger.info(f"Processing all {len(tables)} configured table(s)")
        
        if not tables:
            logger.error("No tables to process")
            return 1
        
        # Process each table
        results = []
        for table_config in tables:
            result = process_table(
                table_config=table_config,
                drift_detector=drift_detector,
                report_manager=report_manager,
                data_loader=data_loader,
                logger=logger,
                use_spark=args.use_spark,
                dry_run=args.dry_run
            )
            results.append(result)
        
        # Print summary
        print_summary(results, logger)
        
        # Determine exit code
        failed_count = sum(1 for r in results if not r.get('success', False))
        drifted_count = sum(1 for r in results 
                          if r.get('success', False) and 
                          r.get('drift_summary', {}).get('dataset_drift', False))
        
        logger.info("\nDrift detection completed")
        
        if failed_count > 0:
            logger.error(f"Exiting with errors ({failed_count} failures)")
            return 1
        elif drifted_count > 0:
            logger.warning(f"Exiting with drift detected ({drifted_count} tables)")
            return 2  # Exit code 2 indicates drift detected
        else:
            logger.info("Exiting successfully (no drift detected)")
            return 0
    
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())