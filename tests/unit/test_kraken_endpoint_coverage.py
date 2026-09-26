"""
Offline route coverage for every Kraken REST wrapper.

Each public wrapper (sync and async) is driven through the real Rust native
client against a local HTTP server, asserting the HTTP method and the official
Kraken REST path documented at https://docs.kraken.com/api-reference/.
"""

# ruff: noqa: ANN401, D103

from __future__ import annotations

import ast
import base64
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
SECRET = base64.b64encode(b"secret").decode()
SPOT = "SPOT"
FUTURES = "FUTURES"

# method name -> (kwargs, HTTP method, official path, API family)
CASES: dict[str, tuple[dict[str, Any], str, str, str]] = {
    # Spot market data
    "get_server_time": ({}, "GET", "/0/public/Time", SPOT),
    "get_spot_system_status": ({}, "GET", "/0/public/SystemStatus", SPOT),
    "get_spot_assets": ({}, "GET", "/0/public/Assets", SPOT),
    "get_spot_asset_pairs": ({}, "GET", "/0/public/AssetPairs", SPOT),
    "get_spot_ticker": ({"product_symbol": "BTC-USD-SPOT"}, "GET", "/0/public/Ticker", SPOT),
    "get_spot_orderbook": ({"product_symbol": "BTC-USD-SPOT"}, "GET", "/0/public/Depth", SPOT),
    "get_spot_public_trades": (
        {"product_symbol": "BTC-USD-SPOT"},
        "GET",
        "/0/public/Trades",
        SPOT,
    ),
    "get_spot_kline": ({"product_symbol": "BTC-USD-SPOT"}, "GET", "/0/public/OHLC", SPOT),
    "get_spot_spread": ({"product_symbol": "BTC-USD-SPOT"}, "GET", "/0/public/Spread", SPOT),
    # Futures market data
    "get_futures_instruments": ({}, "GET", "/derivatives/api/v3/instruments", FUTURES),
    "get_futures_tickers": ({}, "GET", "/derivatives/api/v3/tickers", FUTURES),
    "get_futures_orderbook": (
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/derivatives/api/v3/orderbook",
        FUTURES,
    ),
    "get_futures_public_trades": (
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/derivatives/api/v3/history",
        FUTURES,
    ),
    "get_futures_kline": (
        {"product_symbol": "BTC-USD-SWAP", "timeframe": "1m"},
        "GET",
        "/api/charts/v1/trade/PF_XBTUSD/1m",
        FUTURES,
    ),
    # Spot account data / funding
    "get_spot_account_balance": ({}, "POST", "/0/private/Balance", SPOT),
    "get_spot_trade_balance": ({}, "POST", "/0/private/TradeBalance", SPOT),
    "get_spot_open_positions": ({}, "POST", "/0/private/OpenPositions", SPOT),
    "get_spot_ledgers": ({}, "POST", "/0/private/Ledgers", SPOT),
    "get_spot_trade_volume": ({}, "POST", "/0/private/TradeVolume", SPOT),
    "wallet_transfer_to_futures": (
        {"asset": "USD", "amount": "1"},
        "POST",
        "/0/private/WalletTransfer",
        SPOT,
    ),
    # Earn
    "get_earn_strategies": ({}, "POST", "/0/private/Earn/Strategies", SPOT),
    "get_earn_allocations": ({}, "POST", "/0/private/Earn/Allocations", SPOT),
    "allocate_earn_funds": (
        {"strategy_id": "strategy", "amount": "1"},
        "POST",
        "/0/private/Earn/Allocate",
        SPOT,
    ),
    "deallocate_earn_funds": (
        {"strategy_id": "strategy", "amount": "1"},
        "POST",
        "/0/private/Earn/Deallocate",
        SPOT,
    ),
    "get_earn_allocation_status": (
        {"strategy_id": "strategy"},
        "POST",
        "/0/private/Earn/AllocateStatus",
        SPOT,
    ),
    "get_earn_deallocation_status": (
        {"strategy_id": "strategy"},
        "POST",
        "/0/private/Earn/DeallocateStatus",
        SPOT,
    ),
    # Spot trading
    "place_spot_order": (
        {
            "product_symbol": "BTC-USD-SPOT",
            "side": "buy",
            "ordertype": "limit",
            "volume": "0.01",
            "price": "100",
        },
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_market_order": (
        {"product_symbol": "BTC-USD-SPOT", "side": "buy", "volume": "0.01"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_market_buy_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_market_sell_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_limit_order": (
        {"product_symbol": "BTC-USD-SPOT", "side": "buy", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_limit_buy_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_limit_sell_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_post_only_limit_order": (
        {"product_symbol": "BTC-USD-SPOT", "side": "sell", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_post_only_limit_buy_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "place_spot_post_only_limit_sell_order": (
        {"product_symbol": "BTC-USD-SPOT", "volume": "0.01", "price": "100"},
        "POST",
        "/0/private/AddOrder",
        SPOT,
    ),
    "get_spot_open_orders": ({}, "POST", "/0/private/OpenOrders", SPOT),
    "get_spot_closed_orders": ({}, "POST", "/0/private/ClosedOrders", SPOT),
    "get_spot_orders": ({"txid": "OABC-123"}, "POST", "/0/private/QueryOrders", SPOT),
    "get_spot_trade_history": ({}, "POST", "/0/private/TradesHistory", SPOT),
    "amend_spot_order": (
        {"txid": "OABC-123", "order_qty": "1.25"},
        "POST",
        "/0/private/AmendOrder",
        SPOT,
    ),
    "cancel_spot_order": ({"txid": "OABC-123"}, "POST", "/0/private/CancelOrder", SPOT),
    "cancel_spot_all_orders": ({}, "POST", "/0/private/CancelAll", SPOT),
    "cancel_spot_all_orders_after": (
        {"timeout": 60},
        "POST",
        "/0/private/CancelAllOrdersAfter",
        SPOT,
    ),
    "get_spot_websocket_token": ({}, "POST", "/0/private/GetWebSocketsToken", SPOT),
    # Futures account
    "get_futures_accounts": ({}, "GET", "/derivatives/api/v3/accounts", FUTURES),
    "get_futures_open_positions": ({}, "GET", "/derivatives/api/v3/openpositions", FUTURES),
    "get_futures_fills": ({}, "GET", "/derivatives/api/v3/fills", FUTURES),
    "futures_wallet_transfer": (
        {"amount": "1", "fromAccount": "cash", "toAccount": "flex", "unit": "USD"},
        "POST",
        "/derivatives/api/v3/transfer",
        FUTURES,
    ),
    "withdraw_futures_to_spot_wallet": (
        {"amount": "1", "currency": "USD"},
        "POST",
        "/derivatives/api/v3/withdrawal",
        FUTURES,
    ),
    # Futures trading
    "place_futures_order": (
        {
            "product_symbol": "BTC-USD-SWAP",
            "side": "buy",
            "orderType": "lmt",
            "size": 1,
            "limitPrice": "100",
        },
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_market_order": (
        {"product_symbol": "BTC-USD-SWAP", "side": "buy", "size": 1},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_market_buy_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_market_sell_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_limit_order": (
        {"product_symbol": "BTC-USD-SWAP", "side": "buy", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_limit_buy_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_limit_sell_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_post_only_limit_order": (
        {"product_symbol": "BTC-USD-SWAP", "side": "sell", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_post_only_limit_buy_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "place_futures_post_only_limit_sell_order": (
        {"product_symbol": "BTC-USD-SWAP", "size": 1, "price": "100"},
        "POST",
        "/derivatives/api/v3/sendorder",
        FUTURES,
    ),
    "get_futures_open_orders": ({}, "GET", "/derivatives/api/v3/openorders", FUTURES),
    "get_futures_order_status": (
        {"orderIds": ["order-1"]},
        "POST",
        "/derivatives/api/v3/orders/status",
        FUTURES,
    ),
    "edit_futures_order": (
        {"orderId": "order-1", "limitPrice": "101"},
        "POST",
        "/derivatives/api/v3/editorder",
        FUTURES,
    ),
    "cancel_futures_order": (
        {"order_id": "order-1"},
        "POST",
        "/derivatives/api/v3/cancelorder",
        FUTURES,
    ),
    "cancel_futures_all_orders": ({}, "POST", "/derivatives/api/v3/cancelallorders", FUTURES),
    "cancel_futures_all_orders_after": (
        {"timeout": 60},
        "POST",
        "/derivatives/api/v3/cancelallordersafter",
        FUTURES,
    ),
}


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    names: set[str] = set()
    for path in sorted((base / "kraken").glob("_*_http.py")):
        if path.name == "_http_manager.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not (
                    node.name.startswith("_") or node.name in {"async_init", "close"}
                ):
                    names.add(node.name)
    return names


@contextmanager
def _route_server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode() if length else ""
            received.put(
                {
                    "method": self.command,
                    "path": self.path,
                    "body": body,
                    "api_sign": self.headers.get("API-Sign"),
                    "authent": self.headers.get("Authent"),
                }
            )
            if self.path.startswith("/0/"):
                payload: object = {"error": [], "result": {"token": "ws-token"}}
            else:
                payload = {"result": "success"}
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = _handle  # noqa: N815
        do_POST = _handle  # noqa: N815
        do_PUT = _handle  # noqa: N815
        do_DELETE = _handle  # noqa: N815

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "spot_api_key": "spot-key",
        "spot_api_secret": SECRET,
        "futures_api_key": "futures-key",
        "futures_api_secret": SECRET,
        "base_url": base_url,
        "futures_base_url": base_url,
        "preload_product_table": False,
    }


def _assert_route(request: dict[str, Any], method_name: str) -> None:
    _kwargs, http_method, path, family = CASES[method_name]
    assert request["method"] == http_method, method_name
    assert urlsplit(request["path"]).path == path, method_name
    if family == SPOT and path.startswith("/0/private/"):
        assert request["api_sign"], method_name
        assert "nonce" in dict(parse_qsl(request["body"])), method_name
    if family == FUTURES and method_name in _PRIVATE_FUTURES:
        assert request["authent"], method_name


def _skip_if_stale_native(exc: Exception) -> None:
    if "unsupported Kraken" in str(exc):
        pytest.skip(f"installed dcex._native predates this Rust dispatch: {exc}")


def _call_or_skip_stale_native(method: Any, kwargs: dict[str, Any]) -> None:
    try:
        method(**kwargs)
    except ValueError as exc:
        _skip_if_stale_native(exc)
        raise


_PRIVATE_FUTURES = {
    name
    for name, (_kwargs, _method, path, family) in CASES.items()
    if family == FUTURES
    and not path.startswith("/api/charts")
    and not path.endswith(("/instruments", "/tickers", "/orderbook", "/history"))
}


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_kraken_wrapper_has_a_route_case(mode: str) -> None:
    assert _wrapper_names(mode) == set(CASES)


@pytest.mark.parametrize("method_name", sorted(CASES))
def test_sync_kraken_wrapper_hits_official_route(method_name: str) -> None:
    from dcex.kraken.client import Client

    kwargs = CASES[method_name][0]
    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            _call_or_skip_stale_native(getattr(client, method_name), kwargs)
        finally:
            client.close()
        request = received.get(timeout=5)
        assert received.empty()
    _assert_route(request, method_name)


@pytest.mark.asyncio
@pytest.mark.parametrize("method_name", sorted(CASES))
async def test_async_kraken_wrapper_hits_official_route(method_name: str) -> None:
    from dcex.async_support.kraken.client import Client

    kwargs = CASES[method_name][0]
    with _route_server() as (base_url, received):
        client = await Client(**_client_kwargs(base_url)).async_init()
        try:
            try:
                await getattr(client, method_name)(**kwargs)
            except ValueError as exc:
                _skip_if_stale_native(exc)
                raise
        finally:
            await client.close()
        request = received.get(timeout=5)
        assert received.empty()
    _assert_route(request, method_name)


def test_kraken_spot_limit_order_body_matches_add_order_docs() -> None:
    from dcex.kraken.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            client.place_spot_post_only_limit_buy_order(
                product_symbol="BTC-USD-SPOT", volume="0.01", price="100"
            )
        finally:
            client.close()
        body = dict(parse_qsl(received.get(timeout=5)["body"]))
    assert body["pair"] == "XBTUSD"
    assert body["type"] == "buy"
    assert body["ordertype"] == "limit"
    assert body["volume"] == "0.01"
    assert body["price"] == "100"
    assert "post" in body["oflags"]


def test_kraken_futures_limit_order_body_matches_send_order_docs() -> None:
    from dcex.kraken.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            client.place_futures_post_only_limit_sell_order(
                product_symbol="BTC-USD-SWAP", size=2, price="100"
            )
        finally:
            client.close()
        request = received.get(timeout=5)
    params = dict(parse_qsl(request["body"] or urlsplit(request["path"]).query))
    assert params["symbol"] == "PF_XBTUSD"
    assert params["side"] == "sell"
    assert params["orderType"] == "post"
    assert params["size"] == "2"
    assert params["limitPrice"] == "100"


def test_kraken_dead_man_switch_bodies_carry_timeout() -> None:
    from dcex.kraken.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            client.cancel_spot_all_orders_after(timeout=30)
            spot = received.get(timeout=5)
            client.cancel_futures_all_orders_after(timeout=45)
            futures = received.get(timeout=5)
        finally:
            client.close()
    assert dict(parse_qsl(spot["body"]))["timeout"] == "30"
    futures_params = dict(parse_qsl(futures["body"] or urlsplit(futures["path"]).query))
    assert futures_params["timeout"] == "45"


@pytest.mark.parametrize(
    ("method_name", "kwargs"),
    [
        ("amend_spot_order", {"txid": "OABC-123", "order_qty": "1"}),
        ("edit_futures_order", {"orderId": "order-1", "limitPrice": "101"}),
    ],
)
def test_kraken_amend_wrappers_work_without_product_table(
    method_name: str, kwargs: dict[str, Any]
) -> None:
    from dcex.kraken.client import Client

    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            _call_or_skip_stale_native(getattr(client, method_name), kwargs)
            request = received.get(timeout=5)
        finally:
            client.close()
    sent = parse_qsl(request["body"] or urlsplit(request["path"]).query)
    assert "self" not in dict(sent)
