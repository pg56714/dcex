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
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
WRAPPER_FILES = (
    "_withdrawals_http.py",
    "_transfers_http.py",
    "_batch_http.py",
    "_account_http.py",
    "_market_http.py",
    "_trade_http.py",
)
WRAPPER_FILES += tuple(str(p.relative_to(ROOT / "dcex/bingx")) for p in sorted((ROOT / "dcex/bingx/_generated").glob("*_http.py")))

SPOT_ORDER = ("POST", "/openApi/spot/v1/trade/order")
SWAP_ORDER = ("POST", "/openApi/swap/v2/trade/order")
LISTEN_KEY = "/openApi/user/auth/userDataStream"

# Python wrapper name -> (HTTP method, documented path).
ROUTES: dict[str, tuple[str, str]] = {
    "get_spot_server_time": ("GET", "/openApi/spot/v1/server/time"),
    "replace_swap_batch_orders": ("POST", "/openApi/swap/v1/trade/batchCancelReplace"),
    "get_coin_swap_contracts": ("GET", "/openApi/cswap/v1/market/contracts"),
    "get_coin_swap_orderbook": ("GET", "/openApi/cswap/v1/market/depth"),
    "get_coin_swap_kline": ("GET", "/openApi/cswap/v1/market/klines"),
    "get_coin_swap_premium_index": ("GET", "/openApi/cswap/v1/market/premiumIndex"),
    "get_coin_swap_open_interest": ("GET", "/openApi/cswap/v1/market/openInterest"),
    "get_coin_swap_ticker": ("GET", "/openApi/cswap/v1/market/ticker"),
    "place_coin_swap_order": ("POST", "/openApi/cswap/v1/trade/order"),
    "cancel_coin_swap_order": ("DELETE", "/openApi/cswap/v1/trade/cancelOrder"),
    "cancel_coin_swap_all_orders": ("POST", "/openApi/cswap/v1/trade/allOpenOrders"),
    "close_coin_swap_all_positions": ("POST", "/openApi/cswap/v1/trade/closeAllPositions"),
    "get_coin_swap_open_orders": ("GET", "/openApi/cswap/v1/trade/openOrders"),
    "get_coin_swap_order": ("GET", "/openApi/cswap/v1/trade/orderDetail"),
    "get_coin_swap_order_history": ("GET", "/openApi/cswap/v1/trade/orderHistory"),
    "get_coin_swap_fills": ("GET", "/openApi/cswap/v1/trade/allFillOrders"),
    "get_coin_swap_force_orders": ("GET", "/openApi/cswap/v1/trade/forceOrders"),
    "get_coin_swap_leverage": ("GET", "/openApi/cswap/v1/trade/leverage"),
    "set_coin_swap_leverage": ("POST", "/openApi/cswap/v1/trade/leverage"),
    "get_coin_swap_margin_type": ("GET", "/openApi/cswap/v1/trade/marginType"),
    "set_coin_swap_margin_type": ("POST", "/openApi/cswap/v1/trade/marginType"),
    "adjust_coin_swap_position_margin": ("POST", "/openApi/cswap/v1/trade/positionMargin"),
    "get_coin_swap_commission_rate": ("GET", "/openApi/cswap/v1/user/commissionRate"),
    "get_coin_swap_balance": ("GET", "/openApi/cswap/v1/user/balance"),
    "get_coin_swap_positions": ("GET", "/openApi/cswap/v1/user/positions"),
    "get_spot_historical_kline": ("GET", "/openApi/market/his/v1/kline"),
    "place_spot_oco": ("POST", "/openApi/spot/v1/oco/order"),
    "cancel_spot_oco": ("POST", "/openApi/spot/v1/oco/cancel"),
    "get_spot_oco": ("GET", "/openApi/spot/v1/oco/orderList"),
    "get_spot_open_oco": ("GET", "/openApi/spot/v1/oco/openOrderList"),
    "get_spot_oco_history": ("GET", "/openApi/spot/v1/oco/historyOrderList"),
    "get_deposit_history": ("GET", "/openApi/api/v3/capital/deposit/hisrec"),
    "set_swap_cancel_all_after": ("POST", "/openApi/swap/v2/trade/cancelAllAfter"),
    "get_swap_open_order": ("GET", "/openApi/swap/v2/trade/openOrder"),
    "get_swap_force_orders": ("GET", "/openApi/swap/v2/trade/forceOrders"),
    "get_swap_trade_fills": ("GET", "/openApi/swap/v2/trade/allFillOrders"),
    "adjust_swap_position_margin": ("POST", "/openApi/swap/v2/trade/positionMargin"),
    "amend_swap_order": ("POST", "/openApi/swap/v1/trade/amend"),
    "place_swap_twap_order": ("POST", "/openApi/swap/v1/twap/order"),
    "cancel_swap_twap_order": ("POST", "/openApi/swap/v1/twap/cancelOrder"),
    "get_swap_open_twap_orders": ("GET", "/openApi/swap/v1/twap/openOrders"),
    "get_swap_twap_order_history": ("GET", "/openApi/swap/v1/twap/historyOrders"),
    "get_swap_twap_order": ("GET", "/openApi/swap/v1/twap/orderDetail"),
    "get_swap_asset_mode": ("GET", "/openApi/swap/v1/trade/assetMode"),
    "set_swap_asset_mode": ("POST", "/openApi/swap/v1/trade/assetMode"),
    "get_swap_multi_asset_rules": ("GET", "/openApi/swap/v1/trade/multiAssetsRules"),
    "get_swap_margin_assets": ("GET", "/openApi/swap/v1/user/marginAssets"),
    "get_swap_full_orders": ("GET", "/openApi/swap/v1/trade/fullOrder"),
    "get_swap_fill_history": ("GET", "/openApi/swap/v2/trade/fillHistory"),
    "get_swap_position_history": ("GET", "/openApi/swap/v1/trade/positionHistory"),
    "get_swap_margin_history": ("GET", "/openApi/swap/v1/positionMargin/history"),
    "get_swap_maintenance_margin_ratios": ("GET", "/openApi/swap/v1/maintMarginRatio"),
    "set_swap_auto_add_margin": ("POST", "/openApi/swap/v1/trade/autoAddMargin"),
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
    "get_swap_asset_mode",
    "get_swap_fill_history",
    "get_swap_force_orders",
    "get_swap_full_orders",
    "get_swap_maintenance_margin_ratios",
    "get_swap_margin_assets",
    "get_swap_margin_history",
    "get_swap_multi_asset_rules",
    "get_swap_open_order",
    "get_swap_open_twap_orders",
    "get_swap_position_history",
    "get_swap_trade_fills",
    "get_swap_twap_order",
    "get_swap_twap_order_history",
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


def _call_checked_native(name: str, call: Any) -> Any:  # noqa: ANN401
    try:
        return call()
    except ValueError as exc:
        if STALE_NATIVE_MARKER in str(exc):
            pytest.fail(f"installed dcex._native predates {name}; rebuild the extension")
        raise


CONTROL_CASES = [
    (
        "set_swap_cancel_all_after",
        {"type_": "ACTIVATE", "timeOut": 30},
        "POST",
        "/openApi/swap/v2/trade/cancelAllAfter",
    ),
    (
        "get_swap_open_order",
        {"product_symbol": "BTC-USDT-SWAP", "orderId": 123},
        "GET",
        "/openApi/swap/v2/trade/openOrder",
    ),
    ("get_swap_force_orders", {}, "GET", "/openApi/swap/v2/trade/forceOrders"),
    (
        "get_swap_trade_fills",
        {"tradingUnit": "COIN", "startTs": 1700000000000, "endTs": 1700000100000},
        "GET",
        "/openApi/swap/v2/trade/allFillOrders",
    ),
    (
        "adjust_swap_position_margin",
        {"product_symbol": "BTC-USDT-SWAP", "amount": "2", "type_": 2, "positionSide": "LONG"},
        "POST",
        "/openApi/swap/v2/trade/positionMargin",
    ),
    (
        "amend_swap_order",
        {"product_symbol": "BTC-USDT-SWAP", "quantity": "1", "clientOrderId": "amend-me"},
        "POST",
        "/openApi/swap/v1/trade/amend",
    ),
    (
        "place_swap_twap_order",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "BUY",
            "positionSide": "LONG",
            "priceType": "constant",
            "priceVariance": "1",
            "triggerPrice": "60000",
            "interval": 10,
            "amountPerOrder": "1",
            "totalAmount": "5",
        },
        "POST",
        "/openApi/swap/v1/twap/order",
    ),
    ("cancel_swap_twap_order", {"mainOrderId": "123"}, "POST", "/openApi/swap/v1/twap/cancelOrder"),
    ("get_swap_open_twap_orders", {}, "GET", "/openApi/swap/v1/twap/openOrders"),
    (
        "get_swap_twap_order_history",
        {"pageIndex": 1, "pageSize": 20, "startTime": 1700000000000, "endTime": 1700000100000},
        "GET",
        "/openApi/swap/v1/twap/historyOrders",
    ),
    ("get_swap_twap_order", {"mainOrderId": "123"}, "GET", "/openApi/swap/v1/twap/orderDetail"),
    ("get_swap_asset_mode", {}, "GET", "/openApi/swap/v1/trade/assetMode"),
    (
        "set_swap_asset_mode",
        {"assetMode": "multiAssetsMode", "confirm": True},
        "POST",
        "/openApi/swap/v1/trade/assetMode",
    ),
    ("get_swap_multi_asset_rules", {}, "GET", "/openApi/swap/v1/trade/multiAssetsRules"),
    ("get_swap_margin_assets", {}, "GET", "/openApi/swap/v1/user/marginAssets"),
    ("get_swap_full_orders", {"limit": 20}, "GET", "/openApi/swap/v1/trade/fullOrder"),
    (
        "get_swap_fill_history",
        {"product_symbol": "BTC-USDT-SWAP", "startTs": 1700000000000, "endTs": 1700000100000},
        "GET",
        "/openApi/swap/v2/trade/fillHistory",
    ),
    (
        "get_swap_position_history",
        {"product_symbol": "BTC-USDT-SWAP", "startTs": 1700000000000, "endTs": 1700000100000},
        "GET",
        "/openApi/swap/v1/trade/positionHistory",
    ),
    (
        "get_swap_margin_history",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "positionId": "123",
            "startTime": 1700000000000,
            "endTime": 1700000100000,
            "pageIndex": 1,
            "pageSize": 20,
        },
        "GET",
        "/openApi/swap/v1/positionMargin/history",
    ),
    (
        "get_swap_maintenance_margin_ratios",
        {"product_symbol": "BTC-USDT-SWAP"},
        "GET",
        "/openApi/swap/v1/maintMarginRatio",
    ),
    (
        "set_swap_auto_add_margin",
        {"product_symbol": "BTC-USDT-SWAP", "positionId": "123", "functionSwitch": "true"},
        "POST",
        "/openApi/swap/v1/trade/autoAddMargin",
    ),
]


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
                    if node.name != "export_swap_income":  # Binary export has separate coverage.
                        names.add(node.name)
    return names


class _Recorder(BaseHTTPRequestHandler):
    received: "queue.Queue[dict[str, Any]]"

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        split = urlsplit(self.path)
        self.received.put(
            {
                "method": self.command,
                "path": split.path,
                "query": dict(parse_qsl(split.query)),
                "api_key": self.headers.get("X-BX-APIKEY"),
                "body": body,
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
    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = httpd.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=10)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": "api-key",
        "api_secret": "api-secret",
        "base_url": base_url,
        "preload_product_table": False,
    }


ADDITIONAL_CASES = [
    (
        "get_coin_swap_contracts",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/market/contracts",
    ),
    (
        "get_coin_swap_orderbook",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/market/depth",
    ),
    (
        "get_coin_swap_kline",
        {"product_symbol": "BTC-USD-SWAP", "interval": "1m"},
        "GET",
        "/openApi/cswap/v1/market/klines",
    ),
    (
        "get_coin_swap_premium_index",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/market/premiumIndex",
    ),
    (
        "get_coin_swap_open_interest",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/market/openInterest",
    ),
    (
        "get_coin_swap_ticker",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/market/ticker",
    ),
    (
        "place_coin_swap_order",
        {"product_symbol": "BTC-USD-SWAP", "side": "SELL", "type_": "MARKET", "quantity": "1"},
        "POST",
        "/openApi/cswap/v1/trade/order",
    ),
    (
        "cancel_coin_swap_order",
        {"product_symbol": "BTC-USD-SWAP", "order_id": 1},
        "DELETE",
        "/openApi/cswap/v1/trade/cancelOrder",
    ),
    (
        "cancel_coin_swap_all_orders",
        {"product_symbol": "BTC-USD-SWAP"},
        "POST",
        "/openApi/cswap/v1/trade/allOpenOrders",
    ),
    (
        "close_coin_swap_all_positions",
        {"product_symbol": "BTC-USD-SWAP"},
        "POST",
        "/openApi/cswap/v1/trade/closeAllPositions",
    ),
    (
        "get_coin_swap_open_orders",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/trade/openOrders",
    ),
    (
        "get_coin_swap_order",
        {"product_symbol": "BTC-USD-SWAP", "order_id": 1},
        "GET",
        "/openApi/cswap/v1/trade/orderDetail",
    ),
    (
        "get_coin_swap_order_history",
        {"limit": 20, "product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/trade/orderHistory",
    ),
    ("get_coin_swap_fills", {"order_id": "1"}, "GET", "/openApi/cswap/v1/trade/allFillOrders"),
    (
        "get_coin_swap_force_orders",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/trade/forceOrders",
    ),
    (
        "get_coin_swap_leverage",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/trade/leverage",
    ),
    (
        "set_coin_swap_leverage",
        {"product_symbol": "BTC-USD-SWAP", "side": "LONG", "leverage": "5"},
        "POST",
        "/openApi/cswap/v1/trade/leverage",
    ),
    (
        "get_coin_swap_margin_type",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/trade/marginType",
    ),
    (
        "set_coin_swap_margin_type",
        {"product_symbol": "BTC-USD-SWAP", "margin_type": "ISOLATED"},
        "POST",
        "/openApi/cswap/v1/trade/marginType",
    ),
    (
        "adjust_coin_swap_position_margin",
        {"product_symbol": "BTC-USD-SWAP", "position_side": "LONG", "amount": "1", "type_": 1},
        "POST",
        "/openApi/cswap/v1/trade/positionMargin",
    ),
    ("get_coin_swap_commission_rate", {}, "GET", "/openApi/cswap/v1/user/commissionRate"),
    (
        "get_coin_swap_balance",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/user/balance",
    ),
    (
        "get_coin_swap_positions",
        {"product_symbol": "BTC-USD-SWAP"},
        "GET",
        "/openApi/cswap/v1/user/positions",
    ),
    (
        "get_spot_historical_kline",
        {"product_symbol": "BTC-USDT-SPOT", "interval": "1m"},
        "GET",
        "/openApi/market/his/v1/kline",
    ),
    (
        "place_spot_oco",
        {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "SELL",
            "quantity": "1",
            "limit_price": "120",
            "trigger_price": "90",
            "order_price": "89",
        },
        "POST",
        "/openApi/spot/v1/oco/order",
    ),
    ("cancel_spot_oco", {"order_id": "1"}, "POST", "/openApi/spot/v1/oco/cancel"),
    ("get_spot_oco", {"order_list_id": "1"}, "GET", "/openApi/spot/v1/oco/orderList"),
    (
        "get_spot_open_oco",
        {"page_index": 1, "page_size": 20},
        "GET",
        "/openApi/spot/v1/oco/openOrderList",
    ),
    (
        "get_spot_oco_history",
        {"page_index": 1, "page_size": 20},
        "GET",
        "/openApi/spot/v1/oco/historyOrderList",
    ),
    ("get_deposit_history", {}, "GET", "/openApi/api/v3/capital/deposit/hisrec"),
]
ADDITIONAL_FIELDS = {
    "get_coin_swap_contracts": {"symbol": "BTC-USD"},
    "get_coin_swap_orderbook": {"symbol": "BTC-USD"},
    "get_coin_swap_kline": {"symbol": "BTC-USD", "interval": "1m"},
    "get_coin_swap_premium_index": {"symbol": "BTC-USD"},
    "get_coin_swap_open_interest": {"symbol": "BTC-USD"},
    "get_coin_swap_ticker": {"symbol": "BTC-USD"},
    "place_coin_swap_order": {
        "symbol": "BTC-USD",
        "side": "SELL",
        "type": "MARKET",
        "quantity": "1",
    },
    "cancel_coin_swap_order": {"symbol": "BTC-USD", "orderId": "1"},
    "cancel_coin_swap_all_orders": {"symbol": "BTC-USD"},
    "close_coin_swap_all_positions": {"symbol": "BTC-USD"},
    "get_coin_swap_open_orders": {"symbol": "BTC-USD"},
    "get_coin_swap_order": {"symbol": "BTC-USD", "orderId": "1"},
    "get_coin_swap_order_history": {"limit": "20", "symbol": "BTC-USD"},
    "get_coin_swap_fills": {"orderId": "1"},
    "get_coin_swap_force_orders": {"symbol": "BTC-USD"},
    "get_coin_swap_leverage": {"symbol": "BTC-USD"},
    "set_coin_swap_leverage": {"symbol": "BTC-USD", "side": "LONG", "leverage": "5"},
    "get_coin_swap_margin_type": {"symbol": "BTC-USD"},
    "set_coin_swap_margin_type": {"symbol": "BTC-USD", "marginType": "ISOLATED"},
    "adjust_coin_swap_position_margin": {
        "symbol": "BTC-USD",
        "positionSide": "LONG",
        "amount": "1",
        "type": "1",
    },
    "get_coin_swap_commission_rate": {},
    "get_coin_swap_balance": {"symbol": "BTC-USD"},
    "get_coin_swap_positions": {"symbol": "BTC-USD"},
    "get_spot_historical_kline": {"symbol": "BTC-USDT", "interval": "1m"},
    "place_spot_oco": {
        "symbol": "BTC-USDT",
        "side": "SELL",
        "quantity": "1",
        "limitPrice": "120",
        "triggerPrice": "90",
        "orderPrice": "89",
    },
    "cancel_spot_oco": {"orderId": "1"},
    "get_spot_oco": {"orderListId": "1"},
    "get_spot_open_oco": {"pageIndex": "1", "pageSize": "20"},
    "get_spot_oco_history": {"pageIndex": "1", "pageSize": "20"},
    "get_deposit_history": {},
}
PUBLIC_METHODS.difference_update(
    [
        "place_coin_swap_order",
        "cancel_coin_swap_order",
        "cancel_coin_swap_all_orders",
        "close_coin_swap_all_positions",
        "get_coin_swap_open_orders",
        "get_coin_swap_order",
        "get_coin_swap_order_history",
        "get_coin_swap_fills",
        "get_coin_swap_force_orders",
        "get_coin_swap_leverage",
        "set_coin_swap_leverage",
        "get_coin_swap_margin_type",
        "set_coin_swap_margin_type",
        "adjust_coin_swap_position_margin",
        "get_coin_swap_commission_rate",
        "get_coin_swap_balance",
        "get_coin_swap_positions",
        "place_spot_oco",
        "cancel_spot_oco",
        "get_spot_oco",
        "get_spot_open_oco",
        "get_spot_oco_history",
        "get_deposit_history",
    ]
)
PUBLIC_METHODS.update(
    [
        "get_coin_swap_contracts",
        "get_coin_swap_orderbook",
        "get_coin_swap_kline",
        "get_coin_swap_premium_index",
        "get_coin_swap_open_interest",
        "get_coin_swap_ticker",
        "get_spot_historical_kline",
    ]
)

ADDITIONAL_CASES.extend(
    [
        ("get_swap_server_time", {}, "GET", "/openApi/swap/v2/server/time"),
        (
            "get_swap_price_ticker",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/openApi/swap/v1/ticker/price",
        ),
    ]
)
ADDITIONAL_FIELDS.update(
    {"get_swap_server_time": {}, "get_swap_price_ticker": {"symbol": "BTC-USDT"}}
)
ROUTES.update(
    {
        "get_swap_server_time": ("GET", "/openApi/swap/v2/server/time"),
        "get_swap_price_ticker": ("GET", "/openApi/swap/v1/ticker/price"),
    }
)
PUBLIC_METHODS.update(["get_swap_server_time", "get_swap_price_ticker"])

BATCH_REPLACEMENT = [
    {
        "product_symbol": "BTC-USDT-SWAP",
        "cancelOrderId": "1",
        "side": "SELL",
        "positionSide": "BOTH",
        "type": "STOP_MARKET",
        "stopPrice": 90,
        "quantity": 1,
        "cancelReplaceMode": "STOP_ON_FAILURE",
    }
]

ADDITIONAL_CASES.extend(
    [
        (
            "get_spot_historical_trades",
            {"product_symbol": "BTC-USDT-SPOT"},
            "GET",
            "/openApi/market/his/v1/trade",
        ),
        ("get_coin_network_config", {}, "GET", "/openApi/wallets/v1/capital/config/getall"),
        (
            "get_deposit_addresses",
            {"coin": "USDT"},
            "GET",
            "/openApi/wallets/v1/capital/deposit/address",
        ),
        ("get_deposit_risk_records", {}, "GET", "/openApi/wallets/v1/capital/deposit/riskRecords"),
        (
            "get_swap_historical_trades",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/openApi/swap/v1/market/historicalTrades",
        ),
        (
            "reverse_swap_position",
            {"type_": "Reverse", "product_symbol": "BTC-USDT-SWAP", "confirm": True},
            "POST",
            "/openApi/swap/v1/trade/reverse",
        ),
        ("adjust_simulated_trading_balance", {}, "POST", "/openApi/swap/v2/trade/getVst"),
        ("get_standard_futures_positions", {}, "GET", "/openApi/contract/v1/allPosition"),
        (
            "get_standard_futures_orders",
            {"product_symbol": "BTC-USDT-SWAP"},
            "GET",
            "/openApi/contract/v1/allOrders",
        ),
        ("get_standard_futures_balance", {}, "GET", "/openApi/contract/v1/balance"),
        ("get_api_permissions", {}, "GET", "/openApi/v1/account/apiPermissions"),
        (
            "create_sub_account",
            {"sub_account_string": "trader123"},
            "POST",
            "/openApi/subAccount/v1/create",
        ),
        (
            "set_sub_account_frozen",
            {"sub_uid": 123, "freeze": True},
            "POST",
            "/openApi/subAccount/v1/updateStatus",
        ),
        (
            "create_sub_account_api_key",
            {"sub_uid": 123, "note": "trading", "permissions": [4, 5]},
            "POST",
            "/openApi/subAccount/v1/apiKey/create",
        ),
        (
            "modify_sub_account_api_key",
            {"sub_uid": 123, "api_key": "query-key", "note": "trading", "permissions": [4, 5]},
            "POST",
            "/openApi/subAccount/v1/apiKey/edit",
        ),
        (
            "delete_sub_account_api_key",
            {"sub_uid": 123, "api_key": "query-key"},
            "POST",
            "/openApi/subAccount/v1/apiKey/del",
        ),
        (
            "set_sub_account_transfer_authorization",
            {"sub_uids": "123", "transferable": True},
            "POST",
            "/openApi/account/v1/innerTransfer/authorizeSubAccount",
        ),
        (
            "get_sub_account_deposit_addresses",
            {"coin": "USDT", "sub_uid": 123},
            "GET",
            "/openApi/wallets/v1/capital/subAccount/deposit/address",
        ),
        (
            "get_sub_account_deposit_history",
            {},
            "GET",
            "/openApi/wallets/v1/capital/deposit/subHisrec",
        ),
        ("get_api_restrictions", {}, "GET", "/openApi/v1/account/apiRestrictions"),
        (
            "create_sub_account_deposit_address",
            {"coin": "USDT", "sub_uid": 123, "network": "TRC20", "wallet_type": 1},
            "POST",
            "/openApi/wallets/v1/capital/deposit/createSubAddress",
        ),
    ]
)
ADDITIONAL_FIELDS.update(
    {
        "get_spot_historical_trades": {"symbol": "BTC-USDT"},
        "get_coin_network_config": {},
        "get_deposit_addresses": {"coin": "USDT"},
        "get_deposit_risk_records": {},
        "get_swap_historical_trades": {"symbol": "BTC-USDT"},
        "reverse_swap_position": {"type": "Reverse", "symbol": "BTC-USDT"},
        "adjust_simulated_trading_balance": {},
        "get_standard_futures_positions": {},
        "get_standard_futures_orders": {"symbol": "BTC-USDT"},
        "get_standard_futures_balance": {},
        "get_api_permissions": {},
        "create_sub_account": {"subAccountString": "trader123"},
        "set_sub_account_frozen": {"subUid": "123", "freeze": "true"},
        "create_sub_account_api_key": {
            "subUid": "123",
            "note": "trading",
            "permissions": "[4,5]",
        },
        "modify_sub_account_api_key": {
            "subUid": "123",
            "apiKey": "query-key",
            "note": "trading",
            "permissions": "[4,5]",
        },
        "delete_sub_account_api_key": {"subUid": "123", "apiKey": "query-key"},
        "set_sub_account_transfer_authorization": {"subUids": "123", "transferable": "true"},
        "get_sub_account_deposit_addresses": {"coin": "USDT", "subUid": "123"},
        "get_sub_account_deposit_history": {},
        "get_api_restrictions": {},
        "create_sub_account_deposit_address": {
            "coin": "USDT",
            "subUid": "123",
            "network": "TRC20",
            "walletType": "1",
        },
    }
)
ROUTES.update(
    {
        "get_spot_historical_trades": ("GET", "/openApi/market/his/v1/trade"),
        "get_coin_network_config": ("GET", "/openApi/wallets/v1/capital/config/getall"),
        "get_deposit_addresses": ("GET", "/openApi/wallets/v1/capital/deposit/address"),
        "get_deposit_risk_records": ("GET", "/openApi/wallets/v1/capital/deposit/riskRecords"),
        "get_swap_historical_trades": ("GET", "/openApi/swap/v1/market/historicalTrades"),
        "reverse_swap_position": ("POST", "/openApi/swap/v1/trade/reverse"),
        "adjust_simulated_trading_balance": ("POST", "/openApi/swap/v2/trade/getVst"),
        "get_standard_futures_positions": ("GET", "/openApi/contract/v1/allPosition"),
        "get_standard_futures_orders": ("GET", "/openApi/contract/v1/allOrders"),
        "get_standard_futures_balance": ("GET", "/openApi/contract/v1/balance"),
        "get_api_permissions": ("GET", "/openApi/v1/account/apiPermissions"),
        "create_sub_account": ("POST", "/openApi/subAccount/v1/create"),
        "set_sub_account_frozen": ("POST", "/openApi/subAccount/v1/updateStatus"),
        "create_sub_account_api_key": ("POST", "/openApi/subAccount/v1/apiKey/create"),
        "modify_sub_account_api_key": ("POST", "/openApi/subAccount/v1/apiKey/edit"),
        "delete_sub_account_api_key": ("POST", "/openApi/subAccount/v1/apiKey/del"),
        "set_sub_account_transfer_authorization": (
            "POST",
            "/openApi/account/v1/innerTransfer/authorizeSubAccount",
        ),
        "get_sub_account_deposit_addresses": (
            "GET",
            "/openApi/wallets/v1/capital/subAccount/deposit/address",
        ),
        "get_sub_account_deposit_history": ("GET", "/openApi/wallets/v1/capital/deposit/subHisrec"),
        "get_api_restrictions": ("GET", "/openApi/v1/account/apiRestrictions"),
        "create_sub_account_deposit_address": (
            "POST",
            "/openApi/wallets/v1/capital/deposit/createSubAddress",
        ),
    }
)
PUBLIC_METHODS.update(["get_spot_historical_trades", "get_swap_historical_trades"])


ADDITIONAL_CASES.extend(
    [
        ("get_withdrawal_history", {}, "GET", "/openApi/api/v3/capital/withdraw/history"),
        (
            "get_internal_transfer_records",
            {"coin": "USDT"},
            "GET",
            "/openApi/wallets/v1/capital/innerTransfer/records",
        ),
        (
            "get_sub_account_internal_transfer_records",
            {"coin": "USDT"},
            "GET",
            "/openApi/wallets/v1/capital/subAccount/innerTransfer/records",
        ),
    ]
)
ADDITIONAL_FIELDS.update(
    {
        "get_withdrawal_history": {},
        "get_internal_transfer_records": {"coin": "USDT"},
        "get_sub_account_internal_transfer_records": {"coin": "USDT"},
    }
)
ROUTES.update(
    {
        "get_withdrawal_history": ("GET", "/openApi/api/v3/capital/withdraw/history"),
        "get_internal_transfer_records": (
            "GET",
            "/openApi/wallets/v1/capital/innerTransfer/records",
        ),
        "get_sub_account_internal_transfer_records": (
            "GET",
            "/openApi/wallets/v1/capital/subAccount/innerTransfer/records",
        ),
    }
)


WALLET_CASES = [
    (
        "transfer_master_internal",
        {
            "coin": "USDT",
            "user_account_type": 2,
            "user_account": "123456789",
            "amount": "1.000000000000000001",
            "wallet_type": 1,
            "calling_code": "886",
            "transfer_client_id": "offline1",
        },
        "POST",
        "/openApi/wallets/v1/capital/innerTransfer/apply",
    ),
    (
        "transfer_sub_account_internal",
        {
            "coin": "USDT",
            "user_account_type": 1,
            "user_account": "123456",
            "amount": "1.000000000000000001",
            "wallet_type": 15,
            "transfer_client_id": "offline2",
            "recv_window": 5000,
        },
        "POST",
        "/openApi/wallets/v1/capital/subAccountInnerTransfer/apply",
    ),
    (
        "create_withdrawal",
        {
            "coin": "USDT",
            "address": "offline-address",
            "amount": "1.000000000000000001",
            "wallet_type": 1,
            "network": "BEP20",
            "address_tag": "test",
            "withdraw_order_id": "offline3",
            "vasp_entity_id": "Others",
        },
        "POST",
        "/openApi/wallets/v1/capital/withdraw/apply",
    ),
]
ADDITIONAL_CASES.extend(WALLET_CASES)
ROUTES.update({name: (verb, path) for name, _, verb, path in WALLET_CASES})
ADDITIONAL_FIELDS.update(
    {
        "transfer_master_internal": {
            "coin": "USDT",
            "userAccountType": "2",
            "userAccount": "123456789",
            "amount": "1.000000000000000001",
            "walletType": "1",
            "callingCode": "886",
            "transferClientId": "offline1",
        },
        "transfer_sub_account_internal": {
            "coin": "USDT",
            "userAccountType": "1",
            "userAccount": "123456",
            "amount": "1.000000000000000001",
            "walletType": "15",
            "transferClientId": "offline2",
            "recvWindow": "5000",
        },
        "create_withdrawal": {
            "coin": "USDT",
            "address": "offline-address",
            "amount": "1.000000000000000001",
            "walletType": "1",
            "network": "BEP20",
            "addressTag": "test",
            "withdrawOrderId": "offline3",
            "vaspEntityId": "Others",
        },
    }
)


def _kwargs(method: Any, name: str) -> dict[str, Any]:  # noqa: ANN401
    if name == "replace_swap_batch_orders":
        return {"orders": BATCH_REPLACEMENT}
    for case_name, kwargs, *_ in ADDITIONAL_CASES:
        if name == case_name:
            return kwargs.copy()
    for case_name, kwargs, *_ in CONTROL_CASES:
        if name == case_name:
            return kwargs.copy()
    kwargs: dict[str, Any] = {}
    aliases = {new: old for old, new in getattr(method, "__legacy_keywords__", {}).items()}
    for parameter in inspect.signature(method).parameters.values():
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is not inspect.Parameter.empty:
            continue
        if parameter.name == "product_symbol":
            kwargs[parameter.name] = "BTC-USDT-SPOT" if "spot" in name else "BTC-USDT-SWAP"
        elif aliases.get(parameter.name, parameter.name) in VALUES:
            sample_name = aliases.get(parameter.name, parameter.name)
            kwargs[sample_name] = VALUES[sample_name]
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
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("bingx", name, request)
    assert (request["method"], request["path"]) == ROUTES[name], name
    fields = request["query"]
    if request["body"]:
        import hashlib
        import hmac

        assert fields == {}
        body = (
            json.loads(request["body"], parse_float=Decimal)
            if name == "transfer_sub_account_internal"
            else json.loads(request["body"])
        )
        signature = body.pop("signature")
        assert isinstance(body["timestamp"], int)

        def signing_text(value: Any) -> str:  # noqa: ANN401
            if isinstance(value, list):
                return ",".join(signing_text(item) for item in value)
            if isinstance(value, bool):
                return str(value).lower()
            return str(value)

        canonical = "&".join(f"{key}={signing_text(value)}" for key, value in sorted(body.items()))
        assert signature == hmac.new(b"api-secret", canonical.encode(), hashlib.sha256).hexdigest()
        fields = {
            key: json.dumps(value, separators=(",", ":"))
            if isinstance(value, (list, bool))
            else str(value)
            for key, value in body.items()
        }
        fields["signature"] = signature
        if "subUid" in body:
            assert isinstance(body["subUid"], int)
        if "freeze" in body:
            assert isinstance(body["freeze"], bool)
    if name in ADDITIONAL_FIELDS:
        assert {
            key: value for key, value in fields.items() if key not in {"signature", "timestamp"}
        } == ADDITIONAL_FIELDS[name]
    if name == "replace_swap_batch_orders":
        batch = json.loads(request["query"]["batchOrders"])
        assert batch[0]["symbol"] == "BTC-USDT"
        assert batch[0]["quantity"] == 1
        assert "closePosition" not in batch[0]
        assert batch[0]["cancelOrderId"] == "1"
    signed = "signature" in fields
    if name in {"transfer_master_internal", "create_withdrawal"}:
        import hashlib
        import hmac

        assert request["body"] == b""
        canonical = "&".join(
            f"{key}={value}" for key, value in sorted(fields.items()) if key != "signature"
        )
        assert (
            fields["signature"]
            == hmac.new(b"api-secret", canonical.encode(), hashlib.sha256).hexdigest()
        )
    if name in PUBLIC_METHODS:
        assert not signed, name
    elif name in UNSIGNED_PRIVATE:
        assert request["api_key"] == "api-key", name
        assert not signed, name
    else:
        assert signed, name
        assert request["api_key"] == "api-key", name
    assert "type_" not in request["query"], name
    for case_name, kwargs, *_ in CONTROL_CASES:
        if case_name == name:
            expected = {
                "symbol"
                if key == "product_symbol"
                else "type"
                if key == "type_"
                else key: "BTC-USDT" if key == "product_symbol" else str(value)
                for key, value in kwargs.items()
                if key not in {"confirm", "all_symbols"}
            }
            assert {
                key: value
                for key, value in request["query"].items()
                if key not in {"signature", "timestamp"}
            } == expected


def test_route_table_matches_python_surface() -> None:
    """Every sync/async wrapper is mapped to a documented route."""
    sync_names = _wrapper_names("sync")
    async_names = _wrapper_names("async")
    assert sync_names == async_names
    from tests.unit.test_bingx_schema_requests import NAMES

    assert sync_names == set(ROUTES) | NAMES


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
    assert _call_checked_native(name, lambda: method(**_kwargs(method, name))) is not None
    _assert_route(name, received.get(timeout=10))


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
            aliases = getattr(method, "__legacy_keywords__", {})
            kwargs = {aliases.get(key, key): value for key, value in _kwargs(method, name).items()}
            return await method(**kwargs)

    assert _call_checked_native(name, lambda: asyncio.run(call())) is not None
    _assert_route(name, received.get(timeout=10))


def test_sync_helpers_pin_side_type_and_time_in_force(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Convenience helpers pin side/type/timeInForce and map canonical symbols."""
    from dcex.bingx.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    client.place_swap_post_only_sell_order(
        product_symbol="ETH-USDT-SWAP", quantity="1", price="100", position_side="SHORT"
    )
    query = received.get(timeout=10)["query"]
    assert query["symbol"] == "ETH-USDT"
    assert (query["side"], query["type"], query["timeInForce"]) == ("SELL", "LIMIT", "PostOnly")

    client.cancel_swap_all_orders(product_symbol="BTC-USDT-SWAP", type_="LIMIT")
    query = received.get(timeout=10)["query"]
    assert query["type"] == "LIMIT"

    client.get_spot_orderbook_v2(product_symbol="BTC-USDT-SPOT", depth=20)
    query = received.get(timeout=10)["query"]
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
    "get_spot_server_time",
    "get_swap_server_time",
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
    _call_checked_native(name, lambda: method(**_kwargs(method, name)))
    query = received.get(timeout=10)["query"]
    if name in PUBLIC_WITHOUT_TIMESTAMP:
        assert "timestamp" not in query, name
    else:
        assert query.get("timestamp", "").isdigit(), name
    assert "signature" not in query, name


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        (
            "place_swap_twap_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "side": "BUY",
                "positionSide": "LONG",
                "priceType": "constant",
                "priceVariance": "1",
                "triggerPrice": "100",
                "interval": 4,
                "amountPerOrder": "1",
                "totalAmount": "10",
            },
        ),
        (
            "place_swap_twap_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "side": "BUY",
                "positionSide": "LONG",
                "priceType": "constant",
                "priceVariance": "1",
                "triggerPrice": "100",
                "interval": 10,
                "amountPerOrder": "11",
                "totalAmount": "10",
            },
        ),
        ("amend_swap_order", {"product_symbol": "BTC-USDT-SWAP", "quantity": "1"}),
        (
            "get_swap_position_history",
            {"product_symbol": "BTC-USDT-SWAP", "startTs": 1, "endTs": 8000000000},
        ),
        ("set_swap_asset_mode", {"assetMode": "invalid", "confirm": True}),
    ],
)
async def test_new_risk_controls_reject_invalid_input_before_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    """Invalid trading parameters fail locally in both public Python interfaces."""
    import importlib

    module = importlib.import_module(
        ("dcex.async_support." if mode == "async" else "dcex.") + "bingx.client"
    )
    client = module.Client(**_client_kwargs("http://127.0.0.1:1"))
    try:
        if mode == "async":
            await client.async_init()
        with pytest.raises(
            ValueError,
            match="(?i)(invalid|required|must|requires|outside|unsupported|expected|between|specify|limit)",
        ):
            if mode == "async":
                await getattr(client, method)(**kwargs)
            else:
                getattr(client, method)(**kwargs)
    finally:
        if mode == "async":
            await client.close()
        else:
            client.close()
