"""
Offline route coverage for every BingX REST wrapper (sync and async).

Each public wrapper method is called through the real Python client, the PyO3
bridge and the Rust dispatcher against a local HTTP server; the recorded HTTP
method and path must match the official BingX API docs.
"""

import ast
import asyncio
import inspect
import json
import queue
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
WRAPPER_FILES = ("_account_http.py", "_market_http.py", "_trade_http.py")

SPOT_ORDER = ("POST", "/openApi/spot/v1/trade/order")
SWAP_ORDER = ("POST", "/openApi/swap/v2/trade/order")
LISTEN_KEY = "/openApi/user/auth/userDataStream"

# Python wrapper name -> (HTTP method, documented path).
ROUTES: dict[str, tuple[str, str]] = {
    # Market data.
    "get_swap_instrument_info": ("GET", "/openApi/swap/v2/quote/contracts"),
    "get_spot_instrument_info": ("GET", "/openApi/spot/v1/common/symbols"),
    "get_orderbook": ("GET", "/openApi/swap/v2/quote/depth"),
    "get_spot_orderbook": ("GET", "/openApi/spot/v1/market/depth"),
    "get_spot_orderbook_v2": ("GET", "/openApi/spot/v2/market/depth"),
    "get_public_trades": ("GET", "/openApi/swap/v2/quote/trades"),
    "get_spot_public_trades": ("GET", "/openApi/spot/v1/market/trades"),
    "get_kline": ("GET", "/openApi/swap/v3/quote/klines"),
    # BingX only documents the v2 spot kline route; get_spot_kline uses it too.
    "get_spot_kline": ("GET", "/openApi/spot/v2/market/kline"),
    "get_spot_kline_v2": ("GET", "/openApi/spot/v2/market/kline"),
    "get_open_interest": ("GET", "/openApi/swap/v2/quote/openInterest"),
    "get_mark_price_kline": ("GET", "/openApi/swap/v1/market/markPriceKlines"),
    "get_ticker": ("GET", "/openApi/swap/v2/quote/ticker"),
    "get_swap_premium_index": ("GET", "/openApi/swap/v2/quote/premiumIndex"),
    "get_swap_funding_rate": ("GET", "/openApi/swap/v2/quote/fundingRate"),
    "get_swap_book_ticker": ("GET", "/openApi/swap/v2/quote/bookTicker"),
    "get_swap_trading_rules": ("GET", "/openApi/swap/v1/tradingRules"),
    "get_spot_ticker": ("GET", "/openApi/spot/v1/ticker/24hr"),
    "get_spot_book_ticker": ("GET", "/openApi/spot/v1/ticker/bookTicker"),
    "get_spot_price_ticker": ("GET", "/openApi/spot/v2/ticker/price"),
    # Account / wallet / sub-accounts.
    "get_account_balance": ("GET", "/openApi/swap/v3/user/balance"),
    "get_swap_account_balance": ("GET", "/openApi/swap/v3/user/balance"),
    "get_swap_commission_rate": ("GET", "/openApi/swap/v2/user/commissionRate"),
    "get_spot_account_balance": ("GET", "/openApi/spot/v1/account/balance"),
    "get_fund_account_balance": ("GET", "/openApi/fund/v1/account/balance"),
    "get_all_account_balance": ("GET", "/openApi/account/v1/allAccountBalance"),
    "get_account_uid": ("GET", "/openApi/account/v1/uid"),
    "get_api_key_info": ("GET", "/openApi/account/v1/apiKey/query"),
    "get_transferable_coins": ("GET", "/openApi/api/asset/v1/transfer/supportCoins"),
    "asset_transfer": ("POST", "/openApi/api/asset/v1/transfer"),
    "get_asset_transfer_records": ("GET", "/openApi/api/v3/asset/transferRecord"),
    "get_subaccounts": ("GET", "/openApi/subAccount/v1/list"),
    "get_subaccount_assets": ("GET", "/openApi/subAccount/v1/assets"),
    "get_subaccount_all_account_balance": ("GET", "/openApi/subAccount/v1/allAccountBalance"),
    "get_subaccount_transfer_history": (
        "GET",
        "/openApi/account/transfer/v1/subAccount/asset/transferHistory",
    ),
    "get_subaccount_transferable_amounts": (
        "POST",
        "/openApi/account/transfer/v1/subAccount/transferAsset/supportCoins",
    ),
    "transfer_subaccount_assets": (
        "POST",
        "/openApi/account/transfer/v1/subAccount/transferAsset",
    ),
    "get_open_positions": ("GET", "/openApi/swap/v2/user/positions"),
    "get_fund_flow": ("GET", "/openApi/swap/v2/user/income"),
    "get_listen_key": ("POST", LISTEN_KEY),
    "keep_alive_listen_key": ("PUT", LISTEN_KEY),
    "close_listen_key": ("DELETE", LISTEN_KEY),
    # Spot trading.
    "place_spot_order": SPOT_ORDER,
    "place_spot_market_buy_order": SPOT_ORDER,
    "place_spot_market_sell_order": SPOT_ORDER,
    "place_spot_limit_order": SPOT_ORDER,
    "place_spot_limit_buy_order": SPOT_ORDER,
    "place_spot_limit_sell_order": SPOT_ORDER,
    "place_spot_post_only_order": SPOT_ORDER,
    "place_spot_post_only_buy_order": SPOT_ORDER,
    "place_spot_post_only_sell_order": SPOT_ORDER,
    "place_spot_batch_order": ("POST", "/openApi/spot/v1/trade/batchOrders"),
    "replace_spot_order": ("POST", "/openApi/spot/v1/trade/order/cancelReplace"),
    "cancel_spot_order": ("POST", "/openApi/spot/v1/trade/cancel"),
    "cancel_spot_batch_orders": ("POST", "/openApi/spot/v1/trade/cancelOrders"),
    "cancel_spot_open_orders": ("POST", "/openApi/spot/v1/trade/cancelOpenOrders"),
    "set_spot_cancel_all_after": ("POST", "/openApi/spot/v1/trade/cancelAllAfter"),
    "get_spot_order": ("GET", "/openApi/spot/v1/trade/query"),
    "get_spot_open_orders": ("GET", "/openApi/spot/v1/trade/openOrders"),
    "get_spot_order_history": ("GET", "/openApi/spot/v1/trade/historyOrders"),
    "get_spot_my_trades": ("GET", "/openApi/spot/v1/trade/myTrades"),
    "get_spot_commission_rate": ("GET", "/openApi/spot/v1/user/commissionRate"),
    # USDT-M perpetual trading.
    "place_swap_order": SWAP_ORDER,
    "test_swap_order": ("POST", "/openApi/swap/v2/trade/order/test"),
    "place_swap_market_order": SWAP_ORDER,
    "place_swap_market_buy_order": SWAP_ORDER,
    "place_swap_market_sell_order": SWAP_ORDER,
    "place_swap_limit_order": SWAP_ORDER,
    "place_swap_limit_buy_order": SWAP_ORDER,
    "place_swap_limit_sell_order": SWAP_ORDER,
    "place_swap_post_only_order": SWAP_ORDER,
    "place_swap_post_only_buy_order": SWAP_ORDER,
    "place_swap_post_only_sell_order": SWAP_ORDER,
    "place_swap_batch_order": ("POST", "/openApi/swap/v2/trade/batchOrders"),
    "cancel_swap_order": ("DELETE", "/openApi/swap/v2/trade/order"),
    "cancel_swap_batch_order": ("DELETE", "/openApi/swap/v2/trade/batchOrders"),
    "cancel_swap_all_orders": ("DELETE", "/openApi/swap/v2/trade/allOpenOrders"),
    "replace_swap_order": ("POST", "/openApi/swap/v1/trade/cancelReplace"),
    "close_swap_position": ("POST", "/openApi/swap/v1/trade/closePosition"),
    "close_swap_all_positions": ("POST", "/openApi/swap/v2/trade/closeAllPositions"),
    "get_order_detail": ("GET", "/openApi/swap/v2/trade/order"),
    "get_open_orders": ("GET", "/openApi/swap/v2/trade/openOrders"),
    "get_order_history": ("GET", "/openApi/swap/v2/trade/allOrders"),
    "change_margin_type": ("POST", "/openApi/swap/v2/trade/marginType"),
    "get_margin_type": ("GET", "/openApi/swap/v2/trade/marginType"),
    "set_leverage": ("POST", "/openApi/swap/v2/trade/leverage"),
    "get_leverage": ("GET", "/openApi/swap/v2/trade/leverage"),
    "set_position_mode": ("POST", "/openApi/swap/v1/positionSide/dual"),
    "get_position_mode": ("GET", "/openApi/swap/v1/positionSide/dual"),
}

MARKET_FILE_METHODS = {
    name
    for name in ROUTES
    if name.startswith(("get_swap_", "get_spot_", "get_orderbook", "get_public_", "get_kline"))
} | {"get_open_interest", "get_mark_price_kline", "get_ticker"}
PUBLIC_METHODS = MARKET_FILE_METHODS - {
    "get_swap_account_balance",
    "get_swap_commission_rate",
    "get_spot_account_balance",
    "get_spot_order",
    "get_spot_open_orders",
    "get_spot_order_history",
    "get_spot_my_trades",
    "get_spot_commission_rate",
}
# Signed with X-BX-APIKEY header only (no HMAC signature).
UNSIGNED_PRIVATE = {"get_listen_key"}

VALUES: dict[str, Any] = {
    "side": "BUY",
    "quantity": "1",
    "quoteOrderQty": "10",
    "price": "1",
    "interval": "1m",
    "depth": 20,
    "cancelReplaceMode": "STOP_ON_FAILURE",
    "positionSide": "LONG",
    "positionId": 1,
    "orderIds": [1, 2],
    "marginType": "CROSSED",
    "leverage": 5,
    "dualSidePosition": True,
    "listen_key": "listen-key",
    "uid": 1,
    "subUid": 1,
    "fromAccount": "fund",
    "toAccount": "spot",
    "asset": "USDT",
    "amount": "1",
    "assetName": "USDT",
    "transferAmount": "1",
    "fromUid": 1,
    "toUid": 2,
    "fromType": 1,
    "toType": 1,
    "fromAccountType": 1,
    "toAccountType": 1,
    "remark": "coverage",
    "data": [{"symbol": "BTC-USDT", "side": "BUY", "type": "LIMIT", "quantity": "1", "price": "1"}],
    "batchOrders": [
        {
            "symbol": "BTC-USDT",
            "side": "BUY",
            "type": "LIMIT",
            "positionSide": "LONG",
            "quantity": "1",
            "price": "1",
        }
    ],
}

EXTRA: dict[str, dict[str, Any]] = {
    "place_spot_order": {"quantity": "1", "price": "1", "type_": "LIMIT"},
    "replace_spot_order": {
        "cancelOrderId": 123,
        "type_": "LIMIT",
        "quantity": "1",
        "price": "1",
    },
    "set_spot_cancel_all_after": {"type_": "ACTIVATE", "timeOut": 30},
    "cancel_spot_order": {"orderId": 1},
    "get_spot_order": {"orderId": 1},
    "place_swap_order": {"type_": "LIMIT", "quantity": "1", "price": "1"},
    "test_swap_order": {"type_": "MARKET", "quantity": "1"},
    "replace_swap_order": {
        "cancelOrderId": 1,
        "type_": "LIMIT",
        "quantity": "1",
        "price": "1",
    },
    "cancel_swap_order": {"orderId": 1},
    "cancel_swap_batch_order": {"orderIdList": [1, 2]},
    "get_order_detail": {"orderId": 1},
    "get_asset_transfer_records": {"fromAccount": "fund", "toAccount": "spot"},
    "get_subaccounts": {"page": 1, "limit": 10},
    "get_subaccount_all_account_balance": {"pageIndex": 1, "pageSize": 10},
    "set_leverage": {"side": "LONG"},
}

# Routes added in commit 026d0b9f; an older installed native extension lacks them.
STALE_NATIVE_MARKER = "unsupported BingX private method"


def _call_or_skip_stale(name: str, call: Any) -> Any:  # noqa: ANN401
    try:
        return call()
    except ValueError as exc:
        if STALE_NATIVE_MARKER in str(exc):
            pytest.skip(f"installed dcex._native predates {name}; rebuild the extension")
        raise


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    names: set[str] = set()
    for filename in WRAPPER_FILES:
        tree = ast.parse((base / "bingx" / filename).read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and not (
                    node.name.startswith("_")
                ):
                    names.add(node.name)
    return names


class _Recorder(BaseHTTPRequestHandler):
    received: "queue.Queue[dict[str, Any]]"

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            self.rfile.read(length)
        split = urlsplit(self.path)
        self.received.put(
            {
                "method": self.command,
                "path": split.path,
                "query": dict(parse_qsl(split.query)),
                "api_key": self.headers.get("X-BX-APIKEY"),
            }
        )
        payload = json.dumps({"code": 0, "msg": "", "data": {}, "listenKey": "k"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = do_PUT = do_DELETE = _handle  # noqa: N815

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, "queue.Queue[dict[str, Any]]"]]:
    """Run a local recording HTTP server for the whole module."""
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    handler = type("Handler", (_Recorder,), {"received": received})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = httpd.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "base_url": base_url,
        "preload_product_table": False,
    }


def _kwargs(method: Any, name: str) -> dict[str, Any]:  # noqa: ANN401
    kwargs: dict[str, Any] = {}
    for parameter in inspect.signature(method).parameters.values():
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is not inspect.Parameter.empty:
            continue
        if parameter.name == "product_symbol":
            kwargs[parameter.name] = "BTC-USDT-SPOT" if "spot" in name else "BTC-USDT-SWAP"
        elif parameter.name in VALUES:
            kwargs[parameter.name] = VALUES[parameter.name]
        elif parameter.name == "type_":
            kwargs[parameter.name] = "LIMIT"
        else:
            raise AssertionError(f"{name}: no sample value for {parameter.name}")
    kwargs.update(EXTRA.get(name, {}))
    return kwargs


def _drain(received: "queue.Queue[dict[str, Any]]") -> None:
    while not received.empty():
        received.get_nowait()


def _assert_route(name: str, request: dict[str, Any]) -> None:
    assert (request["method"], request["path"]) == ROUTES[name], name
    signed = "signature" in request["query"]
    if name in PUBLIC_METHODS:
        assert not signed, name
    elif name in UNSIGNED_PRIVATE:
        assert request["api_key"] == "api-key", name
        assert not signed, name
    else:
        assert signed, name
        assert request["api_key"] == "api-key", name
    assert "type_" not in request["query"], name


def test_route_table_matches_python_surface() -> None:
    """Every sync/async wrapper is mapped to a documented route."""
    sync_names = _wrapper_names("sync")
    async_names = _wrapper_names("async")
    assert sync_names == async_names
    assert sync_names == set(ROUTES)


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_sync_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Sync wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.bingx.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    method = getattr(client, name)
    assert _call_or_skip_stale(name, lambda: method(**_kwargs(method, name))) is not None
    _assert_route(name, received.get(timeout=5))


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_async_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Async wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.async_support.bingx.client import Client

    base_url, received = server
    _drain(received)

    async def call() -> Any:  # noqa: ANN401
        async with Client(**_client_kwargs(base_url)) as client:
            method = getattr(client, name)
            return await method(**_kwargs(method, name))

    assert _call_or_skip_stale(name, lambda: asyncio.run(call())) is not None
    _assert_route(name, received.get(timeout=5))


def test_sync_helpers_pin_side_type_and_time_in_force(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Convenience helpers pin side/type/timeInForce and map canonical symbols."""
    from dcex.bingx.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    client.place_swap_post_only_sell_order(
        product_symbol="ETH-USDT-SWAP", quantity="1", price="100"
    )
    query = received.get(timeout=5)["query"]
    assert query["symbol"] == "ETH-USDT"
    assert (query["side"], query["type"], query["timeInForce"]) == ("SELL", "LIMIT", "PostOnly")

    client.cancel_swap_all_orders(product_symbol="BTC-USDT-SWAP", type_="LIMIT")
    query = received.get(timeout=5)["query"]
    assert query["type"] == "LIMIT"

    client.get_spot_orderbook_v2(product_symbol="BTC-USDT-SPOT", depth=20)
    query = received.get(timeout=5)["query"]
    assert query["symbol"] == "BTC_USDT"
    assert query["type"] == "step0"


def test_spot_orderbook_v2_requires_depth() -> None:
    """BingX documents depth as required for the aggregated spot order book."""
    from dcex.async_support.bingx.client import Client as AsyncClient
    from dcex.bingx.client import Client

    for client_class in (Client, AsyncClient):
        parameter = inspect.signature(client_class.get_spot_orderbook_v2).parameters["depth"]
        assert parameter.default is inspect.Parameter.empty


# Official request tables list no timestamp only for these public spot routes.
PUBLIC_WITHOUT_TIMESTAMP = {
    "get_spot_orderbook_v2",
    "get_spot_price_ticker",
    "get_spot_book_ticker",
}


@pytest.mark.parametrize("name", sorted(PUBLIC_METHODS))
def test_public_routes_send_documented_timestamp(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """BingX marks timestamp required on public market endpoints except a few spot routes."""
    from dcex.bingx.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    method = getattr(client, name)
    _call_or_skip_stale(name, lambda: method(**_kwargs(method, name)))
    query = received.get(timeout=5)["query"]
    if name in PUBLIC_WITHOUT_TIMESTAMP:
        assert "timestamp" not in query, name
    else:
        assert query.get("timestamp", "").isdigit(), name
    assert "signature" not in query, name
