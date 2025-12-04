# Detailed Setup Instructions
## Next Best Product Recommendation - MLOps Pipeline

This guide provides step-by-step instructions for setting up and running the MLOps pipeline in both **Local** and **Databricks** environments.

---

## 🎯 Setup Options

Choose your setup based on your environment:

- **Option 1**: [Local Development Setup](#option-1-local-development-setup) (For testing and development)
- **Option 2**: [Databricks Production Setup](#option-2-databricks-production-setup) (For production deployment)

---

## Option 1: Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- 8GB RAM minimum
- 2GB free disk space

### Step 1: Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd databricks-mlops-hyperpersonalization

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure for Local Mode

Edit `config/config.yaml`:

```yaml
# Environment Settings
environment:
  mode: "local"  # IMPORTANT: Set to "local"
  
# Data Source Configuration
data_source:
  type: "csv"  # IMPORTANT: Set to "csv"
```

### Step 3: Run the Pipeline

```bash
# Step 1: Generate synthetic data
jupyter notebook notebooks/00_data_generation.ipynb

# Step 2: Perform EDA
jupyter notebook notebooks/01_eda.ipynb

# Step 3: Create features
jupyter notebook notebooks/02_feature_engineering.ipynb

# Step 4: Train model
jupyter notebook notebooks/03_model_training.ipynb

# Step 5: Register and deploy model (run in sequence)
jupyter notebook notebooks/04a_model_registration.ipynb
jupyter notebook notebooks/04b_set_model_alias_to_staging.ipynb
jupyter notebook notebooks/04c_set_model_alias_to_production.ipynb
jupyter notebook notebooks/04d_model_deployment.ipynb

# Step 6: Monitor model
jupyter notebook notebooks/05_model_monitoring.ipynb

# Step 7: Run batch inference
jupyter notebook notebooks/06_Batch_inference.ipynb

# Step 8: Test real-time inference (choose based on mode)
jupyter notebook notebooks/07_local_realtime_inference.ipynb
# OR
jupyter notebook notebooks/07_databricks_realtime_inference.ipynb
```

### Step 4: Review Outputs

Check the following directories for outputs:

```
outputs/
├── eda/              # EDA visualizations and statistics
├── models/           # Model artifacts
├── monitoring/       # Monitoring reports
└── predictions/      # Batch predictions

mlruns/              # MLflow experiments (created at project root)

data/                # Created at runtime
├── raw/              # Synthetic data (CSV)
└── processed/        # Processed features and predictions
```

### Step 5: View MLflow UI (Optional)

```bash
# Start MLflow UI
mlflow ui --backend-store-uri ./mlruns

# Open browser to: http://localhost:5000
```

---

## Option 2: Databricks Production Setup

### Prerequisites

- Databricks workspace (AWS, Azure, or GCP)
- Unity Catalog enabled
- Cluster with Databricks Runtime 14.x+ (ML recommended)
- Permissions to create tables, models, and jobs

### Step 1: Create Unity Catalog Structure

Run this in a Databricks SQL notebook:

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS data_catalog;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS data_catalog.customer_hc;
CREATE SCHEMA IF NOT EXISTS data_catalog.ml_outputs;
CREATE SCHEMA IF NOT EXISTS data_catalog.feature_store;
CREATE SCHEMA IF NOT EXISTS data_catalog.ml_models;

-- Grant permissions (adjust as needed)
GRANT USE CATALOG ON CATALOG data_catalog TO `your_group`;
GRANT ALL PRIVILEGES ON SCHEMA data_catalog.customer_hc TO `your_group`;
GRANT ALL PRIVILEGES ON SCHEMA data_catalog.ml_outputs TO `your_group`;
```

### Step 2: Upload Project Files

#### Option A: Using Databricks Repos (Recommended)

1. Go to **Workspace** → **Repos**
2. Click **Add Repo**
3. Enter your Git repository URL
4. Clone the repository

#### Option B: Manual Upload

1. Create a folder in Workspace: `/Users/<your-email>/next-best-product-mlops`
2. Upload all files from `notebooks/` directory
3. Upload `config/` directory
4. Upload `utils/` directory

### Step 3: Configure for Databricks Mode

Edit `config/config.yaml`:

```yaml
# Environment Settings
environment:
  mode: "databricks"  # IMPORTANT: Set to "databricks"
  
# Data Source Configuration
data_source:
  type: "unity_catalog"  # IMPORTANT: Set to "unity_catalog"
  
  unity_catalog:
    catalog: "data_catalog"  # Your catalog name
    schema: "customer_hc"
    output_schema: "ml_outputs"

# MLflow Configuration
mlflow:
  databricks:
    tracking_uri: "databricks"
    experiment_name: "/Users/your-email@company.com/next-best-product-recommendation"  # Update with your email
    model_registry_uri: "databricks-uc"
    registered_model_name: "data_catalog.ml_models.next_best_product_model"
```

### Step 4: Create Databricks Cluster

**Cluster Configuration:**

```yaml
Cluster Name: mlops-pipeline-cluster
Databricks Runtime: 14.3 LTS ML
Node Type: Standard_DS3_v2 (or equivalent)
Workers: 2-8 (auto-scaling)

Libraries to Install:
- evidently==0.4.10
- pyyaml==6.0.1
```

**Via UI:**
1. Go to **Compute** → **Create Cluster**
2. Set cluster name and runtime
3. Under **Libraries**, install the required packages
4. Click **Create Cluster**

### Step 5: Run Notebooks in Order

1. **00_data_generation.ipynb**
   - Attach to cluster
   - Run all cells
   - Verify tables created in Unity Catalog

2. **01_eda.ipynb**
   - Run all cells
   - Download EDA outputs if needed

3. **02_feature_engineering.ipynb**
   - Creates feature table
   - Registers to Feature Store

4. **03_model_training.ipynb**
   - Trains model
   - Logs to MLflow
   - Note the Run ID

5. **04a_model_registration.ipynb**
   - Registers model to Unity Catalog
   - Creates model in registry

6. **04b_set_model_alias_to_staging.ipynb**
   - Sets model alias to "staging"
   - Validates gating thresholds (if configured)

7. **04c_set_model_alias_to_production.ipynb**
   - Sets model alias to "production"
   - Requires manual approval (if configured)

8. **04d_model_deployment.ipynb**
   - Creates serving endpoint
   - Deploys production model

9. **05_model_monitoring.ipynb**
   - Creates monitoring reports
   - Detects drift

10. **06_Batch_inference.ipynb**
    - Generates predictions for all customers

11. **07_local_realtime_inference.ipynb** OR **07_databricks_realtime_inference.ipynb**
    - Tests real-time endpoint

---

## 🔧 Troubleshooting

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'utils'`

**Solution**:
```python
# Add this at the top of each notebook
import sys
import os
sys.path.append(os.path.abspath('../'))
```

### Issue: Unity Catalog Access Denied

**Problem**: `PermissionDeniedException`

**Solution**:
1. Check your Unity Catalog permissions
2. Run: `GRANT USE CATALOG ON CATALOG home_credit_catalog TO <your_user>`
3. Verify catalog and schema exist

### Issue: MLflow Experiment Not Found

**Problem**: Experiment path not accessible

**Solution**:
1. Update experiment name in `config.yaml` to your workspace path
2. Ensure path starts with `/Users/<your-email>/`

### Issue: Feature Store Registration Failed

**Problem**: Feature Store unavailable

**Solution**:
1. Ensure Databricks Runtime is ML version
2. Set `feature_store.enabled: false` in config for local mode
3. Check Unity Catalog permissions

### Issue: Model Serving Endpoint Creation Failed

**Problem**: Endpoint API error

**Solution**:
1. Model serving requires specific workspace tiers
2. Create endpoint manually via UI: **Machine Learning** → **Serving**
3. Or skip endpoint creation and use batch inference only

---

## 📊 Validation Checklist

After setup, verify:

- [ ] All notebooks run without errors
- [ ] Data tables created in Unity Catalog (or CSV files locally)
- [ ] MLflow experiments visible in UI
- [ ] Model registered in Model Registry
- [ ] Features available in Feature Store (Databricks)
- [ ] Predictions saved to output tables
- [ ] Monitoring reports generated
- [ ] EDA visualizations created

---

## 🎓 Best Practices

### For Local Development
1. Use small data samples for quick iteration
2. Comment out Feature Store code
3. Use local MLflow tracking
4. Test notebooks individually before workflow

### For Databricks Production
1. Use Unity Catalog for all tables
2. Enable Feature Store
3. Tag all resources appropriately
4. Configure monitoring and alerts

---

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review Databricks documentation: https://docs.databricks.com
3. Check MLflow documentation: https://mlflow.org/docs/latest
4. Review notebook outputs and logs

---

## 🚀 Next Steps

After successful setup:

1. **Customize for Your Data**: Replace synthetic data with real data
2. **Tune Hyperparameters**: Adjust model parameters in `config.yaml`
3. **Add Custom Features**: Extend `utils/feature_engineering.py`
4. **Set Up Monitoring Alerts**: Integrate with your alerting system
5. **Deploy API**: Create production serving endpoint
6. **Automate Pipeline**: Set up Databricks jobs for scheduled execution

---
