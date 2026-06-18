import csv
import io
import os
import time

import boto3
import psycopg


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "recommender")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespwrd")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "ml-artifacts")
ITEM_EMBEDDINGS_KEY = os.getenv(
    "ITEM_EMBEDDINGS_KEY",
    "embeddings/item_embeddings.csv",
)
USER_EMBEDDINGS_KEY = os.getenv(
    "USER_EMBEDDINGS_KEY",
    "embeddings/user_embeddings.csv",
)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        region_name="us-east-1",
    )


def read_csv_from_s3(s3_client, key):
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
    body = response["Body"].read().decode("utf-8")
    return csv.DictReader(io.StringIO(body))


def wait_for_postgres():
    last_error = None
    for _ in range(30):
        try:
            return psycopg.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
            )
        except psycopg.OperationalError as error:
            last_error = error
            time.sleep(2)

    raise RuntimeError(f"PostgreSQL did not become ready: {last_error}")


def load_items(connection, rows):
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE item_emb;")

        count = 0
        for row in rows:
            cursor.execute(
                """
                INSERT INTO item_emb (id, embedding)
                VALUES (%s, %s::vector)
                ON CONFLICT (id) DO UPDATE
                SET embedding = EXCLUDED.embedding;
                """,
                (row["id"], row["embedding"]),
            )
            count += 1

    connection.commit()
    return count


def load_users(connection, rows):
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE user_emb;")

        count = 0
        for row in rows:
            cursor.execute(
                """
                INSERT INTO user_emb (id, embedding)
                VALUES (%s, %s::vector)
                ON CONFLICT (id) DO UPDATE
                SET embedding = EXCLUDED.embedding;
                """,
                (int(row["id"]), row["embedding"]),
            )
            count += 1

    connection.commit()
    return count


def create_indexes(connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS item_emb_embedding_idx
            ON item_emb
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 10);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS user_emb_embedding_idx
            ON user_emb
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 10);
            """
        )
        cursor.execute("ANALYZE item_emb;")
        cursor.execute("ANALYZE user_emb;")

    connection.commit()


def main():
    print(f"Reading embeddings from MinIO bucket {S3_BUCKET}", flush=True)
    s3_client = get_s3_client()

    item_rows = list(read_csv_from_s3(s3_client, ITEM_EMBEDDINGS_KEY))
    user_rows = list(read_csv_from_s3(s3_client, USER_EMBEDDINGS_KEY))

    print(f"Read {len(item_rows)} item embeddings", flush=True)
    print(f"Read {len(user_rows)} user embeddings", flush=True)

    with wait_for_postgres() as connection:
        item_count = load_items(connection, item_rows)
        user_count = load_users(connection, user_rows)
        create_indexes(connection)

    print(f"Loaded {item_count} item embeddings into item_emb", flush=True)
    print(f"Loaded {user_count} user embeddings into user_emb", flush=True)
    print("Vector database is ready", flush=True)


if __name__ == "__main__":
    main()
