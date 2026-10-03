"""Loaded product tables scope native symbols by market before any request is sent."""

import json
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from dcex import _native
from tests.unit.native_http_helpers import _http_server

GENERIC = {"code": 0, "retCode": 0, "success": True, "status": "OK", "error": [], "data": {}}


def _table(*rows: tuple[str, str, str, str, str], **extra: str) -> _native.ProductTable:
    return _native.ProductTable(
        [
            {
                "exchange": exchange,
                "product_symbol": product,
                "exchange_symbol": native,
                "product_type": kind,
                "exchange_type": category,
                "base_currency": product.split("-")[0],
                "quote_currency": product.split("-")[1],
                **extra,
            }
            for exchange, product, native, kind, category in rows
        ]
    )


def _query(request: dict[str, Any]) -> dict[str, list[str]]:
    return parse_qs(urlsplit(request["path"]).query)


def test_bitget_margin_category_resolves_spot_rows():
    table = _table(
        ("bitget", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("bitget", "BTC-USDT-SWAP", "BTCUSDT", "swap", "USDT-FUTURES"),
    )
    with _http_server({"code": "00000", "data": {}}) as (base_url, received):
        client = _native.BitgetHttpClient("key", "secret", "pass", base_url=base_url)
        client.set_product_table(table)
        for symbol in ("BTCUSDT", "BTC-USDT-SPOT"):
            client.private_request_json(
                "get_uta_history_orders", [("category", "MARGIN"), ("product_symbol", symbol)]
            )
            assert _query(received.get_nowait())["symbol"] == ["BTCUSDT"]
        with pytest.raises(Exception, match="BTC-USDT-SWAP"):
            client.private_request_json(
                "get_uta_history_orders",
                [("category", "MARGIN"), ("product_symbol", "BTC-USDT-SWAP")],
            )
        assert received.empty()


def test_bingx_coin_margined_route_ignores_usdt_margined_rows():
    table = _table(("bingx", "BTC-USDT-SWAP", "BTC-USDT", "swap", "perpetual"))
    with _http_server(GENERIC) as (base_url, received):
        client = _native.BingxHttpClient(base_url=base_url)
        client.set_product_table(table)
        client.public_request_json("get_coin_swap_orderbook", [("product_symbol", "BTC-USD")])
        request = received.get_nowait()
        assert urlsplit(request["path"]).path == "/openApi/cswap/v1/market/depth"
        assert _query(request)["symbol"] == ["BTC-USD"]


@pytest.mark.parametrize(
    ("symbol", "pair"),
    [
        ("BTC-USD-SPOT", "XXBTZUSD"),
        ("XXBTZUSD", "XXBTZUSD"),
        ("BTC/USD", "XXBTZUSD"),
        ("XBTUSD", "XBTUSD"),
    ],
)
def test_kraken_accepts_official_altname(symbol, pair):
    table = _table(
        ("kraken", "BTC-USD-SPOT", "XXBTZUSD", "spot", "spot"), exchange_symbol_alias="XBTUSD"
    )
    assert table.rows()[0]["exchange_symbol_alias"] == "XBTUSD"
    with _http_server({"error": [], "result": {}}) as (base_url, received):
        client = _native.KrakenHttpClient(spot_base_url=base_url, futures_base_url=base_url)
        client.set_product_table(table)
        client.public_request_json("get_spot_orderbook", [("product_symbol", symbol)])
        assert _query(received.get_nowait())["pair"] == [pair]
        with pytest.raises(Exception, match="Cannot resolve"):
            client.public_request_json("get_spot_orderbook", [("product_symbol", "xbtusd")])
        assert received.empty()


def test_bybit_unscoped_native_order_symbol_sets_row_category():
    table = _table(
        ("bybit", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("bybit", "BTC-USDT-SWAP", "BTCUSDT", "swap", "linear"),
        ("bybit", "SOL-USDT-SPOT", "SOLUSDT", "spot", "spot"),
    )
    order = [("side", "buy"), ("orderType", "Limit"), ("qty", "1"), ("price", "1")]
    with _http_server(GENERIC) as (base_url, received):
        client = _native.BybitHttpClient("key", "secret", sync_server_time=False, base_url=base_url)
        client.set_product_table(table)
        client.private_request_json("place_order", [("product_symbol", "SOLUSDT"), *order])
        body = json.loads(received.get_nowait()["body"])
        assert (body["category"], body["symbol"]) == ("spot", "SOLUSDT")
        with pytest.raises(Exception, match="BTC-USDT-SPOT.*BTC-USDT-SWAP"):
            client.private_request_json("place_order", [("product_symbol", "BTCUSDT"), *order])
        assert received.empty()


def test_binance_unscoped_native_symbol_routes_to_unique_market():
    table = _table(
        ("binance", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
        ("binance", "XRP-USDT-SWAP", "XRPUSDT", "swap", "PERPETUAL"),
        ("binance_coinm", "BTC-USD-SWAP", "BTCUSD_PERP", "swap", "PERPETUAL"),
    )
    with _http_server({}) as (base_url, received):
        client = _native.BinanceHttpClient(spot_base_url=base_url, futures_base_url=base_url)
        client.set_product_table(table)
        client.public_request_json("get_klines", [("product_symbol", "XRPUSDT"), ("interval", "1m")])
        request = received.get_nowait()
        assert urlsplit(request["path"]).path == "/fapi/v1/klines"
        assert _query(request)["symbol"] == ["XRPUSDT"]
        for symbol, message in (("BTCUSDT", "candidates"), ("BTCUSD_PERP", "coin-futures")):
            with pytest.raises(Exception, match=message):
                client.public_request_json(
                    "get_klines", [("product_symbol", symbol), ("interval", "1m")]
                )
        assert received.empty()


@pytest.mark.parametrize(("network", "market_id"), [("mainnet", 1), ("robinhood", 7)])
def test_lighter_websocket_uses_network_product_namespace(network, market_id):
    table = _table(
        ("lighter", "BTC-USDC-SWAP", "1", "swap", "perp"),
        ("lighter_robinhood", "BTC-USDC-SWAP", "7", "swap", "perp"),
    )
    for kwargs in ({"network": network}, {"network": network, "base_url": "ws://127.0.0.1:9"}):
        client = _native.LighterPublicWebSocketClient(**kwargs)
        client.set_product_table(table)
        assert client.resolve_market_symbol("BTC-USDC-SWAP") == market_id


@pytest.mark.parametrize("symbol", ['["BTC",0]', '["BTC", 0]', "BTC"])
def test_hyperliquid_native_pair_spacing_is_irrelevant(symbol):
    table = _table(("hyperliquid", "BTC-USDC-SWAP", '["BTC",0]', "swap", "perpetual"))
    with _http_server(GENERIC) as (base_url, received):
        client = _native.HyperliquidHttpClient(endpoint=base_url)
        client.set_product_table(table)
        client.public_request_json("get_l2book", [("product_symbol", symbol)])
        assert json.loads(received.get_nowait()["body"])["coin"] == "BTC"


def test_binance_open_orders_routes_usdm_and_rejects_coin_m() -> None:
    table = _table(
        ("binance", "BTC-USDT-SWAP", "BTCUSDT", "swap", "PERPETUAL"),
        ("binance_coinm", "BTC-USD-SWAP", "BTCUSD_PERP", "swap", "PERPETUAL"),
    )
    with _http_server([]) as (base_url, received):
        client = _native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            spot_base_url=base_url,
            futures_base_url=base_url,
            coin_futures_base_url=base_url,
        )
        client.set_product_table(table)
        client.private_request_json(
            "get_all_open_orders", [("product_symbol", "BTC-USDT-SWAP"), ("market_type", "swap")]
        )
        request = received.get_nowait()
        while urlsplit(request["path"]).path.endswith("/time"):
            request = received.get_nowait()
        assert urlsplit(request["path"]).path == "/fapi/v1/openOrders"
        assert _query(request)["symbol"] == ["BTCUSDT"]
        with pytest.raises(Exception, match="candidates|COIN-M"):
            client.private_request_json(
                "get_all_open_orders", [("product_symbol", "BTC-USD-SWAP"), ("market_type", "swap")]
            )
        assert received.empty()


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ([("product_symbol", "BTCUSDT")], {"category": ["linear"], "symbol": ["BTCUSDT"]}),
        ([("product_symbol", "BTC-USD-SWAP")], {"category": ["inverse"], "symbol": ["BTCUSD"]}),
        ([], {"category": ["linear"]}),
    ],
)
def test_bybit_risk_limit_resolves_only_linear_and_inverse(params, expected) -> None:
    table = _table(
        ("bybit", "BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
        ("bybit", "BTC-USDT-SWAP", "BTCUSDT", "swap", "linear"),
        ("bybit", "BTC-USD-SWAP", "BTCUSD", "swap", "inverse"),
    )
    with _http_server({"retCode": 0, "result": {}}) as (base_url, received):
        client = _native.BybitHttpClient(sync_server_time=False, base_url=base_url)
        client.set_product_table(table)
        client.public_request_json("get_risk_limit", params)
        assert _query(received.get_nowait()) == expected
        with pytest.raises(Exception, match="BTC-USDT-SPOT"):
            client.public_request_json("get_risk_limit", [("product_symbol", "BTC-USDT-SPOT")])
        assert received.empty()


def _binance_requests(received) -> list[dict[str, Any]]:
    requests = []
    while not received.empty():
        request = received.get_nowait()
        if not urlsplit(request["path"]).path.endswith("/time"):
            requests.append(request)
    return requests


def test_binance_generic_order_methods_route_options_to_eapi() -> None:
    table = _table(
        ("binance", "BTC-USDT-260925-100000-C", "BTC-260925-100000-C", "option", "option"),
        ("binance_coinm", "BTC-USD-SWAP", "BTCUSD_PERP", "swap", "PERPETUAL"),
    )
    with _http_server({}) as (base_url, received):
        client = _native.BinanceHttpClient(
            api_key="api-key",
            api_secret="api-secret",
            spot_base_url="http://127.0.0.1:9",
            futures_base_url="http://127.0.0.1:9",
            options_base_url=base_url,
            coin_futures_base_url="http://127.0.0.1:9",
        )
        client.set_product_table(table)
        symbol = ("product_symbol", "BTC-USDT-260925-100000-C")
        cases = [
            ("get_open_orders", [symbol], "GET", "/eapi/v1/openOrders", {}),
            ("get_open_orders", [symbol, ("orderId", "7")], "GET", "/eapi/v1/openOrders", {"orderId": ["7"]}),
            ("get_order", [symbol, ("orderId", "7")], "GET", "/eapi/v1/order", {"orderId": ["7"]}),
            (
                "get_order",
                [symbol, ("origClientOrderId", "c1")],
                "GET",
                "/eapi/v1/order",
                {"clientOrderId": ["c1"]},
            ),
            (
                "cancel_order",
                [symbol, ("origClientOrderId", "c1")],
                "DELETE",
                "/eapi/v1/order",
                {"clientOrderId": ["c1"]},
            ),
            ("get_all_open_orders", [symbol], "GET", "/eapi/v1/openOrders", {}),
            ("cancel_all_open_orders", [symbol], "DELETE", "/eapi/v1/allOpenOrders", {}),
        ]
        for method, params, verb, path, extra in cases:
            client.private_request_json(method, params)
            [request] = _binance_requests(received)
            assert (request["method"], urlsplit(request["path"]).path) == (verb, path), method
            query = _query(request)
            assert query["symbol"] == ["BTC-260925-100000-C"]
            for key in ("orderId", "clientOrderId", "origClientOrderId"):
                assert query.get(key) == extra.get(key), (method, key)
        with pytest.raises(Exception, match="client order id"):
            client.private_request_json("get_open_orders", [symbol, ("origClientOrderId", "c1")])
        for method in ("get_open_orders", "get_order", "cancel_order"):
            with pytest.raises(Exception, match="get_coin_futures_open_orders"):
                client.private_request_json(
                    method, [("product_symbol", "BTC-USD-SWAP"), ("orderId", "1")]
                )
        assert not _binance_requests(received)
