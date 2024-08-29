# Project Overview

This repository contains several scripts and notebooks designed to work with Databricks, Delta Live Tables, and S3 for data processing, loading, and transformation. Below is a description of each file and its purpose, along with code snippets illustrating key parts of each file.

## Files Description

### 1. `autoload_with_dlt.ipynb`
This notebook is used to define and load raw JSON data into Delta Live Tables using a streaming approach.

**Key Snippet:**
```python
from pyspark.sql.functions import * 
from pyspark.sql.types import * 
import dlt 

json_schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True), 
    StructField("age", IntegerType(), True), 
    StructField("timestamp", TimestampType(), True)
])

@dlt.table(name="raw_json_data", comment="The raw data ingested from JSON files")
@dlt.expect("Valid ID", "id IS NOT NULL and id != ''")
@dlt.expect("Valid Age", "age IS NOT NULL AND age > 0")
@dlt.expect("Valid Timestamp", "timestamp IS NOT NULL")
def raw_data():
    input = "s3://mybucket/json_files"
    df = (spark.readStream
            .format("CloudFiles")
            .option("cloudFiles.format", "json")
            .option("checkpointLocation", "/tmp/json_checkpoint")
            .schema(json_schema)
            .load(input))
    return df
```

