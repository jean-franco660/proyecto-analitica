# Lab 2 Stream Processor

This service performs the real-time transformation step for the local streaming
pipeline.

It consumes user activity events from Redpanda, calls the recommendation API,
adds recommendations to the event, writes the enriched record to MinIO, and logs
a human-readable recommendation summary for live classroom demos.

## Role In The System

The full streaming path is:

```text
event_producer
  -> streaming_broker
  -> stream_processor
  -> recommendation_api
  -> vector_db
  -> MinIO recommendations bucket
```

This service implements:

```text
Redpanda user-activity
  -> stream_processor
  -> recommendation_api
  -> MinIO recommendations
```

## What It Does

For every event, the processor:

1. Reads the JSON event from Redpanda topic `user-activity`.
2. Looks up product names and metadata from MySQL.
3. Calls `POST /user_embeddings` on the recommendation API.
4. Calls `POST /items_from_user` for user-based recommendations.
5. Calls `GET /items_from_item` for similar item recommendations.
6. Writes the enriched JSON event to MinIO bucket `recommendations`.
7. Prints a readable summary to the container logs.

The logs show product names, not only product codes, so students can understand
what is being recommended in real time.

## Dependencies

Start these services first:

```bash
cd ../db
docker-compose up -d

cd ../min_io
docker-compose up -d

cd ../streaming_broker
docker-compose up -d

cd ../vector_db
docker-compose up -d

cd ../recommendation_api
docker-compose up -d --build

cd ../event_producer
docker-compose up -d --build
```

## Start

From this folder:

```bash
docker-compose up -d --build
```

Follow the live recommendation output:

```bash
docker logs -f lab2-stream-processor
```

## Demo Flow

Open one terminal for processor logs:

```bash
docker logs -f lab2-stream-processor
```

In another terminal, produce one event:

```bash
curl -X POST http://localhost:8010/produce_once
```

You should see a readable summary like:

```text
========================================================================
[2026-05-29T02:49:58.817588+00:00] Customer 324 from London, UK | product_view
Visited / browsed products:
  1. 1968 Ford Mustang (S24_3371, Classic Cars)

Recommended for this user:
  1. 1996 Peterbilt 379 Stake Bed with Outrigger (S32_4485, Trucks and Buses) score=0.729
  2. Pont Yacht (S72_3212, Ships) score=0.721

Similar to: 1968 Ford Mustang (S24_3371)
  1. 1936 Mercedes Benz 500k Roadster (S24_2022, Vintage Cars) score=0.840
  2. 1962 City of Detroit Streetcar (S32_3207, Trains) score=0.802

Wrote enriched event to MinIO:
s3://recommendations/year=2026/month=05/day=29/hour=02/<event_id>.json
========================================================================
```

The exact products depend on the event and model artifacts.

## Continuous Demo

Start producing events every 5 seconds:

```bash
curl -X POST http://localhost:8010/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 5}'
```

Watch recommendations:

```bash
docker logs -f lab2-stream-processor
```

Stop event production:

```bash
curl -X POST http://localhost:8010/stop
```

## MinIO Output

Open the MinIO console:

```text
http://localhost:9101
```

Bucket:

```text
recommendations
```

The processor writes objects partitioned by event time:

```text
year=2026/
  month=05/
    day=29/
      hour=02/
        <event_id>.json
```

You can also list from the terminal:

```bash
AWS_ACCESS_KEY_ID=minioadmin \
AWS_SECRET_ACCESS_KEY=minioadmin \
AWS_DEFAULT_REGION=us-east-1 \
aws --endpoint-url http://localhost:9100 \
  s3 ls s3://recommendations --recursive
```

## Stop

```bash
docker-compose down
```

## Teaching Notes

This service demonstrates the streaming side of the architecture:

```text
event arrives
  -> recommendations are computed immediately
  -> enriched record is stored
  -> visible log output proves the real-time behavior
```

The MinIO output is the data engineering deliverable. The logs are the classroom
demo layer.
