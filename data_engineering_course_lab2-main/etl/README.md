# Lab 2 PySpark ETL

This service runs the lab 2 batch ETL job with PySpark.

The job reads the local MySQL `classicmodels` database, joins customer, product, and rating data, and writes a partitioned Parquet training dataset.

```text
MySQL classicmodels -> Spark ETL -> MinIO Parquet ratings_ml_training
```

## What It Produces

The output schema contains the customer, product, and rating features used by
the recommendation workflow:

```text
customerNumber
city
state
postalCode
country
creditLimit
productCode
productLine
productScale
quantityInStock
buyPrice
MSRP
productRating
```

The output is written to the lab 2 MinIO bucket:

```text
s3a://classicmodels-lab2/ratings_ml_training
```

It is partitioned by `customerNumber`, so the folder layout looks like:

```text
ratings_ml_training/
  customerNumber=103/
  customerNumber=112/
  customerNumber=114/
```

## Services

The Compose stack starts:

```text
lab2-spark-master
lab2-spark-worker-1
lab2-etl-driver
```

The driver submits `run_etl.py` to the Spark master:

```text
spark://spark-master:7077
```

The worker executes the Spark tasks with 1 core and 1 GB of memory. The ETL still reads JDBC data with multiple partitions, but this local stack uses one worker by default to reduce memory pressure on machines with limited Docker memory. The Parquet output is written to MinIO.

The ETL connects to MySQL through:

```text
host.docker.internal:3307
```

That points from Docker containers back to the host machine, where the lab 2 MySQL container publishes port `3307`.

On some Docker environments, especially native Linux Docker,
`host.docker.internal` may not resolve as expected. In that case, use Docker's
internal container DNS instead:

```text
classicmodels-lab2-mysql:3306
```

That uses the MySQL container name and the internal MySQL port. The host
machine can still connect to the same database through `127.0.0.1:3307`.

## Start the Source Database

The database must be running first:

```bash
cd ../db
docker-compose up -d --build
```

MinIO must also be running:

```bash
cd ../min_io
docker-compose up -d
```

## Run the ETL

From this folder:

```bash
docker-compose up --build etl-driver
```

The `etl-driver` container exits when the job finishes. The Spark master and worker stay available so you can inspect the Spark UI.

Open the Spark UI:

```text
http://localhost:8080
```

If Docker is low on memory, stop heavy unrelated containers before running the job. Keep the default one-worker setup unless your Docker environment has more memory available.

## Inspect the Output

Use the MinIO console:

```text
http://localhost:9101
```

Open the `classicmodels-lab2` bucket and look for:

```text
ratings_ml_training/customerNumber=<number>/
```

You can also list the bucket from Docker:

```bash
docker run --rm \
  --network lab-2-minio_default \
  --entrypoint /bin/sh \
  minio/mc:latest \
  -c "mc alias set local http://minio:9000 minioadmin minioadmin >/dev/null && mc ls --recursive local/classicmodels-lab2/ratings_ml_training"
```

## Stop Spark

```bash
docker-compose down
```

To also delete the generated Parquet output:

```bash
docker-compose down -v
```

## Why PySpark Here?

AWS Glue is based on Apache Spark. This local service helps students see the same programming model without AWS:

| AWS Glue | Local PySpark |
| --- | --- |
| Glue Job | `run_etl.py` |
| Glue Connection | JDBC connection to MySQL |
| DynamicFrame/DataFrame | Spark DataFrame |
| S3 Parquet output | MinIO Parquet output |
| Partition keys | `partitionBy("customerNumber")` |

For this dataset, normal Python is enough technically. PySpark is used here because it teaches the distributed ETL model behind Glue.
