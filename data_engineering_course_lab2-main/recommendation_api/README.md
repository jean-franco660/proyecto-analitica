# Lab 2 Recommendation API

This service provides local recommendation inference endpoints.

It exposes HTTP endpoints that the future stream processor can call to get:

```text
user embeddings
items recommended from a user embedding
items similar to a selected product
```

The first local version uses the embeddings already loaded into:

```text
lab2-vector-db
```

It does not yet run the PyTorch model from `best_model.pth`. That can be added
later as an advanced version. For now, this service gives us the same API shape
needed by the streaming pipeline.

## Role In The Local Architecture

Current local pieces:

```text
MySQL
  -> PySpark ETL
  -> MinIO training dataset

MinIO ml-artifacts
  -> vector_db loader
  -> PostgreSQL + pgvector
```

This service adds:

```text
recommendation_api
  -> PostgreSQL + pgvector
  -> recommendation responses
```

Later, the stream processor will call this API:

```text
event_producer
  -> streaming_broker
  -> stream_processor
  -> recommendation_api
  -> vector_db
  -> MinIO recommendations bucket
```

## Endpoints

The API follows the shape expected by the local stream processor:

```text
POST /user_embeddings
POST /items_from_user?limit=5
GET  /items_from_item?item_id=<product_code>&limit=5
```

It also exposes:

```text
GET /health
```

Interactive docs:

```text
http://localhost:8000/docs
```

## Start Dependencies

The vector database must be running and loaded first:

```bash
cd ../vector_db
docker-compose up --build
```

You should see:

```text
Loaded 109 item embeddings into item_emb
Loaded 98 user embeddings into user_emb
Vector database is ready
```

The PostgreSQL container should stay running:

```text
lab2-vector-db
```

## Start The API

From this folder:

```bash
docker-compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Opening that URL in a browser shows a small service landing page with links to
the interactive docs, health check, and a similar-products example.

## Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Test 2: Similar Products From A Product

This endpoint is the easiest to understand. It asks:

```text
Given product S10_1678, which products are closest in vector space?
```

Run:

```bash
curl "http://localhost:8000/items_from_item?item_id=S10_1678&limit=5"
```

Example response:

```json
[
  {"id":"S72_1253","score":0.864779877779838,"distance":0.15636363159526157},
  {"id":"S700_2834","score":0.8102489736311013,"distance":0.2341885427124163},
  {"id":"S24_3969","score":0.7613054224008113,"distance":0.31353326874574794},
  {"id":"S24_3949","score":0.7585776109132517,"distance":0.3182566761970471},
  {"id":"S24_1444","score":0.7267707949419472,"distance":0.3759496212005571}
]
```

The exact decimals may vary slightly, but the product ids should be similar if
the same artifacts are loaded.

## Test 3: Get A User Embedding

The stream processor sends user features to `/user_embeddings`. In a full model
serving implementation, the recommendation service converts those features into
a new user embedding.

This local first version does not run the PyTorch model yet. Instead:

- If `customerNumber` is provided and exists in `user_emb`, it returns that
  stored embedding.
- If only profile fields are provided, it deterministically selects one existing
  user embedding. This keeps the API contract working for the streaming pipeline.

Run:

```bash
curl -X POST "http://localhost:8000/user_embeddings" \
  -H "Content-Type: application/json" \
  -d '[{"customerNumber": 103, "city": "Nantes", "country": "France", "credit_limit": 21000}]'
```

Expected shape:

```json
[
  {
    "id": 103,
    "embedding": "[-0.06069748,0.06968412,...]"
  }
]
```

## Test 4: Recommended Products From A User Embedding

Copy the embedding returned from `/user_embeddings`, or use this two-command
flow with `jq` installed:

```bash
USER_EMBEDDING=$(curl -s -X POST "http://localhost:8000/user_embeddings" \
  -H "Content-Type: application/json" \
  -d '[{"customerNumber": 103, "city": "Nantes", "country": "France", "credit_limit": 21000}]' \
  | jq -r '.[0].embedding')

curl -X POST "http://localhost:8000/items_from_user?limit=5" \
  -H "Content-Type: application/json" \
  -d "{\"id\": 103, \"embedding\": $USER_EMBEDDING}"
```

Expected shape:

```json
[
  {"id":"S32_4485","score":0.7285994538419309,"distance":0.37249622508905866},
  {"id":"S72_3212","score":0.7210869021238459,"distance":0.38679540157318115},
  {"id":"S24_2022","score":0.7055082968371313,"distance":0.41741777450826056},
  {"id":"S700_1138","score":0.6630604630479269,"distance":0.5081580877304077},
  {"id":"S24_4048","score":0.6278980381086212,"distance":0.5926152644340771}
]
```

## Current Limitation

This first version uses existing embeddings from `vector_db`. It does not yet
load:

```text
model/best_model.pth
scalers/*.pkl
```

That means `/items_from_item` is already a real vector similarity endpoint, while
`/user_embeddings` is a local compatibility layer until we implement full model
inference.

This is enough to continue migrating the streaming pipeline because the stream
processor only needs the API contract and recommendation responses.
