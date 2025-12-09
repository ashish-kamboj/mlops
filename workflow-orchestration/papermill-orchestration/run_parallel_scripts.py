"""
Parallel Pipeline Runner - Python Scripts Version

Executes multiple model training pipelines in parallel using ThreadPoolExecutor.
This allows you to train different models (linear_regression, ridge, lasso)
or different hyperparameter configurations concurrently.

Configuration can be changed to test different models or parameters.
"""

import os
import sys
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

# Define multiple training configurations to run in parallel
TRAINING_CONFIGS = [
    {
        'name': 'linear_regression',
        'model_type': 'linear_regression',
        'alpha': '1.0'
    },
    {
        'name': 'ridge (alpha=0.1)',
        'model_type': 'ridge',
        'alpha': '0.1'
    },
    {
        'name': 'ridge (alpha=1.0)',
        'model_type': 'ridge',
        'alpha': '1.0'
    },
    {
        'name': 'ridge (alpha=10.0)',
        'model_type': 'ridge',
        'alpha': '10.0'
    },
    {
        'name': 'lasso (alpha=0.1)',
        'model_type': 'lasso',
        'alpha': '0.1'
    },
]

# ==============================================================================
# EXECUTION
# ==============================================================================

def run_data_preparation():
    """Run data preparation steps (load + preprocess) once."""
    print("=" * 80)
    print("PREPARING DATA (Running Steps 1-2)")
    print("=" * 80)
    
    # Step 1: Load Data
    print("\nStep 1: Loading Data...")
    cmd1 = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, '01_load_data.py'),
        '0.2', '42', 'synthetic', 'outputs'
    ]
    result1 = subprocess.run(cmd1, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result1.returncode != 0:
        print("ERROR: Data loading failed")
        print(result1.stderr)
        return False
    print("Step 1 completed successfully")
    
    # Step 2: Preprocess Data
    print("\nStep 2: Preprocessing Data...")
    cmd2 = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, '02_preprocess_data.py'),
        'true', 'outputs/data', 'outputs/processed'
    ]
    result2 = subprocess.run(cmd2, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if result2.returncode != 0:
        print("ERROR: Data preprocessing failed")
        print(result2.stderr)
        return False
    print("Step 2 completed successfully")
    
    return True

def train_model(config):
    """Train a single model based on configuration."""
    model_type = config['model_type']
    alpha = config['alpha']
    config_name = config['name']
    
    try:
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, '03_train_model.py'),
            model_type, alpha, 'true', 'outputs/processed', 'outputs'
        ]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return {
                'config': config_name,
                'status': 'SUCCESS',
                'output': result.stdout
            }
        else:
            return {
                'config': config_name,
                'status': 'FAILED',
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            'config': config_name,
            'status': 'TIMEOUT',
            'error': 'Training timed out after 60 seconds'
        }
    except Exception as e:
        return {
            'config': config_name,
            'status': 'ERROR',
            'error': str(e)
        }

def evaluate_model(config):
    """Evaluate a trained model."""
    model_type = config['model_type']
    config_name = config['name']
    
    try:
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, '04_evaluate_model.py'),
            model_type, 'outputs/processed', 'outputs/models', 'outputs', 'true'
        ]
        
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return {
                'config': config_name,
                'status': 'SUCCESS'
            }
        else:
            return {
                'config': config_name,
                'status': 'FAILED',
                'error': result.stderr
            }
    except Exception as e:
        return {
            'config': config_name,
            'status': 'ERROR',
            'error': str(e)
        }

def run_parallel_pipeline(max_workers=4):
    """Execute training in parallel with multiple configurations."""
    
    print("=" * 80)
    print("PARALLEL PIPELINE RUNNER - PYTHON SCRIPTS VERSION")
    print("=" * 80)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Max Workers: {max_workers}")
    print(f"\nTraining Configurations ({len(TRAINING_CONFIGS)}):")
    for i, config in enumerate(TRAINING_CONFIGS, 1):
        print(f"  {i}. {config['name']}")
    
    # Step 1-2: Prepare data once
    print("\n")
    if not run_data_preparation():
        print("Data preparation failed. Exiting.")
        return False
    
    # Step 3: Train models in parallel
    print("\n" + "=" * 80)
    print("TRAINING MODELS IN PARALLEL (Step 3)")
    print("=" * 80)
    
    training_start = time.time()
    training_results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(train_model, config): config for config in TRAINING_CONFIGS}
        
        for future in as_completed(futures):
            config = futures[future]
            try:
                result = future.result()
                training_results.append(result)
                status = result['status']
                print(f"[{status}] {result['config']}")
            except Exception as e:
                print(f"[ERROR] {config['name']}: {str(e)}")
                training_results.append({
                    'config': config['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
    
    training_elapsed = time.time() - training_start
    
    # Step 4: Evaluate models in parallel
    print("\n" + "=" * 80)
    print("EVALUATING MODELS IN PARALLEL (Step 4)")
    print("=" * 80)
    
    evaluation_start = time.time()
    evaluation_results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(evaluate_model, config): config for config in TRAINING_CONFIGS}
        
        for future in as_completed(futures):
            config = futures[future]
            try:
                result = future.result()
                evaluation_results.append(result)
                status = result['status']
                print(f"[{status}] {result['config']}")
            except Exception as e:
                print(f"[ERROR] {config['name']}: {str(e)}")
                evaluation_results.append({
                    'config': config['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
    
    evaluation_elapsed = time.time() - evaluation_start
    
    # Print summary
    print("\n" + "=" * 80)
    print("PARALLEL EXECUTION SUMMARY")
    print("=" * 80)
    
    successful_configs = sum(1 for r in training_results if r['status'] == 'SUCCESS')
    print(f"\nTraining Results: {successful_configs}/{len(TRAINING_CONFIGS)} successful")
    print(f"Training Time: {training_elapsed:.2f} seconds")
    print(f"Evaluation Time: {evaluation_elapsed:.2f} seconds")
    print(f"Total Time: {training_elapsed + evaluation_elapsed:.2f} seconds")
    
    print("\nOutput Files Generated:")
    print("  - Data: outputs/data/X_train.csv, X_test.csv, y_train.csv, y_test.csv")
    print("  - Processed: outputs/processed/X_train_processed.csv, X_test_processed.csv")
    print("  - Models: outputs/models/*_model.pkl (multiple model types)")
    print("  - Predictions: outputs/predictions/*_*_predictions.csv")
    print("  - Plots: outputs/plots/*_*.png (multiple model evaluation plots)")
    print("  - Metrics: outputs/models/*_*.json (training metrics and evaluation)")
    
    print("\n" + "=" * 80)
    print("PARALLEL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return True

if __name__ == '__main__':
    max_workers = 4
    if len(sys.argv) > 1:
        try:
            max_workers = int(sys.argv[1])
        except ValueError:
            print(f"Invalid max_workers value: {sys.argv[1]}")
            sys.exit(1)
    
    success = run_parallel_pipeline(max_workers=max_workers)
    sys.exit(0 if success else 1)
