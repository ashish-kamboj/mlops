"""
Logger Setup Module
Configures logging for the data drift detection application.
"""

import logging
import sys
from typing import Optional, Dict, Any


class ADLSLogHandler(logging.Handler):
    """
    Logging handler that appends logs to a file in Azure Data Lake Storage (Gen2).
    Uses service principal or access key based on provided config.
    """
    def __init__(self, adls_config: Dict[str, Any], log_rel_path: str):
        super().__init__()
        try:
            from azure.storage.filedatalake import DataLakeServiceClient
            from azure.identity import ClientSecretCredential
        except Exception as e:
            raise ImportError(
                "Azure packages not installed. Install azure-storage-file-datalake and azure-identity"
            ) from e

        self.storage_account = adls_config['storage_account']
        self.container = adls_config['container']
        base_path = adls_config.get('base_path', '').strip('/')
        # Default logs under base_path/logs/data_drift.log
        self.adls_log_path = f"{base_path}/logs/{log_rel_path}" if base_path else f"logs/{log_rel_path}"

        account_url = f"https://{self.storage_account}.dfs.core.windows.net"
        auth_method = adls_config.get('auth_method', 'service_principal')
        if auth_method == 'service_principal':
            credential = ClientSecretCredential(
                tenant_id=adls_config['tenant_id'],
                client_id=adls_config['client_id'],
                client_secret=adls_config['client_secret']
            )
            self.service_client = DataLakeServiceClient(account_url=account_url, credential=credential)
        else:
            self.service_client = DataLakeServiceClient(account_url=account_url, credential=adls_config['access_key'])

        self.fs_client = self.service_client.get_file_system_client(self.container)
        self.file_client = self.fs_client.get_file_client(self.adls_log_path)

        # Ensure file exists
        try:
            self.file_client.get_file_properties()
        except Exception:
            # Create directories recursively by creating empty placeholder if needed
            self._ensure_path()
            self.file_client.create_file()

        # Detailed formatter by default
        self.setFormatter(logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

    def _ensure_path(self):
        # Create intermediate directories under base path if necessary (idempotent with get_directory_client)
        path_parts = self.adls_log_path.split('/')[:-1]
        cur = ''
        for part in path_parts:
            cur = f"{cur}/{part}" if cur else part
            try:
                self.fs_client.get_directory_client(cur).create_directory()
            except Exception:
                # likely already exists
                pass

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record) + "\n"
            data = msg.encode('utf-8')
            # Determine current size to append
            try:
                props = self.file_client.get_file_properties()
                offset = props.size or 0
            except Exception:
                self._ensure_path()
                self.file_client.create_file()
                offset = 0

            self.file_client.append_data(data, offset=offset, length=len(data))
            self.file_client.flush_data(offset + len(data))
        except Exception:
            # Avoid breaking main flow on logging failures
            pass


def setup_logger(
    log_level: str = 'INFO',
    logger_name: Optional[str] = None,
    adls_config: Optional[Dict[str, Any]] = None,
) -> logging.Logger:
    """
    Set up and configure logger for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Optional[str]): Path to log file (None = console only)
        logger_name (Optional[str]): Name of the logger (None = root logger)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get logger
    logger = logging.getLogger(logger_name)
    
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # ADLS handler (if ADLS config enabled)
    if adls_config and adls_config.get('enabled', False):
        try:
            adls_handler = ADLSLogHandler(adls_config, log_rel_path='data_drift.log')
            adls_handler.setLevel(numeric_level)
            # Already has a detailed formatter
            logger.addHandler(adls_handler)
        except Exception:
            # Fall back silently to console-only if ADLS logging fails
            pass
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)