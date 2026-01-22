# Data Drift Detection with Evidently AI

A comprehensive, production-ready solution for detecting data drift in Databricks Unity Catalog using Evidently AI. This project provides configurable drift detection with support for both Python/Pandas and PySpark implementations.

## 🎯 Features

### Core Capabilities
- ✅ **Multiple Statistical Tests**: Configure various tests for numerical and categorical columns
- ✅ **Flexible Configuration**: YAML-based configuration for easy customization
- ✅ **Dual Implementation**: Python/Pandas for smaller datasets, PySpark for large-scale processing
- ✅ **Multiple Output Formats**: Generate HTML (interactive) and JSON (programmatic) reports
- ✅ **Storage Options**: Save to local filesystem or Azure Data Lake Storage (ADLS)
- ✅ **Version Management**: Automatic comparison of the latest two versions via Unity Catalog history
- ✅ **Column Selection**: Monitor all columns or specific subsets per table
- ✅ **Comprehensive Logging**: Python logging module with configurable levels
- ✅ **Error Handling**: Robust error handling with detailed error messages
- ✅ **OOP Design**: Clean, maintainable object-oriented architecture

### Statistical Tests Supported

#### Numerical Columns
- Kolmogorov-Smirnov (KS) test
- Wasserstein distance
- Kullback-Leibler (KL) divergence
- Population Stability Index (PSI)
- Jensen-Shannon divergence
- Anderson-Darling test
- Cramér-von Mises test
- T-test

#### Categorical Columns
- Chi-square test
- Jensen-Shannon divergence
- Population Stability Index (PSI)
- Kullback-Leibler divergence
- Wasserstein distance
- Hellinger distance
- Z-test

## 📁 Project Structure

```
data-drift-evidently-ai/
├── config/
│   └── drift_config.yaml           # Main configuration file
├── utils/
│   ├── __init__.py                 # Package initializer
│   ├── config_manager.py           # Configuration management
│   ├── drift_detector.py           # Core drift detection logic
│   ├── report_manager.py           # Report generation and storage
│   ├── data_loader.py              # Data loading from Unity Catalog
│   └── logger_setup.py             # Logging configuration
├── notebooks/
│   ├── 01_generate_dummy_data.ipynb        # Test data generation
│   ├── 02_drift_detection_python.ipynb    # Python/Pandas version
│   └── 03_drift_detection_pyspark.ipynb   # PySpark version
├── reports/                        # Local report output directory
│   ├── html/                       # HTML reports
│   └── json/                       # JSON reports
├── logs/                           # Log files
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Getting Started

### Prerequisites

1. **Databricks Environment**
   - Databricks workspace with Unity Catalog enabled
   - Databricks cluster with Spark 3.3+
   - Python 3.8+

2. **Azure (Optional - for ADLS)**
   - Azure Data Lake Storage Gen2 account
   - Service Principal with appropriate permissions

### Installation

1. **Clone or upload this project to your Databricks workspace**

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

   Or in a Databricks notebook:
   ```python
   %pip install evidently==0.7.19 pyyaml==6.0.2 pandas==2.2.3 numpy==2.2.1 azure-storage-file-datalake==12.20.0 azure-identity==1.19.0
   ```

3. **Upload utils module to Databricks**
   - Upload the `utils` folder to your Databricks workspace
   - Or package it as a library and install on your cluster

4. **Configure the YAML file**
   - Edit `config/drift_config.yaml` with your settings
   - Update catalog, schema, and table names
   - Configure statistical tests and output settings

## ⚙️ Configuration

### Main Configuration File: `config/drift_config.yaml`

#### 1. General Settings
```yaml
general:
  log_level: 'INFO'              # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### 2. Databricks Unity Catalog Settings
```yaml
databricks:
  catalog: 'main'
  schema: 'data_quality'
  tables:
    - name: 'customer_data'
      columns: 'all'              # or ['col1', 'col2', ...]
```

#### 3. Statistical Tests Configuration
```yaml
statistical_tests:
  numerical:
    tests:
      - 'ks'                      # Kolmogorov-Smirnov
      - 'wasserstein'             # Wasserstein distance
    threshold: 0.05               # P-value threshold
  
  categorical:
    tests:
      - 'chisquare'               # Chi-square test
      - 'jensenshannon'           # Jensen-Shannon divergence
    threshold: 0.05
```

#### 4. Output Configuration
```yaml
output:
  formats:
    - 'html'                      # Interactive reports
    - 'json'                      # Programmatic analysis
  
  adls:
    enabled: false
    storage_account: 'your_account'
    container: 'drift-reports'
    base_path: 'data-drift'
    auth_method: 'service_principal'
```

Unity Catalog table history is used for version comparison (no config needed).

#### 6. Drift Detection Settings
```yaml
drift_detection:
  confidence_level: 0.95
  min_sample_size: 100
  missing_values_strategy: 'keep'  # 'drop', 'keep', or 'fill'
  column_drift_threshold: 0.3      # 30% columns = dataset drift
```

#### 7. Data Sampling (for large datasets)
```yaml
sampling:
  enabled: false
  method: 'fraction'              # or 'fixed'
  fraction: 0.1                   # 10% of data
  fixed_size: 10000
  random_seed: 42
```

## 📊 Usage

### Step 1: Generate Test Data

Run the data generation notebook to create sample tables with drift:

```python
# In Databricks notebook
%run /Workspace/Repos/<your-repo>/notebooks/01_generate_dummy_data
```

This creates three tables with two versions each (accessible via Unity Catalog history):
- `customer_data` - Customer demographics
- `product_sales` - Sales transactions
- `user_behavior` - User engagement metrics

### Step 2: Run Drift Detection

#### Option A: Python/Pandas Version (Smaller Datasets)

```python
# In Databricks notebook
%run /Workspace/Repos/<your-repo>/notebooks/02_drift_detection_python
```

**Best for:**
- Tables with < 1M rows
- Quick testing and development
- Simple data exploration

#### Option B: PySpark Version (Large Datasets)

```python
# In Databricks notebook
%run /Workspace/Repos/<your-repo>/notebooks/03_drift_detection_pyspark
```

**Best for:**
- Tables with > 1M rows
- Production workloads
- Distributed processing
- Large-scale monitoring

### Step 3: Review Reports

Reports are generated in two formats and saved locally by default (testing-friendly). If ADLS is enabled in config, they are also uploaded to your storage account.
Local Paths:
- HTML: `reports/html/<table>_<timestamp>_drift_report.html`
- JSON: `reports/json/<table>_<timestamp>_drift_report.json`

ADLS Paths (when enabled):
- `abfss://<container>@<account>.dfs.core.windows.net/<base_path>/<format>/<file>`

1. **HTML Reports** - Interactive visualizations
   - Open in browser
   - Visual drift indicators
   - Statistical test results
   - Distribution comparisons

2. **JSON Reports** - Programmatic access
   - Integration with monitoring systems
   - Automated alerting
   - Data analysis pipelines

## 📈 Understanding the Results

### Drift Summary

Each table analysis produces:

```python
{
  'table_name': 'customer_data',
  'timestamp': '2026-01-07T10:30:00',
  'num_columns': 7,
  'num_drifted_columns': 3,
  'drift_share': 0.43,           # 43% of columns drifted
  'dataset_drift': True,         # Overall drift detected
  'drifted_columns': ['age', 'income', 'region'],
  'column_drift_details': {
    'age': {
      'drift_detected': True,
      'drift_score': 0.023,
      'stattest_name': 'ks'
    },
    ...
  }
}
```

### Interpreting Results

- **No Drift (✓)**: Data distributions remain stable
- **Drift Detected (⚠️)**: Significant changes in data distribution

## 🔧 Architecture Overview
- Input: YAML config + Unity Catalog tables (latest and previous via UC History)
- Processing:
  - `ConfigManager`: loads/validates config and provides accessors
  - `DataLoader`: uses Spark and UC History (`DESCRIBE HISTORY` + `VERSION AS OF`) to load previous vs latest, converts to Pandas
  - `DriftDetector`: identifies column types, applies configured tests, builds Evidently `Report` with `DataDriftTable` + `DatasetDriftMetric` and per-column `ColumnDriftMetric`
  - `ReportManager`: generates HTML/JSON and saves locally by default and to ADLS when enabled; injects a summary section
  - Logging: console always; ADLS log handler when enabled
- Output: Local `reports/html` and `reports/json` by default; optional ADLS upload under `<base_path>/<format>/...`

## 🔄 Versioning via Unity Catalog
- No version columns required; the loader fetches latest two versions via UC History.
- Reads data with `SELECT * FROM <catalog.schema.table> VERSION AS OF <n>`.
- Works identically in notebooks and the script.

## 📦 Version Update (Evidently 0.7.19)
- Imports: use `evidently.metrics` (e.g., `DatasetDriftMetric`, `DataDriftTable`, `ColumnDriftMetric`); remove legacy TestSuite/tests.
- Report creation: metrics list provided at construction time; no post-append.
- HTML: use `report.show(mode='inline').data` with fallback to `get_html()` or `save_html()`.
- Dependencies pinned (examples): Evidently 0.7.19, pandas 2.2.3, numpy 2.2.1, pyspark 3.5.3, pyyaml 6.0.2, azure-storage-file-datalake 12.20.0, azure-identity 1.19.0.

## 🧪 Troubleshooting (Quick)
- Module not found: ensure project path added in notebook; upload `utils` to workspace.
- Config not found: use absolute workspace path for `drift_config.yaml`.
- Table not found: verify `catalog.schema.table` exists (`SHOW TABLES`).
- No versions: ensure Unity Catalog History shows at least two versions.
- ADLS auth: verify service principal credentials and container/base path.
- Memory pressure: enable sampling in config or use PySpark notebook.

## ⚙️ Performance Notes
- Python: good for < 1M rows; fast iteration and testing.
- PySpark: recommended for larger datasets; supports sampling; distributed execution.

## 📚 Documentation
- README.md: Full guide, architecture, versioning via Unity Catalog, troubleshooting.
- SETUP.md: 5‑minute quick start for Databricks with install and run steps.
- QUICK_REFERENCE.md: Commands and configuration at a glance.

## 🔗 Quick Links
  - 01 Generate Dummy Data: [notebooks/01_generate_dummy_data.ipynb](notebooks/01_generate_dummy_data.ipynb)
  - 02 Drift Detection (Python): [notebooks/02_drift_detection_python.ipynb](notebooks/02_drift_detection_python.ipynb)
  - 03 Drift Detection (PySpark): [notebooks/03_drift_detection_pyspark.ipynb](notebooks/03_drift_detection_pyspark.ipynb)
  - CLI runner: [drift_detection_script.py](drift_detection_script.py)
## ▶️ Run This

Run in Databricks notebooks (recommended):

```python
# Generate dummy data
%run ./notebooks/01_generate_dummy_data

# Python/Pandas workflow (small-medium tables)
%run ./notebooks/02_drift_detection_python

# PySpark workflow (large tables)
%run ./notebooks/03_drift_detection_pyspark
```

Run the CLI (cluster or local with Spark available):

```bash
# install deps
pip install -r requirements.txt

# run all configured tables
python drift_detection_script.py --config config/drift_config.yaml --verbose

# run a subset of tables
python drift_detection_script.py --config config/drift_config.yaml --tables customer_data,product_sales --verbose

# dry run (no report saving)
python drift_detection_script.py --config config/drift_config.yaml --dry-run
```
### Common Drift Causes

1. **Legitimate Changes**
   - Seasonal patterns
   - Business growth
   - Market changes
   - New product launches

2. **Data Quality Issues**
   - Pipeline bugs
   - Schema changes
   - Missing data handling changes
   - Data source changes

## 🔧 Customization

### Adding New Tables

Edit `config/drift_config.yaml`:

```yaml
databricks:
  tables:
    - name: 'your_new_table'
      columns: 'all'  # or ['col1', 'col2']
```

### Changing Statistical Tests

Edit `config/drift_config.yaml`:

```yaml
statistical_tests:
  numerical:
    tests:
      - 'ks'
      - 'wasserstein'
      - 'psi'              # Add new test
    threshold: 0.01        # Stricter threshold
```

### Custom Column Selection

```yaml
tables:
  - name: 'customer_data'
    columns: ['age', 'income', 'credit_score']  # Only these columns
```

### Adjusting Drift Sensitivity

```yaml
drift_detection:
  column_drift_threshold: 0.2    # Lower = more sensitive (20%)
```

### Enabling ADLS Output

1. Set up Azure credentials:
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-secret"
```

2. Enable in config:
```yaml
output:
  adls:
    enabled: true
    storage_account: 'your_storage_account'
    container: 'drift-reports'
    base_path: 'data-drift'
    auth_method: 'service_principal'
```

## 🏗️ Architecture

### Class Diagram

```
ConfigManager
├── Load YAML configuration
├── Validate settings
└── Provide configuration access

DataLoader
├── Connect to Unity Catalog
├── Load table versions
├── Handle Spark/Pandas conversion
└── Apply sampling

DriftDetector
├── Identify column types
├── Configure statistical tests
├── Run Evidently reports
└── Extract drift metrics

ReportManager
├── Generate HTML reports
├── Generate JSON reports
├── Save to local filesystem
└── Upload to ADLS
```

### Data Flow

```
Unity Catalog Table
    ↓
DataLoader (loads versions)
    ↓
DriftDetector (analyzes drift)
    ↓
Evidently AI (statistical tests)
    ↓
ReportManager (generates reports)
    ↓
Output (Local / ADLS)
```

## 🐛 Troubleshooting

### Common Issues

1. **Module Not Found Error**
   ```python
   # Add utils to path
   sys.path.append('/Workspace/Repos/<your-repo>/data-drift-evidently-ai')
   ```

2. **Configuration File Not Found**
   - Use absolute paths in Databricks
   - Check file location: `/Workspace/Repos/<your-repo>/config/drift_config.yaml`

3. **ADLS Authentication Errors**
   - Verify service principal credentials
   - Check RBAC permissions on storage account
   - Ensure environment variables are set

4. **Memory Issues with Large Tables**
   - Enable sampling in configuration
   - Increase cluster size
   - Use PySpark version

5. **Version Column Not Found**
   - Verify version column name in config
   - Ensure data has version information
   - Check for typos in column names

## 📚 References

### Evidently AI Documentation
- [Evidently AI Official Docs](https://docs.evidentlyai.com/introduction)
- [Old Docs (Legacy)](https://docs-old.evidentlyai.com/)
- [Statistical Tests Guide](https://docs.evidentlyai.com/reference/data-drift)
- [Column Mapping](https://docs.evidentlyai.com/user-guide/input-data/column-mapping)

### Databricks Resources
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [PySpark Documentation](https://spark.apache.org/docs/latest/api/python/)

### Azure Resources
- [ADLS Gen2](https://docs.microsoft.com/azure/storage/blobs/data-lake-storage-introduction)
- [Azure Python SDK](https://docs.microsoft.com/python/api/overview/azure/storage-file-datalake-readme)


## 🙋 Support

For issues or questions:
1. Check troubleshooting section
2. Review configuration documentation
3. Check Evidently AI documentation
4. Review log files for detailed error messages

## 🎯 Roadmap

### Future Enhancements
- [ ] Email/Slack alerting integration
- [ ] Dashboard for drift trends over time
- [ ] Automated threshold optimization
- [ ] Multi-version comparison (>2 versions)
- [ ] Integration with MLflow
- [ ] Custom drift metrics
- [ ] Real-time streaming drift detection
- [ ] Automated remediation suggestions

---