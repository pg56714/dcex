"""Extended WebSocket credential and subscription validation."""

import pytest


@pytest.mark.asyncio
async def test_extended_rejects_empty_credentials_and_invalid_ws_values() -> None:
    native = pytest.importorskip("dcex._native")
    with pytest.raises(ValueError, match="API key must not be empty"):
        native.ExtendedHttpClient(api_key=" ", timeout=2)
    with pytest.raises(ValueError, match="API key must not be empty"):
        native.ExtendedPrivateWebSocketClient(api_key=" ", timeout=2)
    public = native.ExtendedPublicWebSocketClient(timeout=2)
    with pytest.raises(ValueError, match="depth must be 1"):
        await public.subscribe_orderbook(None, 2)
    with pytest.raises(ValueError, match="unsupported Extended candle interval"):
        await public.subscribe_candles("BTC-USD", "trades", "1m")
