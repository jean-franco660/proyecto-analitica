"""
Demo Grupo 3 — Corre producer + consumer juntos.

El producer corre en background (silencioso).
El consumer imprime directamente en este terminal con QUIET_MODE=1
(solo reportes de ventana, sin eventos individuales).

Uso: python run_grupo3_demo.py
Detener: Ctrl+C
"""
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(BASE)
PRODUCER_DIR = os.path.join(PARENT, "event_producer")
PROCESSOR_DIR = os.path.join(PARENT, "stream_processor")

DURATION = 600  # segundos (10 min) — captura ~10 ventanas completas de 1 minuto


def main():
    print("=" * 60)
    print("  Grupo 3 Demo — Producer + Consumer")
    print(f"  Duración: {DURATION}s  |  Solo reportes de ventana")
    print("=" * 60)

    # ── Producer en background, output silenciado ─────────────────
    producer = subprocess.Popen(
        [sys.executable, "-u", "ecommerce_producer.py"],
        cwd=PRODUCER_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"\n  ✓ Producer iniciado (PID {producer.pid})")

    # ── Consumer directo al terminal con QUIET_MODE ───────────────
    env = os.environ.copy()
    env["QUIET_MODE"] = "1"
    env["PYTHONUNBUFFERED"] = "1"

    print(f"  ✓ Lanzando consumer en QUIET_MODE...")
    print(f"  → Esperando {DURATION}s (presiona Ctrl+C para detener antes)\n")
    print("-" * 60)

    consumer = subprocess.Popen(
        [sys.executable, "-u", "ecommerce_metrics_consumer.py"],
        cwd=PROCESSOR_DIR,
        env=env,
        # stdout/stderr heredados del proceso padre → salen directo al terminal
    )
    print(f"  (Consumer PID {consumer.pid} corriendo...)\n")

    try:
        time.sleep(DURATION)
    except KeyboardInterrupt:
        print("\n  Ctrl+C detectado — deteniendo...")
    finally:
        producer.terminate()
        consumer.terminate()
        consumer.wait(timeout=5)
        producer.wait(timeout=5)
        print("\n  ✓ Demo finalizado.")


if __name__ == "__main__":
    main()
