"""Vertex AI Agent Developer Kit (ADK) definition — DEPLOYMENT ARTIFACT ONLY.

This file is NOT executed by the local run. It shows how the local
explicit graph (Router -> Retriever -> Answerer -> Verifier, see
src/enterprise_knowledge_agent/agents.py) maps to a Vertex AI ADK
multi-agent system in GCP. To deploy, follow vertex/DEPLOY.md.
No credentials are stored here.
"""
# ADK-style agent definitions (pseudo-code in the ADK shape).
# In GCP this would use: from google.adk.agents import LlmAgent, SequentialAgent

ROUTER_AGENT = {
    "name": "router",
    "model": "gemini-2.5-flash",
    "instruction": (
        "Classify the user question as factual_qa, write_request, "
        "pii_request, or out_of_scope. Write requests must be routed to "
        "the human-approval agent and never executed directly."
    ),
    "tools": [],
}

RETRIEVER_AGENT = {
    "name": "retriever",
    "model": "gemini-2.5-flash",
    "instruction": (
        "Use the MCP Toolbox tools search_docs, lookup_product and "
        "get_policy to retrieve grounded chunks from BigQuery Vector Search. "
        "Return the top 3 chunks with scores."
    ),
    "tools": ["search_docs", "lookup_product", "get_policy"],
}

ANSWERER_AGENT = {
    "name": "answerer",
    "model": "gemini-2.5-flash",
    "instruction": (
        "Answer ONLY from the retrieved chunks. Every factual claim must "
        "cite a chunk id. If retrieval confidence is below threshold, refuse "
        "rather than guessing."
    ),
    "tools": [],
}

VERIFIER_AGENT = {
    "name": "verifier",
    "model": "gemini-2.5-flash",
    "instruction": (
        "Verify the answer: citations present, no PII in output, answer "
        "terms overlap the cited chunks. Reject the answer if any check fails."
    ),
    "tools": [],
}

# The multi-agent flow, in ADK SequentialAgent order:
# Router -> Retriever -> Answerer -> Verifier -> (HumanApproval if write)
MULTI_AGENT_FLOW = ["router", "retriever", "answerer", "verifier"]
