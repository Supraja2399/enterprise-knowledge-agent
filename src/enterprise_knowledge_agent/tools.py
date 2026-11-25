"""MCP Toolbox pattern — deterministic tools only, allowlisted.

JD mapping: "Implement tools like MCP (Model Context Protocol) Toolbox
to securely connect agents to enterprise databases like BigQuery and Spanner."
Locally the "database" is the synthetic JSON knowledge base; in GCP the
same tool names / schemas would be bound to BigQuery / Spanner via
MCP Toolbox (see vertex/mcp_toolbox.yaml).

Allowlist: lookup_product, search_docs, get_policy.
Anything else — update_price, send_email, delete_doc, run_sql, etc. —
is NOT a tool. Calling it raises ToolNotAllowedError and is audit-logged.
No free-form SQL is accepted anywhere.
"""
from __future__ import annotations

ALLOWED_TOOLS = {"lookup_product", "search_docs", "get_policy"}


class ToolNotAllowedError(ValueError):
    pass


class ToolRegistry:
    """Binds tool names to callables with schema validation."""

    def __init__(self, store, docs: list[dict]):
        self._store = store
        self._docs = docs
        self._by_id = {d["id"]: d for d in docs}

    def call(self, tool: str, **params) -> dict:
        if tool not in ALLOWED_TOOLS:
            raise ToolNotAllowedError(
                f"Tool '{tool}' is not allowlisted. Allowed: {sorted(ALLOWED_TOOLS)}"
            )
        if tool == "lookup_product":
            return self._lookup_product(params)
        if tool == "search_docs":
            return self._search_docs(params)
        if tool == "get_policy":
            return self._get_policy(params)
        raise ToolNotAllowedError(f"Tool '{tool}' is not allowlisted.")

    def _lookup_product(self, params: dict) -> dict:
        query = str(params.get("name_or_sku", "")).strip()
        if not query:
            raise ValueError("lookup_product requires 'name_or_sku' (string)")
        q = query.lower()
        for d in self._docs:
            if d["kind"] != "product":
                continue
            if q in d["title"].lower() or q in d["text"].lower():
                return {"tool": "lookup_product", "doc": d}
        return {"tool": "lookup_product", "doc": None}

    def _search_docs(self, params: dict) -> dict:
        query = str(params.get("query", "")).strip()
        if not query:
            raise ValueError("search_docs requires 'query' (string)")
        top_k = int(params.get("top_k", 3))
        if top_k < 1 or top_k > 5:
            raise ValueError("search_docs top_k must be 1..5")
        return {"tool": "search_docs", "results": self._store.search(query, top_k=top_k)}

    def _get_policy(self, params: dict) -> dict:
        topic = str(params.get("topic", "")).strip().lower()
        if not topic:
            raise ValueError("get_policy requires 'topic' (string)")
        for d in self._docs:
            if d["kind"] != "policy":
                continue
            if topic in d["title"].lower() or topic in d["text"].lower():
                return {"tool": "get_policy", "doc": d}
        return {"tool": "get_policy", "doc": None}
