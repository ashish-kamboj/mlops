"""
Report Manager Module
Handles saving Evidently AI reports to various destinations (local, ADLS).
"""

import os
import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from evidently import Report


class ReportManager:
    """
    Manages saving and organizing drift detection reports.
    
    Supports multiple output formats (HTML, JSON) and destinations (local, ADLS).
    """
    
    # Default local base path for saving reports
    DEFAULT_LOCAL_BASE_PATH = '/Workspace/Users/<<USER_ID>>/data-drift-evidently-ai/reports'

    def __init__(self, config_manager):
        """
        Initialize ReportManager with configuration.
        
        Args:
            config_manager: ConfigManager instance with loaded configuration
        """
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.output_formats = self.config.get_output_formats()
        # Local saving is hardcoded by default for testing convenience
        self.local_base_path = self.DEFAULT_LOCAL_BASE_PATH
        
        # Initialize ADLS client if enabled
        self.adls_client = None
        if self.config.is_adls_output_enabled():
            self._initialize_adls_client()
    
    def _initialize_adls_client(self):
        """Initialize Azure Data Lake Storage client."""
        try:
            from azure.storage.filedatalake import DataLakeServiceClient
            from azure.identity import ClientSecretCredential
            
            adls_config = self.config.get_adls_config()
            storage_account = adls_config['storage_account']
            auth_method = adls_config.get('auth_method', 'service_principal')
            
            if auth_method == 'service_principal':
                # Authenticate using service principal
                credential = ClientSecretCredential(
                    tenant_id=adls_config['tenant_id'],
                    client_id=adls_config['client_id'],
                    client_secret=adls_config['client_secret']
                )
                account_url = f"https://{storage_account}.dfs.core.windows.net"
                self.adls_client = DataLakeServiceClient(
                    account_url=account_url,
                    credential=credential
                )
            elif auth_method == 'access_key':
                # Authenticate using access key
                account_url = f"https://{storage_account}.dfs.core.windows.net"
                self.adls_client = DataLakeServiceClient(
                    account_url=account_url,
                    credential=adls_config['access_key']
                )
            
            self.logger.info("ADLS client initialized successfully")
        
        except ImportError:
            self.logger.error(
                "Azure storage libraries not found. Install: "
                "pip install azure-storage-file-datalake azure-identity"
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize ADLS client: {e}")
            raise
    
    def save_reports(
        self,
        report: Report,
        drift_summary: Dict[str, Any],
        table_name: str
    ) -> Dict[str, str]:
        """
        Save drift detection reports to configured destinations.
        
        Args:
            report: Evidently Report object
            drift_summary: Drift detection summary dictionary
            table_name: Name of the table
            
        Returns:
            Dict[str, str]: Dictionary with paths/URLs where reports were saved
        """
        saved_paths = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate reports in requested formats
        for format_type in self.output_formats:
            try:
                if format_type == 'html':
                    report_content = self._generate_html_report(report, drift_summary)
                    file_name = f"{table_name}_{timestamp}_drift_report.html"
                elif format_type == 'json':
                    report_content = self._generate_json_report(report, drift_summary)
                    file_name = f"{table_name}_{timestamp}_drift_report.json"
                else:
                    self.logger.warning(f"Unsupported format: {format_type}")
                    continue
                
                # Always save to local by default (testing-friendly)
                # Comment out the next two lines before production if you don't want local files:
                local_path = self._save_local(report_content, file_name, format_type)
                saved_paths[f'local_{format_type}'] = local_path
                
                # Save to ADLS if enabled
                if self.config.is_adls_output_enabled():
                    adls_path = self._save_adls(report_content, file_name, format_type)
                    saved_paths[f'adls_{format_type}'] = adls_path
                
                self.logger.info(f"Saved {format_type.upper()} report for {table_name}")
            
            except Exception as e:
                self.logger.error(f"Error saving {format_type} report: {e}")
        
        return saved_paths
    
    def _generate_html_report(
        self,
        report: Report,
        drift_summary: Dict[str, Any]
    ) -> str:
        """
        Generate HTML report with embedded drift summary.
        
        Args:
            report: Evidently Report object
            drift_summary: Drift summary dictionary
            
        Returns:
            str: HTML report content
        """
        # Generate base HTML report from Evidently (updated for 0.7.19)
        # In Evidently 0.7.19, the method is now show() or save_html()
        # We'll use the internal _build_dashboard_info and render
        # no-op placeholder imports removed
        
        # Get HTML content - in 0.7.19, we use show() with output='html'
        try:
            # Try the newer API first
            html_content = report.show(mode='inline').data
        except Exception:
            # Fallback to get_html() if available
            try:
                html_content = report.get_html()
            except AttributeError:
                # If neither works, save to string buffer
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                    report.save_html(f.name)
                    with open(f.name, 'r', encoding='utf-8') as fr:
                        html_content = fr.read()
                import os
                os.unlink(f.name)
        
        # Add custom summary section at the top
        summary_html = self._create_summary_html(drift_summary)
        
        # Insert summary after opening body tag
        if '<body>' in html_content:
            html_content = html_content.replace(
                '<body>',
                f'<body>{summary_html}',
                1
            )
        
        return html_content
    
    def _create_summary_html(self, drift_summary: Dict[str, Any]) -> str:
        """
        Create HTML summary section.
        
        Args:
            drift_summary: Drift summary dictionary
            
        Returns:
            str: HTML content for summary section
        """
        drift_status = "⚠️ DRIFT DETECTED" if drift_summary['dataset_drift'] else "✅ NO DRIFT"
        status_color = "#ff6b6b" if drift_summary['dataset_drift'] else "#51cf66"
        
        html = f"""
        <div style="padding: 20px; margin: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 5px solid {status_color};">
            <h2 style="color: {status_color}; margin-top: 0;">{drift_status}</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                <div>
                    <strong>Table:</strong> {drift_summary['table_name']}
                </div>
                <div>
                    <strong>Timestamp:</strong> {drift_summary['timestamp']}
                </div>
                <div>
                    <strong>Total Columns:</strong> {drift_summary['num_columns']}
                </div>
                <div>
                    <strong>Drifted Columns:</strong> {drift_summary['num_drifted_columns']}
                </div>
                <div>
                    <strong>Drift Share:</strong> {drift_summary['drift_share']:.2%}
                </div>
            </div>
            <div style="margin-top: 15px;">
                <strong>Drifted Columns:</strong> 
                <span style="color: #ff6b6b;">{', '.join(drift_summary['drifted_columns']) if drift_summary['drifted_columns'] else 'None'}</span>
            </div>
        </div>
        """
        return html
    
    def _generate_json_report(
        self,
        report: Report,
        drift_summary: Dict[str, Any]
    ) -> str:
        """
        Generate JSON report combining Evidently report and drift summary.
        
        Args:
            report: Evidently Report object
            drift_summary: Drift summary dictionary
            
        Returns:
            str: JSON report content
        """
        # Get Evidently report as dictionary
        #report_dict = report.as_dict()
        report_json_str = report.json()
        report_dict = json.loads(report_json_str)
        
        # Combine with drift summary
        combined_report = {
            'drift_summary': drift_summary,
            'evidently_report': report_dict
        }
        
        return json.dumps(combined_report, indent=2, default=str)
    
    def _save_local(
        self,
        content: str,
        file_name: str,
        format_type: str
    ) -> str:
        """
        Save report to local filesystem.
        
        Args:
            content: Report content
            file_name: Name of the file
            format_type: Format type ('html' or 'json')
            
        Returns:
            str: Full path where file was saved
        """
        # Use hardcoded local base path (not controlled by config)
        base_path = self.local_base_path
        
        # Create directory if it doesn't exist
        os.makedirs(base_path, exist_ok=True)
        
        # Create subdirectory for format type
        format_dir = os.path.join(base_path, format_type)
        os.makedirs(format_dir, exist_ok=True)
        
        # Full file path
        file_path = os.path.join(format_dir, file_name)
        
        # Write content
        mode = 'w' if format_type in ['html', 'json'] else 'wb'
        with open(file_path, mode, encoding='utf-8' if mode == 'w' else None) as f:
            f.write(content)
        
        self.logger.info(f"Report saved locally: {file_path}")
        return file_path
    
    def _save_adls(
        self,
        content: str,
        file_name: str,
        format_type: str
    ) -> str:
        """
        Save report to Azure Data Lake Storage.
        
        Args:
            content: Report content
            file_name: Name of the file
            format_type: Format type ('html' or 'json')
            
        Returns:
            str: ADLS path where file was saved
        """
        if not self.adls_client:
            raise RuntimeError("ADLS client not initialized")
        
        adls_config = self.config.get_adls_config()
        container_name = adls_config['container']
        base_path = adls_config['base_path']
        
        # Construct full path in ADLS
        adls_path = f"{base_path}/{format_type}/{file_name}"
        
        try:
            # Get file system client
            file_system_client = self.adls_client.get_file_system_client(
                file_system=container_name
            )
            
            # Get file client
            file_client = file_system_client.get_file_client(adls_path)
            
            # Upload content
            file_client.upload_data(
                content.encode('utf-8') if isinstance(content, str) else content,
                overwrite=True
            )
            
            full_adls_path = f"abfss://{container_name}@{adls_config['storage_account']}.dfs.core.windows.net/{adls_path}"
            self.logger.info(f"Report saved to ADLS: {full_adls_path}")
            return full_adls_path
        
        except Exception as e:
            self.logger.error(f"Error saving to ADLS: {e}")
            raise
    
    def save_drift_summary_only(
        self,
        drift_summary: Dict[str, Any],
        table_name: str
    ) -> str:
        """
        Save only the drift summary as JSON (lightweight option).
        
        Args:
            drift_summary: Drift summary dictionary
            table_name: Name of the table
            
        Returns:
            str: Path where summary was saved
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{table_name}_{timestamp}_summary.json"
        content = json.dumps(drift_summary, indent=2, default=str)
        
        if self.config.is_local_output_enabled():
            return self._save_local(content, file_name, 'json')
        elif self.config.is_adls_output_enabled():
            return self._save_adls(content, file_name, 'json')
        else:
            self.logger.warning("No output destination enabled")
            return ""