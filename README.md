# Project Overview

This repository contains a collection of Jupyter notebooks and Python scripts designed for advanced data engineering tasks using Databricks, Delta Live Tables (DLT), and S3. The primary focus is on automating data ingestion, transformation, and movement processes to create a robust and scalable data pipeline. Below, you'll find detailed descriptions of each file, along with code snippets that illustrate the core functionality provided by each.

## Files Description

### 1. `autoload_with_dlt.ipynb`
This notebook is designed to demonstrate how to define a schema and load raw JSON data into Delta Live Tables using a streaming approach. Delta Live Tables (DLT) is a powerful tool within Databricks that allows for the creation of reliable, real-time data pipelines with built-in monitoring and logging.

- **Schema Definition**: The notebook starts by defining a JSON schema using PySpark's `StructType` and `StructField` classes. This schema is essential for ensuring that the data ingested from JSON files conforms to the expected structure.
  
- **Data Loading**: Using DLT, the notebook sets up a streaming job that reads JSON files from an S3 bucket and ingests them into a raw Delta table. The table is defined with expectations (data validation rules) to ensure data quality, such as non-null constraints on `id` and `timestamp` fields.

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
### 2. dbx-sql.ipynb
This notebook is focused on executing complex SQL queries within Databricks. The primary goal is to perform data extraction and transformation operations across multiple tables stored in Databricks.

**Catalog and Schema:** The notebook first sets up the catalog and schema that will be used in the SQL queries. This helps in organizing the data and making the SQL commands reusable across different environments.

**SQL Query:** A complex SQL query is constructed to join several tables, including provider, practice, and member, with the claims table. This process involves filtering, aggregating, and combining data to create a comprehensive dataset for analysis.

**Saving Results:** The final dataset generated from the SQL query is saved as a Delta table. Delta tables provide the advantage of ACID transactions, scalability, and efficient data retrieval.

**Key Snippet:**

```python
catlog = 'em_test'
schema = 'emad'

df = spark.sql(f"""
WITH provider AS ( 
    SELECT DISTINCT provider_id, provider_detail, provider_npi
    FROM {catlog}.{schema}.provider
    WHERE provider_id IS NOT NULL
), 
practice AS ( 
    SELECT DISTINCT practice_id, practice_name, practice_npi, practice_location, practice_lat, practice_long
    FROM {catlog}.{schema}.practice a
    INNER JOIN location l ON a.practice_npi = l.npi 
), 
member AS ( 
    SELECT DISTINCT member_id, member_name, member_dob
    FROM {catlog}.{schema}.member
)
SELECT * 
FROM {catlog}.{schema}.claims c 
INNER JOIN provider p ON c.provider_id = p.provider_id 
INNER JOIN practice pr ON c.practice_id = pr.practice_id 
INNER JOIN member m ON c.member_id = m.member_id
""")

df.write.format("delta").option("inferSchema","true").saveAsTable(f"{catlog}.{schema}.claim_analysis")

```

### 3. moving_filesdatabricks.py
This Python script is designed to automate the movement of files between directories in an S3 bucket using Databricks utilities. This is particularly useful for organizing and archiving data, or for moving data to different environments for further processing.

**File Movement:** The script defines a function move_files_dbx that takes a source path and a destination path as input parameters. It then iterates over the files in the source directory, copying each one to the destination directory using Databricks' dbutils.fs.cp command.

**Date-based File Management:** The script includes a list of dates and moves files from directories corresponding to these dates into a specified destination directory. This is useful for managing time-series data or for batch processing.

**Key Snippet:**

```python
def move_files_dbx(source_path, destination_path): 
    ls = [] 
    for dir_path in dbutils.fs.ls(source_path): 
        file_name = dir_path.name 
        ls.append(file_name) 
        dest = f'{destination_path}{file_name}'
        dbutils.fs.cp(dir_path.path, dest, recurse=True)

date_list = ['2024-06-10', '2024-06-12', '2024-06-14']

for date in date_list: 
    source_path = f's3://somelocation/location/dt={date}'
    destination_path = 's3://somelocation/location/dt=2024-06-24'
    move_files_dbx(source_path, destination_path)


```

### 4. multiplefiles_autoloader.ipynb
This notebook demonstrates how to use Databricks' Autoloader to ingest multiple file types into Delta tables. Autoloader is a highly efficient tool for incrementally and automatically loading data from cloud storage.

**Autoloader Function:** A custom autoloader function is defined to handle the streaming ingestion of data files. The function configures the Autoloader with options like file format, schema location, and file pattern matching to ensure that the correct files are ingested.

**Data Transformation:** The data is transformed during the ingestion process, including operations such as extracting file names from the input paths and splitting strings. These transformations are crucial for organizing the data in a consistent and meaningful way before saving it to Delta tables.

**Key Snippet:**

```python 
def autoloader(
        datasource, 
        format, 
        checkpoint,
        table_name, 
        schema, 
        file
):
    logger.info("Start reading data using readStream")

    query = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", format)
        .option("cloudFiles.schemaLocation", checkpoint)
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.useIncrementalListing", "true")
        .option("recursiveFileLookup", "true")
        .option("header", "true")
        .option("pathGlobFilter", f"*{file}*")
        .schema(schema)
        .load(datasource)
    )

    query = query.withColumn("input_file_name", input_file_name())
    query = query.withColumn("split", split(query["input_file_name"], "/"))
    query = query.withColumn("input_file_name", query["split"][6])
    query = query.drop(query["split"])

    load = (
        query.writeStream
        .format("delta")
        .option("checkpointLocation", checkpoint)
        .option("mergeSchema", "true")
        .trigger(availableNow=True)
        .toTable(table_name)
    )

    return load 

```


