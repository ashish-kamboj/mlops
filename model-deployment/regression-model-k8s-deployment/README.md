# Local ML Model Deployment — FastAPI, Docker, MLflow, Minikube

A compact, configurable machine learning pipeline for training a regression model locally with MLflow, containerizing it with Docker, and serving inference via FastAPI. Optional deploy to Kubernetes (Minikube) and ECR.

## Overview

- Data generation, feature engineering, and training in Jupyter notebooks
- Data stored as CSV in root-level `output/` folder with organized subfolders
- MLflow tracking in `output/mlruns/`
- FastAPI inference server (Dockerized)
- Optional push to ECR and deploy to Minikube (Kubernetes)
- YAML configuration for algorithms and hyperparameters

## Project Structure

```
databricks-model-docker-deployment/
├── config/model_config.yaml
├── output/                                  (← root-level, created by notebooks)
│   ├── data/
│   │   └── training_data.csv
│   ├── feature_engineering/
│   │   ├── train.csv
│   │   ├── val.csv
│   │   ├── test.csv
│   │   └── feature_names.json
│   ├── modeling/
│   │   ├── regression_model.pkl
│   │   ├── model_params.json
│   │   └── feature_names.json
│   └── mlruns/                            (← MLflow tracking data)
├── notebooks/
│   ├── 01_data_generation.ipynb         (→ ../output/data/training_data.csv)
│   ├── 02_feature_engineering.ipynb     (→ ../output/feature_engineering/*.csv)
│   ├── 03_model_training.ipynb          (→ ../output/modeling & ../output/mlruns)
│   └── 04_inference.ipynb
├── src/
│   ├── config.py
│   ├── utils.py
│   └── model.py
├── docker/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── docker-compose.yml
│   ├── run.sh
│   └── run.ps1
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── scripts/
│   ├── ecr_push.sh / ecr_push.ps1
│   ├── k8s_deploy_minikube.sh / k8s_deploy_minikube.ps1
│   └── smoke_test_minikube.ps1
├── tests/
│   └── test_api.py
├── tools/
│   └── quickstart.py
└── [Guides]
    ├── MINIKUBE_SETUP_GUIDE.txt
    ├── ECR_PUSH_GUIDE.txt
    └── SETUP_GUIDE.md
```

## Quick Start

### 1) Configure
- Edit [config/model_config.yaml](config/model_config.yaml); MLflow uses `file:../output/mlruns` (root-level).

### 2) Run Notebooks Locally
```bash
pip install -r docker/requirements.txt
pip install jupyter
jupyter notebook
```
Run in order: 01 → 02 → 03. Use 04 to test HTTP inference.
- **01**: Generates `output/data/training_data.csv`
- **02**: Reads CSV, splits, scales → `output/feature_engineering/*.csv`
- **03**: Trains model, logs to `output/mlruns/` → saves `output/modeling/*.pkl`

### 3) Build & Run Docker
Docker reads model from `../output/modeling/` (mounted at `/output/` in container).
Linux/Mac:
```bash
cd docker && chmod +x run.sh && ./run.sh
```
Windows:
```powershell
cd docker; Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process; .\run.ps1
```
Manual:
```bash
cd docker && docker build -t regression-model-inference:latest .
docker-compose up -d
```

### 4) Test API
```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1,1,1,1,1,1,1,1]}'
```

## Optional: Push to ECR
Set environment variables then run the script.
Windows (PowerShell):
```powershell
$env:PUSH_TO_ECR = "true"
$env:ECR_REGION = "us-east-1"
$env:ECR_REGISTRY = "123456789012.dkr.ecr.us-east-1.amazonaws.com"
$env:ECR_REPOSITORY = "regression-model-inference"
./scripts/ecr_push.ps1 -IMAGE_NAME regression-model-inference -IMAGE_TAG latest
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

For detailed steps, see [MINIKUBE_SETUP_GUIDE.txt](MINIKUBE_SETUP_GUIDE.txt). Quick reference:

**Prerequisites:** `minikube` and `kubectl` installed

**Windows (PowerShell):**
```powershell
# Terminal 1: Start Minikube and mount output files
minikube start --driver=docker --cpus=2 --memory=4096
minikube mount (Resolve-Path .\output).Path:/tmp/ml-output

# Terminal 2: Load image, apply manifests, test
minikube image load regression-model-inference:latest
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl port-forward svc/regression-model-service 30080:5000
```

**Linux/Mac:**
```bash
# Terminal 1: Start and mount
minikube start --driver=docker --cpus=2 --memory=4096
minikube mount $(pwd)/output:/tmp/ml-output

# Terminal 2: Deploy and test
minikube image load regression-model-inference:latest
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl port-forward svc/regression-model-service 30080:5000
```

**Test:** `curl http://localhost:30080/health`

## FastAPI Endpoints
- GET `/health`
- GET `/api/v1/info`
- POST `/api/v1/predict`
- POST `/api/v1/predict_batch`
- POST `/api/v1/predict_dataframe`
- GET `/metrics`
- Docs: `/docs`, `/redoc`

## Troubleshooting

**Health check fails:**
- Docker: verify model files exist in `output/modeling/`
- Minikube: verify `minikube mount` is running in another terminal

**Port connection issues:**
- Docker uses port `5000`
- Minikube port-forward uses `30080 → 5000`

**Feature mismatch:**
- Check feature count: `curl http://localhost:5000/api/v1/info`
- Verify CSV columns match expected features from training

---

## Testing

Run the included test client:
```bash
# Test Docker (port 5000)
python tests/test_api.py --url http://localhost:5000

# Test Minikube (port 30080)
python tests/test_api.py --url http://localhost:30080
```

Or check dependencies and workflow:
```bash
python tools/quickstart.py
```

## 📊 Configuration

Edit [config/model_config.yaml](config/model_config.yaml) to customize:

### Data Generation
```yaml
data_generation:
  num_samples: 5000        # Number of training samples
  num_features: 10         # Number of features
  noise_level: 0.1         # Noise level in target
```

### Feature Engineering
```yaml
feature_engineering:
  scaling_method: "standard"      # standard, minmax, robust
  feature_selection:
    enabled: true
    method: "variance"            # variance, mutual_info, correlation
    n_features: 8                 # Number of features to select
```

### Model Training
```yaml
model_training:
  algorithm: "random_forest"      # Algorithm selection
  hyperparameters:
    random_forest:
      n_estimators: 100
      max_depth: 15
      # ... other parameters
```

**Supported Algorithms:**
- `linear_regression` - Simple linear regression
- `random_forest` - Random Forest Regressor
- `xgboost` - XGBoost Regressor
- `gradient_boosting` - Gradient Boosting Regressor

### MLflow Configuration
```yaml
model_training:
  mlflow:
    experiment_name: "ml_regression_experiment"
    run_name: "regression_model_run"
    metrics:
      - "mse"
      - "rmse"
      - "mae"
      - "r2_score"
```

### Docker Configuration
```yaml
docker:
  image_name: "regression-model-inference"
  image_tag: "latest"
  registry: "your-registry.azurecr.io"
  port: 5000
```

## 🔄 Pipeline Execution

### Notebook 01: Data Generation
Generates synthetic regression dataset with specified features and target variable.

**Outputs:**
- `training_data.parquet` - Raw training data
- Stored in: `datafabric_catalog.ml_outputs.training_data`

**Key Features:**
- Configurable number of samples and features
- Automatic train/val/test split
- Metadata columns (dataset_id, created_at, etc.)

### Notebook 02: Feature Engineering
Transforms raw features and prepares them for modeling.

**Outputs:**
- `engineered_features.parquet` - Processed features
- `feature_metadata.json` - Feature information
- Stored in: `datafabric_catalog.ml_outputs.engineered_features`

**Processing Steps:**
- Feature selection (variance, mutual information, correlation)
- Feature scaling (StandardScaler, MinMaxScaler, RobustScaler)
- Optional polynomial feature interactions
- Data splitting (train/val/test)

### Notebook 03: Model Training
Trains regression model with MLflow tracking.

**Outputs:**
- `regression_model.pkl` - Trained model
- `feature_names.json` - Feature list
- `model_params.json` - Model parameters
- MLflow tracking with metrics and artifacts

**MLflow Artifacts:**
- Model (sklearn format)
- Feature importance
- Model parameters
- Training metrics

### Notebook 04: Inference
Tests model predictions on test set.

**Includes:**
- Single sample inference
- Batch inference
- Performance metrics and analysis
- API endpoint simulation
- Inference speed benchmarking

## 🐳 Docker Deployment

### Build Docker Image

**Linux/Mac:**
```bash
cd docker
chmod +x run.sh
./run.sh
```

**Windows (PowerShell):**
```powershell
cd docker
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\run.ps1
```

**Manual build:**
```bash
cd docker
docker build -t regression-model-inference:latest .
```

### Run Container

**Using Docker:**
```bash
docker run -d \
  --name regression-model-container \
  -p 5000:5000 \
  -v /path/to/regression_model.pkl:/app/model/regression_model.pkl:ro \
  -v /path/to/feature_names.json:/app/model/feature_names.json:ro \
  regression-model-inference:latest
```

**Using Docker Compose:**
```bash
cd docker
docker-compose up -d
```

## 🔌 FastAPI Endpoints

FastAPI provides automatic API documentation via Swagger UI and ReDoc:

- **Interactive API Docs**: http://localhost:5000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:5000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:5000/openapi.json

### API Endpoints

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1.0",
  "features_count": 8,
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

#### 2. Model Information
```bash
curl http://localhost:5000/api/v1/info
```

Response:
```json
{
  "model_version": "1.0",
  "model_type": "RandomForestRegressor",
  "features": ["feature_1", "feature_2", ...],
  "features_count": 8,
  "metadata": {...}
}
```

#### 3. Single Prediction

**FastAPI (List Format):**
```bash
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [5.0, 3.5, 2.1, 4.2, 1.8, 3.9, 2.5, 1.2],
    "request_id": "req_001"
  }'
```

Response:
```json
{
  "request_id": "req_001",
  "prediction": 45.67,
  "status": "success",
  "model_version": "1.0",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

#### 4. Batch Prediction
```bash
curl -X POST http://localhost:5000/api/v1/predict_batch \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      [5.0, 3.5, 2.1, 4.2, 1.8, 3.9, 2.5, 1.2],
      [4.2, 2.8, 1.9, 3.8, 1.6, 3.2, 2.1, 0.9]
    ],
    "request_id": "batch_001"
  }'
```

Response:
```json
{
  "request_id": "batch_001",
  "predictions": [45.67, 42.34],
  "count": 2,
  "status": "success",
  "model_version": "1.0",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

#### 5. DataFrame Predictions
```bash
curl -X POST http://localhost:5000/api/v1/predict_dataframe \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "feature_1": 5.0,
        "feature_2": 3.5,
        "feature_3": 2.1,
        "feature_4": 4.2,
        "feature_5": 1.8,
        "feature_6": 3.9,
        "feature_7": 2.5,
        "feature_8": 1.2
      },
      {
        "feature_1": 4.2,
        "feature_2": 2.8,
        ...
      }
    ]
  }'
```

#### 6. Prometheus Metrics
```bash
curl http://localhost:5000/metrics
```

Response (Prometheus format):
```
# HELP model_inference_requests_total Total inference requests
# TYPE model_inference_requests_total counter
model_inference_requests_total 42

# HELP model_inference_predictions_total Total predictions
# TYPE model_inference_predictions_total counter
model_inference_predictions_total 157

# HELP model_inference_errors_total Total inference errors
# TYPE model_inference_errors_total counter
model_inference_errors_total 0

# HELP model_inference_latency_ms Average latency
# TYPE model_inference_latency_ms gauge
model_inference_latency_ms 2.34

# HELP model_inference_throughput_per_sec Predictions per second
# TYPE model_inference_throughput_per_sec gauge
model_inference_throughput_per_sec 425.50
```

#### 7. JSON Metrics
```bash
curl http://localhost:5000/metrics/json
```

Response:
```json
{
  "uptime_seconds": 3600.5,
  "total_requests": 42,
  "total_predictions": 157,
  "total_errors": 0,
  "error_rate": 0.0,
  "avg_latency_ms": 2.34,
  "predictions_per_sec": 425.50
}
```

## 📋 FastAPI Features

### Automatic API Documentation

FastAPI automatically generates interactive API documentation from your Pydantic models:

```python
# Visit these URLs in your browser:
# Swagger UI:  http://localhost:5000/docs
# ReDoc:       http://localhost:5000/redoc
# OpenAPI JSON: http://localhost:5000/openapi.json
```

### Request Validation

All requests are automatically validated:
- Type checking
- Field validation
- Error responses with helpful messages

Example validation error:
```json
{
  "detail": [
    {
      "type": "value_error.number.not_finite",
      "loc": ["body", "features", 0],
      "msg": "ensure this value is finite",
      "input": "NaN"
    }
  ]
}
```

### Async Support

FastAPI's async support improves throughput:
- Non-blocking I/O operations
- Better handling of concurrent requests
- Improved scalability

## 🔄 Notebook Execution

### Running Jupyter Notebooks Locally

#### 1. Install Dependencies
```bash
pip install -r docker/requirements.txt
pip install jupyter notebook
```

#### 2. Start Jupyter
```bash
jupyter notebook
```

#### 3. Execute Notebooks in Order
- `01_data_generation.ipynb` - Create synthetic data
- `02_feature_engineering.ipynb` - Transform features
- `03_model_training.ipynb` - Train model with MLflow
- `04_inference.ipynb` - Test predictions

### Running in Databricks

#### Upload to Databricks Workspace
```bash
# Create directory structure
databricks workspace mkdirs /Repos/username/ml-deployment/notebooks

# Upload notebooks (converted from .py to .ipynb)
for notebook in notebooks/*.ipynb; do
  databricks workspace import --source "$notebook" \
    --destination "/Repos/username/ml-deployment/notebooks/$(basename $notebook)" \
    --language python
done
```

#### Execute as Databricks Job
```python
# Create job configuration
job_config = {
  "name": "ML Training Pipeline",
  "tasks": [
    {
      "task_key": "data_gen",
      "notebook_task": {"notebook_path": "/Repos/.../01_data_generation"}
    },
    {
      "task_key": "feature_eng",
      "depends_on": [{"task_key": "data_gen"}],
      "notebook_task": {"notebook_path": "/Repos/.../02_feature_engineering"}
    },
    {
      "task_key": "model_train",
      "depends_on": [{"task_key": "feature_eng"}],
      "notebook_task": {"notebook_path": "/Repos/.../03_model_training"}
    }
  ]
}

# Submit job
import requests
databricks_url = "https://your-databricks-instance.com"
token = "your-token"
response = requests.post(
  f"{databricks_url}/api/2.1/jobs/create",
  headers={"Authorization": f"Bearer {token}"},
  json=job_config
)
```

## 📈 MLflow Integration

### Access MLflow

In Databricks notebook:
```python
import mlflow

# View all experiments
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"Experiment: {exp.name}, ID: {exp.experiment_id}")

# Search runs
runs = mlflow.search_runs(experiment_names=["ml_regression_experiment"])
print(runs[['params.algorithm', 'metrics.test_rmse']])

# Load model
model = mlflow.sklearn.load_model("runs:/<run_id>/model")
```

### Model Registry

Models are automatically registered in MLflow with:
- **Name**: `regression_model`
- **Stage**: Production/Staging
- **Description**: Model metadata

## 🔧 Customization

### Change Algorithm

In `config/model_config.yaml`:
```yaml
model_training:
  algorithm: "xgboost"  # Changed from random_forest
  hyperparameters:
    xgboost:
      n_estimators: 150
      max_depth: 8
      learning_rate: 0.05
```

### Modify Feature Engineering

```yaml
feature_engineering:
  feature_selection:
    method: "mutual_info"    # Changed method
    n_features: 12           # Select more features
  feature_interaction:
    enabled: true            # Enable polynomial features
```

### Adjust Data Generation

```yaml
data_generation:
  num_samples: 10000         # More samples
  num_features: 15           # More features
  test_size: 0.15            # Different split
```

## 🧪 Testing

### Local Testing

```bash
# Install dependencies
pip install -r docker/requirements.txt

# Run notebooks locally (requires pandas, sklearn, mlflow)
python notebooks/01_data_generation.py
python notebooks/02_feature_engineering.py
python notebooks/03_model_training.py
python notebooks/04_inference.py
```

### Docker API Testing

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test prediction with sample data
python test_api.py

# Check logs
docker logs -f regression-model-container
```

## 📊 Expected Results

### Data Generation
- Training samples: ~3,500
- Validation samples: ~750
- Test samples: ~750
- Features: 10

### Feature Engineering
- Original features: 10
- Selected features: 8 (via variance method)
- After scaling: 8
- Training samples: ~3,500

### Model Training (Random Forest)
- Algorithm: RandomForestRegressor
- Test RMSE: ~0.15-0.25 (depends on noise level)
- Test R²: ~0.85-0.95
- Training time: ~2-5 seconds

### Inference
- Single prediction: ~1-2 ms
- Batch throughput: ~500-1000 samples/sec
- API response time: ~5-10 ms

## 🔐 Production Deployment

### Best Practices

1. **Security**
   - Use Azure Container Registry for private images
   - Implement authentication for API endpoints
   - Use HTTPS for production APIs

2. **Monitoring**
   - Enable Prometheus metrics
   - Set up alerts for model drift
   - Monitor prediction latency

3. **Scaling**
   - Use Kubernetes for orchestration
   - Enable auto-scaling based on load
   - Use load balancer for multiple replicas

4. **Model Versioning**
   - Use MLflow Model Registry
   - Tag models with environment (dev, staging, prod)
   - Maintain model lineage

### Deployment to Databricks Jobs

Create a Databricks Job for periodic retraining:

```python
# In Databricks Job configuration
{
  "name": "ML Pipeline - Train",
  "tasks": [
    {
      "task_key": "data_gen",
      "notebook_task": {
        "notebook_path": "/Repos/username/databricks-model-docker-deployment/notebooks/01_data_generation"
      }
    },
    {
      "task_key": "feature_eng",
      "depends_on": [{"task_key": "data_gen"}],
      "notebook_task": {
        "notebook_path": "/Repos/username/databricks-model-docker-deployment/notebooks/02_feature_engineering"
      }
    },
    {
      "task_key": "model_train",
      "depends_on": [{"task_key": "feature_eng"}],
      "notebook_task": {
        "notebook_path": "/Repos/username/databricks-model-docker-deployment/notebooks/03_model_training"
      }
    }
  ]
}
```

## 🐛 Troubleshooting

### Issue: "Model not loaded" Error

**Solution:**
```bash
# Check if model files are mounted
docker inspect regression-model-container | grep Mounts

# Verify model file exists
ls -la /tmp/regression_model.pkl
ls -la /tmp/feature_names.json

# Check container logs
docker logs -f regression-model-container
```

### Issue: Feature Dimension Mismatch

**Error:** `Expected 8 features, got 10`

**Solution:**
```python
# Verify feature count in request
import json
with open('feature_names.json', 'r') as f:
    features = json.load(f)
    print(f"Expected features: {len(features)}")

# For single prediction, send list with correct length
curl -X POST http://localhost:5000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]}'
```

### Issue: JSON Parsing Error

**Error:** `Invalid JSON in request body`

**Solution:**
```bash
# Use jq to validate JSON
echo '{"features": [1.0, 2.0, 3.0]}' | jq .

# Or use Python
python -m json.tool <<< '{"features": [1.0, 2.0, 3.0]}'
```

### Issue: Connection Refused

**Error:** `Connection refused on localhost:5000`

**Solution:**
```bash
# Check if container is running
docker ps | grep regression-model

# Start container
docker start regression-model-container

# Check Docker logs
docker logs regression-model-container

# Verify port mapping
docker port regression-model-container
```

### Issue: Slow Predictions

**Solution:**
```bash
# Check inference metrics
curl http://localhost:5000/metrics/json | jq '.avg_latency_ms'

# Monitor container resources
docker stats regression-model-container

# Check for model issues
# - Verify model file is not corrupted
# - Check feature count matches training
# - Ensure input data is properly scaled
```

### Issue: Out of Memory

**Error:** `MemoryError` or container killed

**Solution:**
```bash
# Increase Docker memory limit
docker run --memory=4g \
  -d --name regression-model-container \
  regression-model-inference:latest

# Or in docker-compose.yml:
services:
  model-inference:
    deploy:
      resources:
        limits:
          memory: 4G
```

### Issue: MLflow Tracking Errors

**Error:** `Could not connect to MLflow tracking server`

**Solution:**
```python
# In Databricks notebook, set tracking URI
import mlflow
mlflow.set_tracking_uri("databricks")  # Use Databricks MLflow

# Or specify explicit URI
mlflow.set_tracking_uri("http://localhost:5000")
```

### Issue: Docker Build Fails

**Solution:**
```bash
# Check Docker daemon is running
docker ps

# Clear build cache
docker build --no-cache -t regression-model-inference:latest docker/

# Check for syntax errors in Dockerfile
docker build --progress=plain docker/

# View detailed error logs
docker buildx build --progress=plain docker/
```

### Issue: Batch Requests Timeout

**Error:** Request hangs or times out on large batches

**Solution:**
```python
# Split large batches into smaller chunks
batch_size = 100
for i in range(0, len(features), batch_size):
    batch = features[i:i+batch_size]
    response = requests.post(
        "http://localhost:5000/api/v1/predict_batch",
        json={"features": batch}
    )
    print(f"Batch {i//batch_size + 1}: {len(response.json()['predictions'])} predictions")
```

### Issue: OpenAPI Docs Not Loading

**Error:** `/docs` returns 404 or blank page

**Solution:**
```bash
# Verify FastAPI is running correctly
curl http://localhost:5000/openapi.json

# Check for JavaScript console errors
# Clear browser cache and reload
# Reload: http://localhost:5000/docs
```

## 📚 Additional Resources

- [Databricks Documentation](https://docs.databricks.com/)
- [MLflow Documentation](https://mlflow.org/docs/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

To extend this project:

1. Add new algorithms in `config.model_training.hyperparameters`
2. Implement new feature engineering methods in `src/utils.py`
3. Add new API endpoints in `docker/app.py`
4. Update configuration schema in `config/model_config.yaml`

## ❓ Questions & Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the configuration documentation
3. Check Docker and Databricks logs
4. Consult relevant documentation links

---