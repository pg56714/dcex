"""
Offline route coverage for every Bitget REST wrapper (sync and async).

Each public wrapper method is called through the real Python client, the PyO3
bridge and the Rust dispatcher against a local HTTP server; the recorded HTTP
method and path must match the official Bitget API docs.
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
WRAPPER_FILES = ("_account_http.py", "_earn_http.py", "_market_http.py", "_trade_http.py")

PLACE_SPOT = ("POST", "/api/v2/spot/trade/place-order")
PLACE_FUTURES = ("POST", "/api/v2/mix/order/place-order")

# Python wrapper name -> (HTTP method, documented path).
ROUTES: dict[str, tuple[str, str]] = {
    # Classic spot market data.
    "get_spot_coins": ("GET", "/api/v2/spot/public/coins"),
    "get_spot_symbols": ("GET", "/api/v2/spot/public/symbols"),
    "get_spot_tickers": ("GET", "/api/v2/spot/market/tickers"),
    "get_spot_orderbook": ("GET", "/api/v2/spot/market/orderbook"),
    "get_spot_kline": ("GET", "/api/v2/spot/market/candles"),
    "get_spot_history_kline": ("GET", "/api/v2/spot/market/history-candles"),
    "get_spot_recent_trades": ("GET", "/api/v2/spot/market/fills"),
    "get_spot_market_trades": ("GET", "/api/v2/spot/market/fills-history"),
    # Classic futures market data.
    "get_futures_contracts": ("GET", "/api/v2/mix/market/contracts"),
    "get_futures_ticker": ("GET", "/api/v2/mix/market/ticker"),
    "get_futures_tickers": ("GET", "/api/v2/mix/market/tickers"),
    "get_futures_orderbook": ("GET", "/api/v2/mix/market/merge-depth"),
    "get_futures_kline": ("GET", "/api/v2/mix/market/candles"),
    "get_futures_history_kline": ("GET", "/api/v2/mix/market/history-candles"),
    "get_futures_recent_trades": ("GET", "/api/v2/mix/market/fills"),
    "get_futures_current_funding_rate": ("GET", "/api/v2/mix/market/current-fund-rate"),
    "get_futures_history_funding_rate": ("GET", "/api/v2/mix/market/history-fund-rate"),
    "get_futures_open_interest": ("GET", "/api/v2/mix/market/open-interest"),
    # UTA / Reality market data.
    "get_uta_instruments": ("GET", "/api/v3/market/instruments"),
    "get_uta_tickers": ("GET", "/api/v3/market/tickers"),
    "get_uta_orderbook": ("GET", "/api/v3/market/orderbook"),
    "get_uta_public_fills": ("GET", "/api/v3/market/fills"),
    "get_uta_kline": ("GET", "/api/v3/market/candles"),
    "get_uta_history_kline": ("GET", "/api/v3/market/history-candles"),
    "get_uta_liquidations": ("GET", "/api/v3/market/liquidations"),
    "get_reality_stock_info": ("GET", "/api/v3/reality/market/stock-info"),
    "get_reality_market_states": ("GET", "/api/v3/reality/market/states"),
    "get_reality_market_calendar": ("GET", "/api/v3/reality/market/calendar"),
    # Account, fees and transfers.
    "get_spot_fee_rates": ("GET", "/api/v2/common/trade-rate"),
    "get_futures_fee_rates": ("GET", "/api/v2/common/trade-rate"),
    "get_all_account_balance": ("GET", "/api/v2/account/all-account-balance"),
    "get_funding_assets": ("GET", "/api/v2/account/funding-assets"),
    "get_spot_account_info": ("GET", "/api/v2/spot/account/info"),
    "get_spot_account_assets": ("GET", "/api/v2/spot/account/assets"),
    "get_spot_account_bills": ("GET", "/api/v2/spot/account/bills"),
    "transfer": ("POST", "/api/v2/spot/wallet/transfer"),
    "get_transfer_records": ("GET", "/api/v2/spot/account/transferRecords"),
    "get_transferable_coins": ("GET", "/api/v2/spot/wallet/transfer-coin-info"),
    "get_deposit_records": ("GET", "/api/v2/spot/wallet/deposit-records"),
    "get_uta_account_assets": ("GET", "/api/v3/account/assets"),
    "get_reality_orderbook": ("GET", "/api/v3/account/reality-orderbook"),
    "get_reality_fills": ("GET", "/api/v3/account/reality-fills"),
    "get_uta_account_info": ("GET", "/api/v3/account/info"),
    "get_uta_all_fee_rates": ("GET", "/api/v3/account/all-fee-rate"),
    "get_uta_loan_data": ("GET", "/api/v3/trade/loan-data"),
    "get_uta_collateral_type": ("GET", "/api/v3/account/collateral-type"),
    "get_uta_custom_collateral_coins": ("GET", "/api/v3/account/custom-collateral-coins"),
    "get_uta_pre_set_leverage": ("GET", "/api/v3/account/pre-set-leverage"),
    "set_uta_leverage": ("POST", "/api/v3/account/set-leverage"),
    "set_uta_hold_mode": ("POST", "/api/v3/account/set-hold-mode"),
    "get_futures_account": ("GET", "/api/v2/mix/account/account"),
    "get_futures_accounts": ("GET", "/api/v2/mix/account/accounts"),
    "get_futures_account_bills": ("GET", "/api/v2/mix/account/bill"),
    "set_futures_leverage": ("POST", "/api/v2/mix/account/set-leverage"),
    "set_futures_margin_mode": ("POST", "/api/v2/mix/account/set-margin-mode"),
    "set_futures_position_mode": ("POST", "/api/v2/mix/account/set-position-mode"),
    "get_futures_positions": ("GET", "/api/v2/mix/position/all-position"),
    "get_futures_position": ("GET", "/api/v2/mix/position/single-position"),
    # Crypto loans / UTA liability.
    "get_crypto_loan_coins": ("GET", "/api/v3/loan/coins"),
    "get_crypto_loan_interest": ("GET", "/api/v3/loan/interest"),
    "borrow_crypto_loan": ("POST", "/api/v3/loan/borrow"),
    "get_crypto_loan_ongoing": ("GET", "/api/v3/loan/borrow-ongoing"),
    "get_crypto_loan_borrow_history": ("GET", "/api/v3/loan/borrow-history"),
    "repay_crypto_loan": ("POST", "/api/v3/loan/repay"),
    "get_crypto_loan_repay_history": ("GET", "/api/v3/loan/repay-history"),
    "revise_crypto_loan_pledge": ("POST", "/api/v3/loan/revise-pledge"),
    "get_crypto_loan_pledge_history": ("GET", "/api/v3/loan/pledge-rate-history"),
    "get_crypto_loan_liquidations": ("GET", "/api/v3/loan/reduces"),
    "get_crypto_loan_debts": ("GET", "/api/v3/loan/debts"),
    "repay_uta_liability": ("POST", "/api/v3/account/repay"),
    # Earn.
    "get_earn_account_assets": ("GET", "/api/v2/earn/account/assets"),
    "get_savings_account": ("GET", "/api/v2/earn/savings/account"),
    "get_savings_products": ("GET", "/api/v2/earn/savings/product"),
    "get_savings_assets": ("GET", "/api/v2/earn/savings/assets"),
    "get_savings_records": ("GET", "/api/v2/earn/savings/records"),
    "get_savings_subscription_info": ("GET", "/api/v2/earn/savings/subscribe-info"),
    "subscribe_savings": ("POST", "/api/v2/earn/savings/subscribe"),
    "get_savings_subscription_result": ("GET", "/api/v2/earn/savings/subscribe-result"),
    "redeem_savings": ("POST", "/api/v2/earn/savings/redeem"),
    "get_savings_redemption_result": ("GET", "/api/v2/earn/savings/redeem-result"),
    "get_elite_earn_products": ("GET", "/api/v3/earn/elite-product"),
    "get_elite_earn_subscription_info": ("GET", "/api/v3/earn/elite-subscribe-info"),
    "subscribe_elite_earn": ("POST", "/api/v3/earn/elite-subscribe"),
    "get_elite_earn_subscription_result": ("GET", "/api/v3/earn/elite-subscribe-result"),
    "get_elite_earn_redemption_info": ("GET", "/api/v3/earn/elite-redeem-info"),
    "redeem_elite_earn": ("POST", "/api/v3/earn/elite-redeem"),
    "get_elite_earn_assets": ("GET", "/api/v3/earn/elite-assets"),
    "get_elite_earn_records": ("GET", "/api/v3/earn/elite-records"),
    # Classic spot trading.
    "place_spot_order": PLACE_SPOT,
    "place_spot_market_order": PLACE_SPOT,
    "place_spot_market_buy_order": PLACE_SPOT,
    "place_spot_market_sell_order": PLACE_SPOT,
    "place_spot_limit_order": PLACE_SPOT,
    "place_spot_limit_buy_order": PLACE_SPOT,
    "place_spot_limit_sell_order": PLACE_SPOT,
    "place_spot_post_only_limit_order": PLACE_SPOT,
    "place_spot_post_only_limit_buy_order": PLACE_SPOT,
    "place_spot_post_only_limit_sell_order": PLACE_SPOT,
    "place_spot_batch_orders": ("POST", "/api/v2/spot/trade/batch-orders"),
    "cancel_spot_order": ("POST", "/api/v2/spot/trade/cancel-order"),
    "cancel_spot_batch_orders": ("POST", "/api/v2/spot/trade/batch-cancel-order"),
    "get_spot_order": ("GET", "/api/v2/spot/trade/orderInfo"),
    "get_spot_open_orders": ("GET", "/api/v2/spot/trade/unfilled-orders"),
    "get_spot_history_orders": ("GET", "/api/v2/spot/trade/history-orders"),
    "get_spot_fills": ("GET", "/api/v2/spot/trade/fills"),
    # UTA trading.
    "place_uta_order": ("POST", "/api/v3/trade/place-order"),
    "place_reality_order": ("POST", "/api/v3/trade/place-reality-order"),
    "place_uta_batch_orders": ("POST", "/api/v3/trade/place-batch"),
    "cancel_uta_order": ("POST", "/api/v3/trade/cancel-order"),
    "cancel_reality_order": ("POST", "/api/v3/trade/cancel-reality-order"),
    "cancel_uta_batch_orders": ("POST", "/api/v3/trade/cancel-batch"),
    "get_uta_order": ("GET", "/api/v3/trade/order-info"),
    "get_uta_open_orders": ("GET", "/api/v3/trade/unfilled-orders"),
    "get_uta_history_orders": ("GET", "/api/v3/trade/history-orders"),
    "get_uta_fills": ("GET", "/api/v3/trade/fills"),
    "get_uta_positions": ("GET", "/api/v3/position/current-position"),
    "place_uta_strategy_order": ("POST", "/api/v3/trade/place-strategy-order"),
    "modify_uta_strategy_order": ("POST", "/api/v3/trade/modify-strategy-order"),
    "cancel_uta_strategy_order": ("POST", "/api/v3/trade/cancel-strategy-order"),
    "get_uta_unfilled_strategy_orders": ("GET", "/api/v3/trade/unfilled-strategy-orders"),
    "get_uta_history_strategy_orders": ("GET", "/api/v3/trade/history-strategy-orders"),
    # Classic futures trading.
    "place_futures_order": PLACE_FUTURES,
    "place_futures_market_order": PLACE_FUTURES,
    "place_futures_market_buy_order": PLACE_FUTURES,
    "place_futures_market_sell_order": PLACE_FUTURES,
    "place_futures_limit_order": PLACE_FUTURES,
    "place_futures_limit_buy_order": PLACE_FUTURES,
    "place_futures_limit_sell_order": PLACE_FUTURES,
    "place_futures_post_only_limit_order": PLACE_FUTURES,
    "place_futures_post_only_limit_buy_order": PLACE_FUTURES,
    "place_futures_post_only_limit_sell_order": PLACE_FUTURES,
    "place_futures_batch_orders": ("POST", "/api/v2/mix/order/batch-place-order"),
    "cancel_futures_order": ("POST", "/api/v2/mix/order/cancel-order"),
    "cancel_futures_batch_orders": ("POST", "/api/v2/mix/order/batch-cancel-orders"),
    "get_futures_order": ("GET", "/api/v2/mix/order/detail"),
    "get_futures_open_orders": ("GET", "/api/v2/mix/order/orders-pending"),
    "get_futures_history_orders": ("GET", "/api/v2/mix/order/orders-history"),
    "get_futures_fills": ("GET", "/api/v2/mix/order/fills"),
}

PUBLIC_METHODS = {
    name
    for name in ROUTES
    if name.startswith(("get_spot_", "get_futures_", "get_uta_", "get_reality_"))
    and name
    not in {
        "get_spot_fee_rates",
        "get_futures_fee_rates",
        "get_spot_account_info",
        "get_spot_account_assets",
        "get_spot_account_bills",
        "get_spot_order",
        "get_spot_open_orders",
        "get_spot_history_orders",
        "get_spot_fills",
        "get_futures_account",
        "get_futures_accounts",
        "get_futures_account_bills",
        "get_futures_positions",
        "get_futures_position",
        "get_futures_order",
        "get_futures_open_orders",
        "get_futures_history_orders",
        "get_futures_fills",
        "get_uta_account_assets",
        "get_uta_account_info",
        "get_uta_all_fee_rates",
        "get_uta_loan_data",
        "get_uta_collateral_type",
        "get_uta_custom_collateral_coins",
        "get_uta_pre_set_leverage",
        "get_uta_order",
        "get_uta_open_orders",
        "get_uta_history_orders",
        "get_uta_fills",
        "get_uta_positions",
        "get_uta_unfilled_strategy_orders",
        "get_uta_history_strategy_orders",
        "get_reality_orderbook",
        "get_reality_fills",
    }
}

# Sample values for required wrapper parameters, keyed by parameter name.
VALUES: dict[str, Any] = {
    "product_symbol": "BTC-USDT-SWAP",
    "category": "USDT-FUTURES",
    "side": "buy",
    "orderType": "limit",
    "size": "1",
    "qty": "1",
    "price": "1",
    "granularity": "1min",
    "interval": "1m",
    "marginMode": "crossed",
    "orderList": [{"size": "1", "side": "buy", "orderType": "limit"}],
    "coin": "USDT",
    "amount": "1",
    "fromType": "spot",
    "toType": "usdt_futures",
    "startTime": 1690000000000,
    "endTime": 1700000000000,
    "leverage": "5",
    "posMode": "one_way_mode",
    "holdMode": "one_way_mode",
    "productId": "p1",
    "periodType": "flexible",
    "productSubId": "s1",
    "redeemType": "standard",
    "receiveAccount": "spot",
    "type": "interest",
    "loanCoin": "USDT",
    "pledgeCoin": "BTC",
    "daily": "SEVEN",
    "pledgeAmount": "1",
    "orderId": "1",
    "repayAll": "yes",
    "reviseType": "IN",
    "repayableCoinList": ["USDT"],
    "paymentCoinList": ["USDT"],
}

# Optional parameters that the documented endpoint requires.
EXTRA: dict[str, dict[str, Any]] = {
    "get_spot_order": {"orderId": "1"},
    "cancel_spot_order": {"orderId": "1"},
    "get_uta_order": {"orderId": "1"},
    "cancel_uta_order": {"orderId": "1"},
    "get_futures_order": {"orderId": "1"},
    "cancel_futures_order": {"orderId": "1"},
    "cancel_reality_order": {"orderId": "1"},
    "cancel_uta_strategy_order": {"orderId": "1"},
    "modify_uta_strategy_order": {"orderId": "1"},
    "place_spot_order": {"force": "gtc"},
    "set_futures_leverage": {"leverage": "5"},
    "borrow_crypto_loan": {"pledgeAmount": "1"},
}


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    names: set[str] = set()
    for filename in WRAPPER_FILES:
        tree = ast.parse((base / "bitget" / filename).read_text(encoding="utf-8"))
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
        body = self.rfile.read(length).decode() if length else ""
        split = urlsplit(self.path)
        self.received.put(
            {
                "method": self.command,
                "path": split.path,
                "query": dict(parse_qsl(split.query)),
                "body": body,
                "signed": bool(self.headers.get("ACCESS-SIGN")),
            }
        )
        payload = json.dumps({"code": "00000", "msg": "success", "data": {}}).encode()
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
        "passphrase": "passphrase",
        "base_url": base_url,
        "preload_product_table": False,
    }


def _kwargs(method: Any, name: str) -> dict[str, Any]:  # noqa: ANN401
    kwargs: dict[str, Any] = {}
    for parameter in inspect.signature(method).parameters.values():
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is inspect.Parameter.empty:
            if parameter.name not in VALUES:
                raise AssertionError(f"{name}: no sample value for {parameter.name}")
            kwargs[parameter.name] = VALUES[parameter.name]
    kwargs.update(EXTRA.get(name, {}))
    return kwargs


def _drain(received: "queue.Queue[dict[str, Any]]") -> None:
    while not received.empty():
        received.get_nowait()


def _assert_route(name: str, request: dict[str, Any]) -> None:
    method, path = ROUTES[name]
    assert (request["method"], request["path"]) == (method, path), name
    assert request["signed"] is (name not in PUBLIC_METHODS), name
    if method == "GET":
        assert request["body"] == "", name
    else:
        json.loads(request["body"])


def test_route_table_matches_python_surface() -> None:
    """Every sync/async wrapper (including Earn, outside the generic suffix list) is mapped."""
    sync_names = _wrapper_names("sync")
    async_names = _wrapper_names("async")
    assert sync_names == async_names
    assert sync_names == set(ROUTES)


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_sync_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Sync wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    method = getattr(client, name)
    result = method(**_kwargs(method, name))
    assert result["code"] == "00000"
    _assert_route(name, received.get(timeout=5))


@pytest.mark.parametrize("name", sorted(ROUTES))
def test_async_wrapper_reaches_documented_route(
    name: str, server: tuple[str, "queue.Queue[dict[str, Any]]"]
) -> None:
    """Async wrapper -> PyO3 -> Rust reaches the documented METHOD + path."""
    from dcex.async_support.bitget.client import Client

    base_url, received = server
    _drain(received)

    async def call() -> Any:  # noqa: ANN401
        async with Client(**_client_kwargs(base_url)) as client:
            method = getattr(client, name)
            return await method(**_kwargs(method, name))

    result = asyncio.run(call())
    assert result["code"] == "00000"
    _assert_route(name, received.get(timeout=5))


def test_sync_order_helpers_send_fixed_side_type_and_force(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Convenience helpers pin side/type/force and map canonical symbols."""
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    client.place_spot_post_only_limit_sell_order(
        product_symbol="BTC-USDT-SPOT", size="1", price="100"
    )
    body = json.loads(received.get(timeout=5)["body"])
    assert body["symbol"] == "BTCUSDT"
    assert (body["side"], body["orderType"], body["force"]) == ("sell", "limit", "post_only")

    client.place_futures_market_buy_order(product_symbol="ETH-USDT-SWAP", size="2")
    body = json.loads(received.get(timeout=5)["body"])
    assert body["symbol"] == "ETHUSDT"
    assert (body["side"], body["orderType"]) == ("buy", "market")
    assert body["productType"] == "USDT-FUTURES"

    client.get_futures_fee_rates(product_symbol="BTC-USDT-SWAP")
    request = received.get(timeout=5)
    assert request["query"] == {"symbol": "BTCUSDT", "businessType": "mix"}


def test_sync_client_error_surfaces_bitget_code(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Rust-side validation errors surface before any request is sent."""
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    with pytest.raises(Exception, match="between 1 and 100"):
        client.get_reality_fills(product_symbol="RAAPL-USDT-SPOT", limit=101)
    assert received.empty()


def test_python_validation_rejects_ambiguous_leverage_and_loan_calls(
    server: tuple[str, "queue.Queue[dict[str, Any]]"],
) -> None:
    """Leverage needs a value and crypto-loan borrow needs exactly one amount (sync + async)."""
    from dcex.async_support.bitget.client import Client as AsyncClient
    from dcex.bitget.client import Client

    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    loan = {"loanCoin": "USDT", "pledgeCoin": "BTC", "daily": "SEVEN"}
    with pytest.raises(ValueError, match="leverage, longLeverage, or shortLeverage"):
        client.set_futures_leverage(product_symbol="BTC-USDT-SWAP")
    for amounts in ({}, {"pledgeAmount": "1", "loanAmount": "1"}):
        with pytest.raises(ValueError, match="exactly one of pledgeAmount or loanAmount"):
            client.borrow_crypto_loan(**loan, **amounts)

    async def call_async() -> None:
        async with AsyncClient(**_client_kwargs(base_url)) as async_client:
            with pytest.raises(ValueError, match="leverage, longLeverage, or shortLeverage"):
                await async_client.set_futures_leverage(product_symbol="BTC-USDT-SWAP")
            for amounts in ({}, {"pledgeAmount": "1", "loanAmount": "1"}):
                with pytest.raises(ValueError, match="exactly one of pledgeAmount or loanAmount"):
                    await async_client.borrow_crypto_loan(**loan, **amounts)

    asyncio.run(call_async())
    assert received.empty()

    client.set_futures_leverage(product_symbol="BTC-USDT-SWAP", longLeverage="3")
    body = json.loads(received.get(timeout=5)["body"])
    assert body["longLeverage"] == "3"
    assert "leverage" not in body
