"""Deterministic guardrails — code, not just a prompt.

Enforced in agents.ask() before any answer is returned:
  1. PII blocklist (SSN-like, card-like, email in a write context is refused)
  2. Out-of-scope refusal
  3. Confidence threshold refusal
  4. Citation-required: an answer without citations is refused
  5. Allowlisted tools only (enforced in tools.py)
"""
from __future__ import annotations

import re

PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN-like number"),
    (re.compile(r"\b\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}\b"), "card-like number"),
    (re.compile(r"\b\d{3}[- ]\d{3}[- ]\d{4}\b"), "phone-like number in a PII request"),
]

OUT_OF_SCOPE_PATTERNS = [
    re.compile(r"\bstock price\b", re.I),
    re.compile(r"\bshare price\b", re.I),
    re.compile(r"\bdiagnos(e|is|ing)\b", re.I),
    re.compile(r"\bmedical advice\b", re.I),
    re.compile(r"\bweather\b", re.I),
    re.compile(r"\bwho will win the (election|game|match)\b", re.I),
    re.compile(r"\btell me a joke\b", re.I),
    re.compile(r"\bwrite (me )?a (poem|story|song)\b", re.I),
    re.compile(r"\bwhat is the meaning of life\b", re.I),
    re.compile(r"\bpolitic", re.I),
]

WRITE_VERBS = [
    "update", "change", "delete", "remove", "send", "email", "notify",
    "set the price", "raise the price", "lower the price", "refund",
    "cancel my order", "place an order", "create a ticket",
]


def find_pii(text: str) -> list[str]:
    return [label for pat, label in PII_PATTERNS if pat.search(text)]


def contains_pii(text: str) -> bool:
    return bool(find_pii(text))


def is_out_of_scope(query: str) -> bool:
    return any(p.search(query) for p in OUT_OF_SCOPE_PATTERNS)


def is_write_request(query: str) -> bool:
    q = query.lower()
    return any(v in q for v in WRITE_VERBS)


def redact_pii(text: str) -> str:
    out = text
    for pat, _ in PII_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out
