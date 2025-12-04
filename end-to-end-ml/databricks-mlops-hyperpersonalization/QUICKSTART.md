# Quick Start Guide
## Next Best Product Recommendation MLOps Pipeline

Get started with the pipeline in under 5 minutes!

---

## 🚀 For Local Development (Quickest Start)

### 1. Install Dependencies (1 minute)

```bash
# Clone and navigate to project
cd databricks-mlops-hyperpersonalization

# Install requirements
pip install -r requirements.txt
```

### 2. Verify Configuration (30 seconds)

Check `config/config.yaml` has:
```yaml
environment:
  mode: "local"
data_source:
  type: "csv"
```

### 3. Run the Pipeline (3 minutes)

```bash
# Generate data
python notebooks/00_data_generation.py

# Train model
python notebooks/03_model_training.py

# Make predictions
python notebooks/05_batch_inference.py
```

**Done!** Check `outputs/` folder for results.

---

## 📊 For Databricks (Full Production Setup)

### 1. Upload to Databricks (2 minutes)

1. Go to **Workspace** → **Repos** → **Add Repo**
2. Clone this repository
3. Or upload notebooks manually to `/Users/<you>/next-best-product/`

### 2. Update Config (1 minute)

Edit `config/config.yaml`:
```yaml
environment:
  mode: "databricks"
data_source:
  type: "unity_catalog"
mlflow:
  databricks:
    experiment_name: "/Users/YOUR-EMAIL@company.com/next-best-product"
```

### 3. Create Unity Catalog (1 minute)

Run in SQL notebook:
```sql
CREATE CATALOG IF NOT EXISTS data_catalog;
CREATE SCHEMA IF NOT EXISTS data_catalog.customer_hc;
CREATE SCHEMA IF NOT EXISTS data_catalog.ml_outputs;
```

### 4. Run Notebooks (5 minutes)

Run in order:
1. `00_data_generation.py` → Creates tables
2. `02_feature_engineering.py` → Creates features
3. `03_model_training.py` → Trains model
4. `04_model_deployment.py` → Deploys model
5. `05_batch_inference.py` → Generates predictions
6. `07_local_realtime_inference.py` OR `07_databricks_realtime_inference.py` → Test real-time

**Done!** Check Unity Catalog for tables and MLflow for experiments.

---

## 🎯 What You Get

After running the pipeline:

✅ **Synthetic Data**: 5,000 customers, 50,000 transactions, 8,000 accounts

✅ **Features**: 50+ engineered features per customer

✅ **Model**: Random Forest classifier with 75%+ accuracy

✅ **Predictions**: Top-3 product recommendations per customer

✅ **Monitoring**: Drift detection and quality metrics

✅ **Outputs**:
- `outputs/eda/` → Data analysis charts
- `outputs/models/` → Model artifacts
- `outputs/monitoring/` → Monitoring reports
- `outputs/predictions/` → Batch predictions
- `data/processed/` → Feature tables and predictions (created at runtime)
- MLflow UI → Experiment tracking

---

## 📈 View Results

### Local Mode

```bash
# View MLflow experiments
mlflow ui --backend-store-uri ./mlruns

# Open: http://localhost:5000
```

Check files:
- `outputs/eda/` - EDA visualizations
- `data/processed/product_recommendations.csv` - Predictions

### Databricks Mode

1. **Experiments**: Machine Learning → Experiments
2. **Models**: Machine Learning → Models
3. **Data**: Data → Unity Catalog → datafabric_catalog

---

## 🔍 Key Notebooks Explained

| Notebook | Purpose | Runtime | Output |
|----------|---------|---------|--------|
| `00_data_generation` | Create synthetic data | 1-2 min | Tables/CSVs |
| `01_eda` | Data analysis | 2-3 min | Charts & stats |
| `02_feature_engineering` | Create features | 2-3 min | Feature table |
| `03_model_training` | Train ML model | 2-5 min | Model in MLflow |
| `04a_model_registration` | Register model | 1 min | Model in registry |
| `04b_set_model_alias_to_staging` | Set staging alias | <1 min | Alias updated |
| `04c_set_model_alias_to_production` | Set production alias | <1 min | Alias updated |
| `04d_model_deployment` | Deploy endpoint | 8-10 min | Endpoint created |
| `05_model_monitoring` | Check model health | 1-2 min | Monitoring reports |
| `06_Batch_inference` | Predict all customers | 1-2 min | Recommendations |
| `07_local_realtime_inference` | Test local API | 1 min | Sample predictions |
| `07_databricks_realtime_inference` | Test Databricks API | 1 min | Sample predictions |

---

## ⚡ Pro Tips

### Faster Development
```bash
# Skip EDA during development
# Skip monitoring initially
# Run core pipeline: 00 → 02 → 03 → 04a → 06
```

### Debug Issues
```powershell
# View specific outputs
Get-ChildItem outputs\eda\
Get-ChildItem outputs\models\
```

### Customize
```yaml
# In config/config.yaml

# Use smaller data for testing
# Adjust in data generation: n_customers=500

# Try different algorithms
model:
  algorithm: "logistic_regression"  # or "random_forest"

# Change top-K recommendations
deployment:
  batch_inference:
    top_k_recommendations: 5  # default is 3
```

---

## 🆘 Common Issues

**Issue**: `ModuleNotFoundError: No module named 'utils'`
```python
# Add to notebook top:
import sys
sys.path.append('../')
```

**Issue**: CSV files not found
```bash
# Check config points to correct paths
# Or run data generation first
python notebooks/00_data_generation.py
```

**Issue**: MLflow experiment not found
```yaml
# Update experiment path in config.yaml
# For local: use "./mlruns"
# For Databricks: use "/Users/your-email/..."
```

---

## 📚 Learn More

- **Full Documentation**: See [README.md](README.md)
- **Detailed Setup**: See [SETUP.md](SETUP.md)
- **Configuration**: See [config/config.yaml](config/config.yaml)

---

## ✅ Verification Checklist

After running, verify:

- [ ] Data generated in `data/raw/` or Unity Catalog
- [ ] Features created in `data/processed/` or Feature Store
- [ ] Model visible in MLflow UI
- [ ] Model registered in Unity Catalog (if using Databricks)
- [ ] Model aliases set (staging/production)
- [ ] Predictions in `product_recommendations.csv`
- [ ] EDA charts in `outputs/eda/`

---

**Next Steps**:
1. Review EDA outputs to understand patterns
2. Experiment with different models
3. Add your own custom features
4. Deploy to Databricks for production use

---

**Questions?** Check [SETUP.md](SETUP.md) for detailed troubleshooting.
