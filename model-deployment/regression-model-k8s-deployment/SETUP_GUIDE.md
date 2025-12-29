# Local Setup Guide (FastAPI + Docker + MLflow + Minikube)

Concise steps to set up and run the project locally. No Databricks required.

## Prerequisites
- Python 3.9+
- Docker Desktop
- Git
- Optional: Minikube + kubectl; AWS CLI (for ECR)

## 1) Get the Code
```bash
git clone https://github.com/your-org/databricks-model-docker-deployment.git
cd databricks-model-docker-deployment
```

## 2) Create Virtual Env and Install
Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r docker/requirements.txt
pip install jupyter
python tools/quickstart.py   # Check setup
```
Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r docker/requirements.txt
pip install jupyter
python tools/quickstart.py   # Check setup
```

## 3) Configure
Edit [config/model_config.yaml](config/model_config.yaml). MLflow defaults to `file:./mlruns`.

## 4) Run Notebooks
```bash
jupyter notebook
```
Execute: 01_data_generation → 02_feature_engineering → 03_model_training.
- **01**: Generates root-level `output/data/training_data.csv` (5000 samples)
- **02**: Reads CSV, splits, scales → `output/feature_engineering/train.csv`, `val.csv`, `test.csv`
- **03**: Trains model, logs to root-level `output/mlruns/`, saves `output/modeling/regression_model.pkl`

## 5) Build & Run Docker
Windows:
```powershell
cd docker; Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\run.ps1
```
Linux/Mac:
```bash
cd docker && chmod +x run.sh && ./run.sh
```
Manual run:
```bash
cd docker && docker build -t regression-model-inference:latest .
docker-compose up -d
```
Docker mounts root-level `output/` to `/output/` in container.

## 6) Test API
```bash
python tests/test_api.py
```
Output should show tests passing. Or use curl directly:
```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/v1/predict -H "Content-Type: application/json" -d '{"features": [1,1,1,1,1,1,1,1]}'
```

## Optional: Push to ECR
Windows:
```powershell
$env:PUSH_TO_ECR = "true"
$env:ECR_REGION = "us-east-1"
$env:ECR_REGISTRY = "123456789012.dkr.ecr.us-east-1.amazonaws.com"
$env:ECR_REPOSITORY = "regression-model-inference"
./scripts/ecr_push.ps1
```
Linux/Mac:
```bash
export PUSH_TO_ECR=true
export ECR_REGION=us-east-1
export ECR_REGISTRY=123456789012.dkr.ecr.us-east-1.amazonaws.com
export ECR_REPOSITORY=regression-model-inference
./scripts/ecr_push.sh
```

## Optional: Deploy to Minikube
Windows:
```powershell
./scripts/k8s_deploy_minikube.ps1
# Access: http://localhost:30080/health
```
Linux/Mac:
```bash
./scripts/k8s_deploy_minikube.sh
# Access: http://localhost:30080/health
```

## Troubleshooting
- Model not found: ensure root-level `output/modeling/regression_model.pkl` exists after notebook 03.
- Feature count mismatch: use `features_count` from `/health`.
- Connection refused: verify ports `5000` (Docker) or `30080` (Minikube).
- Data not saving: notebooks write to `../output/` subfolders; ensure write permissions.

## Folder Structure Overview
```
output/
├── data/              (raw training data)
├── feature_engineering/  (split, scaled datasets)
├── modeling/          (trained model + metadata)
└── mlruns/            (MLflow experiment tracking)
```

Refer to [README.md](README.md) for details and endpoint list.