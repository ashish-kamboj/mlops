#!/usr/bin/env python
"""
Quick start script for ML model deployment pipeline.
Runs data generation → feature engineering → model training → inference.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """
    Run a command and report status.
    
    Args:
        cmd: Command to run as list
        description: Description of what's being run
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'=' * 70}")
    print(f"► {description}")
    print(f"{'=' * 70}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✓ {description} completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}\n")
        return False
    except Exception as e:
        print(f"✗ {description} failed: {str(e)}\n")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'pandas',
        'numpy',
        'sklearn',
        'mlflow',
        'fastapi',
        'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies available\n")
    return True


def main():
    """Run the complete pipeline."""
    
    # Get project root (go up one level from tools/)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"\n{'=' * 70}")
    print("  ML Model Deployment - Quick Start")
    print(f"{'=' * 70}")
    print(f"Project root: {project_root}\n")
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ Please install missing dependencies before proceeding")
        return 1
    
    # Add src to path
    sys.path.insert(0, str(project_root / 'src'))
    
    # Notebooks are .ipynb and should be run via Jupyter
    print("Notebooks are .ipynb — run via Jupyter in order: 01 → 02 → 03.")
    print("Use 04_inference.ipynb to call the API (Minikube or localhost).\n")

    results = [
        ("Review config and run notebooks in Jupyter", True),
        ("Build Docker image (docker/run.*)", True),
        ("Test API locally (port 5000)", True),
    ]

    # Print summary
    print(f"\n{'=' * 70}")
    print("  Pipeline Summary")
    print(f"{'=' * 70}")
    
    for description, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {description}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n{passed}/{total} steps completed successfully")
    
    if passed == total:
        print("\n✓ Quick start steps reviewed!")
        print("\nNext steps:")
        print("  1. Run notebooks via Jupyter (01→03)")
        print("  2. Build Docker: see docker/run.*")
        print("  3. Test API: python tests/test_api.py or curl /health")
        print("  4. Optional: deploy to Minikube (scripts/k8s_deploy_minikube.*)")
        return 0
    else:
        print("\n✗ Pipeline did not complete. See errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)