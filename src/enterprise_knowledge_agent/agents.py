"""Multi-agent flow: Router -> Retriever -> Answerer -> Verifier.

This is an explicit state machine in pure Python. LangGraph is NOT
used here, deliberately: the local run must be $0 and offline with no
extra dependency, and the flow is small enough that an explicit graph
is clearer and fully testable. The flow mirrors a LangGraph graph
(node per step, shared state dict, conditional edges for refusal /
approval), and vertex/adk_agents.py shows the same flow as a Vertex AI
Agent Developer Kit (ADK) multi-agent definition for GCP deployment.
See README for the JD mapping.
"""
from __future__ import annotations

from pathlib import Path

from . import guardrails
from .config import CONFIDENCE_THRESHOLD, DATA_PATH, TOP_K
from .gate import ApprovalGate
from .ingestion import build_chunks, load_docs
from .retrieval import VectorStore
from .tools import ToolRegistry


class KnowledgeAgent:
    def __init__(self, docs_path: str | Path = DATA_PATH):
        self.docs = load_docs(docs_path)
        self.chunks = build_chunks(self.docs)
        self.store = VectorStore(self.chunks)
        self.tools = ToolRegistry(self.store, self.docs)
        self.gate = ApprovalGate()

    # -- Router ---------------------------------------------------------
    def _route(self, question: str) -> str:
        if guardrails.contains_pii(question):
            return "pii_request"
        if guardrails.is_write_request(question):
            return "write_request"
        if guardrails.is_out_of_scope(question):
            return "out_of_scope"
        return "factual_qa"

    # -- Public entry point ---------------------------------------------
    def ask(self, question: str) -> dict:
        q = (question or "").strip()
        if not q:
            return self._refuse("empty_question", "Question was empty.")
        route = self._route(q)

        if route == "pii_request":
            return self._refuse(
                "pii_detected",
                "I cannot process requests containing personal identifiers such as SSN or card numbers.",
            )
        if route == "write_request":
            pending = self.gate.request_write(action="write_request", payload={"question": q})
            return {
                "status": "pending_approval",
                "route": route,
                "answer": None,
                "citations": [],
                "confidence": None,
                "approval_id": pending["approval_id"],
                "refusal_reason": "Write/update/send actions require explicit human confirmation and are never auto-executed.",
            }
        if route == "out_of_scope":
            return self._refuse(
                "out_of_scope",
                "That question is outside the BrightHarvest product and support knowledge base.",
            )

        # Retriever (via the allowlisted MCP-style tool)
        result = self.tools.call("search_docs", query=q, top_k=TOP_K)
        results = result["results"]
        if not results:
            return self._refuse("low_confidence", "No relevant document was found for that question.")
        top_score = results[0]["score"]
        if top_score < CONFIDENCE_THRESHOLD:
            return self._refuse(
                "low_confidence",
                f"Retrieval confidence {top_score} is below the threshold {CONFIDENCE_THRESHOLD}. I will not guess.",
            )
        # Coverage check: at least 2 distinct query content tokens must
        # appear in the top chunk. A single-token match (e.g. a nonsense
        # query that happens to contain the word "warranty") is not grounding.
        from .retrieval import tokenize as _tokenize

        top_chunk = results[0]["chunk"]
        top_text = (top_chunk["text"] + " " + top_chunk.get("title", "")).lower()
        matched_tokens = {t for t in set(_tokenize(q)) if t in top_text}
        if len(matched_tokens) < 2:
            return self._refuse(
                "low_confidence",
                f"Only {len(matched_tokens)} query term(s) matched the top document. I will not guess.",
            )

        # Answerer: extractive, grounded only in retrieved chunks
        citations = [r["chunk"]["doc_id"] for r in results]
        lines = []
        for r in results:
            chunk = r["chunk"]
            lines.append(f"[{chunk['doc_id']}] {chunk['text']}")
        answer = "Based on the retrieved documents:\n" + "\n".join(lines)

        # Verifier: citation-required, no PII in output, confidence checked
        if not citations:
            return self._refuse("no_citation", "Answer had no citations, so it was refused.")
        if guardrails.contains_pii(answer):
            return self._refuse("pii_in_output", "Generated answer contained PII-like text and was refused.")
        return {
            "status": "answered",
            "route": route,
            "answer": answer,
            "citations": citations,
            "confidence": top_score,
            "refusal_reason": None,
        }

    @staticmethod
    def _refuse(reason: str, message: str) -> dict:
        return {
            "status": "refused",
            "route": "refused",
            "answer": None,
            "citations": [],
            "confidence": None,
            "refusal_reason": f"{reason}: {message}",
        }
