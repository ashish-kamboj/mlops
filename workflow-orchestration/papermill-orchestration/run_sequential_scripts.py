"""
Sequential Pipeline Runner - Python Scripts Version

Executes the complete ML pipeline using pure Python scripts in sequence:
1. Load Data
2. Preprocess Data
3. Train Model
4. Evaluate Model

This approach provides better visibility of execution results compared to 
Jupyter notebooks executed with Papermill.
"""

import os
import sys
import subprocess
import time

# ==============================================================================
# CONFIGURATION
# ==============================================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')

# Pipeline definition: list of (script_name, args)
PIPELINE = [
    ('01_load_data.py', ['0.2', '42', 'synthetic', 'outputs']),
    ('02_preprocess_data.py', ['true', 'outputs/data', 'outputs/processed']),
    ('03_train_model.py', ['linear_regression', '1.0', 'true', 'outputs/processed', 'outputs']),
    ('04_evaluate_model.py', ['linear_regression', 'outputs/processed', 'outputs/models', 'outputs', 'true']),
]

# ==============================================================================
# EXECUTION
# ==============================================================================

def run_pipeline():
    """Execute all scripts in the pipeline sequentially."""
    
    print("=" * 80)
    print("SEQUENTIAL PIPELINE RUNNER - PYTHON SCRIPTS VERSION")
    print("=" * 80)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Scripts Directory: {SCRIPTS_DIR}")
    print(f"\nPipeline Steps: {len(PIPELINE)}")
    for i, (script, args) in enumerate(PIPELINE, 1):
        print(f"  {i}. {script} {' '.join(args[:2])}...")
    
    results = []
    
    print("\n" + "=" * 80)
    print("STARTING PIPELINE EXECUTION")
    print("=" * 80)
    
    for idx, (script_name, args) in enumerate(PIPELINE, 1):
        script_path = os.path.join(SCRIPTS_DIR, script_name)
        
        if not os.path.exists(script_path):
            print(f"\nERROR: Script not found: {script_path}")
            return False
        
        print(f"\n{'-' * 80}")
        print(f"STEP {idx}: {script_name}")
        print(f"{'-' * 80}")
        
        step_start = time.time()
        
        try:
            # Build command
            python_exe = sys.executable
            cmd = [python_exe, script_path] + args
            
            print(f"Command: {' '.join(cmd)}\n")
            
            # Execute script
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=False,
                text=True,
                check=False
            )
            
            step_elapsed = time.time() - step_start
            
            if result.returncode == 0:
                print(f"\nStep {idx} completed in {step_elapsed:.2f} seconds")
                results.append({
                    'step': idx,
                    'script': script_name,
                    'status': 'SUCCESS',
                    'elapsed_seconds': step_elapsed
                })
            else:
                print(f"\nStep {idx} failed with return code {result.returncode}")
                results.append({
                    'step': idx,
                    'script': script_name,
                    'status': 'FAILURE',
                    'elapsed_seconds': step_elapsed,
                    'return_code': result.returncode
                })
                return False
        
        except Exception as e:
            step_elapsed = time.time() - step_start
            print(f"\nStep {idx} raised exception: {str(e)}")
            results.append({
                'step': idx,
                'script': script_name,
                'status': 'ERROR',
                'elapsed_seconds': step_elapsed,
                'error': str(e)
            })
            return False
    
    # Print summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    for result in results:
        status_text = result['status']
        print(f"Step {result['step']}: {result['script']} ({result['elapsed_seconds']:.2f}s) - {status_text}")
    
    total_elapsed = sum(r['elapsed_seconds'] for r in results)
    print(f"\nTotal Execution Time: {total_elapsed:.2f} seconds")
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nOutput Files Generated:")
    print("  - Data: outputs/data/X_train.csv, X_test.csv, y_train.csv, y_test.csv")
    print("  - Processed: outputs/processed/X_train_processed.csv, X_test_processed.csv")
    print("  - Models: outputs/models/linear_regression_model.pkl")
    print("  - Predictions: outputs/predictions/linear_regression_*_predictions.csv")
    print("  - Plots: outputs/plots/linear_regression_*.png (4 plots)")
    print("  - Metrics: outputs/models/linear_regression_*.json (3 files)")
    print("\n" + "=" * 80)
    
    return True

if __name__ == '__main__':
    success = run_pipeline()
    sys.exit(0 if success else 1)
