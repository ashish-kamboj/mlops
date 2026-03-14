# Databricks notebook source
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

df = spark.table("data_catalog.outputs.propensity_staging")

df.write \
  .mode("overwrite") \
  .saveAsTable("data_catalog.outputs.propensity_final")

print("Final table refreshed")