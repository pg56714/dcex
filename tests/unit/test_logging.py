"""
Offline tests that HTTP managers emit log records on request paths.

These use a fake session so no network call is made. They assert that a debug
record is emitted when a request is sent and an error record is emitted just
before a failed request is raised.
"""

import logging

import pytest

from dcex.base.http_manager import BaseHTTPManager
from dcex.utils.common import Common


def test_default_logger_has_null_handler() -> None:
    """The resolved default logger carries a NullHandler so the lib is quiet."""

    class Dummy(BaseHTTPManager):
        EXCHANGE = Common.BINANCE

    logger = Dummy()._setup_logger(None)
    assert any(isinstance(h, logging.NullHandler) for h in logger.handlers)


def test_log_failed_request_emits_error(caplog: pytest.LogCaptureFixture) -> None:
    """_log_failed_request emits an error record naming the exchange."""

    class Dummy(BaseHTTPManager):
        EXCHANGE = Common.OKX

        def __init__(self) -> None:
            self._logger = logging.getLogger("dcex.test.okx")

    with caplog.at_level(logging.ERROR, logger="dcex.test.okx"):
        Dummy()._log_failed_request("boom", 500)

    assert any("request failed" in r.message and "okx" in r.message for r in caplog.records)


def test_request_logs_redact_query_parameters_and_credentials(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Request and failure logs must not expose signed query values."""

    class Dummy(BaseHTTPManager):
        EXCHANGE = Common.MEXC

        def __init__(self) -> None:
            self._logger = logging.getLogger("dcex.test.redaction")

    with caplog.at_level(logging.DEBUG, logger="dcex.test.redaction"):
        manager = Dummy()
        manager._log_request(
            "POST",
            "https://api.example.com/order?timestamp=1&signature=url-secret",
        )
        manager._log_failed_request(
            "failed for https://api.example.com/order?signature=message-secret "
            "with 'api_key': 'private-key' and Authorization: Bearer bearer-token",
            401,
        )

    rendered = "\n".join(record.message for record in caplog.records)
    assert "https://api.example.com/order" in rendered
    for sensitive_value in (
        "timestamp",
        "signature",
        "url-secret",
        "message-secret",
        "api_key",
        "private-key",
        "bearer-token",
    ):
        assert sensitive_value not in rendered
