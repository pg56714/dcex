"""Unit tests for the shared HTTP manager base helpers."""

from dcex.base.http_manager import BaseHTTPManager
from dcex.utils.common import Common


def test_setup_logger_defaults_to_module_name() -> None:
    """Without a supplied logger, the logger is named after the class module."""

    class Dummy(BaseHTTPManager):
        EXCHANGE = Common.BINANCE

    logger = Dummy()._setup_logger(None)
    assert logger.name == Dummy.__module__


def test_setup_logger_uses_supplied_logger() -> None:
    """A supplied logger is returned unchanged."""
    import logging

    class Dummy(BaseHTTPManager):
        pass

    custom = logging.getLogger("custom-test-logger")
    assert Dummy()._setup_logger(custom) is custom


def test_exception_response_details_extracts_native_http_status() -> None:
    """Native Rust HTTP errors expose the status in the RuntimeError message."""
    status_code, headers = BaseHTTPManager._exception_response_details(
        RuntimeError("HTTP request failed with status 400: bad request"),
    )

    assert status_code == 400
    assert headers is None
