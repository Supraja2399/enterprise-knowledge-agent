# Deploying to Vertex AI / BigQuery (GCP)

> This project is a **local stand-in, not a Vertex production deployment**.
> Nothing in this repo has run on Vertex AI or BigQuery. The files in
> `vertex/` show the mapping; they do not claim a deployment happened.

## What changes in GCP

| Local | GCP / Vertex AI |
|---|---|
| `data/synthetic/docs.json` | BigQuery tables in `vertex/bigquery_schema.sql` |
| `src/.../retrieval.py` (TF-IDF, pure Python) | BigQuery Vector Search / AlloyDB vector engine, embeddings from `text-embedding-004` |
| `src/.../tools.py` (allowlisted, in-process) | MCP Toolbox for Databases, `vertex/mcp_toolbox.yaml` |
| `src/.../agents.py` (explicit graph) | Vertex AI ADK multi-agent system, `vertex/adk_agents.py` |
| `eval/run_eval.py` (local) | Vertex AI Pipelines stage, `vertex/pipeline_config.yaml` |
| FastAPI on localhost | Cloud Run + Vertex AI Agent Engine / Agent Builder |

## Steps (summary — do not run without a GCP project and owner approval)

1. Create a GCP project, enable Vertex AI, BigQuery, Cloud Run.
2. Create the BigQuery dataset/tables from `vertex/bigquery_schema.sql`.
3. Load the synthetic docs, generate embeddings with Vertex AI, create the Vector Search index.
4. Deploy the MCP Toolbox server with `vertex/mcp_toolbox.yaml` (read-only tools only).
5. Deploy the ADK agents from `vertex/adk_agents.py` to Vertex AI Agent Engine.
6. Run the pipeline in `vertex/pipeline_config.yaml`; the eval gate must pass 48/48 with 0 false automatic actions before any production traffic.
7. Keep the human approval gate: write actions must still pause for explicit confirmation in production — do not wire a write tool into the agent.

## What does NOT change

- Guardrails stay deterministic code (allowlist, PII blocklist, citation-required, confidence threshold), not just a prompt.
- The frozen 48-case eval stays the release gate.
- No write is ever auto-executed.
