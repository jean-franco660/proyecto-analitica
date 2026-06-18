import json
import os
import random
import threading
import time
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pymysql
from confluent_kafka import Producer
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "classicmodels")
MYSQL_USER = os.getenv("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "adminpwrd")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-activity")
DEFAULT_INTERVAL_SECONDS = float(os.getenv("DEFAULT_INTERVAL_SECONDS", "5"))
MAX_BROWSE_HISTORY_ITEMS = int(os.getenv("MAX_BROWSE_HISTORY_ITEMS", "5"))

EVENT_TYPES = [
    "product_view",
    "add_to_cart",
    "product_search",
    "checkout_started",
]


app = FastAPI(
    title="Lab 2 Event Producer",
    description=(
        "Controlled producer for simulated user activity events. "
        "It reads real customers/products from MySQL and publishes JSON events "
        "to the Redpanda user-activity topic."
    ),
    version="0.1.0",
)


class StartRequest(BaseModel):
    interval_seconds: float | None = None


class ProducerState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.running = False
        self.interval_seconds = DEFAULT_INTERVAL_SECONDS
        self.produced_count = 0
        self.failed_count = 0
        self.last_event: dict[str, Any] | None = None
        self.last_error: str | None = None
        self.customers: list[dict[str, Any]] = []
        self.products: list[str] = []
        self.producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS})


state = ProducerState()


def connect_mysql():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor,
    )


def load_source_data() -> tuple[list[dict[str, Any]], list[str]]:
    with connect_mysql() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT customerNumber,
                       city,
                       country,
                       creditLimit
                FROM customers
                WHERE creditLimit IS NOT NULL
                ORDER BY customerNumber;
                """
            )
            customers = list(cursor.fetchall())

            cursor.execute(
                """
                SELECT productCode
                FROM products
                ORDER BY productCode;
                """
            )
            products = [row["productCode"] for row in cursor.fetchall()]

    if not customers:
        raise RuntimeError("No customers were found in MySQL")
    if not products:
        raise RuntimeError("No products were found in MySQL")

    return customers, products


def delivery_callback(error, message) -> None:
    with state.lock:
        if error is not None:
            state.failed_count += 1
            state.last_error = str(error)
            return

        state.last_error = None


def build_event() -> dict[str, Any]:
    customer = random.choice(state.customers)
    history_size = random.randint(1, min(MAX_BROWSE_HISTORY_ITEMS, len(state.products)))
    selected_products = random.sample(state.products, history_size)

    return {
        "event_id": str(uuid4()),
        "event_time": datetime.now(UTC).isoformat(),
        "event_type": random.choice(EVENT_TYPES),
        "customer_number": int(customer["customerNumber"]),
        "city": customer["city"],
        "country": customer["country"],
        "credit_limit": float(customer["creditLimit"]),
        "browse_history": [
            {"product_code": product_code}
            for product_code in selected_products
        ],
    }


def publish_event(event: dict[str, Any]) -> None:
    payload = json.dumps(event, separators=(",", ":"))
    state.producer.produce(
        KAFKA_TOPIC,
        key=str(event["customer_number"]),
        value=payload,
        callback=delivery_callback,
    )
    state.producer.poll(0)
    state.producer.flush(5)

    with state.lock:
        state.produced_count += 1
        state.last_event = event


def producer_loop() -> None:
    while not state.stop_event.is_set():
        try:
            event = build_event()
            publish_event(event)
        except Exception as error:  # noqa: BLE001 - keep producer alive for demos.
            with state.lock:
                state.failed_count += 1
                state.last_error = str(error)

        state.stop_event.wait(state.interval_seconds)

    with state.lock:
        state.running = False


@app.get("/health")
def health() -> dict[str, str]:
    customers, products = load_source_data()
    return {
        "status": "ok",
        "customers": str(len(customers)),
        "products": str(len(products)),
        "topic": KAFKA_TOPIC,
    }


@app.get("/status")
def status() -> dict[str, Any]:
    with state.lock:
        return {
            "running": state.running,
            "interval_seconds": state.interval_seconds,
            "produced_count": state.produced_count,
            "failed_count": state.failed_count,
            "last_error": state.last_error,
            "last_event": state.last_event,
            "kafka_bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
            "topic": KAFKA_TOPIC,
            "cached_customers": len(state.customers),
            "cached_products": len(state.products),
        }


@app.post("/start")
def start(request: StartRequest | None = None) -> dict[str, Any]:
    with state.lock:
        if state.running:
            already_running = True
        else:
            already_running = False

    if already_running:
        return status()

    with state.lock:
        interval = (
            request.interval_seconds
            if request and request.interval_seconds is not None
            else DEFAULT_INTERVAL_SECONDS
        )
        if interval <= 0:
            raise HTTPException(
                status_code=400,
                detail="interval_seconds must be greater than 0",
            )

        try:
            customers, products = load_source_data()
        except Exception as error:  # noqa: BLE001 - return readable API error.
            raise HTTPException(status_code=500, detail=str(error)) from error

        state.customers = customers
        state.products = products
        state.interval_seconds = interval
        state.stop_event.clear()
        state.running = True
        state.thread = threading.Thread(target=producer_loop, daemon=True)
        state.thread.start()

    return status()


@app.post("/stop")
def stop() -> dict[str, Any]:
    with state.lock:
        if not state.running:
            already_stopped = True
            thread = None
        else:
            already_stopped = False
            state.stop_event.set()
            thread = state.thread

    if already_stopped:
        return status()

    if thread:
        thread.join(timeout=10)

    return status()


@app.post("/produce_once")
def produce_once() -> dict[str, Any]:
    with state.lock:
        if not state.customers or not state.products:
            try:
                customers, products = load_source_data()
            except Exception as error:  # noqa: BLE001 - return readable API error.
                raise HTTPException(status_code=500, detail=str(error)) from error

            state.customers = customers
            state.products = products

    event = build_event()
    publish_event(event)
    return event


@app.get("/sample_event")
def sample_event(
    customer_number: int | None = Query(
        default=None,
        description="Optional customer number to force into the sample event",
    ),
) -> dict[str, Any]:
    customers, products = load_source_data()

    with state.lock:
        state.customers = customers
        state.products = products

    event = build_event()
    if customer_number is not None:
        matching_customer = next(
            (
                customer
                for customer in customers
                if int(customer["customerNumber"]) == customer_number
            ),
            None,
        )
        if matching_customer is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_number} was not found",
            )

        event["customer_number"] = int(matching_customer["customerNumber"])
        event["city"] = matching_customer["city"]
        event["country"] = matching_customer["country"]
        event["credit_limit"] = float(matching_customer["creditLimit"])

    return event
