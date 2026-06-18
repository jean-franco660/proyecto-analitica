CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS item_emb (
  id varchar PRIMARY KEY,
  embedding vector(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_emb (
  id int PRIMARY KEY,
  embedding vector(32) NOT NULL
);
