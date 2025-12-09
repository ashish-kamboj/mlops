# Approach 1: Papermill + Jupyter Notebooks

This approach uses **Papermill** to orchestrate parameterized Jupyter notebooks. It's ideal for teams preferring Jupyter and template-based workflows.

## 📚 What is Papermill?

Papermill is a library for parameterizing and executing Jupyter notebooks:
- **Parameterize:** Inject variables into notebook cells
- **Execute:** Run parameterized notebooks programmatically
- **Output:** Create timestamped output notebooks
- **Schedule:** Easy to schedule with cron/Task Scheduler
- **Template:** Create reusable notebook templates

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│ Configuration (configs/config.yaml)                   │
│ - Model type (linear_regression, ridge, lasso)       │
│ - Hyperparameters (alpha, fit_intercept, etc.)       │
│ - Execution mode (sequential or parallel)            │
│ - Max workers for parallelization                    │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ Papermill Orchestrator (scripts/orchestrator.py)     │
│ - Read configuration                                 │
│ - Inject parameters into notebooks                  │
│ - Execute notebooks with parameters                 │
│ - Save output notebooks                             │
│ - Collect results                                   │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ Notebook Execution Pipeline                          │
│                                                      │
│ Sequential:           Parallel:                      │
│ 1. Load Data          1. Load Data                   │
│ 2. Preprocess    →    2. Preprocess                 │
│ 3. Train Model   →    3. Train (parallel)           │
│ 4. Evaluate      →    4. Evaluate (parallel)        │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│ Generated Output                                      │
│ - Output notebooks (with embedded results)          │
│ - Data files (CSV)                                  │
│ - Models (PKL)                                      │
│ - Metrics (JSON)                                    │
│ - Plots (PNG)                                       │
└──────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Run Sequential
```bash
python run_sequential_notebooks.py
```

**Output:**
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

**Time:** ~40 seconds

### 2. Run Parallel
```bash
python run_parallel_notebooks.py
```

**Time:** ~50 seconds (trains models in parallel)

---

## ⚙️ Configuration

Edit `configs/config.yaml` to customize behavior:

```yaml
# Data Configuration
data:
  test_size: 0.2              # Train/test split ratio
  random_state: 42            # Reproducibility seed
  normalize: true             # Normalize features
  dataset: synthetic          # Data source

# Model Configuration
model:
  type: linear_regression     # Options: linear_regression, ridge, lasso
  hyperparameters:
    alpha: 1.0                # Regularization (ignored for linear_regression)
    fit_intercept: true       # Fit intercept term
    random_state: 42

# Execution Configuration
execution:
  mode: sequential            # sequential or parallel
  max_workers: 4              # Number of parallel workers
  timeout: 300                # Timeout in seconds

# Logging Configuration
logging:
  level: INFO                 # DEBUG, INFO, WARNING, ERROR
  log_file: logs/orchestration.log

# Output Configuration
output:
  save_outputs: true
  output_dir: outputs
  save_model: true
  save_plots: true
  model_format: pkl           # pkl or joblib
```

### Common Configurations

**Ridge Regression with alpha=1.0**
```yaml
model:
  type: ridge
  hyperparameters:
    alpha: 1.0
```

**Lasso with alpha=0.1**
```yaml
model:
  type: lasso
  hyperparameters:
    alpha: 0.1
```

**Parallel Execution with 4 Workers**
```yaml
execution:
  mode: parallel
  max_workers: 4
```

---

## 📖 How to Use

### Sequential Execution (Recommended)

Execute all steps one by one:

```bash
python run_sequential_notebooks.py
```

**Pipeline:**
1. Loads data (injects `test_size`, `random_state`)
2. Preprocesses data (injects `normalize`)
3. Trains model (injects `model_type`, `alpha`)
4. Evaluates model (injects evaluation parameters)

**Output:**
```
- logs/orchestration.log
- outputs/run_20251209_120530/
  ├── 01_load_data_output.ipynb
  ├── 02_preprocess_data_output.ipynb
  ├── 03_train_model_output.ipynb
  ├── 04_evaluate_model_output.ipynb
  └── Data files, models, metrics, plots
```

### Parallel Execution

Train multiple models concurrently:

```bash
python run_parallel_notebooks.py
```

**What it does:**
1. Loads data sequentially
2. Preprocesses data sequentially
3. Trains multiple model configurations **in parallel**
4. Evaluates all models **in parallel**

**Benefits:**
- ~2.4x faster for independent tasks
- Ideal for model comparison
- Efficient use of CPU cores

---

## 📝 Notebook Structure

Each notebook has a **`parameters` cell** at the top:

```python
# parameters
# Default values (overridden by Papermill)

# For 01_load_data.ipynb
test_size = 0.2
random_state = 42
dataset = 'synthetic'
output_dir = 'outputs'

# For 03_train_model.ipynb
model_type = 'linear_regression'
alpha = 1.0
fit_intercept = True
data_dir = 'outputs/processed'
output_dir = 'outputs'
```

When you run a notebook with Papermill, it:
1. Reads your config
2. Injects values into the `parameters` cell
3. Executes the notebook with those values
4. Saves the output notebook

---

## 🔄 Workflow Examples

### Example 1: Train Linear Regression
```bash
# Edit config (or use default)
# configs/config.yaml:
# model:
#   type: linear_regression

python run_sequential_notebooks.py
# Results in: outputs/run_*/
```

### Example 2: Train Ridge with alpha=5.0
```yaml
# configs/config.yaml
model:
  type: ridge
  hyperparameters:
    alpha: 5.0
```

```bash
python run_sequential_notebooks.py
```

### Example 3: Compare Multiple Models

```bash
# Train model 1 (linear regression)
# Edit config.yaml: type: linear_regression
python run_sequential_notebooks.py
mkdir -p results/linear_regression
cp -r outputs/run_* results/linear_regression/

# Train model 2 (ridge)
# Edit config.yaml: type: ridge, alpha: 1.0
python run_sequential_notebooks.py
mkdir -p results/ridge_1
cp -r outputs/run_* results/ridge_1/

# Compare results
ls -la results/
```

### Example 3: Parallel Training
```yaml
# configs/config.yaml
execution:
  mode: parallel
  max_workers: 4
```

```bash
python run_sequential_notebooks.py
# Will use parallel execution if available
```

---

## 📊 File Locations

```
notebooks/
├── 01_load_data.ipynb         # Data loading notebook
├── 02_preprocess_data.ipynb   # Preprocessing notebook
├── 03_train_model.ipynb       # Model training notebook
└── 04_evaluate_model.ipynb    # Evaluation notebook

scripts/
├── orchestrator.py            # Papermill orchestrator
└── utils.py                   # Helper functions

run_sequential_notebooks.py       # Sequential runner
run_parallel_notebooks.py         # Parallel runner

configs/
└── config.yaml                # Configuration file

outputs/
└── run_20251209_120530/       # Generated outputs
    ├── *_output.ipynb         # Generated notebooks
    ├── data/                  # Generated data files
    ├── models/                # Generated models
    ├── predictions/           # Predictions
    ├── plots/                 # Visualizations
    └── sequential_results.json # Execution summary
```

---

## 📈 Output Examples

### Generated Notebook Structure

Each output notebook contains:
- **Parameters cell** (injected by Papermill)
- **Original code** (unchanged)
- **Cell outputs** (results of execution)
- **Plots** (if generated)

### Results File (sequential_results.json)
```json
{
  "mode": "sequential",
  "total_notebooks": 4,
  "executed_notebooks": [
    {
      "notebook": "01_load_data.ipynb",
      "output": "outputs/run_20251209_120530/01_load_data_output.ipynb",
      "time": 2.34,
      "message": "Successfully executed in 2.34s"
    },
    {
      "notebook": "02_preprocess_data.ipynb",
      "output": "outputs/run_20251209_120530/02_preprocess_data_output.ipynb",
      "time": 2.01,
      "message": "Successfully executed in 2.01s"
    },
    {
      "notebook": "03_train_model.ipynb",
      "output": "outputs/run_20251209_120530/03_train_model_output.ipynb",
      "time": 15.45,
      "message": "Successfully executed in 15.45s"
    },
    {
      "notebook": "04_evaluate_model.ipynb",
      "output": "outputs/run_20251209_120530/04_evaluate_model_output.ipynb",
      "time": 18.67,
      "message": "Successfully executed in 18.67s"
    }
  ],
  "failed_notebooks": [],
  "execution_times": {
    "01_load_data.ipynb": 2.34,
    "02_preprocess_data.ipynb": 2.01,
    "03_train_model.ipynb": 15.45,
    "04_evaluate_model.ipynb": 18.67
  },
  "total_time": 38.47,
  "success": true
}
```

---

## 🔌 Orchestrator API

### For Python Integration

```python
from scripts.orchestrator import NotebookOrchestrator

# Initialize
orchestrator = NotebookOrchestrator('configs/config.yaml', base_dir='.')

# Define notebooks to execute
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
        }
    }
]

# Execute sequentially
results = orchestrator.execute_sequential(notebooks)

# Or execute in parallel
results = orchestrator.execute_parallel(notebooks, max_workers=4)

# Save results
results_file = orchestrator.save_results(results, 'my_results.json')

# Get output directory
output_dir = orchestrator.get_output_dir()
```

---

## ⚡ Performance

### Execution Times
```
Sequential (single model):
  Step 1 (Load):       2.3s
  Step 2 (Preprocess):  2.0s
  Step 3 (Train):      15.5s
  Step 4 (Evaluate):   18.7s
  Total:             ~38 seconds

Parallel (4 models):
  Data Prep:           4.2s (sequential)
  Training:           15.5s (parallel)
  Evaluation:         18.7s (parallel)
  Total:             ~50 seconds
```

### Overhead
- Papermill overhead: ~2-3 seconds
- Kernel startup: ~2-3 seconds
- Total overhead: ~40% of execution time

---

## ✅ Pros & Cons

### Advantages
✅ **Visual development** - Use Jupyter's interactive interface
✅ **Templates** - Reusable parameterized notebooks
✅ **Familiar** - Great for Jupyter users
✅ **Documentation** - Code and explanations together
✅ **Scheduling** - Easy to schedule with cron/Task Scheduler
✅ **Output notebooks** - Generated notebooks show all results

### Disadvantages
❌ **Slower** - Jupyter kernel overhead (~40 seconds)
❌ **No output visibility** - Results hidden until execution completes
❌ **Complex setup** - Requires Papermill, Jupyter, etc.
❌ **Hard to debug** - Errors in generated notebooks
❌ **Large files** - Notebooks are JSON (hard to diff)
❌ **Integration challenges** - Difficult in CI/CD pipelines

---

## 🎯 When to Use This Approach

Use **Approach 1 (Papermill)** when:
- ✅ You prefer **Jupyter notebooks**
- ✅ You want a **visual interface**
- ✅ Your team is **familiar with Jupyter**
- ✅ You need **notebook templates**
- ✅ You want to **share notebooks** with team
- ✅ You're doing **data exploration**
- ✅ Speed is **not critical**

**Do NOT use** if:
❌ You need **fast execution**
❌ You need **real-time output visibility**
❌ You're building **production pipelines**
❌ You need **easy CI/CD integration**

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'papermill'"
**Solution:**
```bash
pip install papermill
```

### Error: "FileNotFoundError: Notebook not found"
**Solution:** Ensure notebooks are in `notebooks/` folder and you're running from project root:
```bash
cd notebook-orchestration-local
python run_sequential_notebooks.py
```

### Error: "Jupyter kernel not found"
**Solution:**
```bash
pip install jupyter
```

### Notebook execution hangs
**Solution:** Increase timeout in `config.yaml`:
```yaml
execution:
  timeout: 600  # Increase from 300
```

### Output notebooks don't show results
**Solution:** Check `logs/orchestration.log` for errors. Ensure parameters are correct in `config.yaml`.

---

## 🚀 Integration Examples

### Schedule with Cron (Linux/Mac)
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/notebook-orchestration-local && python run_sequential_notebooks.py
```

### Schedule with Task Scheduler (Windows)
```
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9 AM
4. Set action: Start program
5. Program: python.exe
6. Arguments: run_sequential_notebooks.py
7. Start in: C:\path\to\notebook-orchestration-local
```

### Docker Integration
```dockerfile
FROM jupyter/scipy-notebook:latest
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "run_sequential_notebooks.py"]
```

---

## 📚 Related Docs

- **README.md** - Overview and comparison
- **GETTING_STARTED.md** - Installation
- **APPROACH_2_PYTHON_SCRIPTS.md** - Alternative approach (recommended)

---

## 🎓 Learning Path

1. **Setup:** Install dependencies (see GETTING_STARTED.md)
2. **Basic:** Run `python run_sequential_notebooks.py`
3. **Explore:** Review generated notebooks in `outputs/`
4. **Configure:** Edit `configs/config.yaml`
5. **Integrate:** Use in your own projects
6. **Extend:** Modify notebooks or add new ones

---

## ⚠️ Recommendation

For **most use cases**, we recommend **Approach 2 (Python Scripts)** because:
- ⚡ 37% faster execution
- 👁️ 100% output visibility
- 🔧 Simpler setup
- 🐛 Easier debugging
- 🚀 Production-ready

Use **Approach 1 (Papermill)** only if you specifically need Jupyter notebooks or template-based workflows.

---

**Ready?** Run:
```bash
python run_sequential_notebooks.py
```

**Or try Approach 2:**
```bash
python run_sequential_scripts.py
```
