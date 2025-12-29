# Project File Index

Quick reference for where things are and what they do.

## 📂 Top-Level Files

| File | Purpose |
|------|---------|
| `README.md` | Start here — overview and quick start |
| `SETUP_GUIDE.md` | Step-by-step local setup |
| `ARCHITECTURE.md` | System design and data flow |
| `MINIKUBE_SETUP_GUIDE.txt` | Detailed Minikube setup |
| `ECR_PUSH_GUIDE.txt` | Push Docker image to AWS ECR |
| `requirements.txt` | Python dependencies (development) |
| `config/model_config.yaml` | Central configuration (algorithms, parameters) |

## 📁 Main Directories

### `/notebooks` — Training Pipeline
Run these in order (local, via Jupyter):

1. **01_data_generation.ipynb** — Generates synthetic data → `../output/data/training_data.csv`
2. **02_feature_engineering.ipynb** — Splits and scales → `../output/feature_engineering/*.csv`
3. **03_model_training.ipynb** — Trains model → `../output/modeling/regression_model.pkl`, logs to `../output/mlruns/`
4. **04_inference.ipynb** — Test predictions locally or via API

### `/src` — Reusable Code
- **config.py** — Load YAML configuration
- **utils.py** — Utilities: splitting, scaling, metrics
- **model.py** — Model building and MLflow

(Used by notebooks and Docker app)

### `/docker` — API Server
- **app.py** — FastAPI inference server
- **Dockerfile** — Container definition
- **requirements.txt** — Container Python packages
- **docker-compose.yml** — Run with volume mounts
- **run.sh** / **run.ps1** — Quick build/run scripts

### `/k8s` — Kubernetes (Minikube)
- **deployment.yaml** — Pod definition
- **service.yaml** — Service exposes port 30080

### `/scripts` — Automation
- **k8s_deploy_minikube.ps1** / **.sh** — Deploy to Minikube
- **smoke_test_minikube.ps1** — End-to-end test
- **ecr_push.ps1** / **.sh** — Push to AWS ECR

### `/tests` — Testing
- **test_api.py** — Test API endpoints
  - Usage: `python tests/test_api.py --url http://localhost:5000`

### `/tools` — Helpers
- **quickstart.py** — Check dependencies and show workflow
  - Usage: `python tools/quickstart.py`

### `/output` — Generated Artifacts (created during notebook runs)
```
output/
├── data/
│   └── training_data.csv
├── feature_engineering/
│   ├── train.csv
│   ├── val.csv
│   ├── test.csv
│   └── feature_names.json
├── modeling/
│   ├── regression_model.pkl
│   ├── model_params.json
│   └── feature_names.json
└── mlruns/
    └── (MLflow run directories)
```

## 🔄 Data & Execution Flow

```
Local Development (Jupyter)
  01_data_generation.ipynb
    ↓
  output/data/training_data.csv
    ↓
  02_feature_engineering.ipynb
    ↓
  output/feature_engineering/{train,val,test}.csv
    ↓
  03_model_training.ipynb
    ↓
  output/modeling/regression_model.pkl
  output/mlruns/ (MLflow logs)

Docker & Kubernetes
  docker/app.py reads output/modeling/*.pkl
    ↓
  Serves: http://localhost:5000/health, /predict, etc.
    ↓
  (Optional) Deploy to Minikube/K8s
  Serves: http://localhost:30080/health, /predict, etc.
```

## 💡 Quick Answers

**Where to change the model algorithm?**
→ Edit `config/model_config.yaml`, section `model_training.algorithm`

**Where to change data generation?**
→ Edit `config/model_config.yaml`, section `data_generation`

**Where to add new API endpoints?**
→ Edit `docker/app.py`, add new `@app.get()` or `@app.post()` function

**Where to add utilities?**
→ Edit `src/utils.py`

**How to test locally?**
→ `python tests/test_api.py --url http://localhost:5000` (after Docker is running)

**How to deploy to Minikube?**
→ Follow [MINIKUBE_SETUP_GUIDE.txt](MINIKUBE_SETUP_GUIDE.txt) or run `scripts/k8s_deploy_minikube.ps1` (Windows)

**How to push to ECR?**
→ Follow [ECR_PUSH_GUIDE.txt](ECR_PUSH_GUIDE.txt)

## 📚 Reading Order for New Users

1. **README.md** — Understand what this project does
2. **SETUP_GUIDE.md** — Get everything installed
3. **ARCHITECTURE.md** — Learn how pieces fit together
4. **config/model_config.yaml** — See what's configurable
5. **notebooks/** — Study the code in order (01 → 04)
6. **docker/app.py** — Understand the API server
7. **MINIKUBE_SETUP_GUIDE.txt** — When ready to deploy to K8s

## 🎯 Common Tasks

### Run the Full Pipeline Locally
```bash
pip install -r docker/requirements.txt
pip install jupyter
jupyter notebook
# Run notebooks 01, 02, 03 in order
cd docker && docker-compose up -d
python tests/test_api.py
```

### Deploy to Minikube
```bash
minikube start --driver=docker --cpus=2 --memory=4096
minikube mount $(pwd)/output:/tmp/ml-output  # Terminal 1
./scripts/k8s_deploy_minikube.sh               # Terminal 2
python tests/test_api.py --url http://localhost:30080
```

### Push to ECR and Deploy
```bash
export PUSH_TO_ECR=true
export ECR_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com
./scripts/ecr_push.ps1

# Update k8s/deployment.yaml with ECR image URL
# Deploy to your cluster
```

## 🗂️ What to Edit vs. What NOT to Edit

**Edit these (usually):**
- `config/model_config.yaml` — Change algorithm, parameters, data size
- `notebooks/*.ipynb` — Custom data processing, features
- `docker/app.py` — Add endpoints, change inference logic
- `k8s/deployment.yaml` — Replicas, resource limits (for cloud)

**Don't edit (usually):**
- `src/config.py` — Edit config.yaml instead
- `src/utils.py` — Unless adding new utilities
- `docker/Dockerfile` — Unless adding packages
- `.gitignore` — Unless excluding new file types

## 📦 What to Commit to Git

**Commit:**
- Source code (`src/`, `notebooks/`, `docker/`, `k8s/`, `scripts/`, `tools/`, `tests/`)
- Configuration (`config/model_config.yaml`)
- Documentation (.md files, .txt guides)
- `requirements.txt`

**Don't commit:**
- `output/` directory (data, models, MLflow runs)
- `.env` or credentials files
- `__pycache__`, `.pyc` files
- `venv/` or virtual environment

(Covered by `.gitignore`)

---