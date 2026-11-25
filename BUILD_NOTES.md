# Build Notes — Enterprise Knowledge Agent (Tiger Analytics FDE proof)

## What it does

Answers questions over a fictional CPG client (BrightHarvest Foods, 80
synthetic docs: 30 products, 20 policies, 30 support notes), grounded only
in retrieved documents, with citations. Multi-agent flow
Router → Retriever → Answerer → Verifier. Allowlisted MCP-style tools
(`lookup_product`, `search_docs`, `get_policy`). Human approval gate for
any write/update/send action. Deterministic guardrails in code.
Locally runnable, $0, no API keys, no GCP credentials.

## What it will NOT do

- No auto-writes, updates, sends, deletes, or refunds.
- No answers without citations; low-confidence questions are refused.
- No PII handling; SSN/card-like requests are refused.
- No Vertex AI / BigQuery production deployment is claimed.
  `vertex/` is a deployment mapping only.
- No real client data; all data is synthetic.
- Nothing pushed to GitHub, nothing submitted.

## Eval cases summary

Frozen set `eval/cases.json`: exactly **48 cases**.
- 24 factual QA (product price / shelf life / allergens / storage; policy
  windows; support how-tos) — each with an expected substring and doc.
- 12 grounding/citation (answer must cite the expected doc and contain
  the expected fact).
- 12 guardrail/refusal: 3 write attempts (must return PENDING_APPROVAL),
  3 PII, 3 out-of-scope, 3 low-confidence/nonsense.

## Verified numbers (from actually running the code, Nov 25, 2026)

- `pytest -q`: **14 passed, 0 failed** (14 tests in `tests/test_agent.py`).
- `python eval/run_eval.py`: **48/48 passed (100%)**
  - Factual: **24/24**
  - Grounding: **12/12**
  - Guardrail: **12/12**
  - Citation coverage: **36/36 answered cases with ≥1 citation (100%)**
  - False automatic actions: **0** (must be 0)
- Total cost to run: **$0** (local, no API calls).
- Full per-case results: `EVAL_RESULTS.md`.

## Failure found and fixed during development (honest record)

1. First pytest run: **13 passed, 1 failed** —
   `test_low_confidence_refuses`. The nonsense query
   "Zorblax quantum flux capacitor warranty details" was *answered* from
   the warranty policy, because the single word "warranty" matched with a
   TF-IDF score of 0.1801, above the original 0.08 threshold.
   Fix: raised the confidence threshold to **0.20** (lowest answerable eval
   case scores 0.2214) and added a **token-coverage check** — at least 2
   distinct query content tokens must match the top document.
   After the fix: pytest **14/14**, eval **48/48**.
2. First install attempt failed on PEP 668 (system Python is externally
   managed). Fix: documented venv setup in README; the build is verified
   with a venv. Not a code failure.
3. Starlette TestClient emits a deprecation warning suggesting `httpx2`
   instead of `httpx`. Warning only; all tests pass. Left as-is.

## Exact resume-ready numbers (verified only)

Use only these, and only with the stated scope:

- "Built a Vertex AI-pattern enterprise knowledge agent over a synthetic
  80-document CPG knowledge base; frozen 48-case eval: 48/48 passed
  (24/24 factual, 12/12 grounding, 12/12 guardrail), 100% citation
  coverage on answered questions, 0 false automatic actions; $0 local run."
- "Implemented a human-approval gate: all write/update/send actions return
  PENDING_APPROVAL and are never auto-executed; 14/14 pytest tests pass."

Do NOT claim: Vertex AI production deployment, BigQuery production use,
or performance on a real client corpus. The eval measures this synthetic
KB only, with TF-IDF retrieval as a stand-in for BigQuery Vector Search.

## GitHub status

Owner's GitHub (Supraja2399, https://github.com/Supraja2399) is new/empty
with 0 public repos. A push would need a new repo created first, with her
approval. **Nothing has been pushed.**
