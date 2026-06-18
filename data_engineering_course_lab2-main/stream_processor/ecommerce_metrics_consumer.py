"""
Grupo 3 — Ecommerce Metrics Consumer
======================================
Consume eventos del topic 'user-activity' de Redpanda y calcula:
  - Conteo de eventos por tipo cada minuto (ventana de 1 min)
  - Top 5 productos más vistos (product_view)
  - Guarda automáticamente los resultados agrupados en docs/resultados_metricas.csv

Salida esperada (formato del enunciado):
    Window: 17:58-17:59
    product_view: 320
    add_to_cart: 44
    purchase: 12
    top_product: S18_3029

Uso:
    pip install confluent-kafka
    python ecommerce_metrics_consumer.py

Conecta a localhost:19092 (puerto externo de Redpanda).
"""

import csv
import json
import os
import signal
import sys
from collections import Counter
from datetime import UTC, datetime

from confluent_kafka import Consumer, KafkaException

# ── Configuración ────────────────────────────────────────────────────────────

KAFKA_BOOTSTRAP_SERVERS = "localhost:19092"   # Puerto externo de Redpanda
KAFKA_TOPIC = "user-activity"
KAFKA_GROUP_ID = "grupo3-metrics-consumer"

WINDOW_SECONDS = 60          # Ventana de 1 minuto
QUIET_MODE = os.environ.get("QUIET_MODE", "0") == "1"  # Suprimir logs de eventos individuales
TOP_N_PRODUCTS = 5           # Top N productos más vistos

# Ruta absoluta para el archivo CSV resultante (carpeta docs/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_OUTPUT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "docs", "resultados_metricas.csv"))

RUNNING = True


# ── Señales de shutdown ───────────────────────────────────────────────────────

def handle_shutdown(_sig, _frame) -> None:
    global RUNNING
    RUNNING = False
    print("\n  Señal de parada recibida. Cerrando consumer...\n")


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ── Ventana de Métricas ───────────────────────────────────────────────────────

class MetricsWindow:
    """Acumula métricas para una ventana de tiempo fija y las persiste."""

    def __init__(self, start: datetime) -> None:
        self.start = start
        self.event_counts: Counter = Counter()      # por event_type
        self.product_views: Counter = Counter()     # product_code → vistas
        self.total = 0

    def record(self, event: dict) -> None:
        event_type = event.get("event_type", "unknown")
        product_code = event.get("product_code", "")

        self.event_counts[event_type] += 1
        self.total += 1

        # Solo contar product_view para el ranking de productos
        if event_type == "product_view" and product_code:
            self.product_views[product_code] += 1

    def window_label(self) -> str:
        end = self.start.replace(
            minute=(self.start.minute + 1) % 60,
            second=0,
            microsecond=0,
        )
        return f"{self.start:%H:%M}-{end:%H:%M}"

    def top_products(self, n: int = TOP_N_PRODUCTS) -> list[tuple[str, int]]:
        return self.product_views.most_common(n)

    def print_report(self) -> None:
        sep = "=" * 50
        print(sep)
        print(f"Window: {self.window_label()}")
        print(f"Total eventos en ventana: {self.total}")
        print()

        # Conteo por tipo de evento (orden descendente)
        if self.event_counts:
            for event_type, count in sorted(
                self.event_counts.items(), key=lambda x: -x[1]
            ):
                print(f"  {event_type}: {count}")
        else:
            print("  (sin eventos en esta ventana)")

        print()

        # Top 5 productos más vistos
        top = self.top_products()
        if top:
            top_code, top_count = top[0]
            print(f"top_product: {top_code}")
            print()
            print(f"  Top {TOP_N_PRODUCTS} productos (product_view):")
            for rank, (code, views) in enumerate(top, start=1):
                print(f"    {rank}. {code} — {views} vistas")
        else:
            print("top_product: (ningún product_view en esta ventana)")

        print(sep)
        print()

    def save_to_csv(self, filepath: str) -> None:
        """Guarda la información de la ventana en el archivo CSV especificado."""
        end = self.start.replace(
            minute=(self.start.minute + 1) % 60,
            second=0,
            microsecond=0,
        )
        window_start_str = self.start.strftime("%Y-%m-%d %H:%M:%S")
        window_end_str = end.strftime("%Y-%m-%d %H:%M:%S")

        # Formatear el top 5 de productos como cadena de texto
        top_5 = self.top_products()
        top_5_str = "; ".join([f"{code}({views})" for code, views in top_5])
        top_prod = top_5[0][0] if top_5 else ""

        # Verificar si el archivo ya existe para escribir las cabeceras
        file_exists = os.path.exists(filepath)

        # Crear directorios padres si no existen
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "window_start", "window_end", "total_events",
                    "product_view", "add_to_cart", "purchase",
                    "top_product", "top_5_products"
                ])
            writer.writerow([
                window_start_str,
                window_end_str,
                self.total,
                self.event_counts.get("product_view", 0),
                self.event_counts.get("add_to_cart", 0),
                self.event_counts.get("purchase", 0),
                top_prod,
                top_5_str
            ])


# ── Helpers ───────────────────────────────────────────────────────────────────

def current_window_start() -> datetime:
    """Retorna el inicio del minuto actual (truncado a segundos 0)."""
    now = datetime.now(UTC)
    return now.replace(second=0, microsecond=0)


def parse_event(raw_value: bytes) -> dict | None:
    try:
        return json.loads(raw_value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"  ⚠ No se pudo parsear mensaje: {e}")
        return None


# ── Consumer principal ────────────────────────────────────────────────────────

def create_consumer() -> Consumer:
    return Consumer(
        {
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "latest",       # Leer eventos nuevos
            "enable.auto.commit": True,
        }
    )


def main() -> int:
    print("=" * 60)
    print("  Grupo 3 — Ecommerce Metrics Consumer")
    print("=" * 60)
    print(f"  Broker    : {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"  Topic     : {KAFKA_TOPIC}")
    print(f"  Group ID  : {KAFKA_GROUP_ID}")
    print(f"  Ventana   : {WINDOW_SECONDS}s  |  Top productos: {TOP_N_PRODUCTS}")
    print(f"  CSV Output: {CSV_OUTPUT_PATH}")
    print("=" * 60)
    print("  Esperando eventos... (Ctrl+C para detener)\n")

    consumer = create_consumer()
    consumer.subscribe([KAFKA_TOPIC])

    window = MetricsWindow(start=current_window_start())

    try:
        while RUNNING:
            message = consumer.poll(timeout=1.0)

            # ── Revisar si la ventana expiró ──────────────────────────────
            now_window = current_window_start()
            if now_window > window.start:
                # Imprimir reporte de la ventana que cerró
                window.print_report()
                # Guardar métricas de la ventana expirada en CSV
                try:
                    window.save_to_csv(CSV_OUTPUT_PATH)
                    print(f"  → Métricas guardadas en: {CSV_OUTPUT_PATH}\n")
                except Exception as e:
                    print(f"  ⚠ Error al guardar CSV: {e}\n")
                # Abrir nueva ventana
                window = MetricsWindow(start=now_window)

            # ── Procesar mensaje ──────────────────────────────────────────
            if message is None:
                continue

            if message.error():
                raise KafkaException(message.error())

            event = parse_event(message.value())
            if event is None:
                continue

            window.record(event)

            # Log en tiempo real de cada evento recibido (solo si no estamos en modo silencioso)
            if not QUIET_MODE:
                print(
                    f"  ← [{event.get('event_time', '?')}] "
                    f"customer={event.get('customer_id', '?'):<4}  "
                    f"type={event.get('event_type', '?'):<14}  "
                    f"product={event.get('product_code', '?')}"
                )

    except KafkaException as e:
        print(f"\n  Error de Kafka: {e}", file=sys.stderr)
        return 1
    finally:
        # Imprimir la ventana parcial al cerrar y guardarla
        if window.total > 0:
            print("\n  (Ventana parcial al cerrar)")
            window.print_report()
            try:
                window.save_to_csv(CSV_OUTPUT_PATH)
                print(f"  → Métricas parciales guardadas en: {CSV_OUTPUT_PATH}\n")
            except Exception as e:
                print(f"  ⚠ Error al guardar CSV parcial: {e}\n")
        consumer.close()
        print("  Consumer detenido.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
