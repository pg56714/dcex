"""Offline tests for synchronous HTTP session lifecycle handling."""
# ruff: noqa: D103

from typing import Any

import pytest
import requests

from dcex.aster.client import Client as AsterClient
from dcex.aster.endpoints.market import SpotMarket as AsterSpotMarket
from dcex.backpack.client import Client as BackpackClient
from dcex.binance.client import Client as BinanceClient
from dcex.binance.endpoints.market import SpotMarket as BinanceSpotMarket
from dcex.bingx.client import Client as BingXClient
from dcex.bitget.client import Client as BitgetClient
from dcex.bitmart.client import Client as BitmartClient
from dcex.bitmart.endpoints.market import SpotMarket as BitmartSpotMarket
from dcex.bitmex.client import Client as BitmexClient
from dcex.bybit.client import Client as BybitClient
from dcex.gateio.client import Client as GateioClient
from dcex.hyperliquid.client import Client as HyperliquidClient
from dcex.kraken.client import Client as KrakenClient
from dcex.kucoin.client import Client as KuCoinClient
from dcex.lighter.client import Client as LighterClient
from dcex.mexc.client import Client as MEXCClient
from dcex.okx.client import Client as OKXClient
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


class _Session:
    closed = False

    def close(self) -> None:
        self.closed = True


class _RaisingSession(_Session):
    def __init__(self, response: requests.Response) -> None:
        self.response = response

    def get(self, *args: object, **kwargs: object) -> requests.Response:
        raise requests.RequestException("transport failed", response=self.response)


@pytest.mark.parametrize("client_type", _CLIENT_TYPES)
def test_sync_client_closes_session(client_type: type[Any]) -> None:
    client = client_type(preload_product_table=False)
    session = _Session()
    client.session = session

    client.close()

    assert session.closed


@pytest.mark.parametrize("client_type", _CLIENT_TYPES)
def test_sync_client_preserves_transport_error_response(client_type: type[Any]) -> None:
    response = requests.Response()
    response.status_code = 429
    response.headers["Retry-After"] = "1"
    assert not response

    client = client_type(preload_product_table=False)
    client.session = _RaisingSession(response)

    with pytest.raises(FailedRequestError) as exc_info:
        client._request("GET", _REQUEST_PATHS.get(client_type, "/test"), signed=False)

    assert exc_info.value.status_code == 429
    assert exc_info.value.resp_headers == {"Retry-After": "1"}
