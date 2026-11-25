"""Tests for the Enterprise Knowledge Agent. Run: pytest -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from fastapi.testclient import TestClient

from enterprise_knowledge_agent.agents import KnowledgeAgent
from enterprise_knowledge_agent.api import app
from enterprise_knowledge_agent.guardrails import contains_pii, is_out_of_scope, is_write_request
from enterprise_knowledge_agent.ingestion import build_chunks, load_docs
from enterprise_knowledge_agent.tools import ToolNotAllowedError, ToolRegistry


@pytest.fixture(scope="module")
def agent():
    return KnowledgeAgent()


def test_docs_load_and_chunk(agent):
    assert len(agent.docs) == 80
    assert len(agent.chunks) == 80  # short docs => 1 chunk each
    assert all(c["chunk_id"].endswith("#c1") for c in agent.chunks)


def test_retrieval_finds_correct_product(agent):
    out = agent.ask("What is the price of BrightHarvest Almond Crunch Granola?")
    assert out["status"] == "answered"
    assert "P001" in out["citations"]
    assert "$8.99" in out["answer"]


def test_retrieval_returns_policy(agent):
    out = agent.ask("Within how many days can unopened products be returned?")
    assert out["status"] == "answered"
    assert "POL-01" in out["citations"]
    assert "30 days" in out["answer"]


def test_answer_always_cites(agent):
    for q in [
        "What is the shelf life of BrightHarvest Brown Rice Basmati?",
        "How should Green Tea Blend be brewed?",
    ]:
        out = agent.ask(q)
        assert out["status"] == "answered"
        assert len(out["citations"]) >= 1


def test_low_confidence_refuses(agent):
    out = agent.ask("Zorblax quantum flux capacitor warranty details")
    assert out["status"] == "refused"
    assert "low_confidence" in (out["refusal_reason"] or "")


def test_out_of_scope_refuses(agent):
    assert is_out_of_scope("What is the stock price of BrightHarvest?")
    out = agent.ask("What is the stock price of BrightHarvest?")
    assert out["status"] == "refused"
    assert "out_of_scope" in (out["refusal_reason"] or "")


def test_pii_refuses(agent):
    assert contains_pii("My SSN is 123-45-6789")
    out = agent.ask("My SSN is 123-45-6789, what is my order status?")
    assert out["status"] == "refused"
    assert "pii" in (out["refusal_reason"] or "")


def test_write_request_is_gated_not_executed(agent):
    assert is_write_request("Update the price of BrightHarvest Almond Crunch Granola to $5.00")
    out = agent.ask("Update the price of BrightHarvest Almond Crunch Granola to $5.00")
    assert out["status"] == "pending_approval"
    assert out["approval_id"]
    # The knowledge base must be unchanged after a gated write request.
    again = agent.ask("What is the price of BrightHarvest Almond Crunch Granola?")
    assert "$8.99" in again["answer"]


def test_confirm_write_denied_does_nothing(agent):
    pending = agent.ask("Delete the returns policy document")
    approval_id = pending["approval_id"]
    result = agent.gate.confirm_write(approval_id, confirmed=False)
    assert result["status"] == "DENIED"
    out = agent.ask("Within how many days can unopened products be returned?")
    assert out["status"] == "answered"


def test_confirm_write_approved_is_audit_only(agent):
    pending = agent.ask("Send an email to all customers about the recall")
    approval_id = pending["approval_id"]
    result = agent.gate.confirm_write(approval_id, confirmed=True)
    assert result["status"] == "APPROVED_AUDIT_ONLY"
    # KB still unchanged: returns policy still answerable.
    out = agent.ask("Within how many days can unopened products be returned?")
    assert "30 days" in (out["answer"] or "")


def test_disallowed_tool_is_blocked(agent):
    with pytest.raises(ToolNotAllowedError):
        agent.tools.call("update_price", product="P001", price="$5.00")
    with pytest.raises(ToolNotAllowedError):
        agent.tools.call("run_sql", sql="DELETE FROM docs")


def test_allowlisted_tools_work(agent):
    r = agent.tools.call("lookup_product", name_or_sku="BH-GRN-001")
    assert r["doc"]["id"] == "P001"
    r = agent.tools.call("get_policy", topic="returns")
    assert r["doc"]["id"] == "POL-01"


def test_empty_question_refuses(agent):
    out = agent.ask("   ")
    assert out["status"] == "refused"


def test_api_health_and_ask():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    r = client.post("/ask", json={"question": "What is the price of BrightHarvest Maple Syrup Pure?"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "answered"
    assert "P027" in body["citations"]
