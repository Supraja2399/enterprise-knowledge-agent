"""Ingestion: load synthetic docs, chunk them, validate.

Stand-in for: Vertex AI document loaders + BigQuery load jobs.
In GCP this would be a Dataflow / Vertex AI ingestion pipeline writing
to BigQuery (see vertex/bigquery_schema.sql). Locally it is plain JSON.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import MAX_CHUNK_WORDS

PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-like
    re.compile(r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"),  # card-like
]


def contains_pii(text: str) -> bool:
    return any(p.search(text) for p in PII_PATTERNS)


def chunk_text(text: str, doc_id: str, max_words: int = MAX_CHUNK_WORDS) -> list[dict]:
    """Split text into word-bounded chunks. Short synthetic docs => 1 chunk."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        part = " ".join(words[i : i + max_words])
        chunks.append(
            {
                "chunk_id": f"{doc_id}#c{i // max_words + 1}",
                "doc_id": doc_id,
                "text": part,
            }
        )
    return chunks


def load_docs(path: str | Path) -> list[dict]:
    path = Path(path)
    docs = json.loads(path.read_text(encoding="utf-8"))
    for d in docs:
        if not all(k in d for k in ("id", "title", "text")):
            raise ValueError(f"doc missing id/title/text: {d!r}")
        if contains_pii(d["text"]):
            raise ValueError(f"synthetic doc {d['id']} unexpectedly contains PII-like text")
    return docs


def build_chunks(docs: list[dict]) -> list[dict]:
    chunks: list[dict] = []
    for d in docs:
        for c in chunk_text(d["text"], d["id"]):
            c["title"] = d["title"]
            c["kind"] = d.get("kind", "unknown")
            chunks.append(c)
    return chunks
