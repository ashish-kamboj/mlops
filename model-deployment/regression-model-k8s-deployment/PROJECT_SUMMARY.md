# Project Summary (Local-Only)

## Overview
Production-ready ML regression pipeline with local notebooks, MLflow file store, FastAPI Docker service, optional ECR push, and Minikube deployment.

## File Structure
```
databricks-model-docker-deployment/
├── config/model_config.yaml
├── notebooks/{01..04}.ipynb
├── src/{config.py, utils.py, model.py}
├── docker/{app.py, Dockerfile, requirements.txt, docker-compose.yml, run.*}
├── k8s/{deployment.yaml, service.yaml}
├── scripts/{ecr_push.*, k8s_deploy_minikube.*, smoke_test_minikube.ps1}
├── tests/test_api.py
├── tools/quickstart.py
├── output/{data, feature_engineering, modeling, mlruns}    (← created by notebooks)
└── [Guides] README.md, SETUP_GUIDE.md, ARCHITECTURE.md, MINIKUBE_SETUP_GUIDE.txt, ECR_PUSH_GUIDE.txt
```

## Key Features
- Data generation → feature engineering → model training (Jupyter, CSV-based)
- MLflow tracking (local file store: `output/mlruns/`)
- FastAPI inference (Uvicorn) with `/health`, `/predict`, `/info`, `/metrics`
- Dockerized service; Compose for local run
- Optional ECR push (PowerShell/Bash scripts)
- Minikube manifests and deploy scripts
- Test client and dependency checker included

## Quick Start
- Edit [config/model_config.yaml](config/model_config.yaml)
- Run notebooks 01→02→03 locally
- Build & run Docker: [docker/run.ps1](docker/run.ps1) or [docker/run.sh](docker/run.sh)
- Test API: `python tests/test_api.py` or http://localhost:5000/health
- Optional deploy: Follow [MINIKUBE_SETUP_GUIDE.txt](MINIKUBE_SETUP_GUIDE.txt) or run `scripts/k8s_deploy_minikube.ps1`

## Expected Performance
- Training: seconds (RandomForest default)
- Inference: single ms-level; batch supported

## Dependencies
- pandas, numpy, scikit-learn, joblib
- mlflow (file store), fastapi, uvicorn, pydantic, prometheus-client

## Next Steps
- Customize algorithms/hyperparameters in YAML
- Push image to ECR if needed
- Scale via Kubernetes replicas

---
