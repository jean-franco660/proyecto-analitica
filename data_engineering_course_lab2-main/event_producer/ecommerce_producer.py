"""
Grupo 3 — Ecommerce Event Producer
===================================
Emite eventos de actividad ecommerce al topic 'user-activity' de Redpanda.

Esquema del evento (según enunciado Grupo 3):
{
    "event_id": "evt-001",
    "customer_id": 276,
    "event_type": "product_view",
    "product_code": "S18_3029",
    "event_time": "2026-05-29T17:58:28Z"
}

Uso:
    pip install confluent-kafka
    python ecommerce_producer.py

El producer conecta a localhost:19092 (puerto externo de Redpanda).
Para ajustar la tasa de eventos: cambia EVENTS_PER_SECOND.
"""

import json
import random
import time
import uuid
from datetime import UTC, datetime

from confluent_kafka import Producer

# ── Configuración ────────────────────────────────────────────────────────────

KAFKA_BOOTSTRAP_SERVERS = "localhost:19092"   # Puerto externo de Redpanda
KAFKA_TOPIC = "user-activity"
EVENTS_PER_SECOND = 5          # Ajusta para más o menos volumen
PRINT_EVERY_N = 10             # Mostrar en consola cada N eventos

# Tipos de evento del enunciado
EVENT_TYPES = ["product_view", "add_to_cart", "purchase"]

# Pesos para que product_view sea el más frecuente (simula comportamiento real)
EVENT_WEIGHTS = [0.70, 0.20, 0.10]

# Productos del catálogo classicmodels (muestra representativa)
PRODUCT_CODES = [
    "S10_1678", "S10_1949", "S10_2016", "S10_4698", "S10_4757",
    "S12_1099", "S12_1108", "S12_2823", "S12_3148", "S12_3380",
    "S18_1097", "S18_1129", "S18_1342", "S18_1367", "S18_1589",
    "S18_1749", "S18_1984", "S18_2238", "S18_2319", "S18_2432",
    "S18_2581", "S18_2625", "S18_2795", "S18_2870", "S18_2949",
    "S18_3029", "S18_3136", "S18_3140", "S18_3232", "S18_3259",
    "S18_3278", "S18_3320", "S18_3482", "S18_3685", "S18_3782",
    "S18_4027", "S18_4409", "S18_4522", "S24_1046", "S24_1444",
    "S24_1578", "S24_1628", "S24_2000", "S24_2011", "S24_2022",
    "S24_2360", "S24_2972", "S24_3151", "S24_3420", "S24_3432",
    "S24_3816", "S24_3949", "S24_4048", "S24_4258", "S24_4278",
    "S32_1268", "S32_1374", "S32_2206", "S32_3207", "S32_4485",
    "S50_1341", "S50_1392", "S50_1514", "S50_4713", "S72_1253",
    "S700_1138", "S700_1938", "S700_2466", "S700_2610", "S700_2824",
    "S700_3167", "S700_3505", "S700_3962", "S700_4002",
]

# Rango de customer_id (refleja los customerNumber de classicmodels)
CUSTOMER_IDS = list(range(103, 500))


# ── Kafka Producer ────────────────────────────────────────────────────────────

def make_producer() -> Producer:
    return Producer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "linger.ms": 5,               # Micro-batching para eficiencia
            "acks": "all",
        }
    )


def delivery_callback(err, msg) -> None:
    if err is not None:
        print(f"  ✗ Delivery error: {err}")


# ── Generación de Eventos ─────────────────────────────────────────────────────

def build_event() -> dict:
    """Construye un evento con el esquema exacto del enunciado Grupo 3."""
    return {
        "event_id": f"evt-{uuid.uuid4().hex[:8]}",
        "customer_id": random.choice(CUSTOMER_IDS),
        "event_type": random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS, k=1)[0],
        "product_code": random.choice(PRODUCT_CODES),
        "event_time": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Grupo 3 — Ecommerce Event Producer")
    print("=" * 60)
    print(f"  Broker   : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Topic    : {KAFKA_TOPIC}")
    print(f"  Rate     : {EVENTS_PER_SECOND} eventos/segundo")
    print(f"  Tipos    : {', '.join(EVENT_TYPES)}")
    print("=" * 60)
    print("  Presiona Ctrl+C para detener.\n")

    producer = make_producer()
    sleep_seconds = 1.0 / EVENTS_PER_SECOND

    produced = 0
    try:
        while True:
            event = build_event()
            payload = json.dumps(event)

            producer.produce(
                topic=KAFKA_TOPIC,
                key=str(event["customer_id"]),
                value=payload,
                callback=delivery_callback,
            )
            producer.poll(0)
            produced += 1

            # Log en consola cada N eventos
            if produced % PRINT_EVERY_N == 0:
                print(
                    f"  [{event['event_time']}] #{produced:>6} "
                    f"customer={event['customer_id']:<4} "
                    f"type={event['event_type']:<14} "
                    f"product={event['product_code']}"
                )

            time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        print(f"\n  Stopping — flushing {producer.__len__()} mensajes pendientes...")
    finally:
        producer.flush(10)
        print(f"  Total producidos: {produced} eventos")
        print("  Producer detenido.")


if __name__ == "__main__":
    main()
