#!/usr/bin/env python3
"""PySpark ETL for the lab 2 recommendation training dataset.

This is the local batch ETL job:

    MySQL classicmodels -> Spark transformation -> partitioned Parquet
"""

from __future__ import annotations

import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


DEFAULT_MYSQL_HOST = "classicmodels-lab2-mysql"
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MYSQL_USER = "admin"
DEFAULT_MYSQL_PASSWORD = "adminpwrd"
DEFAULT_MYSQL_DATABASE = "classicmodels"
DEFAULT_TARGET_PATH = "s3a://classicmodels-lab2/ratings_ml_training"
DEFAULT_JDBC_PARTITIONS = 4
DEFAULT_S3_ENDPOINT = "http://minio:9000"
DEFAULT_S3_ACCESS_KEY = "minioadmin"
DEFAULT_S3_SECRET_KEY = "minioadmin"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the ratings ML training dataset with PySpark."
    )
    parser.add_argument("--mysql-host", default=DEFAULT_MYSQL_HOST)
    parser.add_argument("--mysql-port", type=int, default=DEFAULT_MYSQL_PORT)
    parser.add_argument("--mysql-user", default=DEFAULT_MYSQL_USER)
    parser.add_argument("--mysql-password", default=DEFAULT_MYSQL_PASSWORD)
    parser.add_argument("--mysql-database", default=DEFAULT_MYSQL_DATABASE)
    parser.add_argument("--target-path", default=DEFAULT_TARGET_PATH)
    parser.add_argument("--jdbc-partitions", type=int, default=DEFAULT_JDBC_PARTITIONS)
    parser.add_argument("--s3-endpoint", default=DEFAULT_S3_ENDPOINT)
    parser.add_argument("--s3-access-key", default=DEFAULT_S3_ACCESS_KEY)
    parser.add_argument("--s3-secret-key", default=DEFAULT_S3_SECRET_KEY)
    return parser.parse_args()


def build_spark_session(args: argparse.Namespace) -> SparkSession:
    return (
        SparkSession.builder.appName("classicmodels-lab2-ratings-etl")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.hadoop.fs.s3a.endpoint", args.s3_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", args.s3_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", args.s3_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        .getOrCreate()
    )


def read_mysql_table(
    spark: SparkSession,
    jdbc_url: str,
    table_name: str,
    user: str,
    password: str,
    partition_column: str | None = None,
    lower_bound: int | None = None,
    upper_bound: int | None = None,
    num_partitions: int | None = None,
) -> DataFrame:
    reader = (
        spark.read.format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", table_name)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
    )

    if partition_column:
        reader = (
            reader.option("partitionColumn", partition_column)
            .option("lowerBound", str(lower_bound))
            .option("upperBound", str(upper_bound))
            .option("numPartitions", str(num_partitions))
        )

    dataframe = reader.load()
    print(
        f"Read {table_name}: {dataframe.count():,} rows "
        f"across {dataframe.rdd.getNumPartitions()} Spark partition(s)"
    )
    return dataframe


def build_training_dataset(
    customers: DataFrame,
    products: DataFrame,
    ratings: DataFrame,
) -> DataFrame:
    return (
        ratings.alias("r")
        .join(products.alias("p"), F.col("p.productCode") == F.col("r.productCode"), "inner")
        .join(
            customers.alias("c"),
            F.col("c.customerNumber") == F.col("r.customerNumber"),
            "inner",
        )
        .select(
            F.col("r.customerNumber").cast("int").alias("customerNumber"),
            F.col("c.city"),
            F.col("c.state"),
            F.col("c.postalCode"),
            F.col("c.country"),
            F.col("c.creditLimit").cast("double").alias("creditLimit"),
            F.col("r.productCode"),
            F.col("p.productLine"),
            F.col("p.productScale"),
            F.col("p.quantityInStock").cast("int").alias("quantityInStock"),
            F.col("p.buyPrice").cast("double").alias("buyPrice"),
            F.col("p.MSRP").cast("double").alias("MSRP"),
            F.col("r.productRating").cast("int").alias("productRating"),
        )
    )


def main() -> None:
    args = parse_args()
    spark = build_spark_session(args)
    spark.sparkContext.setLogLevel("WARN")

    jdbc_url = (
        f"jdbc:mysql://{args.mysql_host}:{args.mysql_port}/{args.mysql_database}"
        "?useSSL=false&allowPublicKeyRetrieval=true"
    )

    customers = read_mysql_table(
        spark,
        jdbc_url,
        "customers",
        args.mysql_user,
        args.mysql_password,
        partition_column="customerNumber",
        lower_bound=100,
        upper_bound=500,
        num_partitions=args.jdbc_partitions,
    )
    products = read_mysql_table(
        spark,
        jdbc_url,
        "products",
        args.mysql_user,
        args.mysql_password,
    )
    ratings = read_mysql_table(
        spark,
        jdbc_url,
        "ratings",
        args.mysql_user,
        args.mysql_password,
        partition_column="customerNumber",
        lower_bound=100,
        upper_bound=500,
        num_partitions=args.jdbc_partitions,
    )

    training_dataset = build_training_dataset(customers, products, ratings)

    print("Training dataset schema:")
    training_dataset.printSchema()
    print(f"Training dataset rows: {training_dataset.count():,}")

    (
        training_dataset.write.mode("overwrite")
        .partitionBy("customerNumber")
        .parquet(args.target_path)
    )

    print(f"Wrote partitioned Parquet dataset to {args.target_path}")
    spark.stop()


if __name__ == "__main__":
    main()
