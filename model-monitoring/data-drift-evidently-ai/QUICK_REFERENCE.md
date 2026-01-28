# 🚀 Quick Reference Card

## 📁 Project Files Overview

```
data-drift-evidently-ai/
├── 📋 Documentation (2 files)
│   ├── README.md .................. Complete documentation
│   ├── SETUP.md ................... Quick start guide (5 min)
│   └── QUICK_REFERENCE.md ........ Command quick reference
│
├── ⚙️ Configuration (1 file)
│   └── drift_config.yaml .......... Main config (CUSTOMIZE THIS)
│
├── 🛠️ Utilities (6 files)
│   ├── config_manager.py .......... Configuration handling
│   ├── drift_detector.py .......... Drift detection logic
│   ├── report_manager.py .......... Report generation
│   ├── data_loader.py ............. Data loading
│   ├── logger_setup.py ............ Logging setup
│   └── __init__.py ................ Package init
│
├── 📓 Scripts (4 files)
│   ├── 01_generate_dummy_data.py .. Test data generation
│   ├── 02_drift_detection_python.py  Python version
│   ├── 03_drift_detection_pyspark.py PySpark version
│   └── drift_detection_script.py .. Command-line runner
│
├── 📂 Output Directories
│   ├── reports/ ................... Generated reports
│   │   ├── html/ .................. HTML reports
│   │   └── json/ .................. JSON reports
│   └── logs/ ...................... Log files
│
└── 📦 Other
    └── requirements.txt ........... Dependencies
```

## Quick Commands

### Install Dependencies
```bash
pip install -r requirements.txt
# or in Databricks
%pip install evidently==0.7.19 pyyaml==6.0.2 pandas==2.2.3 numpy==2.2.1
```

### Run in Databricks
```python
# Generate test data
%run ./notebooks/01_generate_dummy_data.py

# Run drift detection (Python)
%run ./notebooks/02_drift_detection_python.py

# Run drift detection (PySpark)
%run ./notebooks/03_drift_detection_pyspark.py
```

### Run as Script
```bash
# All tables
python drift_detection_script.py --config config/drift_config.yaml

# Specific tables
python drift_detection_script.py --tables customer_data,product_sales

# Dry run
python drift_detection_script.py --dry-run --verbose
```

## Configuration Hotspots

### Most Important Settings

```yaml
# 1. Your Databricks details
databricks:
  catalog: 'YOUR_CATALOG'      # ← Change this
  schema: 'YOUR_SCHEMA'        # ← Change this
  tables:                      # ← Add your tables
    - name: 'YOUR_TABLE'
      columns: 'all'

# 2. Statistical tests
statistical_tests:
  numerical:
    tests: ['ks', 'wasserstein']    # ← Customize
  categorical:
    tests: ['chisquare', 'jensenshannon']  # ← Customize

# 3. Output location
# Local saving is on by default (reports/html, reports/json)
output:
  adls:
    enabled: false             # ← Set true to also upload to ADLS

# 4. Drift sensitivity
drift_detection:
  column_drift_threshold: 0.3  # ← Lower = more sensitive
```

## Statistical Tests Available

### Numerical Columns
- `ks` - Kolmogorov-Smirnov ⭐ (recommended)
- `wasserstein` - Wasserstein distance ⭐ (recommended)
- `psi` - Population Stability Index
- `kl_div` - Kullback-Leibler divergence
- `jensenshannon` - Jensen-Shannon divergence
- `anderson` - Anderson-Darling test
- `cramer_von_mises` - Cramér-von Mises test
- `t_test` - Student's t-test

### Categorical Columns
- `chisquare` - Chi-square test ⭐ (recommended)
- `jensenshannon` - Jensen-Shannon ⭐ (recommended)
- `psi` - Population Stability Index
- `kl_div` - Kullback-Leibler divergence
- `wasserstein` - Wasserstein distance
- `hellinger` - Hellinger distance
- `z` - Z-test

## 🔧 Common Tasks

### Add a New Table
```yaml
# In drift_config.yaml
tables:
  - name: 'new_table_name'
    columns: 'all'              # or ['col1', 'col2']
```

### Change Tests
```yaml
# In drift_config.yaml
statistical_tests:
  numerical:
    tests: ['ks', 'wasserstein', 'psi']  # Add/remove tests
```

### Adjust Sensitivity
```yaml
# Lower = more alerts
drift_detection:
  column_drift_threshold: 0.2  # From 0.0 to 1.0
```

### Enable ADLS
```yaml
# Set environment variables first:
# AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET

output:
  adls:
    enabled: true
    storage_account: 'your_account'
    container: 'drift-reports'
```

### Enable Sampling (for large tables)
```yaml
sampling:
  enabled: true
  method: 'fraction'
  fraction: 0.1  # Use 10% of data
```

## Code Examples

### Import in Python
```python
from utils import (
    ConfigManager,
    DriftDetector,
    ReportManager,
    DataLoader,
    setup_logger
)

# Load config
config = ConfigManager('config/drift_config.yaml')

# Setup logging
logger = setup_logger(
  log_level=config.get_log_level(),
  adls_config=config.get_adls_config() if config.is_adls_output_enabled() else None,
)

# Initialize components
drift_detector = DriftDetector(config)
report_manager = ReportManager(config)
data_loader = DataLoader(config, spark=spark)
```

### Detect Drift
```python
# Load data
ref_data, cur_data = data_loader.load_table_versions(
    table_name='customer_data',
    use_spark=True
)

# Detect drift
report, summary = drift_detector.detect_drift(
    reference_data=ref_data,
    current_data=cur_data,
    table_name='customer_data'
)

# Save reports
paths = report_manager.save_reports(
    report=report,
    drift_summary=summary,
    table_name='customer_data'
)
```

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Module not found | `sys.path.append('/path/to/project')` |
| Config not found | Use absolute path to config file |
| Table not found | Check catalog.schema.table name |
| No versions | Ensure Unity Catalog history has at least 2 versions |
| Out of memory | Enable sampling in config |
| ADLS auth error | Check environment variables |

## Performance Guide

| Dataset Size | Use | Expected Time |
|-------------|-----|---------------|
| < 100K rows | Python notebook | < 2 min |
| 100K - 1M rows | Python notebook | 2-10 min |
| 1M - 10M rows | PySpark notebook | 5-15 min |
| > 10M rows | PySpark + sampling | 10-30 min |

## Best Practices

1. **Start Small**: Test with dummy data first
2. **Tune Tests**: Start with KS and Chi-square
3. **Monitor Logs**: Check logs/data_drift.log
4. **Review Reports**: Check HTML reports regularly
5. **Adjust Thresholds**: Fine-tune based on results
6. **Enable Sampling**: For tables > 10M rows
7. **Use PySpark**: For production workloads
8. **Schedule Jobs**: Automate in Databricks
9. **Save to ADLS**: For production environments
10. **Version Control**: Keep configs in Git

## Get Help

1. **Documentation**: See README.md
2. **Setup Guide**: See SETUP.md
3. **Architecture**: See ARCHITECTURE.md
4. **Logs**: Check logs/data_drift.log
5. **Evidently Docs**: https://docs.evidentlyai.com/

## Pre-Flight Checklist

Before running in production:

- [ ] Config file customized with your settings
- [ ] Tables exist in Unity Catalog
- [ ] Tables have version/timestamp columns
- [ ] At least 2 versions of data exist
- [ ] Utils accessible in Python path
- [ ] Cluster has sufficient resources
- [ ] Output directory permissions OK
- [ ] ADLS credentials configured (if using)
- [ ] Tested with dummy data successfully
- [ ] Logging working correctly

## 🎉 Ready to Go!

1. Edit `config/drift_config.yaml`
2. Run test data generation notebook
3. Run drift detection notebook
4. Review HTML reports
5. Adjust configuration as needed
6. Deploy to production

---

**Quick Links:**
- Full Docs: README.md
- Setup: SETUP.md
- Architecture: ARCHITECTURE.md
- Config: config/drift_config.yaml
