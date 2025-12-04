# Project Guide: Next Best Product Recommendation MLOps Pipeline

## 📋 Overview

This project implements an end-to-end MLOps pipeline for Next Best Product Recommendation using Databricks. It demonstrates complete ML lifecycle from data generation to model monitoring with both local and Databricks execution modes.

**Business Use Case:** Recommend the next best banking product to customers based on their profile, transaction history, and behavioral patterns.

---

## 🏗️ Project Structure

```
home-credit-hyperpersonalization-poc/
│
├── config/
│   └── config.yaml                    # Central configuration
│
├── utils/                             # Reusable utility modules
│   ├── common_utils.py               # Logging, config, Spark session
│   ├── data_loader.py                # Data loading/saving
│   ├── feature_engineering.py        # Feature creation
│   ├── model_training.py             # Model training & evaluation
│   ├── model_deployment.py           # Deployment utilities
│   ├── model_monitoring.py           # Monitoring & drift detection
│   └── eda_utils.py                  # EDA helper functions
│
├── notebooks/                         # Execution pipeline (run in order)
│   ├── 00_data_generation.ipynb      # Generate synthetic data
│   ├── 01_eda.ipynb                  # Exploratory data analysis
│   ├── 02_feature_engineering.ipynb  # Feature creation
│   ├── 03_model_training.ipynb       # Model training & MLflow
│   ├── 04a_model_registration.ipynb  # Register model to Unity Catalog
│   ├── 04b_set_model_alias_to_staging.ipynb  # Set model alias to staging
│   ├── 04c_set_model_alias_to_production.ipynb # Set model alias to production
│   ├── 04d_model_deployment.ipynb    # Deploy model endpoint
│   ├── 05_model_monitoring.ipynb     # Model monitoring
│   ├── 06_Batch_inference.ipynb      # Batch predictions
│   ├── 07_local_realtime_inference.ipynb        # Local real-time inference
│   └── 07_databricks_realtime_inference.ipynb   # Databricks real-time inference
│
├── data/                              # Created at runtime
│   ├── raw/                          # Raw CSV files (generated)
│   └── processed/                    # Processed features & predictions
│
├── outputs/                           # Output directories
│   ├── eda/                          # EDA results
│   ├── models/                       # Model artifacts
│   ├── monitoring/                   # Monitoring reports
│   └── predictions/                  # Prediction outputs
│
├── requirements.txt                   # Python dependencies
├── README.md                          # Main documentation
├── SETUP.md                          # Setup instructions
├── QUICKSTART.md                     # Quick start guide
├── ER_diagram.txt                    # Database schema
└── Table_DDL.txt                     # SQL DDL statements
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 8GB RAM minimum
- 2GB free disk space

### Installation

```powershell
# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `config/config.yaml` for your environment:

```yaml
# For local development
environment:
  mode: "local"

data_source:
  type: "csv"

# For Databricks production
environment:
  mode: "databricks"

data_source:
  type: "unity_catalog"
```

### Run Pipeline

Execute notebooks in sequence:

```powershell
# 1. Generate data
jupyter notebook notebooks/00_data_generation.ipynb

# 2. Run EDA
jupyter notebook notebooks/01_eda.ipynb

# 3. Create features
jupyter notebook notebooks/02_feature_engineering.ipynb

# 4. Train model
jupyter notebook notebooks/03_model_training.ipynb

# 5. Deploy model
jupyter notebook notebooks/04_model_deployment.ipynb

# 6. Run batch inference
jupyter notebook notebooks/05_batch_inference.ipynb

# 7. Monitor model
jupyter notebook notebooks/06_model_monitoring.ipynb

# 8a. Test real-time inference (Local mode)
jupyter notebook notebooks/07_local_realtime_inference.ipynb

# 8b. Test real-time inference (Databricks mode)
jupyter notebook notebooks/07_databricks_realtime_inference.ipynb
```

---

## 📊 Data Flow

### Training Phase

```
00_data_generation.ipynb
    ↓ Generates
data/raw/*.csv (9 tables: party, customer, account, transaction, etc.)
    ↓ Reads
02_feature_engineering.ipynb
    ↓ Creates
data/processed/customer_features.csv (50+ features)
data/processed/customer_targets.csv
    ↓ Reads
03_model_training.ipynb
    ↓ Filters to customers with target (~3,500)
    ↓ Splits 80-20
    ↓ Train: ~2,800 | Test: ~700
    ↓ Trains & Evaluates
    ↓ Logs to
MLflow (mlruns/ or Databricks)
    ↓ Registers via
04a_model_registration.ipynb
    ↓ Stages via
04b_set_model_alias_to_staging.ipynb
04c_set_model_alias_to_production.ipynb
```

### Inference Phase

```
04d_model_deployment.ipynb
    ↓ Deploys model
Model Serving Endpoint
    ↓
06_Batch_inference.ipynb
    ↓ Loads features
data/processed/customer_features.csv
    ↓ Filters to unseen customers (~1,500 without target)
    ↓ Loads model
Model Registry
    ↓ Generates predictions
data/processed/product_recommendations.csv
    ↓
05_model_monitoring.ipynb
    ↓ Monitors
Feature drift, data quality, model performance
```

---

## 🔑 Key Features

### 1. Dual-Mode Execution
- **Local Mode**: Uses CSV files and local MLflow
- **Databricks Mode**: Uses Unity Catalog and Databricks MLflow
- Switch modes by changing `config.yaml`

### 2. MLflow Integration
- Automatic experiment tracking
- Model versioning and registry
- Parameter and metric logging
- Model artifacts storage

### 3. Feature Engineering
Creates 50+ features across 5 categories:
- **Demographic**: Age, tenure, location
- **Account**: Account counts, balances, interest rates
- **Transaction**: Frequency, recency, amounts
- **Communication**: Engagement metrics
- **Behavioral**: Product diversity, account patterns

### 4. Model Training
- Algorithm: Random Forest Classifier (configurable)
- Evaluation metrics: Accuracy, Precision, Recall, F1, ROC-AUC
- Top-K accuracy: Top-1, Top-3, Top-5
- Feature importance analysis
- Train-test split: 80-20 with stratification

### 5. Batch Inference
- Filters to unseen customers (not used in training)
- Generates top-K product recommendations
- Configurable recommendation count
- Saves predictions with confidence scores

### 6. Model Monitoring
- Feature drift detection (Kolmogorov-Smirnov test)
- Data quality metrics
- Model performance tracking
- Prediction distribution analysis

---

## ⚙️ Configuration Guide

### Environment Settings

```yaml
environment:
  mode: "local"  # or "databricks"
  log_level: "INFO"
```

### Data Source

```yaml
data_source:
  type: "csv"  # or "unity_catalog"
  
  csv:
    input_path: "./data/raw"         # Created when notebooks run
    output_path: "./data/processed"  # Created when notebooks run
  
  unity_catalog:
    catalog: "home_credit_catalog"
    schema: "banking_data"
    output_schema: "ml_outputs"
```

### MLflow

```yaml
mlflow:
  local:
    tracking_uri: "./mlruns"  # Created at project root
    experiment_name: "next_best_product_local"
    registered_model_name: "next_best_product_model"
  
  databricks:
    tracking_uri: "databricks"
    experiment_name: "/Users/your-email@company.com/next-best-product"
    model_registry_uri: "databricks-uc"
    registered_model_name: "home_credit_catalog.ml_models.next_best_product_model"
```

### Model Parameters

```yaml
model:
  algorithm: "random_forest"  # or "logistic_regression"
  test_size: 0.2
  random_state: 42
  
  hyperparameters:
    random_forest:
      n_estimators: 100
      max_depth: 15
      min_samples_split: 10
      min_samples_leaf: 5
      class_weight: "balanced"
```

---

## 📈 Model Evaluation

### Training Metrics
- **Accuracy**: Overall correctness (target: >70%)
- **Precision/Recall**: Per-class performance (target: >65%)
- **F1-Score**: Balanced metric (target: >0.70)
- **ROC-AUC**: Classification quality (target: >0.80)

### Recommendation Metrics
- **Top-1 Accuracy**: True product is #1 recommendation
- **Top-3 Accuracy**: True product in top-3 (target: >85%)
- **Top-5 Accuracy**: True product in top-5 (target: >95%)

### Production Metrics
- **Conversion Rate**: Recommendations that lead to purchases
- **Click-Through Rate**: Customer engagement
- **Revenue Impact**: Business value generated
- **Feature Drift**: Statistical tests for data changes
- **Data Quality**: Completeness, validity checks

---

## 🔍 Important Clarifications

### Training vs Inference Data

**Training (03_model_training.ipynb):**
- Uses customers with known purchases (~3,500)
- Splits 80-20: Train (~2,800) | Test (~700)
- Model learns patterns from training set
- Evaluated on test set (never seen during training)

**Inference (05_batch_inference.ipynb):**
- Filters to customers WITHOUT target (~1,500)
- These customers were never used in training
- Represents true unseen inference scenario
- No data leakage between training and inference

**In Production:**
- Training uses historical data (e.g., data up to Sep 2024)
- Inference uses current data (e.g., Nov 2024)
- Features recalculated with latest transactions
- Can include new customers not in training set

---

## 🛠️ Troubleshooting

### Common Issues

**Import errors:**
```python
# Add to notebook top if needed
import sys
sys.path.append('../')
```

**CSV files not found:**
```powershell
# Run data generation first
jupyter notebook notebooks/00_data_generation.ipynb
```

**MLflow tracking URI:**
```yaml
# Check config.yaml
mlflow:
  local:
    tracking_uri: "./mlruns"  # For local mode
```

**Data leakage concerns:****
- Batch inference filters out customers used in training
- Only predicts on unseen customers
- Proper train-test split during training

---

## 📚 Additional Resources

### Documentation
- **README.md**: Comprehensive project overview
- **SETUP.md**: Detailed setup for local and Databricks
- **QUICKSTART.md**: 5-minute quick start guide
- **config/config.yaml**: All configuration options with comments

### External Links
- [Databricks Documentation](https://docs.databricks.com)
- [MLflow Documentation](https://mlflow.org/docs/latest)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

---

## ✅ Production Checklist

Before deploying to production:

- [ ] Replace synthetic data with real banking data
- [ ] Tune hyperparameters using validation set
- [ ] Set up CI/CD pipeline
- [ ] Configure monitoring alerts
- [ ] Implement A/B testing framework
- [ ] Set up model retraining schedule
- [ ] Create model documentation and governance
- [ ] Test with production data volume
- [ ] Validate prediction latency
- [ ] Set up backup and rollback procedures

---

## 🎯 Next Steps

1. **Understand the baseline**: Run all notebooks to generate outputs
2. **Explore EDA results**: Review charts and statistics in `outputs/eda/`
3. **Experiment with models**: Try different algorithms in `config.yaml`
4. **Add custom features**: Extend `utils/feature_engineering.py`
5. **Deploy to Databricks**: Follow SETUP.md Databricks section
6. **Set up monitoring**: Configure alerts in `06_model_monitoring.ipynb`
7. **Integrate with systems**: Connect predictions to downstream applications

---

## 📞 Support

For questions or issues:
1. Check SETUP.md troubleshooting section
2. Review inline code comments
3. Check MLflow UI for experiment details
4. Verify configuration in config.yaml

---
