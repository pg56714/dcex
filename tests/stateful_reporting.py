"""Minimal, redacted reporting for explicitly selected stateful tests."""

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from scripts.live.redaction import redact

RESULT_FIELDS = (
    "exchange",
    "mode",
    "market",
    "stage",
    "status",
    "error_code",
    "error_message",
    "order_id",
    "client_order_id",
    "prior_client_order_ids",
    "price",
    "cleanup",
    "skip_reason",
)
RESULTS = pytest.StashKey[dict[str, dict[str, str]]]()
DETAILS = pytest.StashKey[dict[str, str]]()


def initial_result(nodeid: str) -> dict[str, str]:
    """Extract only non-sensitive identity fields from the test path."""
    parts = nodeid.replace("\\", "/").split("/")
    mode = next((part for part in parts if part in {"sync_support", "async_support"}), "")
    index = parts.index(mode) if mode else -1
    result = dict.fromkeys(RESULT_FIELDS, "")
    result.update(
        exchange=parts[index + 1] if index >= 0 else "unknown",
        mode=mode.removesuffix("_support"),
        market="unknown",
        stage="setup",
        status="running",
    )
    return result


def update_report(result: dict[str, str], report: object) -> dict[str, str]:
    """Record the final outcome without serializing pytest tracebacks or locals."""
    row = sanitize_result(result)
    if getattr(report, "skipped", False):
        row["status"] = "N/A" if row["stage"] == "not_applicable" else "skipped"
        reason = getattr(report, "longrepr", "")
        row["skip_reason"] = redact(reason[-1] if isinstance(reason, tuple) else reason)
    elif getattr(report, "failed", False):
        row["status"] = "failed"
        if not row["error_message"]:
            # Do not copy formatted traceback source lines, locals, or request bodies.
            crash = getattr(getattr(report, "longrepr", None), "reprcrash", None)
            row["error_message"] = redact(getattr(crash, "message", "test failed"))
    elif getattr(report, "when", "") == "call" and row["status"] != "failed":
        row["status"] = "passed"
    return row


def write_results(directory: Path, results: list[dict[str, str]]) -> Path | None:
    """Write only the fixed summary schema, and only when stateful tests ran."""
    if not results:
        return None
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{stamp}-{uuid4().hex[:8]}.json"
    rows = [sanitize_result(row) for row in results]
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    return path


def sanitize_result(result: dict[str, str]) -> dict[str, str]:
    """Preserve order identifiers even when they match an environment value."""
    return {
        key: redact(
            result.get(key, ""),
            mask_environment=key not in {"order_id", "client_order_id", "prior_client_order_ids"},
        )
        for key in RESULT_FIELDS
    }
