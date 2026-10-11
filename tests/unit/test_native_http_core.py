"""Offline coverage for native client construction."""
# ruff: noqa: D100, D103

import pytest


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 1e300])
def test_native_http_client_rejects_invalid_timeout(timeout: float) -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="HTTP timeout must be a positive finite number"):
        native.BinanceHttpClient(timeout=timeout)


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 1e300])
def test_native_websocket_client_rejects_invalid_timeout(timeout: float) -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="WebSocket timeout must be a positive finite number"):
        native.BinancePublicWebSocketClient(timeout=timeout)
