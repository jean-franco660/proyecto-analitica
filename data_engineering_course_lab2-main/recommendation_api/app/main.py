import hashlib
import os
from typing import Any

import psycopg
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "lab2-vector-db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "recommender")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgrespwrd")


app = FastAPI(
    title="Lab 2 Recommendation API",
    description=(
        "Local recommendation inference service. "
        "It queries PostgreSQL + pgvector to return product recommendations."
    ),
    version="0.1.0",
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index() -> str:
    """Return a small browser-friendly landing page for the service."""
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Lab 2 Recommendation API</title>
        <style>
          body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: #f6f8fb;
            color: #172033;
          }
          main {
            max-width: 820px;
            margin: 56px auto;
            padding: 0 24px;
          }
          h1 {
            font-size: 34px;
            margin-bottom: 10px;
          }
          p {
            color: #4a5568;
            line-height: 1.55;
            font-size: 16px;
          }
          .panel {
            background: #ffffff;
            border: 1px solid #d6e0eb;
            border-radius: 8px;
            padding: 22px;
            margin-top: 24px;
          }
          code {
            background: #edf2f7;
            border-radius: 4px;
            padding: 2px 6px;
          }
          a {
            color: #0f6fbd;
            font-weight: 700;
          }
          ul {
            line-height: 1.8;
          }
        </style>
      </head>
      <body>
        <main>
          <h1>Lab 2 Recommendation API</h1>
          <p>
            This service exposes local recommendation endpoints for the
            streaming pipeline. It queries PostgreSQL with pgvector to find
            products with similar embeddings.
          </p>
          <div class="panel">
            <p><strong>Useful links</strong></p>
            <ul>
              <li><a href="/docs">Interactive API docs</a></li>
              <li><a href="/health">Health check</a></li>
              <li><a href="/items_from_item?item_id=S10_1678&limit=5">Example similar-products request</a></li>
            </ul>
          </div>
          <div class="panel">
            <p><strong>Main endpoints</strong></p>
            <ul>
              <li><code>POST /user_embeddings</code></li>
              <li><code>POST /items_from_user?limit=5</code></li>
              <li><code>GET /items_from_item?item_id=&lt;product_code&gt;&amp;limit=5</code></li>
            </ul>
          </div>
        </main>
      </body>
    </html>
    """


class UserFeatures(BaseModel):
    city: str | None = None
    country: str | None = None
    creditlimit: float | None = Field(default=None, alias="credit_limit")
    customerNumber: int | None = None

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class EmbeddingRequest(BaseModel):
    id: int | str | None = None
    embedding: list[float] | str


def connect():
    """Create a PostgreSQL connection using the service environment settings."""
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def normalize_embedding(embedding: list[float] | str) -> str:
    """Convert an embedding list into pgvector text format when needed."""
    if isinstance(embedding, str):
        return embedding

    return "[" + ", ".join(str(value) for value in embedding) + "]"


def row_to_recommendation(row: tuple[Any, ...]) -> dict[str, Any]:
    """Convert a database similarity row into the API recommendation shape."""
    item_id, distance = row
    return {
        "id": item_id,
        "score": float(1 / (1 + distance)),
        "distance": float(distance),
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Check that the API can connect to PostgreSQL."""
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()

    return {"status": "ok"}


@app.get("/items_from_item")
def items_from_item(
    item_id: str = Query(..., description="Product code, for example S10_1678"),
    limit: int = Query(5, ge=1, le=50),
) -> list[dict[str, Any]]:
    """Return products whose embeddings are closest to a selected product."""
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM item_emb WHERE id = %s;", (item_id,))
            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} was not found in item_emb",
                )

            cursor.execute(
                """
                SELECT other.id,
                       base.embedding <=> other.embedding AS distance
                FROM item_emb base
                JOIN item_emb other ON base.id <> other.id
                WHERE base.id = %s
                ORDER BY base.embedding <=> other.embedding
                LIMIT %s;
                """,
                (item_id, limit),
            )
            rows = cursor.fetchall()

    return [row_to_recommendation(row) for row in rows]


@app.post("/items_from_user")
def items_from_user(
    request: EmbeddingRequest,
    limit: int = Query(5, ge=1, le=50),
) -> list[dict[str, Any]]:
    """Return products whose embeddings are closest to a user embedding."""
    embedding = normalize_embedding(request.embedding)

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id,
                       embedding <=> %s::vector AS distance
                FROM item_emb
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (embedding, embedding, limit),
            )
            rows = cursor.fetchall()

    return [row_to_recommendation(row) for row in rows]


@app.post("/user_embeddings")
def user_embeddings(users: list[UserFeatures]) -> list[dict[str, Any]]:
    """Return stored user embeddings for one or more user feature payloads."""
    if not users:
        return []

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM user_emb ORDER BY id;")
            user_ids = [row[0] for row in cursor.fetchall()]

            if not user_ids:
                raise HTTPException(
                    status_code=500,
                    detail="No user embeddings are loaded in user_emb",
                )

            responses = []
            for user in users:
                user_id = select_user_embedding_id(user, user_ids)
                cursor.execute(
                    "SELECT id, embedding::text FROM user_emb WHERE id = %s;",
                    (user_id,),
                )
                row = cursor.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Selected user embedding {user_id} was not found",
                    )

                responses.append({"id": row[0], "embedding": row[1]})

    return responses


def select_user_embedding_id(user: UserFeatures, user_ids: list[int]) -> int:
    """Select the best available stored user embedding for a user payload."""
    if user.customerNumber in user_ids:
        return int(user.customerNumber)

    key = "|".join(
        [
            user.city or "",
            user.country or "",
            str(user.creditlimit or ""),
        ]
    )
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(user_ids)
    return int(user_ids[index])
