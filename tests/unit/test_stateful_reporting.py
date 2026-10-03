"""Offline checks for stateful summaries and credential redaction."""

import json
from types import SimpleNamespace

from tests.stateful_reporting import (
    RESULT_FIELDS,
    initial_result,
    redact,
    update_report,
    write_results,
)

pytest_plugins = ["pytester"]


def test_vault_redaction_does_not_destroy_order_identifiers(monkeypatch, tmp_path):
    monkeypatch.setenv("EXTENDED_VAULT_NUMBER", "12")
    assert redact("vault 12 orderId 9876543210123") == "vault [redacted] orderId 9876543210123"
    monkeypatch.setenv("MOCK_API_SECRET", "9876543210123")
    record = dict(order_id="9876543210123", client_order_id="12", error_message="vault 12")
    row = update_report(record, SimpleNamespace(when="call", skipped=False, failed=False))
    saved = json.loads(write_results(tmp_path, [row]).read_text())[0]
    assert saved["order_id"] == "9876543210123"
    assert saved["client_order_id"] == "12"
    assert "12" not in saved["error_message"]


def test_jwt_is_redacted_even_when_each_segment_is_short():
    token = "eyJmb28iOjF9.eyJiYXIiOjJ9.c2lnbmF0dXJl"
    assert redact("rejected " + token) == "rejected [jwt redacted]"


def test_redaction_removes_known_secrets_addresses_and_request_urls(monkeypatch):
    secret = "synthetic-sensitive-value"
    monkeypatch.setenv("EXAMPLE_API_SECRET", secret)
    address = "0x" + "ab" * 20
    text = redact(f"rejected {secret} {address} https://example.invalid?signature=opaque")
    assert secret not in text and address not in text
    assert "signature=opaque" not in text
    assert "rejected" in text
    assert "other synthetic value" not in redact('{"api_secret": "other synthetic value"}')


def test_redaction_covers_unlabelled_base64_and_short_vault_numbers(monkeypatch):
    value = "+/" + "Ab0=" * 10 + "=="
    assert len(value) == 44
    assert value not in redact("failure: " + value)
    assert "4321" not in redact('vault_number="4321"')
    monkeypatch.setenv("EXTENDED_VAULT_NUMBER", "4321")
    assert "4321" not in redact("opaque account identifier 4321")


def test_summary_uses_only_allowlisted_fields_and_does_not_save_tracebacks(tmp_path):
    row = initial_result("tests/sync_support/kucoin/test_stateful_trade.py::test_order[spot]")
    row.update(
        market="spot",
        stage="cancel",
        order_id="123456",
        api_secret="do-not-write",
        cleanup="cleanup cancellation unconfirmed",
    )
    report = SimpleNamespace(
        when="call",
        failed=True,
        skipped=False,
        longrepr=SimpleNamespace(reprcrash=SimpleNamespace(message="cancel rejected")),
    )
    result = update_report(row, report)
    path = write_results(tmp_path / "results", [result])
    assert path is not None
    stored = json.loads(path.read_text())
    assert set(stored[0]) == set(RESULT_FIELDS)
    assert stored[0]["exchange"] == "kucoin"
    assert stored[0]["mode"] == "sync"
    assert stored[0]["status"] == "failed"
    assert stored[0]["stage"] == "cancel"
    assert stored[0]["order_id"] == "123456"
    assert stored[0]["cleanup"] == "cleanup cancellation unconfirmed"
    assert "do-not-write" not in path.read_text()


def test_empty_offline_run_does_not_create_a_results_directory(tmp_path):
    directory = tmp_path / "results"
    assert write_results(directory, []) is None
    assert not directory.exists()


def test_skip_reason_and_error_messages_are_redacted():
    row = initial_result("tests/async_support/arcus/test_stateful_trade.py::test_order[spot]")
    report = SimpleNamespace(
        when="setup",
        skipped=True,
        failed=False,
        longrepr=("test.py", 1, "insufficient balance; api_key=do-not-keep"),
    )
    result = update_report(row, report)
    assert result["status"] == "skipped"
    assert "insufficient balance" in result["skip_reason"]
    assert "do-not-keep" not in result["skip_reason"]


def test_pytest_hook_writes_only_stateful_results(pytester):
    pytester.makeini(
        "[pytest]\nmarkers = stateful: mock stateful lifecycle\nasyncio_default_fixture_loop_scope = function\n"
    )
    pytester.makeconftest("""
from tests.conftest import (
    stateful_result, pytest_runtest_makereport,
    pytest_sessionfinish, pytest_terminal_summary,
)
""")
    pytester.makepyfile("""
import pytest

@pytest.mark.stateful
def test_mock_lifecycle(stateful_result):
    stateful_result.update(exchange="kucoin", mode="sync", market="spot", stage="cancelled", cleanup="cleanup-unconfirmed")

def test_offline():
    pass
""")
    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=2)
    assert "cleanup-unconfirmed" in result.stdout.str()
    files = list((pytester.path / "live-results").glob("*.json"))
    assert len(files) == 1
    rows = json.loads(files[0].read_text())
    assert len(rows) == 1
    assert rows[0]["stage"] == "cancelled"
    assert rows[0]["status"] == "passed"
