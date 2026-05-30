"""Offline tests that HTTP managers emit log records on request paths.

These use a fake session so no network call is made. They assert that a debug
record is emitted when a request is sent and an error record is emitted just
before a failed request is raised.
"""

import logging

import pytest

from dcex.base.http_manager import BaseHTTPManager
from dcex.utils.common import Common
from dcex.utils.errors import FailedRequestError


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, text: str = "") -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.text = text

    def json(self) -> dict:
        return self._payload


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


def test_binance_request_logs_debug_and_error(caplog: pytest.LogCaptureFixture) -> None:
    """Binance emits a debug send record and an error record on API failure."""
    from dcex.binance._http_manager import HTTPManager
    from dcex.binance.endpoints.market import SpotMarket

    manager = HTTPManager(api_key="k", api_secret="s", preload_product_table=False)
    manager.session = _FakeSession()  # type: ignore[assignment]

    logger_name = "dcex.binance._http_manager"
    with caplog.at_level(logging.DEBUG, logger=logger_name):
        with pytest.raises(FailedRequestError):
            manager._request("GET", SpotMarket.EXCHANGE_INFO, query={}, signed=False)

    messages = [r.message for r in caplog.records]
    assert any("request:" in m for m in messages)
    assert any("request failed" in m for m in messages)


class _FakeSession:
    """Minimal stand-in for requests.Session returning a Binance API error."""

    def get(self, *args: object, **kwargs: object) -> _FakeResponse:
        return _FakeResponse({"code": -1100, "msg": "illegal"}, status_code=200)
