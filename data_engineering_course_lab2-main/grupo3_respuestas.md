# Grupo 3 — Proyecto Kafka: Respuestas de Discusión

## Entregable de Métricas (Formato esperado)

```text
Window: 17:58-17:59
product_view: 320
add_to_cart: 44
purchase: 12
top_product: S18_3029
```

---

## Preguntas de Discusión

### ¿Qué es un topic?

Un **topic** es un canal nombrado dentro del broker Kafka/Redpanda donde los
producers publican mensajes y los consumers los leen.

- Es como una carpeta de correos: el topic `user-activity` recibe todos los
  eventos de la tienda (vistas de productos, carritos, compras).
- Los topics se dividen en **particiones** para escalar horizontalmente.
- Los mensajes se retienen durante un tiempo configurable (retention), no se
  borran inmediatamente después de ser consumidos.

En este proyecto usamos el topic:

```text
user-activity
```

Creado con 3 particiones y factor de replicación 1.

---

### ¿Cuál es la diferencia entre producer y consumer?

| Concepto | Producer | Consumer |
|---|---|---|
| **Rol** | Escribe mensajes al topic | Lee mensajes del topic |
| **Dirección** | Push (empuja datos al broker) | Pull (jala datos del broker) |
| **Dependencia** | No necesita saber quién lee | No necesita saber quién escribe |
| **En este proyecto** | `ecommerce_producer.py` emite eventos de actividad | `ecommerce_metrics_consumer.py` calcula métricas |

El **producer** genera el evento cuando el usuario ve un producto:

```python
producer.produce(topic="user-activity", key="276", value='{"event_type": "product_view", ...}')
```

El **consumer** lee ese mismo evento y actualiza sus contadores:

```python
message = consumer.poll(1.0)
event = json.loads(message.value())
window.record(event)
```

---

### ¿Por qué los sistemas de streaming usan offsets?

Un **offset** es el número de posición de un mensaje dentro de una partición.
Empieza en 0 y aumenta con cada mensaje nuevo.

```text
Partición 0:
  offset 0 → {"event_type": "product_view", "product_code": "S18_3029"}
  offset 1 → {"event_type": "add_to_cart",  "product_code": "S18_3029"}
  offset 2 → {"event_type": "purchase",      "product_code": "S18_3029"}
```

El consumer guarda en el broker **hasta qué offset leyó**. Esto permite:

1. **Retomar donde se quedó**: si el consumer se reinicia, sigue desde el offset
   guardado sin repetir ni perder mensajes.
2. **Múltiples consumers independientes**: diferentes grupos de consumers pueden
   tener offsets distintos en el mismo topic (uno para métricas, otro para
   recomendaciones).
3. **Replay**: es posible resetear el offset al inicio para reprocesar datos
   históricos.

Sin offsets, el broker no sabría qué ya fue procesado y qué no.

---

### ¿Qué pasa si el consumer está fuera de línea durante unos minutos?

Redpanda (y Kafka) **retiene los mensajes en disco** durante el período de
retención configurado (por defecto, 1 semana).

Escenario:

```text
17:55 — Producer emite 300 eventos por minuto
17:58 — Consumer cae (se reinicia el servidor)
18:02 — Consumer vuelve en línea
```

Cuando el consumer reconecta:
1. Lee su último **offset guardado** (por ejemplo, offset 714 de las 17:57).
2. Consume todos los mensajes que se acumularon entre 17:57 y 18:02 (~1500 eventos).
3. Los procesa en ráfaga hasta alcanzar al producer.
4. Las métricas de las ventanas 17:57, 17:58, 17:59, 18:00 y 18:01 se calculan
   correctamente aunque el consumer los lea en 18:02.

> **Clave**: Los mensajes no se pierden. El consumer simplemente llega tarde
> y se pone al día.

---

### ¿Por qué un broker es útil entre la aplicación y el procesador?

Sin broker (llamada directa):

```text
Event Producer ──── HTTP call ───→ Stream Processor
```

**Problemas**:
- Si el procesador cae, el evento se pierde.
- El producer tiene que esperar a que el procesador responda (acoplamiento).
- Si hay picos de tráfico, el procesador puede saturarse.

Con broker Redpanda:

```text
Event Producer → topic user-activity → Stream Processor
                     (Redpanda)
```

**Ventajas**:
- **Desacoplamiento temporal**: el producer escribe sin importar si el consumer
  está disponible.
- **Durabilidad**: los eventos se guardan en disco hasta ser procesados.
- **Escalabilidad**: múltiples consumers pueden leer el mismo topic de forma
  independiente (métricas + recomendaciones + alertas al mismo tiempo).
- **Tolerancia a fallos**: si el procesador cae y vuelve, retoma desde donde
  quedó gracias a los offsets.
- **Buffer natural**: amortigua picos de tráfico; el procesador procesa a su
  propio ritmo.

En este proyecto Redpanda actúa como el "buzón" entre el sitio web (producer)
y el motor de métricas/recomendaciones (consumer).

---

## Cómo Ejecutar el Proyecto

### 1. Levantar Redpanda (broker)

```bash
cd streaming_broker
docker-compose up -d
docker exec -it lab2-redpanda rpk topic list
# Debe mostrar: user-activity
```

### 2. Terminal 1 — Producer

```bash
cd event_producer
pip install confluent-kafka
python ecommerce_producer.py
```

### 3. Terminal 2 — Consumer con métricas

```bash
cd stream_processor
pip install confluent-kafka
python ecommerce_metrics_consumer.py
```

### Verificar topic manualmente

```bash
# Publicar un evento de prueba
docker exec -i lab2-redpanda rpk topic produce user-activity <<'EOF'
{"event_id":"evt-001","customer_id":276,"event_type":"product_view","product_code":"S18_3029","event_time":"2026-05-29T17:58:28Z"}
EOF

# Consumir el evento
docker exec -it lab2-redpanda rpk topic consume user-activity --num 1 --offset start
```
