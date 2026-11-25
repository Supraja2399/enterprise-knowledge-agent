"""Configuration. All values are local defaults; no secrets here."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "synthetic" / "docs.json"
AUDIT_LOG_PATH = PROJECT_ROOT / "data" / "audit_log.jsonl"

TOP_K = 3
# TF-IDF cosine threshold below which the agent refuses (low confidence).
# Set at 0.20 after measurement: the lowest-scoring answerable eval case
# scores 0.2214, while a single-token nonsense match scores 0.1801.
# A token-coverage check (agents.py) also applies, so a one-word match
# can never ground an answer on its own.
CONFIDENCE_THRESHOLD = 0.20
MAX_CHUNK_WORDS = 60
