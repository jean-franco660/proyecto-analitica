import json
import os
import random
import signal
import sys
import time
from datetime import UTC, datetime
from typing import Any

import boto3
import pymysql
import requests
from confluent_kafka import Consumer, KafkaException


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-activity")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "lab2-stream-processor")

RECOMMENDATION_API_URL = os.getenv(
    "RECOMMENDATION_API_URL",
    "http://lab2-recommendation-api:8000",
).rstrip("/")
ITEM_LIMIT = int(os.getenv("ITEM_LIMIT", "5"))

MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "classicmodels")
MYSQL_USER = os.getenv("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "adminpwrd")

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "recommendations")

RUNNING = True


def handle_shutdown(_signum, _frame) -> None:
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def log(message: str) -> None:
    print(message, flush=True)


def connect_mysql():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )


def load_product_catalog() -> dict[str, dict[str, Any]]:
    with connect_mysql() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT productCode,
                       productName,
                       productLine,
                       productVendor,
                       MSRP
                FROM products;
                """
            )
            rows = cursor.fetchall()

    return {
        row["productCode"]: {
            "product_code": row["productCode"],
            "product_name": row["productName"],
            "product_line": row["productLine"],
            "product_vendor": row["productVendor"],
            "msrp": float(row["MSRP"]),
        }
        for row in rows
    }


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY_ID,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        region_name="us-east-1",
    )


def get_user_embedding(event: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{RECOMMENDATION_API_URL}/user_embeddings",
        json=[
            {
                "customerNumber": event.get("customer_number"),
                "city": event.get("city"),
                "country": event.get("country"),
                "credit_limit": event.get("credit_limit"),
            }
        ],
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    return payload[0] if isinstance(payload, list) else payload


def get_items_from_user(user_embedding: dict[str, Any]) -> list[dict[str, Any]]:
    response = requests.post(
        f"{RECOMMENDATION_API_URL}/items_from_user",
        params={"limit": ITEM_LIMIT},
        json=user_embedding,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_items_from_item(product_code: str) -> list[dict[str, Any]]:
    response = requests.get(
        f"{RECOMMENDATION_API_URL}/items_from_item",
        params={"item_id": product_code, "limit": ITEM_LIMIT},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def product_info(product_code: str, catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return catalog.get(
        product_code,
        {
            "product_code": product_code,
            "product_name": "Unknown product",
            "product_line": None,
            "product_vendor": None,
            "msrp": None,
        },
    )


def enrich_recommendations(
    recommendations: list[dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched = []
    for item in recommendations:
        metadata = product_info(item["id"], catalog)
        enriched.append(
            {
                **metadata,
                "score": item.get("score"),
                "distance": item.get("distance"),
            }
        )

    return enriched


def enrich_browse_history(
    browse_history: list[dict[str, Any]],
    catalog: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    enriched = []
    for item in browse_history:
        product_code = item.get("product_code")
        if not product_code:
            continue
        enriched.append(product_info(product_code, catalog))

    return enriched


def choose_selected_product(browse_history: list[dict[str, Any]]) -> str:
    product_codes = [
        item.get("product_code")
        for item in browse_history
        if item.get("product_code")
    ]
    if not product_codes:
        raise ValueError("Event does not contain browse_history product_code values")

    return random.choice(product_codes)


def parse_event_time(event: dict[str, Any]) -> datetime:
    event_time = event.get("event_time")
    if not event_time:
        return datetime.now(UTC)

    try:
        parsed = datetime.fromisoformat(str(event_time).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(UTC)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)

    return parsed.astimezone(UTC)


def recommendation_key(event: dict[str, Any]) -> str:
    event_dt = parse_event_time(event)
    event_id = event.get("event_id") or f"{int(time.time() * 1000)}"
    return (
        f"year={event_dt:%Y}/"
        f"month={event_dt:%m}/"
        f"day={event_dt:%d}/"
        f"hour={event_dt:%H}/"
        f"{event_id}.json"
    )


def write_to_minio(s3_client, event: dict[str, Any]) -> str:
    key = recommendation_key(event)
    body = json.dumps(event, indent=2).encode("utf-8")
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    return key


def format_product_line(index: int, item: dict[str, Any]) -> str:
    score = item.get("score")
    score_text = f" score={score:.3f}" if isinstance(score, (int, float)) else ""
    return (
        f"  {index}. {item['product_name']} "
        f"({item['product_code']}, {item.get('product_line')}){score_text}"
    )


def log_recommendation_summary(event: dict[str, Any], minio_key: str) -> None:
    line = "=" * 72
    log(line)
    log(
        f"[{event.get('event_time')}] "
        f"Customer {event.get('customer_number')} from {event.get('city')}, "
        f"{event.get('country')} | {event.get('event_type')}"
    )
    log("Visited / browsed products:")
    for index, item in enumerate(event["browse_history_enriched"], start=1):
        log(f"  {index}. {item['product_name']} ({item['product_code']}, {item['product_line']})")

    log("")
    log("Recommended for this user:")
    for index, item in enumerate(event["recommended_items"], start=1):
        log(format_product_line(index, item))

    selected = event["similar_items"]["selected_product"]
    log("")
    log(f"Similar to: {selected['product_name']} ({selected['product_code']})")
    for index, item in enumerate(event["similar_items"]["items"], start=1):
        log(format_product_line(index, item))

    log("")
    log(f"Wrote enriched event to MinIO: s3://{S3_BUCKET}/{minio_key}")
    log(line)


def process_event(
    event: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    s3_client,
) -> str:
    browse_history = event.get("browse_history") or []
    selected_product_code = choose_selected_product(browse_history)

    user_embedding = get_user_embedding(event)
    recommended_items = get_items_from_user(user_embedding)
    similar_items = get_items_from_item(selected_product_code)

    enriched = {
        **event,
        "browse_history_enriched": enrich_browse_history(browse_history, catalog),
        "user_embedding_id": user_embedding.get("id"),
        "recommended_items": enrich_recommendations(recommended_items, catalog),
        "similar_items": {
            "selected_product": product_info(selected_product_code, catalog),
            "items": enrich_recommendations(similar_items, catalog),
        },
        "processed_at": datetime.now(UTC).isoformat(),
    }

    minio_key = write_to_minio(s3_client, enriched)
    log_recommendation_summary(enriched, minio_key)
    return minio_key


def create_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "latest",
            "enable.auto.commit": False,
        }
    )


def main() -> int:
    log("Starting stream processor")
    log(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS} topic={KAFKA_TOPIC} group={KAFKA_GROUP_ID}")
    log(f"Recommendation API: {RECOMMENDATION_API_URL}")
    log(f"MinIO output: s3://{S3_BUCKET}")

    catalog = load_product_catalog()
    log(f"Loaded {len(catalog)} products from MySQL")

    s3_client = get_s3_client()
    consumer = create_consumer()
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while RUNNING:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                raise KafkaException(message.error())

            try:
                event = json.loads(message.value().decode("utf-8"))
                process_event(event, catalog, s3_client)
                consumer.commit(message=message, asynchronous=False)
            except Exception as error:  # noqa: BLE001 - keep stream alive for demos.
                log(f"Failed to process message at offset {message.offset()}: {error}")
    finally:
        log("Stopping stream processor")
        consumer.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
