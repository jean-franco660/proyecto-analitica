# Lab 2 Event Producer

This service simulates sales-platform user activity for the local streaming
pipeline.

It reads real customers and product codes from the lab 2 MySQL database, builds
JSON activity events, and publishes them to Redpanda:

```text
MySQL classicmodels
  -> event_producer
  -> Redpanda topic: user-activity
```

The producer has an HTTP control API, so you can start and stop event generation
without stopping the container.

## Role In The System

The local streaming path is:

```text
event_producer
  -> streaming_broker
  -> stream_processor
  -> recommendation_api
  -> MinIO recommendations bucket
```

This folder implements the first part:

```text
event_producer -> streaming_broker
```

## Services

The Compose stack starts:

```text
lab2-event-producer
```

API URL:

```text
http://localhost:8010
```

Interactive docs:

```text
http://localhost:8010/docs
```

## Dependencies

Start these services first:

```bash
cd ../db
docker-compose up -d

cd ../streaming_broker
docker-compose up -d
```

The producer connects to:

```text
MySQL:    mysql:3306
Redpanda: redpanda:9092
Topic:    user-activity
```

## Start

From this folder:

```bash
docker-compose up --build
```

Or in the background:

```bash
docker-compose up -d --build
```

## Endpoints

```text
GET  /health
GET  /status
GET  /sample_event
POST /produce_once
POST /start
POST /stop
```

## Test The Service

Health check:

```bash
curl http://localhost:8010/health
```

Expected shape:

```json
{
  "status": "ok",
  "customers": "122",
  "products": "110",
  "topic": "user-activity"
}
```

Generate a sample event without publishing it:

```bash
curl http://localhost:8010/sample_event
```

Generate a sample event for a specific customer:

```bash
curl "http://localhost:8010/sample_event?customer_number=103"
```

Publish one event:

```bash
curl -X POST http://localhost:8010/produce_once
```

Start continuous production every 5 seconds:

```bash
curl -X POST http://localhost:8010/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 5}'
```

Check status:

```bash
curl http://localhost:8010/status
```

Stop continuous production:

```bash
curl -X POST http://localhost:8010/stop
```

## Verify Events In Redpanda

Consume one event from the beginning of the topic:

```bash
docker exec -it lab2-redpanda \
  rpk topic consume user-activity --num 1 --offset start
```

Watch new events:

```bash
docker exec -it lab2-redpanda \
  rpk topic consume user-activity
```

## Event Shape

Example event:

```json
{
  "event_id": "53ed4c7e-21cc-4f96-9e2d-df913474c845",
  "event_time": "2026-05-29T02:15:00.000000+00:00",
  "event_type": "product_view",
  "customer_number": 103,
  "city": "Nantes",
  "country": "France",
  "credit_limit": 21000.0,
  "browse_history": [
    {"product_code": "S10_1678"},
    {"product_code": "S24_3969"}
  ]
}
```

The values come from the real `classicmodels` database:

```text
customers -> customer_number, city, country, credit_limit
products  -> browse_history product_code values
```

## Teaching Notes

This service is intentionally controlled by HTTP endpoints. That makes it easy
to demonstrate streaming behavior in class:

```text
1. Start Redpanda.
2. Open a consumer watching user-activity.
3. Call /produce_once to show one event.
4. Call /start to begin continuous activity.
5. Call /stop to pause the stream.
```

The next service is:

```text
stream_processor/
```

It will consume these events, call `recommendation_api`, and write enriched
recommendation records to MinIO.
