# Quick Setup Guide

This guide will help you quickly set up and run the data drift detection solution.

## Quick Start (5 Minutes)

### Step 1: Environment Setup (2 min)

#### In Databricks Notebook:
```python
# Install dependencies
%pip install evidently==0.7.19 pyyaml==6.0.2 pandas==2.2.3 numpy==2.2.1 azure-storage-file-datalake==12.20.0 azure-identity==1.19.0 plotly==5.24.1

# Restart Python
dbutils.library.restartPython()
```

### Step 2: Upload Files to Databricks (2 min)

1. **Upload project to Databricks Repos**
   - Go to Databricks Repos
   - Import from Git or upload files directly
   - Path example: `/Workspace/Repos/<your-username>/data-drift-evidently-ai`

2. **Verify structure**
   ```
   /Workspace/Repos/<your-username>/data-drift-evidently-ai/
   ├── config/
   ├── utils/
   └── notebooks/
   ```

### Step 3: Configure (1 min)

Edit `config/drift_config.yaml`:

```yaml
databricks:
  catalog: 'main'                    # Your catalog name
  schema: 'data_quality'             # Your schema name
  tables:
    - name: 'customer_data'          # Your table name
      columns: 'all'

output:
  adls:
    enabled: false                   # Disable ADLS for testing
```

### Step 4: Generate Test Data (Optional)

If you want to test with dummy data:

```python
# Run in Databricks notebook
%run ./notebooks/01_generate_dummy_data.py
```

### Step 5: Run Drift Detection (<1 min)

#### For smaller datasets (< 1M rows):
```python
%run ./notebooks/02_drift_detection_python.py
```

#### For larger datasets (> 1M rows):
```python
%run ./notebooks/03_drift_detection_pyspark.py
```

## Verification

After running, you should see:
- Summary table with drift results
- Reports saved locally (reports/html, reports/json) by default
- Reports saved to ADLS if enabled
- Log messages showing processing status

## View Reports

### Option 1: Download and Open Locally
```python
# In Databricks notebook
dbutils.fs.cp("file:/Workspace/.../reports/html/", "dbfs:/FileStore/drift-reports/", True)
```
Then download from DBFS and open in browser.

### Option 2: Display in Notebook
```python
from IPython.display import HTML, display
with open('reports/html/customer_data_..._drift_report.html', 'r') as f:
    display(HTML(f.read()))
```

## Common Configurations
### Enable ADLS

```yaml
output:
  adls:
    enabled: true
    storage_account: 'your_account'
    container: 'drift-reports'
    base_path: 'data-drift'
    auth_method: 'service_principal'
```

### Disable Local Saving for Production
Local saving is hardcoded in `ReportManager.save_reports()`. Before production, comment out the local saving lines (marked with a comment) to prevent writing files to the driver.

File: `utils/report_manager.py`
- Inside `save_reports()`, comment out the lines that call `_save_local(...)`.

### Monitor Multiple Tables

```yaml
databricks:
  tables:
    - name: 'customer_data'
      columns: 'all'
    
    - name: 'product_sales'
      columns: ['category', 'price', 'quantity']
    
    - name: 'user_behavior'
      columns: 'all'
```

### Change Statistical Tests

```yaml
statistical_tests:
  numerical:
    tests:
      - 'ks'              # Fast, good for general use
      - 'wasserstein'     # Distance-based
    threshold: 0.05

  categorical:
    tests:
      - 'chisquare'       # Standard statistical test
      - 'jensenshannon'   # Information-theoretic
    threshold: 0.05
```

### Enable Sampling for Large Tables

```yaml
sampling:
  enabled: true
  method: 'fraction'
  fraction: 0.1           # Use 10% of data
  random_seed: 42
```

### Adjust Drift Sensitivity

```yaml
drift_detection:
  column_drift_threshold: 0.3    # 30% columns = dataset drift
  # Lower values = more sensitive
```

## Quick Troubleshooting

### Issue: Module not found

**Solution:**
```python
import sys
sys.path.append('/Workspace/Repos/<your-username>/data-drift-evidently-ai')
from utils import ConfigManager, DriftDetector, ReportManager, DataLoader, setup_logger
```

### Issue: Config file not found

**Solution:**
Use absolute path:
```python
CONFIG_PATH = '/Workspace/Repos/<your-username>/data-drift-evidently-ai/config/drift_config.yaml'
```

### Issue: Table not found

**Solution:**
Verify table exists:
```python
spark.sql("SHOW TABLES IN main.data_quality").show()
```

### Issue: Version handling

This project uses Unity Catalog History to fetch versions:

- Internally runs `DESCRIBE HISTORY <catalog.schema.table>`
- Reads data via `SELECT * FROM <table> VERSION AS OF <n>`

No version or timestamp columns are required in the data.

### Issue: Out of memory

**Solution:**
Enable sampling:
```yaml
sampling:
  enabled: true
  method: 'fraction'
  fraction: 0.05    # Use only 5% of data
```

Or increase cluster size.

## Pre-flight Checklist

Before running in production:

- [ ] Configuration file updated with your settings
- [ ] Utils module accessible in Python path
- [ ] Tables exist in Unity Catalog
- [ ] Unity Catalog has at least 2 table versions
- [ ] At least 2 versions of data exist
- [ ] Cluster has sufficient resources
- [ ] Output directory is writable
- [ ] (Optional) ADLS credentials configured

## Next Steps

1. **Test with dummy data** - Run data generation notebook
2. **Run on real data** - Update config with your tables
3. **Review results** - Check HTML reports
4. **Tune configuration** - Adjust tests and thresholds
5. **Schedule jobs** - Set up automated monitoring
6. **Set up alerts** - Configure notifications

## Additional Resources

- **Full Documentation**: See `README.md`
- **Configuration Guide**: See `config/drift_config.yaml` comments
- **Evidently AI Docs**: https://docs.evidentlyai.com/
- **Support**: Check logs in `logs/data_drift.log`

---

**Need Help?**
1. Check the main `README.md`
2. Review log files
3. Check Evidently AI documentation
4. Verify your configuration