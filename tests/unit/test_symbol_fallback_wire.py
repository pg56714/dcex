"""Public symbol conversion through both Python wrappers and the native transport."""

import importlib
import inspect
import os
from urllib.parse import parse_qs, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def _client_options(exchange: str, base_url: str) -> dict[str, object]:
    options: dict[str, object] = {"base_url": base_url, "preload_product_table": False}
    if exchange in {"bybit", "okx"}:
        options.pop("base_url")
        if exchange == "okx":
            options["base_api"] = base_url
        else:
            options["sync_server_time"] = False
    if exchange in {"kraken", "kucoin"}:
        options["futures_base_url"] = base_url
    if exchange == "mexc":
        options["contract_base_url"] = base_url
    if exchange == "aster":
        options.pop("base_url")
        options.update(
            spot_base_url=base_url, futures_base_url=base_url, prediction_base_url=base_url
        )
    return options


def _inject_bybit_mock(client: object, exchange: str, base_url: str) -> None:
    if exchange == "bybit":
        native = importlib.import_module("dcex._native")
        client._native_client = native.BybitHttpClient(  # type: ignore[attr-defined]
            base_url=base_url, sync_server_time=False
        )


@pytest.fixture(autouse=True)
def _remove_real_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith(
            (
                "EXTENDED_",
                "BITGET_",
                "BYBIT_",
                "OKX_",
                "KRAKEN_",
                "KUCOIN_",
                "BINGX_",
                "MEXC_",
                "ASTER_",
                "BACKPACK_",
            )
        ):
            monkeypatch.delenv(name)


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("exchange", "method", "kwargs", "native_symbol"),
    [
        ("extended", "get_order_book", {"market": "BTC-USD-SPOT"}, "BTCSPOT-USD"),
        ("extended", "get_order_book", {"market": "ETH-USD-SPOT"}, "ETHSPOT-USD"),
        ("extended", "get_order_book", {"market": "USDT-USD-SPOT"}, "USDTSPOT-USD"),
        (
            "bitget",
            "get_uta_tickers",
            {"category": "COIN-FUTURES", "product_symbol": "BTC-USD-SWAP"},
            "BTCUSD_CM",
        ),
        (
            "bitget",
            "get_uta_tickers",
            {"category": "USDC-FUTURES", "product_symbol": "BTC-USDC-SWAP"},
            "BTCPERP",
        ),
        (
            "bybit",
            "get_instruments_info",
            {"category": "linear", "product_symbol": "BTC-USDC-SWAP"},
            "BTCPERP",
        ),
        (
            "okx",
            "get_orderbook",
            {"product_symbol": "BTC-USD-261225-80000-C"},
            "BTC-USD-261225-80000-C",
        ),
        ("kraken", "get_spot_ticker", {"product_symbol": "DOGE-USD-SPOT"}, "XDGUSD"),
        ("kraken", "get_spot_ticker", {"product_symbol": "AAPLx-USD-SPOT"}, "AAPLxUSD"),
        ("kucoin", "get_spot_ticker", {"product_symbol": "BTC-USDT-SPOT"}, "BTC-USDT"),
        ("kucoin", "get_futures_ticker", {"product_symbol": "BTC-USDT-SWAP"}, "XBTUSDTM"),
        (
            "kucoin",
            "get_uta_tickers",
            {"trade_type": "FUTURES", "product_symbol": "BTC-USDT-SWAP"},
            "XBTUSDTM",
        ),
        ("aster", "get_spot_orderbook", {"product_symbol": "BTC-USDT-SPOT"}, "BTCUSDT"),
        ("backpack", "get_order_book_depth", {"product_symbol": "BTC-USDC-SWAP"}, "BTC_USDC_PERP"),
    ],
)
@pytest.mark.asyncio
async def test_public_symbol_wire(
    async_mode: bool,
    exchange: str,
    method: str,
    kwargs: dict[str, str],
    native_symbol: str,
) -> None:
    """The two wrappers must send the same complete official symbol."""
    module = importlib.import_module(
        f"dcex.{'async_support.' if async_mode else ''}{exchange}.client"
    )
    payload = {
        "status": "OK",
        "code": {"bitget": "00000", "kucoin": "200000"}.get(exchange, "0"),
        "retCode": 0,
        "data": [],
        "result": {},
        "error": [],
    }
    with _http_server(payload) as (base_url, received):
        client = module.Client(**_client_options(exchange, base_url))
        if async_mode:
            await client.async_init()
        _inject_bybit_mock(client, exchange, base_url)
        try:
            result = getattr(client, method)(**kwargs)
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
    request = received.get_nowait()
    url = urlsplit(request["path"])
    if exchange == "extended":
        assert url.path == f"/api/v1/info/markets/{native_symbol}/orderbook"
    else:
        key = "instId" if exchange == "okx" else "pair" if exchange == "kraken" else "symbol"
        assert parse_qs(url.query)[key] == [native_symbol]
    assert received.empty()


@pytest.mark.parametrize("async_mode", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    ("exchange", "method", "kwargs"),
    [
        ("extended", "get_order_book", {"market": "BTC-USD-261225-FUTURES"}),
        (
            "bitget",
            "get_uta_tickers",
            {"category": "COIN-FUTURES", "product_symbol": "BTC-USD-BTCCMZ26-FUTURES"},
        ),
        (
            "bybit",
            "get_instruments_info",
            {"category": "linear", "product_symbol": "BTC-USDT-09OCT26-SWAP"},
        ),
        ("bingx", "get_orderbook", {"product_symbol": "NEIRO-USDT-SWAP"}),
        ("mexc", "get_contract_depth", {"product_symbol": "NVDA-USDT-SWAP"}),
        ("extended", "get_order_book", {"market": "AAPL-USD-SWAP"}),
        ("backpack", "get_order_book_depth", {"product_symbol": "FOMC0126H0-USDC-PREDICTION"}),
        ("kucoin", "get_futures_ticker", {"product_symbol": "BTC-USD-XBTMZ26-FUTURES"}),
    ],
)
@pytest.mark.asyncio
async def test_unknown_contract_requires_table_before_transport(
    async_mode: bool,
    exchange: str,
    method: str,
    kwargs: dict[str, str],
) -> None:
    """A canonical expiry cannot accidentally turn into a perpetual request."""
    module = importlib.import_module(
        f"dcex.{'async_support.' if async_mode else ''}{exchange}.client"
    )
    with _http_server() as (base_url, received):
        client = module.Client(**_client_options(exchange, base_url))
        if async_mode:
            await client.async_init()
        _inject_bybit_mock(client, exchange, base_url)
        try:
            with pytest.raises(ValueError, match="product table"):
                result = getattr(client, method)(**kwargs)
                if inspect.isawaitable(result):
                    await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.empty()
