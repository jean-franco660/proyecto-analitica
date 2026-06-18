# Data Engineering Lab 2: Local Batch and Streaming Pipelines

This repository contains a local data engineering lab for teaching batch and
streaming recommendation pipelines.

![System design diagram](docs/system-design.svg)

The lab mirrors common cloud data engineering patterns using local Docker
services:

- Amazon RDS MySQL as the operational source database.
- Spark-style batch ETL for data preparation.
- Amazon S3 as the data lake and recommendations destination.
- Amazon RDS PostgreSQL with `pgvector` as the vector database.
- HTTP services for model inference and stream transformation.
- A Kafka-compatible broker for the streaming pipeline.

The goal is to make the full workflow runnable on any machine with Docker
and Docker Compose, following the same hands-on style as `data-engineering-lab-1`.

## Target Local Architecture

```text
Batch path:

MySQL classicmodels + ratings
  -> local ETL job
  -> MinIO data lake
  -> Parquet training dataset

Streaming path:

event producer
  -> local stream broker
  -> stream processor
  -> recommendation API
  -> PostgreSQL + pgvector
  -> MinIO recommendations output
```

## Cloud to Local Mapping

| Cloud-style service | Local replacement | Folder |
| --- | --- | --- |
| Amazon RDS MySQL | MySQL container | `db/` |
| Batch ETL job | PySpark ETL container | `etl/` |
| Amazon S3 data lake | MinIO | `min_io/` |
| RDS PostgreSQL + pgvector | PostgreSQL with pgvector container | `vector_db/` |
| Model inference function | FastAPI recommendation service | `recommendation_api/` |
| Kinesis Data Streams / Firehose | Redpanda, Kafka, or compatible local broker | `streaming_broker/` |
| Stream transformation function | Python stream processor | `stream_processor/` |
| Simulated platform activity | Python event producer | `event_producer/` |

## Folder Structure

```text
.
├── db/                     # Local MySQL source database.
├── etl/                    # Local batch pipeline replacing AWS Glue.
├── event_producer/         # Simulated real-time user activity.
├── min_io/                 # Local S3-compatible object storage.
├── ml-artifacts/           # Local copy of downloaded ML artifacts.
├── recommendation_api/     # Local model/recommendation API replacing inference Lambda.
├── stream_processor/       # Streaming transformation job replacing transformation Lambda.
├── streaming_broker/       # Local streaming service.
└── vector_db/              # PostgreSQL + pgvector service.
```

## Design Principles

1. Build one component at a time.
2. Make every service runnable with Docker Compose from its own folder.
3. Prefer small, inspectable datasets for students.
4. Preserve the business story: product recommendations from customer, product, rating, and browsing data.
5. Preserve the architectural contrast between batch and streaming.
6. Keep data contracts clear between services.

## Implementation Plan

### Phase 1: Source Database

Create the local MySQL service in `db/`.

Needed inputs:

- `classicmodels` SQL dump.
- `ratings` table definition and data.

The file `db/classicmodels_lab2.sql` contains the source schema and data,
including the required `ratings` table.

Expected outcome:

```text
MySQL container running classicmodels with:
- customers
- products
- orders
- orderdetails
- ratings
```

Run it with:

```bash
cd db
docker-compose up -d --build
```

Connect from your host machine on port `3307`:

```bash
mysql --host=127.0.0.1 --port=3307 --user=admin --password=adminpwrd classicmodels
```

### Phase 2: Object Storage

Create the MinIO service in `min_io/`.

Buckets to create:

- `classicmodels-lab2`
- `ml-artifacts`
- `recommendations`

Purpose:

- `classicmodels-lab2`: batch ETL output.
- `ml-artifacts`: embeddings, model files, scalers, and exported AWS artifacts.
- `recommendations`: streaming output.

Run it before the ETL because the ETL writes Parquet output to MinIO:

```bash
cd min_io
docker-compose up -d
```

Verify it in the MinIO web console:

```text
URL: http://localhost:9101
Username: minioadmin
Password: minioadmin
```

Open the `ml-artifacts` bucket and confirm it contains the seeded folders:

```text
embeddings/
model/
scalers/
```

### Phase 3: Batch ETL

Create the local ETL service in `etl/`.

The batch ETL job reads:

- `classicmodels.products`
- `classicmodels.customers`
- `classicmodels.ratings`

Then it creates a training dataset with customer features, product features, and `productRating`.

Local replacement:

- Python or PySpark job.
- Reads from local MySQL.
- Writes Parquet to MinIO.
- Keeps partitioning by `customerNumber` if useful for the lesson.

Expected output:

```text
s3a://classicmodels-lab2/ratings_ml_training/customerNumber=<number>/...
```

Run it after MySQL and MinIO are running:

```bash
cd etl
docker-compose up --build etl-driver
```

Network note:

The ETL container needs to reach the MySQL container. On some Docker
environments, especially native Linux Docker, `host.docker.internal` may not
resolve the same way it does in Docker Desktop. If the ETL cannot connect to
MySQL, use Docker's internal container DNS instead:

```text
classicmodels-lab2-mysql:3306
```

That means containers talk to MySQL by container name and internal MySQL port.
The host machine can still connect through the published port:

```text
127.0.0.1:3307
```

Verify it in the MinIO web console:

```text
http://localhost:9101
```

Open the `classicmodels-lab2` bucket and check for:

```text
ratings_ml_training/
_SUCCESS
customerNumber=<number>/
```

The exact `customerNumber=<number>/` folders depend on the source data, but
their presence confirms that Spark wrote partitioned Parquet training files.

### Phase 4: Vector Database

Create the local vector database in `vector_db/`.

In the real workflow, a data scientist trains a recommendation model outside
this infrastructure lab. That trained model produces embedding values for users
and products. Our data engineering task is to take those exported embedding
files and load them into PostgreSQL with `pgvector`, so the application can run
similarity searches for recommendations.

Local replacement:

- PostgreSQL container with `pgvector`.
- Tables equivalent to:
  - `item_emb`
  - `user_emb`

Needed inputs:

- `item_embeddings.csv`
- `user_embeddings.csv`

Cloud-hosted PostgreSQL can import from object storage with provider-specific
extensions. Locally this is handled by a Python loader.

Run it after MinIO is running and the `ml-artifacts` bucket has been seeded:

```bash
cd vector_db
docker-compose up -d --build
```

The loader imports the embeddings and then exits. PostgreSQL stays running.

Verify the import from your host machine:

```bash
psql --host=127.0.0.1 --port=5433 --username=postgres --dbname=recommender
```

Password:

```text
postgrespwrd
```

Then run:

```sql
SELECT COUNT(*) FROM item_emb;
SELECT COUNT(*) FROM user_emb;
```

### Phase 5: Recommendation API

Create the local recommendation API in `recommendation_api/`.

This service provides model-style inference endpoints for the streaming pipeline.

Modern recommendation systems often represent users and products as vectors,
also called embeddings. A vector is a list of numbers that captures learned
patterns about a user or product. Products with similar vectors are treated as
similar products, and users whose vectors are close to product vectors are good
candidates for recommendations.

In this lab, the API asks `pgvector` to compare embeddings. For example:

```text
GET /items_from_item?item_id=S10_1678&limit=5
```

returns products with vectors close to product `S10_1678`.

The response includes:

```json
{
  "id": "S72_1253",
  "score": 0.864779877779838,
  "distance": 0.15636363159526157
}
```

Meaning:

- `id`: the recommended or similar product code.
- `distance`: how far this product vector is from the query vector. Smaller distance means more similar.
- `score`: a friendlier value calculated from the distance with `1 / (1 + distance)`. Higher score means more similar.

So a product with `distance = 0.15` receives a higher score than a product with
`distance = 0.37`, because it is closer in vector space.

The transformation Lambda expects these endpoints:

```text
POST /user_embeddings
POST /items_from_user?limit=5
GET  /items_from_item?item_id=<product_code>&limit=5
```

Possible first version:

- Use simple deterministic mock embeddings.
- Query `pgvector` for similar items.
- Return JSON in the same shape expected by the stream processor.

Later version:

- Load the real model artifacts from AWS if available.
- Load scalers and model weights from `ml-artifacts/` or MinIO.

Run it after the vector database is running:

```bash
cd recommendation_api
docker-compose up -d --build
```

The API will be available at:

```text
http://localhost:8000
```

Verify it with:

```bash
curl http://localhost:8000/health
```

You can also open the interactive API docs:

```text
http://localhost:8000/docs
```

### Phase 6: Streaming Pipeline

Create the streaming service in `streaming_broker/`.

This service is the event buffer between the application that produces user
activity and the processor that generates recommendations. Without a broker,
the producer and processor would need to be online at exactly the same time and
call each other directly. With a broker, user events are written to a topic,
held in order, and consumed independently by the stream processor.

In the system design, this is the start of the streaming path:

```text
event producer
  -> Redpanda topic: user-activity
  -> stream processor
  -> recommendation API
  -> MinIO recommendations output
```

Local replacement:

- Redpanda single-node Kafka-compatible broker.
- Topic initialization container.
- Host access through `localhost:19092`.
- Docker service access through `redpanda:9092`.

Topic:

```text
user-activity
```

Run it with:

```bash
cd streaming_broker
docker-compose up -d
```

Check that Redpanda is running:

```bash
docker ps --filter name=lab2-redpanda
```

Verify the topic was created:

```bash
docker exec -it lab2-redpanda rpk topic list
```

You should see:

```text
user-activity
```

Optional end-to-end broker test:

```bash
docker exec -i lab2-redpanda rpk topic produce user-activity <<'EOF'
{"customer_number":103,"city":"Nantes","country":"France","credit_limit":21000,"browse_history":[{"product_code":"S10_1678"}]}
EOF
```

Then consume one message from the beginning:

```bash
docker exec -it lab2-redpanda rpk topic consume user-activity --num 1 --offset start
```

### Phase 7: Event Producer

Create the event generator in `event_producer/`.

This service simulates the activity that would normally come from users
interacting with a product website or mobile app. For example, a customer opens
a page, views a product, adds something to the cart, or browses several product
pages in one session. In a real system, those frontend/backend interactions
would emit events. In this lab, the event producer generates those events for us
so students can see the streaming pipeline working.

Local behavior:

- Reads real customers from MySQL.
- Reads real product codes from MySQL.
- Publishes JSON events to Redpanda topic `user-activity`.
- Provides HTTP endpoints to start, stop, inspect, and produce one event.

It simulates sales-platform events such as:

- product views
- browse history
- add-to-cart actions
- customer session activity

The event schema should include enough fields for the stream processor:

```json
{
  "customer_number": 103,
  "city": "Nantes",
  "country": "France",
  "credit_limit": 21000,
  "browse_history": [
    {"product_code": "S10_1678"}
  ],
  "event_time": "2026-05-26T12:00:00Z"
}
```

Run it with:

```bash
cd event_producer
docker-compose up -d --build
```

The control API is available at:

```text
http://localhost:8010/docs
```

Useful commands:

```bash
curl http://localhost:8010/health
curl http://localhost:8010/status
curl http://localhost:8010/sample_event
```

Publish one user activity event:

```bash
curl -X POST http://localhost:8010/produce_once
```

Start continuous event production every 5 seconds:

```bash
curl -X POST http://localhost:8010/start \
  -H "Content-Type: application/json" \
  -d '{"interval_seconds": 5}'
```

Stop continuous event production:

```bash
curl -X POST http://localhost:8010/stop
```

Verify events are arriving in Redpanda:

```bash
docker exec -it lab2-redpanda rpk topic consume user-activity --num 1 --offset start
```

### Phase 8: Stream Processor

Create the stream processor in `stream_processor/`.

This replaces the transformation Lambda.

In a production product system, this component would usually send the computed
recommendations back to the website, mobile app, backend API, cache, or another
serving layer so the user can see recommended products in near real time. In
this local teaching lab, we write the enriched recommendation records to MinIO
instead. That makes the result easy to inspect, replay, and discuss without
needing to build a full frontend recommendation experience.

Responsibilities:

- Consume events from the local stream broker.
- Call the local recommendation API.
- Add `recommended_items` and `similar_items`.
- Write enriched events to the `recommendations` bucket in MinIO.
- Print a readable live recommendation summary with product names.

Run it with:

```bash
cd stream_processor
docker-compose up -d --build
docker logs -f lab2-stream-processor
```

When the full streaming path is working, the logs should show a readable
summary for each consumed user activity event. This is the classroom-friendly
view of the recommendation flow: the processor receives a browsing event,
asks the recommendation API for product suggestions, enriches the event with
those recommendations, and writes the final JSON record to MinIO.

Example output:

```text
========================================================================
[2026-05-29T17:58:28.216847+00:00] Customer 276 from North Sydney, Australia | product_view
Visited / browsed products:
  1. 1999 Yamaha Speed Boat (S18_3029, Ships)
  2. 1937 Lincoln Berline (S18_1342, Vintage Cars)
  3. 1965 Aston Martin DB5 (S18_1589, Classic Cars)

Recommended for this user:
  1. 1992 Porsche Cayenne Turbo Silver (S24_4048, Classic Cars) score=0.650
  2. 2002 Chevy Corvette (S24_3432, Classic Cars) score=0.624
  3. 1958 Chevy Corvette Limited Edition (S24_2840, Classic Cars) score=0.617
  4. 1960 BSA Gold Star DBD34 (S24_2000, Motorcycles) score=0.609
  5. American Airlines: B767-300 (S700_1691, Planes) score=0.606

Similar to: 1999 Yamaha Speed Boat (S18_3029)
  1. 2003 Harley-Davidson Eagle Drag Bike (S10_4698, Motorcycles) score=0.752
  2. 1948 Porsche Type 356 Roadster (S18_3685, Classic Cars) score=0.728
  3. 1974 Ducati 350 Mk3 Desmo (S32_4485, Motorcycles) score=0.723
  4. 1982 Camaro Z28 (S700_2824, Classic Cars) score=0.719
  5. 1961 Chevrolet Impala (S24_4620, Classic Cars) score=0.711

Wrote enriched event to MinIO: s3://recommendations/year=2026/month=05/day=29/hour=17/a60071d9-e698-4bc4-8abc-401045803cca.json
========================================================================
```

How to read this output:

- The first line identifies the customer, location, and event type consumed from Redpanda.
- `Visited / browsed products` shows the products that triggered the recommendation request.
- `Recommended for this user` uses the customer embedding to find products that match the user's profile.
- `Similar to` uses the visited product embedding to find nearby products in vector space.
- `score` is the similarity score returned by the recommendation API. Higher scores mean stronger matches.
- The final line confirms that the enriched event was written to the `recommendations` bucket in MinIO, partitioned by event time.
