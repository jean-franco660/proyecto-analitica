# Lab 2 Vector Database

This folder contains the local PostgreSQL database with the `pgvector`
extension.

The vector database is the next step after the batch ETL. The ETL produced the
training dataset in MinIO:

```text
MySQL classicmodels
  -> PySpark ETL
  -> MinIO classicmodels-lab2/ratings_ml_training
```

In this lab, assume a data scientist uses that training dataset to train a
recommendation model. The model training itself is outside the scope of the core
data engineering workflow, so this lab uses provided pre-trained ML artifacts.

## Current Local Stack

This folder now contains:

```text
docker-compose.yml          # PostgreSQL + pgvector and one-shot loader service
init/01-init.sql            # Creates pgvector extension and embedding tables
loader/load_embeddings.py   # Reads embeddings from lab2 MinIO and loads Postgres
loader/requirements.txt     # Python dependencies for the loader
```

The Compose stack starts:

```text
lab2-vector-db          # PostgreSQL with pgvector
lab2-vector-db-loader   # one-shot import job
```

The loader reads from lab2 MinIO:

```text
s3://ml-artifacts/embeddings/item_embeddings.csv
s3://ml-artifacts/embeddings/user_embeddings.csv
```

and imports into:

```text
item_emb
user_emb
```

Run it with:

```bash
cd vector_db
docker-compose up --build
```

The loader container exits after the import finishes. PostgreSQL keeps running.

Connect from your host machine on port `5433`:

```bash
psql --host=127.0.0.1 --port=5433 --username=postgres --dbname=recommender
```

Password:

```text
postgrespwrd
```

Verify row counts:

```sql
SELECT COUNT(*) FROM item_emb;
SELECT COUNT(*) FROM user_emb;
```

Try a similarity query:

```sql
SELECT other.id,
       base.embedding <=> other.embedding AS distance
FROM item_emb base
JOIN item_emb other ON base.id <> other.id
WHERE base.id = 'S10_1678'
ORDER BY base.embedding <=> other.embedding
LIMIT 5;
```

Stop the stack:

```bash
docker-compose down
```

Delete the PostgreSQL data volume and reload from scratch:

```bash
docker-compose down -v
docker-compose up --build
```

Those artifacts are expected to look like this:

```text
ml-artifacts/
  embeddings/
    item_embeddings.csv
    user_embeddings.csv
  model/
    best_model.pth
  scalers/
    item_ohe.pkl
    item_std_scaler.pkl
    user_ohe.pkl
    user_std_scaler.pkl
```

## Why A Vector Database?

The recommendation model converts users and products into embeddings. An
embedding is a list of numbers that represents the behavior or characteristics of
something.

Example product embedding:

```text
S10_1678 -> [0.12, -0.44, 0.91, ...]
```

Products with similar vectors are treated as similar products. Users with
similar vectors are treated as having similar preferences.

A normal database is good at queries like:

```sql
SELECT * FROM products WHERE productCode = 'S10_1678';
```

A vector database is good at queries like:

```text
Find the 5 products whose embeddings are closest to product S10_1678.
```

Locally, PostgreSQL plus `pgvector` gives us this capability.

## Role In The System

The full local lab has two paths: batch and streaming.

Batch path:

```text
MySQL
  -> PySpark ETL
  -> MinIO training dataset
  -> ML artifacts are produced or provided
```

Vector database setup:

```text
ML artifacts
  -> item_embeddings.csv
  -> user_embeddings.csv
  -> PostgreSQL + pgvector
```

Streaming path:

```text
user activity event
  -> stream processor
  -> recommendation API
  -> vector_db
  -> recommendations
  -> MinIO recommendations bucket
```

The vector database does not replace the model. It stores the embeddings created
by the model so the recommendation API can search for similar users and products
quickly.

## Two Recommendation Patterns

The recommendation model supports two recommendation patterns.

### 1. User-Based Recommendations

The model receives user features, such as:

```text
city
country
creditLimit
```

It converts those features into a user embedding:

```text
user features -> model -> user embedding
```

Then the recommendation API compares that user embedding with product embeddings
to find products the user may like:

```text
user embedding + item embeddings -> recommended products
```

Example:

```text
Customer profile says this user may like products A, B, and C.
```

### 2. Item-Based Recommendations

When a user interacts with a product, the system can find products with similar
embeddings.

```text
selected product -> product embedding -> similar product embeddings
```

Example:

```text
User viewed S10_1678, so recommend similar products S10_1949 and S12_1099.
```

This is where `pgvector` is especially useful. Instead of comparing one product
against every other product manually in Python, PostgreSQL can perform similarity
search using vector distance.

## Local Tables

The vector database uses two tables:

```sql
CREATE TABLE item_emb (
  id varchar PRIMARY KEY,
  embedding vector(32)
);

CREATE TABLE user_emb (
  id int PRIMARY KEY,
  embedding vector(32)
);
```

Local meaning:

```text
item_emb
  productCode -> product embedding

user_emb
  customerNumber -> user embedding
```

Some cloud PostgreSQL environments can load these CSV files from object storage
with provider-specific extensions. Locally, this lab uses a Python loader.

## Incremental Implementation Plan

### Step 1: Collect The ML Artifacts

Copy the provided artifacts into the local `ml-artifacts/` folder and upload
them to the lab 2 MinIO `ml-artifacts` bucket.

Expected files:

```text
embeddings/item_embeddings.csv
embeddings/user_embeddings.csv
model/best_model.pth
scalers/item_ohe.pkl
scalers/item_std_scaler.pkl
scalers/user_ohe.pkl
scalers/user_std_scaler.pkl
```

For the local lab, store them in one or both places:

```text
ml-artifacts/
MinIO bucket: ml-artifacts/
```

### Step 2: Create PostgreSQL With pgvector

Add a Docker Compose service in this folder for PostgreSQL with the `pgvector`
extension enabled.

Expected local service:

```text
container: lab2-vector-db
database: recommender
user: postgres
port: 5433 on the host machine -> 5432 in the container
```

The port should avoid conflicts with any PostgreSQL service from other labs.

### Step 3: Create The Embedding Tables

Initialize the database with:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS item_emb (
  id varchar PRIMARY KEY,
  embedding vector(32)
);

CREATE TABLE IF NOT EXISTS user_emb (
  id int PRIMARY KEY,
  embedding vector(32)
);
```

### Step 4: Load The Embeddings

Load:

```text
item_embeddings.csv -> item_emb
user_embeddings.csv -> user_emb
```

The local version should not use:

```sql
aws_s3.table_import_from_s3(...)
```

Instead, use either:

```text
psql \copy
```

or:

```text
Python loader with psycopg
```

### Step 5: Validate Similarity Search

Run a query that proves the vector database can return similar items.

Example goal:

```text
Given product S10_1678, return the 5 closest products.
```

Conceptually, the query will compare embeddings using a vector distance
operator from `pgvector`.

### Step 6: Connect Recommendation API

After the vector database works, the next local service is:

```text
recommendation_api/
```

That service provides model-style recommendation endpoints.

The stream processor expects endpoints like:

```text
POST /user_embeddings
POST /items_from_user?limit=5
GET  /items_from_item?item_id=<product_code>&limit=5
```

The recommendation API will query `vector_db` to return similar or recommended
items.

### Step 7: Connect Streaming Pipeline

Once the API can query the vector database, the final implementation phase is the
streaming path:

```text
event_producer
  -> streaming_broker
  -> stream_processor
  -> recommendation_api
  -> vector_db
  -> MinIO recommendations bucket
```

## Can We Generate The ML Artifacts?

Technically yes, but that would turn this into an ML training lab.

To generate the artifacts locally, we would need to implement:

```text
ratings_ml_training reader
feature preprocessing
one-hot encoders
standard scalers
PyTorch recommendation model
training loop
model checkpoint export
user embedding export
item embedding export
```

That would produce:

```text
best_model.pth
item_ohe.pkl
item_std_scaler.pkl
user_ohe.pkl
user_std_scaler.pkl
item_embeddings.csv
user_embeddings.csv
```

For this data engineering lab, the recommended path is to use the provided
artifacts first. A simplified local trainer can be added later as an optional
advanced assignment.

## Teaching Notes

This phase is useful for students because it separates responsibilities:

```text
Data engineer:
  prepares training data
  stores model artifacts
  loads embeddings into serving storage
  builds reliable batch and streaming pipelines

Data scientist:
  trains the model
  creates embeddings
  exports model artifacts
```

The vector database is the bridge between those roles. It takes the output of
model training and makes it available to a real-time recommendation system.
