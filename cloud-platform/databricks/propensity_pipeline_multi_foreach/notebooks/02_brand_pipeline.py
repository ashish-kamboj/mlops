# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import json
import random

spark = SparkSession.builder.getOrCreate()

# Receive parameters
dbutils.widgets.text("brand_batch_config", "")

brand_batch_config = dbutils.widgets.get("brand_batch_config")

print(brand_batch_config)

brand_batch_config = json.loads(brand_batch_config)

brand = brand_batch_config["brand"]
category = brand_batch_config["category"]

print(f"Running pipeline for {category} - {brand}")

df = spark.table("data_catalog.outputs.feature_base")

# Feature Engineering2 (example)
df = df.withColumn("brand_feature", lit(1))

# Label creation (dummy)
df = df.withColumn("label", (df.spend > 150).cast("int"))

# Modeling (dummy score)
df = df.withColumn("propensity_score", lit(random.random()))

# add metadata
df = df.withColumn("brand", lit(brand))
df = df.withColumn("category", lit(category))

df.write \
    .mode("append") \
    .saveAsTable("data_catalog.outputs.propensity_staging")

print(f"Completed {brand}")