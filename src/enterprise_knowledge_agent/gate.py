"""Human-at-the-gate: no write/update/send action is ever auto-executed.

Design:
- request_write() returns PENDING_APPROVAL with an approval_id and logs
  the attempt. It never mutates the knowledge base.
- confirm_write(approval_id, confirmed=True) only marks the request
  APPROVED and appends an audit entry. In this local demo, even an
  approved write is NOT applied to docs.json — it is audit-logged only.
  That is stated in the README so a reviewer is not misled.
- confirm_write(..., confirmed=False) leaves it pending / records a denial.
- Every attempt (request, confirm, deny, blocked-tool call) is appended
  to data/audit_log.jsonl.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import AUDIT_LOG_PATH


def _log(event: dict) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


class ApprovalGate:
    """In-memory pending-write store backed by an append-only audit log."""

    def __init__(self, audit_path: str | Path = AUDIT_LOG_PATH):
        self.audit_path = Path(audit_path)
        self._pending: dict[str, dict] = {}

    def request_write(self, action: str, payload: dict) -> dict:
        approval_id = str(uuid.uuid4())[:8]
        record = {"approval_id": approval_id, "action": action, "payload": payload, "status": "PENDING_APPROVAL"}
        self._pending[approval_id] = record
        _log({"event": "write_requested", "approval_id": approval_id, "action": action})
        return {"status": "PENDING_APPROVAL", "approval_id": approval_id,
                "message": "Write action requires explicit human confirmation. It has NOT been executed."}

    def confirm_write(self, approval_id: str, confirmed: bool) -> dict:
        record = self._pending.get(approval_id)
        if record is None:
            return {"status": "NOT_FOUND", "approval_id": approval_id}
        if not confirmed:
            record["status"] = "DENIED"
            _log({"event": "write_denied", "approval_id": approval_id, "action": record["action"]})
            return {"status": "DENIED", "approval_id": approval_id,
                    "message": "Write denied by human. Nothing was executed."}
        record["status"] = "APPROVED_AUDIT_ONLY"
        _log({"event": "write_approved_audit_only", "approval_id": approval_id, "action": record["action"]})
        return {"status": "APPROVED_AUDIT_ONLY", "approval_id": approval_id,
                "message": "Approved by human and audit-logged. In this local demo the write is NOT applied to the knowledge base."}

    def pending_count(self) -> int:
        return sum(1 for r in self._pending.values() if r["status"] == "PENDING_APPROVAL")
