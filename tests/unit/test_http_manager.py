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
        RuntimeError("Bybit API Error: [10001] bad request (HTTP 400)"),
    )

    assert status_code == 400
    assert headers is None


def test_exception_without_status_is_none_never_unknown() -> None:
    status_code, _ = BaseHTTPManager._exception_response_details(RuntimeError("timeout"))
    assert status_code is None


def test_native_http_errors_carry_status_and_shared_format() -> None:
    from dcex import _native
    from dcex.utils.errors import FailedRequestError, api_error_from_body, api_error_message

    assert (
        api_error_from_body(
            "Ondo", 400, '{"error":"IOC only","error_code":"reduce_only_invalid_tif"}'
        )
        == "Ondo API Error: [reduce_only_invalid_tif] IOC only (HTTP 400)"
    )
    assert api_error_message("Bybit", 200, None, "") == (
        "Bybit API Error: [HTTP 200] no error message (HTTP 200)"
    )
    error = FailedRequestError(request="GET /x", message="Bybit API Error: [1] x (HTTP 400)")
    assert "Unknown" not in str(error) and error.status_code is None
    assert _native.api_error_message("OKX", 400, "51000", "bad") == (
        "OKX API Error: [51000] bad (HTTP 400)"
    )
