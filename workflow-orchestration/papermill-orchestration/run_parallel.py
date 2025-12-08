"""
Example: Parallel Execution
Demonstrates running notebooks in parallel with the orchestrator.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.orchestrator import NotebookOrchestrator


def main():
    """Run parallel execution example."""
    
    # Get base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'configs', 'config.yaml')
    
    # Initialize orchestrator
    print("\n" + "="*60)
    print("NOTEBOOK ORCHESTRATION - PARALLEL EXAMPLE")
    print("="*60 + "\n")
    
    orchestrator = NotebookOrchestrator(config_path, base_dir)
    
    # Define independent notebooks that can run in parallel
    # Note: In parallel mode, notebooks should be independent or properly ordered
    # For this example, we'll demonstrate parallel execution of training different models
    
    notebooks = [
        {
            'notebook': '01_load_data.ipynb',
            'params': {
                'test_size': 0.2,
                'random_state': 42,
                'dataset': 'synthetic',
                'output_dir': orchestrator.output_dir
            },
            'output_name': '01_load_data_output.ipynb'
        },
        {
            'notebook': '02_preprocess_data.ipynb',
            'params': {
                'normalize': True,
                'data_dir': os.path.join(orchestrator.output_dir, 'data'),
                'output_dir': orchestrator.output_dir
            },
            'output_name': '02_preprocess_data_output.ipynb'
        },
        # Multiple model training notebooks can run in parallel
        # (In a real scenario, you might have separate notebooks for different models)
        {
            'notebook': '03_train_model.ipynb',
            'params': {
                'model_type': 'linear_regression',
                'alpha': 1.0,
                'fit_intercept': True,
                'data_dir': os.path.join(orchestrator.output_dir, 'processed'),
                'output_dir': orchestrator.output_dir
            },
            'output_name': '03_train_linear_regression_output.ipynb'
        },
        {
            'notebook': '04_evaluate_model.ipynb',
            'params': {
                'model_type': 'linear_regression',
                'output_dir': orchestrator.output_dir,
                'generate_plots': True
            },
            'output_name': '04_evaluate_linear_regression_output.ipynb'
        }
    ]
    
    # Execute in parallel with 2 workers
    results = orchestrator.execute_parallel(notebooks, max_workers=2)
    
    # Save results
    results_path = orchestrator.save_results(results, 'parallel_results.json')
    
    # Print output location
    print(f"\n{'='*60}")
    print("SUCCESS: Parallel Execution Completed")
    print(f"{'='*60}")
    print(f"Output Directory: {orchestrator.get_output_dir()}")
    print(f"Results File: {results_path}")
    print(f"\nStatus: {'SUCCESS' if results['success'] else 'FAILED'}")
    print(f"Executed: {len(results['executed_notebooks'])}/{results['total_notebooks']}")
    print(f"Total Time: {results['total_time']:.2f}s")
    print(f"Max Workers: {results['max_workers']}")
    print(f"{'='*60}\n")
    
    return orchestrator.get_output_dir()


if __name__ == '__main__':
    main()
