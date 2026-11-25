# Enterprise Knowledge Agent — Vertex AI pattern, locally runnable

Proof project for **Tiger Analytics — Forward Deployed Engineer (Generative AI)**,
Remote, New York, NY.
Live JD: https://apply.workable.com/tiger-analytics/j/E4AC6AEB4A
(verified still live Nov 25, 2026; no years bar, no salary listed).

## What it does

Answers questions over a **fictional CPG client's** product/support knowledge
base — BrightHarvest Foods, 80 synthetic documents (30 products, 20 policies,
30 support notes). Every answer is grounded **only** in retrieved documents
and must cite chunk IDs, or the agent refuses.

- **One clear job:** grounded Q&A with citations. Nothing else.
- **Multi-agent flow:** Router → Retriever → Answerer → Verifier
  (explicit state machine in `src/enterprise_knowledge_agent/agents.py`).
- **Retrieval:** deterministic offline TF-IDF (pure Python) as a stand-in for
  BigQuery Vector Search / AlloyDB. The `VectorStore.search()` interface is
  adapter-shaped so BigQuery can be swapped in (see `vertex/`).
- **MCP Toolbox pattern:** allowlisted deterministic tools only —
  `lookup_product`, `search_docs`, `get_policy`. No free-form SQL, no deletes.
- **Human at the gate:** any write/update/send action returns
  `PENDING_APPROVAL` and is never auto-executed. Confirming it in the demo
  only audit-logs it; it is **not** applied to the knowledge base.
- **Deterministic guardrails (code, not just a prompt):** allowlisted tools
  only, PII blocklist, citation-required, confidence threshold (0.20) plus a
  token-coverage check (≥2 query terms must match the top document),
  out-of-scope refusal.
- **API:** FastAPI with `/health`, `/ask`, `/confirm-write`.
- **Cost to run locally: $0.** No API calls, no API keys, no GCP credentials.

## What it will NOT do

- No writes, updates, sends, deletes, or refunds — ever automatically.
- No answers without citations; low-confidence questions are refused, not guessed.
- No PII handling: requests containing SSN/card-like numbers are refused.
- No Vertex AI / BigQuery production deployment — this is a **local stand-in**.
  `vertex/` shows the deployment mapping; nothing here has run on Vertex AI.
- No real client data. All data is synthetic and labelled as such.
- No GitHub push, no application submission. Those need the owner's approval.

## Architecture — JD mapping

| JD requirement | This build |
|---|---|
| Vertex AI Agent Builder, ADK multi-agent systems | Explicit Router→Retriever→Answerer→Verifier graph locally; ADK definition in `vertex/adk_agents.py` |
| MCP Toolbox to BigQuery/Spanner | Allowlisted tools in `src/.../tools.py`; Toolbox config in `vertex/mcp_toolbox.yaml` (read-only) |
| Vertex AI training/tuning/deployment, BigQuery feature engineering | `vertex/bigquery_schema.sql`, `vertex/pipeline_config.yaml`; local ingestion in `src/.../ingestion.py` |
| Dataflow streaming pipelines, RunInference / Vertex endpoints | Documented in `vertex/DEPLOY.md`; local retrieval is the stand-in |
| Grounding in live context, BigQuery / AlloyDB vector engines | TF-IDF `VectorStore` with the same `search()` interface; citation-required verifier |
| Python, SQL for BigQuery, Google Cloud Storage, Vertex endpoints | Python throughout; BigQuery SQL in `vertex/bigquery_schema.sql` |
| On-site deployment, client-facing, consultative approach | Human-approval gate, audit log, status/explanation in every refusal |

## Setup — under 5 minutes

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python eval/run_eval.py
```

Run the API:

```bash
uvicorn enterprise_knowledge_agent.api:app --reload
# or: PYTHONPATH=src python -m enterprise_knowledge_agent.api
curl -X POST http://127.0.0.1:8000/ask -H 'Content-Type: application/json' \
  -d '{"question": "What is the price of BrightHarvest Almond Crunch Granola?"}'
```

Note: on Debian/Ubuntu, plain `pip install` may refuse with PEP 668
("externally managed environment") — use the venv above, which is the
documented path.

## Tests and eval — real numbers

- `pytest -q` — **14 passed** (see BUILD_NOTES.md for the run).
- `python eval/run_eval.py` — frozen 48-case set in `eval/cases.json`:
  24 factual QA, 12 grounding/citation, 12 guardrail/refusal.
  Result: **48/48 passed**, citation coverage **36/36**, false automatic
  actions **0**. Full per-case results in `EVAL_RESULTS.md`.
- One failure was found and fixed during development: a nonsense query
  containing the single word "warranty" was answered from the warranty
  policy. Fixed with a confidence threshold of 0.20 plus a ≥2-token
  coverage check. See BUILD_NOTES.md.

## Limits (honest)

- Retrieval is TF-IDF, not embeddings — it is a stand-in, not a claim of
  Vertex AI / BigQuery Vector Search performance.
- LangGraph is **not** used. The graph is explicit pure Python, to keep the
  local run $0 and offline; the ADK file shows the GCP equivalent.
- The 48-case eval measures this synthetic KB only. It does not prove
  performance on a real client corpus.
- Write confirmation in the demo is audit-log-only; it does not mutate data.
- GitHub: the owner's account (Supraja2399, https://github.com/Supraja2399)
  is new/empty with 0 public repos — a push would need a new repo created
  first, with her approval. Nothing has been pushed.
