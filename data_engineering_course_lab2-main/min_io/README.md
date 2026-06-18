# Lab 2 Local MinIO Service

This folder starts a local MinIO service for lab 2. MinIO is an
S3-compatible object store, so it plays the object-storage role for the local
batch and streaming pipelines.

In the AWS lab, S3 stores:

- batch ETL output from AWS Glue
- ML artifacts such as embeddings and model files
- streaming recommendation output from Firehose

In this local lab, MinIO stores those same categories of files.

## Buckets

The Compose setup creates three buckets:

```text
classicmodels-lab2
ml-artifacts
recommendations
```

During startup, Compose also copies the local `../ml-artifacts/` folder into
the `ml-artifacts` bucket. This makes the pretrained embeddings, model file,
and scalers available in MinIO as soon as the service starts.

Purpose:

| Bucket | Purpose |
| --- | --- |
| `classicmodels-lab2` | Data lake bucket for batch ETL output such as `ratings_ml_training`. |
| `ml-artifacts` | Local replacement for the AWS ML artifacts bucket. Store embeddings, model files, and scalers here. |
| `recommendations` | Output bucket for enriched streaming recommendation events. |

## Start MinIO

From this folder:

```bash
docker-compose up -d
```

Or, with the newer Docker Compose plugin:

```bash
docker compose up -d
```

After startup, the `ml-artifacts` bucket should contain:

```text
embeddings/item_embeddings.csv
embeddings/user_embeddings.csv
model/best_model.pth
scalers/item_ohe.pkl
scalers/item_std_scaler.pkl
scalers/user_ohe.pkl
scalers/user_std_scaler.pkl
```

## Open the Console

Lab 1 already uses ports `9000` and `9001`, so lab 2 uses `9100` and `9101`.

Open:

```text
http://localhost:9101
```

Login:

```text
Username: minioadmin
Password: minioadmin
```

## S3 Endpoint

Applications inside Docker should use:

```text
http://classicmodels-lab2-minio:9000
```

Applications running on the host machine should use:

```text
http://localhost:9100
```

Example credentials:

```text
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
S3_ENDPOINT=http://localhost:9100
S3_BUCKET=classicmodels-lab2
```

## Stop MinIO

```bash
docker-compose down
```

## Reset MinIO Data

This deletes the local MinIO volume and recreates empty buckets.

```bash
docker-compose down -v
docker-compose up -d
```

## AWS Mapping

| AWS S3 concept | Local MinIO equivalent |
| --- | --- |
| Data lake bucket | `classicmodels-lab2` |
| ML artifacts bucket | `ml-artifacts` |
| Recommendations bucket | `recommendations` |
| S3 API endpoint | `http://localhost:9100` |
| S3 console | `http://localhost:9101` |
