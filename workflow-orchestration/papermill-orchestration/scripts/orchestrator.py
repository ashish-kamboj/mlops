"""
Notebook Orchestrator using Papermill
Supports sequential and parallel execution of parameterized notebooks
"""

import os
import sys
import time
from typing import Dict, Any, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import papermill as pm
import json

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils import (
    load_config,
    save_config,
    setup_logging,
    create_output_dir,
    resolve_path,
    ensure_file_exists
)


class NotebookOrchestrator:
    """
    Orchestrates the execution of parameterized Jupyter notebooks
    using Papermill with support for sequential and parallel execution.
    """
    
    def __init__(self, config_path: str, base_dir: str = None):
        """
        Initialize the orchestrator.
        
        Args:
            config_path: Path to configuration file (YAML)
            base_dir: Base directory for resolving relative paths
        """
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.config_path = resolve_path(config_path, self.base_dir)
        ensure_file_exists(self.config_path)
        
        # Load configuration
        self.config = load_config(self.config_path)
        
        # Setup logging
        log_file = resolve_path(self.config['logging']['log_file'], self.base_dir)
        self.logger = setup_logging(log_file, self.config['logging']['level'])
        
        # Create output directory
        self.output_dir = create_output_dir(
            resolve_path(self.config['output']['output_dir'], self.base_dir)
        )
        
        # Save config to output for record-keeping
        config_copy_path = os.path.join(self.output_dir, 'config.yaml')
        save_config(self.config, config_copy_path)
        
        self.logger.info("Orchestrator initialized")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Execution mode: {self.config['execution']['mode']}")
    
    def _resolve_notebook_path(self, notebook: str) -> str:
        """Resolve notebook path relative to notebooks directory."""
        # base_dir is the project root, notebooks are in notebooks/ subdirectory
        notebooks_dir = os.path.join(self.base_dir, 'notebooks')
        return resolve_path(notebook, notebooks_dir)
    
    def _prepare_parameters(self, 
                           notebook_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare parameters for notebook execution.
        Resolve relative paths to absolute paths.
        """
        prepared_params = {}
        for key, value in notebook_params.items():
            if isinstance(value, str) and ('dir' in key or 'path' in key):
                # Resolve paths relative to base directory
                prepared_params[key] = resolve_path(value, self.base_dir)
            else:
                prepared_params[key] = value
        return prepared_params
    
    def execute_notebook(self, 
                        notebook: str,
                        notebook_params: Dict[str, Any] = None,
                        output_name: str = None) -> Tuple[str, bool, str]:
        """
        Execute a single notebook using Papermill.
        
        Args:
            notebook: Path to input notebook
            notebook_params: Dictionary of parameters to inject
            output_name: Name for output notebook
            
        Returns:
            Tuple of (output_path, success, message)
        """
        try:
            input_path = self._resolve_notebook_path(notebook)
            ensure_file_exists(input_path)
            
            # Generate output filename
            if output_name is None:
                output_name = os.path.splitext(os.path.basename(notebook))[0] + '_output.ipynb'
            
            output_path = os.path.join(self.output_dir, output_name)
            
            # Prepare parameters
            params = notebook_params or {}
            params = self._prepare_parameters(params)
            
            # Log execution start
            self.logger.info(f"Starting execution: {notebook}")
            self.logger.debug(f"Input: {input_path}")
            self.logger.debug(f"Output: {output_path}")
            self.logger.debug(f"Parameters: {params}")
            
            # Execute notebook with Papermill
            start_time = time.time()
            pm.execute_notebook(
                input_path,
                output_path,
                parameters=params,
                kernel_name='python3'
            )
            exec_time = time.time() - start_time
            
            # Log success
            message = f"Successfully executed in {exec_time:.2f}s"
            self.logger.info(f"SUCCESS: {notebook}: {message}")
            
            return output_path, True, message
            
        except pm.PapermillException as e:
            message = f"Papermill execution error: {str(e)}"
            self.logger.error(f"ERROR: {notebook}: {message}")
            return None, False, message
        except Exception as e:
            message = f"Execution error: {str(e)}"
            self.logger.error(f"✗ {notebook}: {message}")
            return None, False, message
    
    def execute_sequential(self, 
                          notebooks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute notebooks sequentially.
        
        Args:
            notebooks: List of notebook configurations
                      Each config should have 'notebook' key and optional 'params' key
                      
        Returns:
            Execution results dictionary
        """
        self.logger.info("=" * 60)
        self.logger.info("STARTING SEQUENTIAL EXECUTION")
        self.logger.info("=" * 60)
        
        results = {
            'mode': 'sequential',
            'total_notebooks': len(notebooks),
            'executed_notebooks': [],
            'failed_notebooks': [],
            'execution_times': {},
            'start_time': time.time(),
            'end_time': None,
            'total_time': None,
            'success': True
        }
        
        for i, notebook_config in enumerate(notebooks, 1):
            notebook = notebook_config.get('notebook')
            params = notebook_config.get('params', {})
            output_name = notebook_config.get('output_name')
            
            self.logger.info(f"\n[{i}/{len(notebooks)}] Executing: {notebook}")
            
            exec_start = time.time()
            output_path, success, message = self.execute_notebook(
                notebook, params, output_name
            )
            exec_time = time.time() - exec_start
            
            results['execution_times'][notebook] = exec_time
            
            if success:
                results['executed_notebooks'].append({
                    'notebook': notebook,
                    'output': output_path,
                    'time': exec_time,
                    'message': message
                })
            else:
                results['failed_notebooks'].append({
                    'notebook': notebook,
                    'error': message
                })
                results['success'] = False
                self.logger.error(f"Stopping execution due to failure in {notebook}")
                break
        
        results['end_time'] = time.time()
        results['total_time'] = results['end_time'] - results['start_time']
        
        self._log_execution_summary(results)
        return results
    
    def execute_parallel(self, 
                        notebooks: List[Dict[str, Any]],
                        max_workers: int = None) -> Dict[str, Any]:
        """
        Execute notebooks in parallel using ThreadPoolExecutor.
        
        Args:
            notebooks: List of notebook configurations
            max_workers: Maximum number of parallel workers
            
        Returns:
            Execution results dictionary
        """
        max_workers = max_workers or self.config['execution'].get('max_workers', 4)
        
        self.logger.info("=" * 60)
        self.logger.info(f"STARTING PARALLEL EXECUTION (max_workers={max_workers})")
        self.logger.info("=" * 60)
        
        results = {
            'mode': 'parallel',
            'max_workers': max_workers,
            'total_notebooks': len(notebooks),
            'executed_notebooks': [],
            'failed_notebooks': [],
            'execution_times': {},
            'start_time': time.time(),
            'end_time': None,
            'total_time': None,
            'success': True
        }
        
        # Submit all notebooks for execution
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a mapping from future to notebook config
            future_to_notebook = {}
            
            for notebook_config in notebooks:
                notebook = notebook_config.get('notebook')
                params = notebook_config.get('params', {})
                output_name = notebook_config.get('output_name')
                
                future = executor.submit(
                    self.execute_notebook,
                    notebook,
                    params,
                    output_name
                )
                future_to_notebook[future] = notebook_config
            
            # Process completed futures
            for future in as_completed(future_to_notebook):
                notebook_config = future_to_notebook[future]
                notebook = notebook_config.get('notebook')
                
                try:
                    output_path, success, message = future.result()
                    
                    # Try to get actual execution time if possible
                    # For now, we'll use a placeholder
                    results['execution_times'][notebook] = 'concurrent'
                    
                    if success:
                        results['executed_notebooks'].append({
                            'notebook': notebook,
                            'output': output_path,
                            'message': message
                        })
                        self.logger.info(f"SUCCESS: {notebook}: {message}")
                    else:
                        results['failed_notebooks'].append({
                            'notebook': notebook,
                            'error': message
                        })
                        results['success'] = False
                        self.logger.error(f"✗ {notebook}: {message}")
                        
                except Exception as e:
                    results['failed_notebooks'].append({
                        'notebook': notebook,
                        'error': str(e)
                    })
                    results['success'] = False
                    self.logger.error(f"✗ {notebook}: {str(e)}")
        
        results['end_time'] = time.time()
        results['total_time'] = results['end_time'] - results['start_time']
        
        self._log_execution_summary(results)
        return results
    
    def _log_execution_summary(self, results: Dict[str, Any]) -> None:
        """Log execution summary."""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Mode: {results['mode']}")
        self.logger.info(f"Total Notebooks: {results['total_notebooks']}")
        self.logger.info(f"Executed: {len(results['executed_notebooks'])}")
        self.logger.info(f"Failed: {len(results['failed_notebooks'])}")
        self.logger.info(f"Total Time: {results['total_time']:.2f}s")
        self.logger.info(f"Status: {'SUCCESS' if results['success'] else 'FAILURE'}")
        
        if results['failed_notebooks']:
            self.logger.warning("\nFailed Notebooks:")
            for failed in results['failed_notebooks']:
                self.logger.warning(f"  - {failed['notebook']}: {failed.get('error', 'Unknown error')}")
        
        self.logger.info("=" * 60)
    
    def save_results(self, results: Dict[str, Any], 
                    filename: str = 'execution_results.json') -> str:
        """
        Save execution results to file.
        
        Args:
            results: Execution results dictionary
            filename: Output filename
            
        Returns:
            Path to saved results file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert any non-serializable values
        def convert_to_serializable(obj):
            if isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(v) for v in obj]
            else:
                return str(obj)
        
        results_copy = convert_to_serializable(results)
        
        with open(filepath, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        self.logger.info(f"Execution results saved to {filepath}")
        return filepath
    
    def get_output_dir(self) -> str:
        """Get the output directory path."""
        return self.output_dir


def main():
    """Example usage of NotebookOrchestrator."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    
    # Load configuration
    config_path = os.path.join(base_dir, 'configs', 'config.yaml')
    
    # Initialize orchestrator
    orchestrator = NotebookOrchestrator(config_path, base_dir)
    
    # Define notebook pipeline
    notebooks = [
        {
            'notebook': '01_load_data.ipynb',
            'params': {
                'test_size': orchestrator.config['data']['test_size'],
                'random_state': orchestrator.config['data']['random_state'],
                'dataset': orchestrator.config['data']['dataset'],
                'output_dir': orchestrator.output_dir
            }
        },
        {
            'notebook': '02_preprocess_data.ipynb',
            'params': {
                'normalize': orchestrator.config['data']['normalize'],
                'data_dir': os.path.join(orchestrator.output_dir, 'data'),
                'output_dir': orchestrator.output_dir
            }
        },
        {
            'notebook': '03_train_model.ipynb',
            'params': {
                'model_type': orchestrator.config['model']['type'],
                'alpha': orchestrator.config['model']['hyperparameters']['alpha'],
                'fit_intercept': orchestrator.config['model']['hyperparameters']['fit_intercept'],
                'data_dir': os.path.join(orchestrator.output_dir, 'processed'),
                'output_dir': orchestrator.output_dir
            }
        },
        {
            'notebook': '04_evaluate_model.ipynb',
            'params': {
                'model_type': orchestrator.config['model']['type'],
                'output_dir': orchestrator.output_dir,
                'generate_plots': orchestrator.config['output']['save_plots']
            }
        }
    ]
    
    # Execute based on configuration
    execution_mode = orchestrator.config['execution']['mode']
    
    if execution_mode == 'sequential':
        results = orchestrator.execute_sequential(notebooks)
    elif execution_mode == 'parallel':
        max_workers = orchestrator.config['execution'].get('max_workers', 4)
        results = orchestrator.execute_parallel(notebooks, max_workers)
    else:
        orchestrator.logger.error(f"Unknown execution mode: {execution_mode}")
        return
    
    # Save results
    orchestrator.save_results(results)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Output Directory: {orchestrator.output_dir}")
    print(f"{'='*60}")
    
    return orchestrator.output_dir


if __name__ == '__main__':
    main()
