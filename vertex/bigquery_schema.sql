-- BigQuery schema — DEPLOYMENT ARTIFACT ONLY.
-- Locally the same shape is data/synthetic/docs.json (docs) plus
-- chunks derived in src/enterprise_knowledge_agent/ingestion.py.
-- In GCP, load docs.json into these tables, then create a Vector Search
-- index on the embedding column. No data is loaded by this file alone.

CREATE SCHEMA IF NOT EXISTS `{{PROJECT_ID}}.knowledge`;

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.knowledge.docs` (
  id STRING NOT NULL,
  kind STRING NOT NULL,  -- 'product' | 'policy' | 'support'
  title STRING NOT NULL,
  text STRING NOT NULL,
  tags ARRAY<STRING>
);

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.knowledge.chunks` (
  chunk_id STRING NOT NULL,
  doc_id STRING NOT NULL,
  title STRING,
  kind STRING,
  text STRING NOT NULL,
  embedding ARRAY<FLOAT64>  -- populated by Vertex AI text-embedding model
);

-- Vector Search index (create after embeddings are populated):
-- CREATE VECTOR INDEX IF NOT EXISTS chunks_vector_idx
-- ON `{{PROJECT_ID}}.knowledge.chunks`(embedding)
-- OPTIONS (distance_type = 'COSINE', index_type = 'IVF',
--          ivf_options = '{"num_lists": 100}');
