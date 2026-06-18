# Lab 2 Streaming Broker

This folder contains the local streaming broker for user activity events.

The local broker uses Redpanda, which is Kafka-compatible and simpler to run
locally than a full Kafka + ZooKeeper stack.

## Role In The System

The local lab now has:

```text
MySQL
  -> PySpark ETL
  -> MinIO training dataset

MinIO ml-artifacts
  -> vector_db
  -> recommendation_api
```

This service starts the streaming path:

```text
event_producer
  -> streaming_broker
  -> stream_processor
  -> recommendation_api
  -> MinIO recommendations bucket
```

The broker receives user activity events. Later, the stream processor will read
those events, call the recommendation API, and write enriched recommendation
results into MinIO.

## Services

The Compose stack starts:

```text
lab2-redpanda                 # Kafka-compatible broker
lab2-redpanda-create-topics   # one-shot topic creation job
```

It creates this topic:

```text
user-activity
```

Connection addresses:

```text
From your host machine: localhost:19092
From Docker services: redpanda:9092
```

Redpanda admin/metrics endpoint:

```text
http://localhost:9644
```

## Start

From this folder:

```bash
docker-compose up -d
```

Check containers:

```bash
docker ps --filter name=lab2-redpanda
```

List topics:

```bash
docker exec -it lab2-redpanda rpk topic list
```

Expected topic:

```text
user-activity
```

## Test With A Real Event

Produce one event:

```bash
docker exec -i lab2-redpanda rpk topic produce user-activity <<'EOF'
{"customer_number":103,"city":"Nantes","country":"France","credit_limit":21000,"browse_history":[{"product_code":"S10_1678"}]}
EOF
```

Consume from the beginning:

```bash
docker exec -it lab2-redpanda rpk topic consume user-activity --num 1 --offset start
```

Expected shape:

```json
{
  "customer_number": 103,
  "city": "Nantes",
  "country": "France",
  "credit_limit": 21000,
  "browse_history": [
    {
      "product_code": "S10_1678"
    }
  ]
}
```

## Why Redpanda?

Managed cloud streams do not run locally. Redpanda gives us a Kafka-compatible
local stream broker with a single container.

For teaching, the mapping is:

```text
Kinesis Data Stream -> Redpanda topic
Kinesis record      -> Kafka message
Firehose consumer   -> stream_processor service
```

## Stop

```bash
docker-compose down
```

Delete broker data and topics:

```bash
docker-compose down -v
```

## Next Step

After this broker is running, create:

```text
event_producer/
```

That service will generate user activity events and publish them to:

```text
user-activity
```

Then create:

```text
stream_processor/
```

That service will consume `user-activity`, call `recommendation_api`, and write
recommendation records to the MinIO `recommendations` bucket.
