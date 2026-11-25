"""Deterministic offline retrieval (TF-IDF cosine, pure Python).

Stand-in for: BigQuery Vector Search / AlloyDB vector engine.
The interface is deliberately adapter-shaped: `VectorStore.search(query)`
returns ranked chunks with scores. In GCP, swap this class for a
BigQueryVectorStore that calls BigQuery ML / Vector Search with the
same method signature (see vertex/bigquery_schema.sql and vertex/DEPLOY.md).
No embeddings API is called locally; TF-IDF is computed from the docs.
"""
from __future__ import annotations

import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "what", "how", "why", "when",
    "where", "which", "who", "does", "do", "did", "can", "could", "should",
    "would", "will", "of", "for", "in", "on", "at", "to", "and", "or", "it",
    "its", "this", "that", "with", "by", "from", "as", "be", "have", "has",
    "i", "you", "we", "my", "your", "please", "tell", "me", "about", "there",
    "if", "so", "not", "no", "yes", "per", "per", "use", "used",
}

_TOKEN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN.findall(text.lower())
    return [t for t in tokens if t not in STOPWORDS]


class VectorStore:
    """TF-IDF vector store over document chunks."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self._doc_freq: Counter = Counter()
        self._vectors: list[dict[str, float]] = []
        self._norms: list[float] = []
        n = len(chunks)
        tokenised = [tokenize(c["text"] + " " + c.get("title", "")) for c in chunks]
        for toks in tokenised:
            for t in set(toks):
                self._doc_freq[t] += 1
        for toks in tokenised:
            counts = Counter(toks)
            vec: dict[str, float] = {}
            for term, count in counts.items():
                tf = 1.0 + math.log(count) if count else 0.0
                idf = math.log((n + 1) / (self._doc_freq[term] + 1)) + 1.0
                vec[term] = tf * idf
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self._vectors.append(vec)
            self._norms.append(norm)
        self._n = n

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Return top_k chunks as {chunk, score} sorted by cosine score desc."""
        qtokens = tokenize(query)
        if not qtokens:
            return []
        qcounts = Counter(qtokens)
        qvec: dict[str, float] = {}
        for term, count in qcounts.items():
            tf = 1.0 + math.log(count) if count else 0.0
            idf = math.log((self._n + 1) / (self._doc_freq.get(term, 0) + 1)) + 1.0
            qvec[term] = tf * idf
        qnorm = math.sqrt(sum(v * v for v in qvec.values())) or 1.0
        scored = []
        for idx, vec in enumerate(self._vectors):
            dot = sum(qvec[t] * vec.get(t, 0.0) for t in qvec)
            score = dot / (qnorm * self._norms[idx]) if dot else 0.0
            scored.append((score, idx))
        scored.sort(key=lambda x: (-x[0], self.chunks[x[1]]["chunk_id"]))
        return [
            {"chunk": self.chunks[idx], "score": round(float(score), 4)}
            for score, idx in scored[:top_k]
            if score > 0
        ]
