# Propensity Pipeline (Databricks Multi-ForEach)

This repository contains a Databricks workflow built to validate **parallel execution with `for_each_task`**.
The pipeline takes a brand configuration, splits work into batches, runs brand-level modeling tasks in parallel, and merges the results into a final table.

## Purpose

The main goal of this project is to test and demonstrate Databricks job parallelism using **ForEach tasks**.
Instead of running one large modeling notebook serially, the workflow fans out brand/category combinations and processes them concurrently.

## Repository Layout

- `config/brands_config.json`  
  Input configuration of categories and brands.
- `notebooks/01_feature_engineering1.ipynb`  
  Prepares base features and publishes task values (`batch1`, `batch2`) for downstream fan-out.
- `notebooks/02_brand_pipeline.ipynb`  
  Runs per-brand processing (feature step, label creation, dummy modeling score) and appends to staging.
- `notebooks/03_merge_results.ipynb`  
  Consolidates staging output into final output table.
- `workflows/Propensity_Run_Multi_ForEach.yaml`  
  Databricks job definition with two parallel ForEach branches.

## Workflow Overview

The job has four task stages:

1. **Feature_Engineering**
   - Reads `brands_config.json`
   - Flattens category/brand combinations
   - Splits them into two lists: `batch1` and `batch2`
   - Stores both lists with `dbutils.jobs.taskValues.set(...)`
   - Creates a base feature table: `data_catalog.outputs.feature_base`

2. **Modeling_1** (ForEach)
   - Input: `{{tasks.Feature_Engineering.values.batch1}}`
   - Executes notebook `02_brand_pipeline` once per batch item
   - Passes each item through `brand_batch_config`
   - Configured with `concurrency: 4`

3. **Modeling_2** (ForEach)
   - Input: `{{tasks.Feature_Engineering.values.batch2}}`
   - Executes the same brand notebook per item
   - Also configured with `concurrency: 4`

4. **Result_insert**
   - Waits for both ForEach branches to finish
   - Refreshes final table `data_catalog.outputs.propensity_final` from staging

## ForEach Parallel Execution (Key Focus)

This pipeline is intentionally designed around Databricks **ForEach fan-out** to test parallel execution behavior:

- Work items are generated dynamically from configuration.
- Two independent ForEach tasks (`Modeling_1`, `Modeling_2`) run after feature engineering.
- Each ForEach task runs multiple notebook iterations concurrently (`concurrency: 4`).
- Total throughput improves because brand-level workloads run in parallel instead of one-by-one.
- Final consolidation starts only when both fan-out branches complete.

In short, this project validates a practical orchestration pattern for scaling notebook-based pipelines using Databricks task-level parallelism.

## Data Flow

- Config input: `config/brands_config.json`
- Intermediate/base table: `data_catalog.outputs.feature_base`
- Staging table: `data_catalog.outputs.propensity_staging`
- Final table: `data_catalog.outputs.propensity_final`

## Current Example Logic

The notebook logic is intentionally lightweight for orchestration testing:

- Base feature data is mocked with sample customer spend values.
- Label creation uses a simple threshold (`spend > 150`).
- Propensity score is a dummy random value.

This keeps the workflow focused on validating **task decomposition, parameter passing, and parallel fan-out behavior**.

## Notes for Running in Databricks

- Update workspace-specific paths as needed (for example, notebook and config paths).
- Ensure target catalog/schema/table locations exist and are writable.
- Confirm the job has permissions to read config and write output tables.

Once those prerequisites are in place, run `Propensity_Run_Multi_ForEach` and monitor parallel notebook iterations under both ForEach branches in the Databricks job run view.
