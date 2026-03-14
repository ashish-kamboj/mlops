# Databricks notebook source
from pyspark.sql import SparkSession
import json

spark = SparkSession.builder.getOrCreate()

config_path = "/Workspace/Users/<<USER_NAME>>/propensity_pipeline/config/brands_config.json"

config = json.loads(dbutils.fs.head(config_path))

# flatten category + brand
brand_configs = []

for category, brands in config["categories"].items():
    for brand in brands:
        brand_configs.append({
            "category": category,
            "brand": brand
        })

print("Total brands:", len(brand_configs))

# split into two batches
mid = len(brand_configs) // 2

batch1 = brand_configs[:mid]
batch2 = brand_configs[mid:]

print("Batch1:", len(batch1), batch1)
print("Batch2:", len(batch2), batch2)

# pass to workflow
dbutils.jobs.taskValues.set(key="batch1", value=batch1)
dbutils.jobs.taskValues.set(key="batch2", value=batch2)

# dummy base feature table
data = [
    ("cust1",100),
    ("cust2",200),
    ("cust3",300)
]

df = spark.createDataFrame(data,["customer_id","spend"])

df.write.mode("overwrite").saveAsTable("data_catalog.outputs.feature_base")

print("Feature engineering completed")
