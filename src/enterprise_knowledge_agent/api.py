"""FastAPI app: /health, /ask, /confirm-write.

Run: uvicorn enterprise_knowledge_agent.api:app --reload
or: python -m enterprise_knowledge_agent.api
"""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .agents import KnowledgeAgent

app = FastAPI(title="Enterprise Knowledge Agent (Vertex AI pattern, local)")
_agent = KnowledgeAgent()


class AskRequest(BaseModel):
    question: str


class ConfirmRequest(BaseModel):
    approval_id: str
    confirmed: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "docs": len(_agent.docs), "chunks": len(_agent.chunks)}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    return _agent.ask(req.question)


@app.post("/confirm-write")
def confirm_write(req: ConfirmRequest) -> dict:
    return _agent.gate.confirm_write(req.approval_id, confirmed=req.confirmed)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
