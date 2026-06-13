"""Offline tests for asynchronous HTTP session lifecycle handling."""
# ruff: noqa: D103

from typing import Any

import httpx
import pytest

from dcex.async_support.aster.client import Client as AsterClient
from dcex.async_support.aster.endpoints.market import SpotMarket as AsterSpotMarket
from dcex.async_support.backpack.client import Client as BackpackClient
from dcex.async_support.binance.client import Client as BinanceClient
from dcex.async_support.binance.endpoints.market import SpotMarket as BinanceSpotMarket
from dcex.async_support.bingx.client import Client as BingXClient
from dcex.async_support.bitget.client import Client as BitgetClient
from dcex.async_support.bitmart.client import Client as BitmartClient
from dcex.async_support.bitmart.endpoints.market import SpotMarket as BitmartSpotMarket
from dcex.async_support.bitmex.client import Client as BitmexClient
from dcex.async_support.bybit.client import Client as BybitClient
from dcex.async_support.gateio.client import Client as GateioClient
from dcex.async_support.hyperliquid.client import Client as HyperliquidClient
from dcex.async_support.kraken.client import Client as KrakenClient
from dcex.async_support.kucoin.client import Client as KuCoinClient
from dcex.async_support.lighter.client import Client as LighterClient
from dcex.async_support.mexc.client import Client as MEXCClient
from dcex.async_support.okx.client import Client as OKXClient
from dcex.async_support.product_table.manager import ProductTableManager
from dcex.product_table.manager import ProductTableError
from dcex.utils.errors import FailedRequestError

_CLIENT_TYPES = [
    AsterClient,
    BackpackClient,
    BinanceClient,
    BingXClient,
    BitgetClient,
    BitmartClient,
    BitmexClient,
    BybitClient,
    GateioClient,
    HyperliquidClient,
    KrakenClient,
    KuCoinClient,
    LighterClient,
    MEXCClient,
    OKXClient,
]

_REQUEST_PATHS = {
    AsterClient: AsterSpotMarket.PING,
    BinanceClient: BinanceSpotMarket.SERVER_TIME,
    BitmartClient: BitmartSpotMarket.GET_TRADING_PAIRS,
}


class _RaisingSession:
    is_closed = False

    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    async def get(self, *args: object, **kwargs: object) -> httpx.Response:
        request = httpx.Request("GET", "https://example.test")
        error = httpx.ReadError("transport failed", request=request)
        error.response = self.response
        raise error


@pytest.mark.asyncio
@pytest.mark.parametrize("client_type", _CLIENT_TYPES)
async def test_async_client_reuses_open_session(client_type: type[Any]) -> None:
    client = client_type(preload_product_table=False)
    await client.async_init()
    original_session = client.session

    try:
        assert original_session is not None
        await client.async_init()
        assert client.session is original_session

        entered = await client.__aenter__()
        assert entered is client
        assert client.session is original_session
        assert not original_session.is_closed
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("client_type", _CLIENT_TYPES)
async def test_product_table_failure_does_not_create_session(
    client_type: type[Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fail_get_instance(
        cls: type[ProductTableManager],
        exchange_name: str | None = None,
    ) -> ProductTableManager:
        raise ProductTableError(f"failed to load {exchange_name}")

    monkeypatch.setattr(ProductTableManager, "get_instance", classmethod(fail_get_instance))
    client = client_type()

    with pytest.raises(ProductTableError):
        await client.async_init()

    assert client.session is None


@pytest.mark.asyncio
@pytest.mark.parametrize("client_type", _CLIENT_TYPES)
async def test_async_client_preserves_transport_error_response(
    client_type: type[Any],
) -> None:
    request = httpx.Request("GET", "https://example.test")
    response = httpx.Response(
        429,
        headers={"Retry-After": "1"},
        request=request,
    )
    client = client_type(preload_product_table=False)
    await client.async_init()
    assert client.session is not None
    await client.session.aclose()
    client.session = _RaisingSession(response)

    with pytest.raises(FailedRequestError) as exc_info:
        await client._request("GET", _REQUEST_PATHS.get(client_type, "/test"), signed=False)

    assert exc_info.value.status_code == 429
    assert exc_info.value.resp_headers == {"retry-after": "1"}
