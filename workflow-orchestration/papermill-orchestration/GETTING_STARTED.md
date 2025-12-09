# Getting Started

This guide covers installation and basic setup. For approach-specific details, see:
- **Approach 1:** APPROACH_1_PAPERMILL.md
- **Approach 2:** APPROACH_2_PYTHON_SCRIPTS.md (recommended)

---

## 📋 Prerequisites

- **Python 3.8+** (3.11+ recommended)
- **pip** or **conda** (package manager)
- **~500 MB** disk space
- **Internet connection** (for installation only)

Check if Python is installed:
```bash
python --version
```

---

## 🔧 Installation

### Step 1: Navigate to Project Directory
```bash
cd notebook-orchestration-local
```

### Step 2: Create Virtual Environment (Optional but Recommended)

**On Windows:**
```bash
python -m venv notebook-orch-venv
notebook-orch-venv\Scripts\activate
```

**On Linux/Mac:**
```bash
python -m venv notebook-orch-venv
source notebook-orch-venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- **Data handling:** pandas, numpy
- **Machine Learning:** scikit-learn
- **Visualization:** matplotlib, seaborn
- **Notebooks:** jupyter, papermill
- **Configuration:** pyyaml

### Step 4: Verify Installation
```bash
python -c "import pandas, numpy, sklearn; print('✓ Installation successful!')"
```

---

## ✅ Verify Everything Works

### Quick Test - Approach 2 (Python Scripts)
```bash
python run_sequential_scripts.py
```

Expected output:
```
================================================================================
SEQUENTIAL PIPELINE RUNNER - PYTHON SCRIPTS VERSION
================================================================================

STEP 1: LOAD DATA
...
Dataset shape: (500, 11)
...

STEP 2: PREPROCESS DATA
...

STEP 3: TRAIN MODEL
...
Training Metrics: MSE: 365.38, RMSE: 19.12, R²: 0.983
...

STEP 4: EVALUATE MODEL
...

================================================================================
PIPELINE EXECUTION SUMMARY
================================================================================
Step 1: 01_load_data.py (5.60s) - SUCCESS
Step 2: 02_preprocess_data.py (4.87s) - SUCCESS
Step 3: 03_train_model.py (4.48s) - SUCCESS
Step 4: 04_evaluate_model.py (10.09s) - SUCCESS

Total Execution Time: 25.04 seconds

PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

Time: ~25 seconds ✓

### Quick Test - Approach 1 (Papermill)
```bash
python run_sequential_notebooks.py
```

Expected output:
```
============================================================
NOTEBOOK ORCHESTRATION - SEQUENTIAL EXAMPLE
============================================================

SUCCESS: Execution Completed
============================================================
Output Directory: outputs/run_20251209_120530
Results File: outputs/run_20251209_120530/sequential_results.json
Status: SUCCESS
Executed: 4/4
Total Time: 38.89s
============================================================
```

Time: ~40 seconds ✓

---

## 📁 Project Structure

```
notebook-orchestration-local/
├── README.md                      # Start here
├── GETTING_STARTED.md             # This file
├── APPROACH_1_PAPERMILL.md        # Papermill details
├── APPROACH_2_PYTHON_SCRIPTS.md   # Python scripts details
│
├── run_sequential_scripts.py      # ⭐ Run this first (Approach 2)
├── run_parallel_scripts.py        # Parallel runner (Approach 2)
├── run_sequential_notebooks.py    # Sequential runner (Approach 1)
├── run_parallel_notebooks.py      # Parallel runner (Approach 1)
│
├── scripts/                       # Python scripts (Approach 2)
│   ├── 01_load_data.py
│   ├── 02_preprocess_data.py
│   ├── 03_train_model.py
│   └── 04_evaluate_model.py
│
├── notebooks/                     # Jupyter notebooks (Approach 1)
│   ├── 01_load_data.ipynb
│   ├── 02_preprocess_data.ipynb
│   ├── 03_train_model.ipynb
│   └── 04_evaluate_model.ipynb
│
├── configs/
│   └── config.yaml                # Configuration (Approach 1)
│
├── requirements.txt               # Dependencies
└── outputs/                       # Generated files (auto-created)
```

---

## 🚀 First Run

### Recommended: Approach 2 (Python Scripts)

```bash
python run_sequential_scripts.py
```

What happens:
1. ✓ Generates 500 synthetic data points
2. ✓ Splits into training (80%) and test (20%)
3. ✓ Preprocesses (normalization)
4. ✓ Trains Linear Regression model
5. ✓ Evaluates and generates plots
6. ✓ All outputs saved to `outputs/`

Total time: ~25 seconds

### Alternative: Approach 1 (Papermill)

```bash
python run_sequential_notebooks.py
```

What happens:
1. ✓ Executes Jupyter notebooks with Papermill
2. ✓ Injects parameters into each notebook
3. ✓ Generates output notebooks
4. ✓ All outputs saved to `outputs/`

Total time: ~40 seconds

---

## 📊 Check Your Results

After running, explore the outputs:

```bash
# List all generated files
ls -la outputs/

# View metrics
cat outputs/models/*_metrics.json

# View plots (visual exploration)
# Open: outputs/plots/
```

---

## 🔧 Configuration (Approach 1 Only)

Edit `configs/config.yaml` to customize Papermill execution:

```yaml
data:
  test_size: 0.2              # Train/test split ratio
  random_state: 42            # Reproducibility
  dataset: synthetic          # Data source

model:
  type: linear_regression     # Model: linear_regression, ridge, lasso
  hyperparameters:
    alpha: 1.0                # Regularization strength

execution:
  mode: sequential            # sequential or parallel
  max_workers: 4              # Number of parallel workers
```

Then run:
```bash
python run_sequential_notebooks.py
```

---

## ⚡ Using Command-Line Parameters (Approach 2)

Approach 2 allows passing parameters directly:

### Load Data
```bash
python scripts/01_load_data.py 0.3 42 synthetic outputs
# Format: test_size random_state dataset output_dir
```

### Train Model
```bash
python scripts/03_train_model.py ridge 5.0 true outputs/processed outputs
# Format: model_type alpha fit_intercept data_dir output_dir
```

---

## 🔄 Running Parallel Execution

### Approach 2: Train Multiple Models in Parallel
```bash
python run_parallel_scripts.py
```

Trains 5 different models concurrently:
- Linear Regression
- Ridge (α=0.1)
- Ridge (α=1.0)
- Ridge (α=10.0)
- Lasso (α=0.1)

Time: ~35 seconds

### Approach 1: Parallel with Papermill
```bash
python run_parallel_notebooks.py
```

Configurable in `configs/config.yaml`:
```yaml
execution:
  mode: parallel
  max_workers: 2              # Adjust concurrency
```

---

## 🐛 Troubleshooting

### Problem: "python: command not found"
**Solution:** Python not in PATH. Install Python from python.org or reinstall.

### Problem: "ModuleNotFoundError: No module named 'pandas'"
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "FileNotFoundError: Notebook not found"
**Solution:** Run from project directory:
```bash
cd notebook-orchestration-local
python run_sequential_notebooks.py
```

### Problem: Scripts run but no outputs in `outputs/` folder
**Solution:** Check terminal for error messages. All errors are printed there.

### Problem: "Permission denied" on Linux/Mac
**Solution:**
```bash
chmod +x *.py scripts/*.py
```

### Problem: Virtual environment issues
**Solution:** Deactivate and recreate:
```bash
deactivate
rm -rf notebook-orch-venv
python -m venv notebook-orch-venv
source notebook-orch-venv/bin/activate  # or Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📚 Next Steps

### 1. Read Overview (5 min)
Open and read `README.md`

### 2. Choose Your Approach

**For production and speed:**
→ Read `APPROACH_2_PYTHON_SCRIPTS.md`

**For notebooks and templates:**
→ Read `APPROACH_1_PAPERMILL.md`

### 3. Explore Examples

**Approach 2:**
- Sequential: `python run_sequential_scripts.py`
- Parallel: `python run_parallel_scripts.py`

**Approach 1:**
- Sequential: `python run_sequential_notebooks.py`
- Parallel: `python run_parallel_notebooks.py`

### 4. Customize for Your Use Case

Modify scripts or configuration to fit your needs.

---

## 📋 Quick Reference

| Command | Purpose | Approach | Time |
|---------|---------|----------|------|
| `python run_sequential_scripts.py` | Run pipeline sequentially | 2 | ~25s |
| `python run_parallel_scripts.py` | Train 5 models in parallel | 2 | ~35s |
| `python run_sequential_notebooks.py` | Run with Papermill | 1 | ~40s |
| `python run_parallel_notebooks.py` | Parallel with Papermill | 1 | ~50s |
| `python scripts/01_load_data.py ...` | Custom parameters | 2 | varies |

---

## ✅ System Check

Run this to verify everything is installed correctly:

```python
# save as check_setup.py
import sys
print(f"✓ Python: {sys.version}")

try:
    import pandas as pd
    print(f"✓ pandas: {pd.__version__}")
except ImportError:
    print("✗ pandas: NOT INSTALLED")

try:
    import numpy as np
    print(f"✓ numpy: {np.__version__}")
except ImportError:
    print("✗ numpy: NOT INSTALLED")

try:
    import sklearn
    print(f"✓ scikit-learn: {sklearn.__version__}")
except ImportError:
    print("✗ scikit-learn: NOT INSTALLED")

try:
    import matplotlib
    print(f"✓ matplotlib: {matplotlib.__version__}")
except ImportError:
    print("✗ matplotlib: NOT INSTALLED")

try:
    import papermill
    print(f"✓ papermill: {papermill.__version__}")
except ImportError:
    print("✗ papermill: NOT INSTALLED (needed for Approach 1)")

try:
    import jupyter
    print(f"✓ jupyter: installed")
except ImportError:
    print("✗ jupyter: NOT INSTALLED (needed for Approach 1)")

print("\n✓ Setup complete!" if all else "✗ Please install missing packages")
```

Run:
```bash
python check_setup.py
```

---

## 🎯 You're Ready!

✅ Environment set up
✅ Dependencies installed
✅ Basic verification done

**Next:** Open README.md for overview, then choose Approach 1 or 2.

**Start here:**
```bash
python run_sequential_scripts.py
```

---

## 📞 Support

- **Installation issues:** See troubleshooting section above
- **Usage questions:** See README.md for overview
- **Approach-specific:** See APPROACH_1_PAPERMILL.md or APPROACH_2_PYTHON_SCRIPTS.md
- **Code issues:** Check terminal output for error messages

---

## 💡 Tips

- Always run from project root directory
- Check `outputs/` folder after running
- Use terminal output for troubleshooting
- Both approaches generate identical data outputs
- Start with Approach 2 if unsure
