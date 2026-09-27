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
    "delete_spot_export_report": (
        {"id": "report1", "report_action": "cancel"},
        "POST",
        "/0/private/RemoveExport",
        SPOT,
    ),
    "get_spot_export_status": ({"report": "trades"}, "POST", "/0/private/ExportStatus", SPOT),
    "request_spot_export_report": (
        {
            "report": "trades",
            "format": "CSV",
            "description": "history",
            "starttm": 1700000000,
            "endtm": 1700000060,
        },
        "POST",
        "/0/private/AddExport",
        SPOT,
    ),
    "simulate_futures_portfolio": (
        {
            "portfolio": {
                "positions": [{"instrument": "PF_XBTUSD", "size": -1.25, "entryPrice": 60000.25}]
            }
        },
        "POST",
        "/derivatives/api/v3/portfolio-margining/simulate",
        FUTURES,
    ),
    "get_futures_market_analytics": (
        {
            "symbol": "PF_XBTUSD",
            "analytics_type": "open-interest",
            "since": 1700000000,
            "interval": 60,
        },
        "GET",
        "/api/charts/v1/analytics/PF_XBTUSD/open-interest",
        FUTURES,
    ),
    "check_futures_api_key": ({}, "GET", "/api/auth/v1/api-keys/v3/check", FUTURES),
    "get_futures_ticker": (
        {"symbol": "PF_XBTUSD"},
        "GET",
        "/derivatives/api/v3/tickers/PF_XBTUSD",
        FUTURES,
    ),
    "get_futures_pnl_preferences": ({}, "GET", "/derivatives/api/v3/pnlpreferences", FUTURES),
    "set_futures_pnl_preference": (
        {"symbol": "PF_XBTUSD", "pnl_preference": "USD"},
        "PUT",
        "/derivatives/api/v3/pnlpreferences",
        FUTURES,
    ),
    "create_spot_subaccount": (
        {"username": "trader1", "email": "trader@example.com"},
        "POST",
        "/0/private/CreateSubaccount",
        SPOT,
    ),
    "get_futures_subaccounts": ({}, "GET", "/derivatives/api/v3/subaccounts", FUTURES),
    "get_spot_post_trade_data": ({"symbol": "BTC/USD"}, "GET", "/0/public/PostTrade", SPOT),
    "get_spot_pre_trade_data": ({"symbol": "BTC/USD"}, "GET", "/0/public/PreTrade", SPOT),
    "get_spot_api_key_info": ({}, "POST", "/0/private/GetApiKeyInfo", SPOT),
    "get_spot_credit_lines": (
        {"rebase_multiplier": "base"},
        "POST",
        "/0/private/CreditLines",
        SPOT,
    ),
    "get_spot_order_amends": (
        {"order_id": "OID-1", "rebase_multiplier": "base"},
        "POST",
        "/0/private/OrderAmends",
        SPOT,
    ),
    "get_spot_wallet_accounts": ({}, "POST", "/0/private/ListWalletAccounts", SPOT),
    "get_spot_ledger_entries": (
        {"ledger_ids": "ledger1,ledger2", "trades": True, "rebase_multiplier": "base"},
        "POST",
        "/0/private/QueryLedgers",
        SPOT,
    ),
    "get_futures_portfolio_margin_parameters": (
        {},
        "GET",
        "/derivatives/api/v3/portfolio-margining/parameters",
        FUTURES,
    ),
    "get_futures_unwind_queue": ({}, "GET", "/derivatives/api/v3/unwindqueue", FUTURES),
    "get_futures_notifications": ({}, "GET", "/derivatives/api/v3/notifications", FUTURES),
    "get_spot_grouped_orderbook": (
        {"product_symbol": "BTC-USD-SPOT", "depth": 25, "grouping": 100},
        "GET",
        "/0/public/GroupedBook",
        SPOT,
    ),
    "get_spot_maintenance_schedule": ({}, "GET", "/0/public/MaintenanceSchedule", SPOT),
    "get_futures_self_trade_strategy": (
        {},
        "GET",
        "/derivatives/api/v3/self-trade-strategy",
        FUTURES,
    ),
    "set_futures_self_trade_strategy": (
        {"strategy": "CANCEL_MAKER_SELF"},
        "PUT",
        "/derivatives/api/v3/self-trade-strategy",
        FUTURES,
    ),
    "get_futures_trading_instruments": (
        {"contract_types": ["futures_inverse", "flexible_futures"]},
        "GET",
        "/derivatives/api/v3/trading/instruments",
        FUTURES,
    ),
    "get_futures_subaccount_trading_status": (
        {"subaccount_uid": "abcd-1234"},
        "GET",
        "/derivatives/api/v3/subaccount/abcd-1234/trading-enabled",
        FUTURES,
    ),
    "set_futures_subaccount_trading_status": (
        {"subaccount_uid": "abcd-1234", "trading_enabled": False},
        "PUT",
        "/derivatives/api/v3/subaccount/abcd-1234/trading-enabled",
        FUTURES,
    ),
    "get_spot_trades_info": (
        {"txid": "trade-1,trade-2", "trades": True, "rebase_multiplier": "base"},
        "POST",
        "/0/private/QueryTrades",
        SPOT,
    ),
    "get_futures_account_log_csv": (
        {"conversion_details": True},
        "GET",
        "/api/history/v3/accountlogcsv",
        FUTURES,
    ),
    "get_futures_account_log": (
        {
            "since": 1000,
            "before": 2000,
            "count": 10,
            "conversion_details": True,
            "info": ["futures trade", "funding rate change"],
        },
        "GET",
        "/api/history/v3/account-log",
        FUTURES,
    ),
    "get_futures_execution_events": (
        {"since": 1000, "before": 2000, "count": 10},
        "GET",
        "/api/history/v3/executions",
        FUTURES,
    ),
    "get_futures_order_events": (
        {"since": 1000, "before": 2000, "count": 10},
        "GET",
        "/api/history/v3/orders",
        FUTURES,
    ),
    "get_futures_position_events": (
        {"since": 1000, "before": 2000, "count": 10},
        "GET",
        "/api/history/v3/positions",
        FUTURES,
    ),
    "get_futures_trigger_events": (
        {"since": 1000, "before": 2000, "count": 10},
        "GET",
        "/api/history/v3/triggers",
        FUTURES,
    ),
    "get_spot_deposit_addresses": (
        {"asset": "XBT", "method": "Bitcoin"},
        "POST",
        "/0/private/DepositAddresses",
        SPOT,
    ),
    "get_spot_deposit_methods": ({"asset": "XBT"}, "POST", "/0/private/DepositMethods", SPOT),
    "get_futures_instrument_status": (
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/derivatives/api/v3/instruments/PF_XBTUSD/status",
        FUTURES,
    ),
    "get_futures_instrument_statuses": (
        {"contract_types": ["futures_inverse", "flexible_futures"]},
        "GET",
        "/derivatives/api/v3/instruments/status",
        FUTURES,
    ),
    "transfer_spot_sub_account": (
        {"asset": "XBT", "amount": "1.25", "from_account": "master-id", "to_account": "sub-id"},
        "POST",
        "/0/private/AccountTransfer",
        SPOT,
    ),
    "transfer_futures_sub_account": (
        {
            "from_user": "master-id",
            "to_user": "sub-id",
            "from_account": "cash",
            "to_account": "flex",
            "unit": "USD",
            "amount": "1.25",
        },
        "POST",
        "/derivatives/api/v3/transfer/subaccount",
        FUTURES,
    ),
    "get_spot_deposit_status": (
        {"cursor": True, "limit": 10},
        "POST",
        "/0/private/DepositStatus",
        SPOT,
    ),
    "get_spot_level3_orderbook": (
        {"product_symbol": "BTC-USD-SPOT", "depth": 0},
        "POST",
        "/0/private/Level3",
        SPOT,
    ),
    "manage_futures_batch_orders": (
        {
            "orders": [
                {
                    "order": "send",
                    "order_tag": "1",
                    "orderType": "lmt",
                    "product_symbol": "BTC-USD-SWAP",
                    "side": "buy",
                    "size": 1,
                    "limitPrice": 100,
                    "reduceOnly": False,
                },
                {"order": "edit", "cliOrdId": "c-1", "size": 2},
                {"order": "cancel", "cliOrdId": "c-2"},
            ]
        },
        "POST",
        "/derivatives/api/v3/batchorder",
        FUTURES,
    ),
    "get_futures_funding_history": (
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/derivatives/api/v3/historical-funding-rates",
        FUTURES,
    ),
    "place_spot_batch_orders": (
        {
            "product_symbol": "BTC-USD-SPOT",
            "orders": [
                {"type": "buy", "ordertype": "limit", "price": "100", "volume": "1"},
                {"type": "sell", "ordertype": "market", "volume": "1"},
            ],
            "validate": True,
        },
        "POST",
        "/0/private/AddOrderBatch",
        SPOT,
    ),
    "cancel_spot_batch_orders": (
        {"orders": ["OABC", 42], "cl_ord_ids": ["client-a"]},
        "POST",
        "/0/private/CancelOrderBatch",
        SPOT,
    ),
    "get_spot_extended_balance": (
        {"rebase_multiplier": "base"},
        "POST",
        "/0/private/BalanceEx",
        SPOT,
    ),
    "get_futures_leverage_preferences": (
        {},
        "GET",
        "/derivatives/api/v3/leveragepreferences",
        FUTURES,
    ),
    "set_futures_leverage_preference": (
        {"product_symbol": "BTC-USD-SWAP", "max_leverage": "3"},
        "PUT",
        "/derivatives/api/v3/leveragepreferences",
        FUTURES,
    ),
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
    if method_name in RISK_FIELDS:
        sent = parse_qsl(request["body"] or urlsplit(request["path"]).query)
        assert sorted((k, v) for k, v in sent if k != "nonce") == sorted(RISK_FIELDS[method_name])
    assert request["method"] == http_method, method_name
    assert urlsplit(request["path"]).path == path, method_name
    if family == SPOT and path.startswith("/0/private/"):
        assert request["api_sign"], method_name
        body = (
            json.loads(request["body"])
            if request["body"].startswith("{")
            else dict(parse_qsl(request["body"]))
        )
        assert "nonce" in body, method_name
        if request["body"].startswith("{"):
            import hashlib
            import hmac

            digest = hashlib.sha256((str(body["nonce"]) + request["body"]).encode()).digest()
            signature = base64.b64encode(
                hmac.new(b"secret", path.encode() + digest, hashlib.sha512).digest()
            ).decode()
            assert request["api_sign"] == signature
            if method_name == "place_spot_batch_orders":
                assert body["orders"] == CASES[method_name][0]["orders"]
                assert body["validate"] is True
                assert body["pair"] == "XBTUSD"
            else:
                assert body["orders"] == ["OABC", 42]
                assert body["cl_ord_ids"] == ["client-a"]
    if method_name == "manage_futures_batch_orders":
        value = json.loads(dict(parse_qsl(request["body"]))["json"])
        expected = [dict(order) for order in CASES[method_name][0]["orders"]]
        expected[0].pop("product_symbol")
        expected[0]["symbol"] = "PF_XBTUSD"
        assert value == {"batchOrder": expected}
    if family == FUTURES and method_name in _PRIVATE_FUTURES:
        assert request["authent"], method_name


def _fail_if_stale_native(exc: Exception) -> None:
    if "unsupported Kraken" in str(exc):
        pytest.fail(f"installed dcex._native predates this Rust dispatch: {exc}")


def _call_checked_native(method: Any, kwargs: dict[str, Any]) -> None:
    try:
        method(**kwargs)
    except ValueError as exc:
        _fail_if_stale_native(exc)
        raise


RISK_FIELDS = {
    "get_spot_trades_info": [
        ("txid", "trade-1,trade-2"),
        ("trades", "true"),
        ("rebase_multiplier", "base"),
    ],
    "get_futures_account_log_csv": [("conversion_details", "true")],
    "get_futures_account_log": [
        ("since", "1000"),
        ("before", "2000"),
        ("count", "10"),
        ("conversion_details", "true"),
        ("info", "futures trade"),
        ("info", "funding rate change"),
    ],
    "get_futures_execution_events": [("since", "1000"), ("before", "2000"), ("count", "10")],
    "get_futures_order_events": [("since", "1000"), ("before", "2000"), ("count", "10")],
    "get_futures_position_events": [("since", "1000"), ("before", "2000"), ("count", "10")],
    "get_futures_trigger_events": [("since", "1000"), ("before", "2000"), ("count", "10")],
    "get_spot_deposit_addresses": [("asset", "XBT"), ("method", "Bitcoin")],
    "get_spot_deposit_methods": [("asset", "XBT")],
    "get_futures_instrument_status": [],
    "get_futures_instrument_statuses": [
        ("contractType", "futures_inverse"),
        ("contractType", "flexible_futures"),
    ],
    "transfer_spot_sub_account": [
        ("asset", "XBT"),
        ("amount", "1.25"),
        ("from", "master-id"),
        ("to", "sub-id"),
    ],
    "transfer_futures_sub_account": [
        ("fromUser", "master-id"),
        ("toUser", "sub-id"),
        ("fromAccount", "cash"),
        ("toAccount", "flex"),
        ("unit", "USD"),
        ("amount", "1.25"),
    ],
    "get_spot_deposit_status": [("cursor", "true"), ("limit", "10")],
    "get_spot_level3_orderbook": [("pair", "XBTUSD"), ("depth", "0")],
}

_PRIVATE_FUTURES = {
    name
    for name, (_kwargs, _method, path, family) in CASES.items()
    if family == FUTURES
    and name
    not in {
        "get_futures_instrument_status",
        "get_futures_instrument_statuses",
        "get_futures_ticker",
    }
    and not path.startswith("/api/charts")
    and not path.endswith(
        ("/instruments", "/tickers", "/orderbook", "/history", "/historical-funding-rates")
    )
}


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_kraken_wrapper_has_a_route_case(mode: str) -> None:
    assert _wrapper_names(mode) == set(CASES) | {"retrieve_spot_export"}


@pytest.mark.parametrize("method_name", sorted(CASES))
def test_sync_kraken_wrapper_hits_official_route(method_name: str) -> None:
    from dcex.kraken.client import Client

    kwargs = CASES[method_name][0]
    with _route_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            _call_checked_native(getattr(client, method_name), kwargs)
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
                _fail_if_stale_native(exc)
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
            _call_checked_native(getattr(client, method_name), kwargs)
            request = received.get(timeout=5)
        finally:
            client.close()
    sent = parse_qsl(request["body"] or urlsplit(request["path"]).query)
    assert "self" not in dict(sent)


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("get_spot_level3_orderbook", {"product_symbol": "BTC-USD-SPOT", "depth": 50}),
        ("get_spot_trades_info", {"txid": ",".join(["id"] * 21)}),
        ("get_spot_trades_info", {"txid": "id,,other"}),
        ("get_spot_deposit_addresses", {"asset": "BTC", "method": "Bitcoin Lightning"}),
        (
            "transfer_spot_sub_account",
            {"asset": "BTC", "amount": "NaN", "from_account": "master", "to_account": "sub"},
        ),
        ("get_futures_account_log", {"since": 2000, "before": 1000}),
        ("get_futures_account_log", {"info": ["not-a-ledger-type"]}),
        ("get_futures_execution_events", {"count": 0}),
        ("get_futures_instrument_statuses", {"contract_types": []}),
    ],
)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_risk_parameters_rejected_without_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    if mode == "sync":
        from dcex.kraken.client import Client

        client = Client(**_client_kwargs("http://127.0.0.1:1"))
        try:
            with pytest.raises(ValueError):
                getattr(client, method)(**kwargs)
        finally:
            client.close()
    else:
        from dcex.async_support.kraken.client import Client as AsyncClient

        client = await AsyncClient(**_client_kwargs("http://127.0.0.1:1")).async_init()
        try:
            with pytest.raises(ValueError):
                await getattr(client, method)(**kwargs)
        finally:
            await client.close()


RISK_FIELDS.update(
    {
        "get_spot_api_key_info": [],
        "get_spot_credit_lines": [("rebase_multiplier", "base")],
        "get_spot_order_amends": [("order_id", "OID-1"), ("rebase_multiplier", "base")],
        "get_spot_wallet_accounts": [],
        "get_spot_ledger_entries": [
            ("id", "ledger1,ledger2"),
            ("trades", "true"),
            ("rebase_multiplier", "base"),
        ],
        "get_futures_portfolio_margin_parameters": [],
        "get_futures_unwind_queue": [],
        "get_futures_notifications": [],
        "get_spot_grouped_orderbook": [("pair", "XBTUSD"), ("depth", "25"), ("grouping", "100")],
        "get_spot_maintenance_schedule": [],
        "get_futures_self_trade_strategy": [],
        "set_futures_self_trade_strategy": [("strategy", "CANCEL_MAKER_SELF")],
        "get_futures_trading_instruments": [
            ("contractType", "futures_inverse"),
            ("contractType", "flexible_futures"),
        ],
        "get_futures_subaccount_trading_status": [],
        "set_futures_subaccount_trading_status": [("tradingEnabled", "false")],
    }
)

RISK_FIELDS.update(
    {
        "delete_spot_export_report": [("id", "report1"), ("type", "cancel")],
        "get_spot_export_status": [("report", "trades")],
        "request_spot_export_report": [
            ("report", "trades"),
            ("format", "CSV"),
            ("description", "history"),
            ("starttm", "1700000000"),
            ("endtm", "1700000060"),
        ],
        "simulate_futures_portfolio": [
            (
                "json",
                '{"positions":[{"instrument":"PF_XBTUSD","size":-1.25,"entryPrice":60000.25}]}',
            )
        ],
        "get_futures_market_analytics": [("since", "1700000000"), ("interval", "60")],
        "check_futures_api_key": [],
        "get_futures_ticker": [],
        "get_futures_pnl_preferences": [],
        "set_futures_pnl_preference": [("symbol", "PF_XBTUSD"), ("pnlPreference", "USD")],
        "create_spot_subaccount": [("username", "trader1"), ("email", "trader@example.com")],
        "get_futures_subaccounts": [],
        "get_spot_post_trade_data": [("symbol", "BTC/USD")],
        "get_spot_pre_trade_data": [("symbol", "BTC/USD")],
    }
)
