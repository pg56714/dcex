"""
Offline end-to-end route coverage for every Backpack Python wrapper.

Every public wrapper on the sync and async Backpack clients is called against a
local HTTP server through the real native transport. Each case asserts the HTTP
method and REST path from the official Backpack OpenAPI spec
(https://docs.backpack.exchange/), the resolved exchange symbol, and that
private endpoints carry the ED25519 signing headers. The shared generic wrapper
tests only use a fake native client, so they never check the wire route.
"""

# ruff: noqa: D103

from __future__ import annotations

import base64
import inspect
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit

import pytest

pytest.importorskip("dcex._native")

ROOT = Path(__file__).resolve().parents[2]
PERP = "BTC-USDC-SWAP"
SPOT = "BTC-USDC-SPOT"
RFQ = "AAPL.US-USDC-RFQ"
BORROW_POSITION = {"quantity": "1", "side": "Borrow", "symbol": "BTC"}
BORROW = base64.b64encode(b'{"quantity":"1","side":"Borrow","symbol":"BTC"}').decode()


@dataclass(frozen=True)
class Case:
    """One wrapper call and the HTTP request it must produce."""

    method_name: str
    kwargs: dict[str, Any]
    route: str
    query: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    signed: bool = True


CASES: tuple[Case, ...] = (
    Case(
        "submit_rfq_quote",
        {
            "rfq_id": "rfq-1",
            "bid_price": "100.000000000000000001",
            "ask_price": "101",
            "client_id": 17,
            "auto_lend": False,
            "auto_borrow_repay": True,
        },
        "POST /api/v1/rfq/quote",
        body={
            "rfqId": "rfq-1",
            "bidPrice": "100.000000000000000001",
            "askPrice": "101",
            "clientId": 17,
            "autoLend": False,
            "autoBorrowRepay": True,
        },
    ),
    Case(
        "create_withdrawal",
        {
            "address": "offline-address",
            "blockchain": "Solana",
            "symbol": "USDC",
            "quantity": "1.000000000000000001",
            "client_id": "offline-1",
            "two_factor_token": "fixture-token",
            "auto_borrow": False,
            "auto_lend_redeem": True,
            "recipient_information": {
                "withdrawal_address_id": 123,
                "withdrawal_purpose": "test",
                "sanctions_representation": True,
            },
        },
        "POST /wapi/v1/capital/withdrawals",
        body={
            "address": "offline-address",
            "blockchain": "Solana",
            "symbol": "USDC",
            "quantity": "1.000000000000000001",
            "clientId": "offline-1",
            "twoFactorToken": "fixture-token",
            "autoBorrow": False,
            "autoLendRedeem": True,
            "recipientInformation": {
                "withdrawal_address_id": 123,
                "withdrawal_purpose": "test",
                "sanctions_representation": True,
            },
        },
    ),
    Case(
        "execute_borrow_lend",
        {"quantity": "1", "side": "Borrow", "symbol": "BTC"},
        "POST /api/v1/borrowLend",
        body={"quantity": "1", "side": "Borrow", "symbol": "BTC"},
    ),
    Case("get_prediction_events", {}, "GET /api/v1/prediction", signed=False, query={}),
    Case("get_prediction_tags", {}, "GET /api/v1/prediction/tags", signed=False, query={}),
    Case("get_vaults", {}, "GET /api/v1/vaults", signed=False, query={}),
    Case(
        "vault_mint",
        {"vault_id": 1, "symbol": "USDC", "quantity": "1"},
        "POST /api/v1/vault/mint",
        signed=True,
        body={"vaultId": 1, "symbol": "USDC", "quantity": "1"},
    ),
    Case(
        "vault_redeem",
        {"vault_id": 1, "all": True},
        "POST /api/v1/vault/redeem",
        signed=True,
        body={"vaultId": 1},
    ),
    Case(
        "vault_redeem_cancel",
        {"vault_id": 1},
        "DELETE /api/v1/vault/redeem",
        signed=True,
        body={"vaultId": 1},
    ),
    Case(
        "get_vault_pending_redeems",
        {"vault_id": 1},
        "GET /api/v1/vault/redeems/pending",
        signed=True,
        query={"vaultId": "1"},
    ),
    Case("get_vault_nav", {}, "GET /api/v1/vault/nav", signed=True, query={}),
    Case(
        "get_vault_history",
        {"interval": "1d"},
        "GET /api/v1/vaults/history",
        signed=False,
        query={"interval": "1d"},
    ),
    Case(
        "create_strategy",
        {
            "product_symbol": "BTC-USDC-SWAP",
            "side": "Bid",
            "strategy_type": "Scheduled",
            "quantity": "1",
            "duration": 60000,
            "interval": 10000,
        },
        "POST /api/v1/strategy",
        body={
            "symbol": "BTC_USDC_PERP",
            "side": "Bid",
            "strategyType": "Scheduled",
            "quantity": "1",
            "duration": 60000,
            "interval": 10000,
        },
    ),
    Case(
        "get_open_strategy",
        {"product_symbol": "BTC-USDC-SWAP", "strategy_id": "100"},
        "GET /api/v1/strategy",
        query={"symbol": "BTC_USDC_PERP", "strategyId": "100"},
    ),
    Case(
        "cancel_strategy",
        {"product_symbol": "BTC-USDC-SWAP", "client_strategy_id": 7},
        "DELETE /api/v1/strategy",
        body={"symbol": "BTC_USDC_PERP", "clientStrategyId": 7},
    ),
    Case(
        "get_open_strategies",
        {"product_symbol": "BTC-USDC-SWAP", "strategy_type": "Scheduled"},
        "GET /api/v1/strategies",
        query={"symbol": "BTC_USDC_PERP", "strategyType": "Scheduled"},
    ),
    Case(
        "cancel_open_strategies",
        {"product_symbol": "BTC-USDC-SWAP"},
        "DELETE /api/v1/strategies",
        body={"symbol": "BTC_USDC_PERP"},
    ),
    Case(
        "get_strategy_history",
        {"limit": 10, "market_type": ["PERP"]},
        "GET /wapi/v1/history/strategies",
        query={"limit": "10", "marketType": "PERP"},
    ),
    # Public market data.
    Case("get_assets", {}, "GET /api/v1/assets", signed=False),
    Case("get_collateral", {}, "GET /api/v1/collateral", signed=False),
    Case("get_borrow_lend_markets", {}, "GET /api/v1/borrowLend/markets", signed=False),
    Case(
        "get_borrow_lend_market_history",
        {"interval": "1d", "symbol": "USDC"},
        "GET /api/v1/borrowLend/markets/history",
        query={"interval": "1d", "symbol": "USDC"},
        signed=False,
    ),
    Case("get_borrow_lend_apy", {}, "GET /api/v1/borrowLend/apy", signed=False),
    Case(
        "get_borrow_lend_liquidation_price",
        {"borrow": BORROW_POSITION},
        "GET /api/v1/borrowLend/position/liquidationPrice",
        query={"borrow": BORROW},
        signed=False,
    ),
    Case(
        "get_markets",
        {"marketType": "PERP"},
        "GET /api/v1/markets",
        query={"marketType": "PERP"},
        signed=False,
    ),
    Case(
        "get_market",
        {"product_symbol": PERP},
        "GET /api/v1/market",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case(
        "get_order_book_depth",
        {"product_symbol": SPOT},
        "GET /api/v1/depth",
        query={"symbol": "BTC_USDC"},
        signed=False,
    ),
    Case("get_market_sessions", {}, "GET /api/v1/market-sessions", signed=False),
    Case("get_market_holidays", {}, "GET /api/v1/market-holidays", signed=False),
    Case("get_securities", {}, "GET /api/v1/securities", signed=False),
    Case(
        "get_mark_prices",
        {"product_symbol": PERP},
        "GET /api/v1/markPrices",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case(
        "get_open_interest",
        {"product_symbol": PERP},
        "GET /api/v1/openInterest",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case(
        "get_funding_rates",
        {"product_symbol": PERP},
        "GET /api/v1/fundingRates",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case(
        "get_klines",
        {"product_symbol": PERP, "interval": "1m", "startTime": 1700000000},
        "GET /api/v1/klines",
        query={"symbol": "BTC_USDC_PERP", "interval": "1m", "startTime": "1700000000"},
        signed=False,
    ),
    Case(
        "get_ticker",
        {"product_symbol": PERP},
        "GET /api/v1/ticker",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case("get_tickers", {}, "GET /api/v1/tickers", signed=False),
    Case("get_status", {}, "GET /api/v1/status", signed=False),
    Case("ping", {}, "GET /api/v1/ping", signed=False),
    Case("get_time", {}, "GET /api/v1/time", signed=False),
    Case("get_wallets", {}, "GET /api/v1/wallets", signed=False),
    Case(
        "get_recent_trades",
        {"product_symbol": PERP},
        "GET /api/v1/trades",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    Case(
        "get_historical_trades",
        {"product_symbol": PERP},
        "GET /api/v1/trades/history",
        query={"symbol": "BTC_USDC_PERP"},
        signed=False,
    ),
    # Account.
    Case("get_account", {}, "GET /api/v1/account"),
    Case(
        "update_account",
        {"leverageLimit": "5", "autoLend": True, "autoRepayBorrows": False},
        "PATCH /api/v1/account",
        body={"leverageLimit": "5", "autoLend": True, "autoRepayBorrows": False},
    ),
    Case(
        "get_max_borrow_quantity",
        {"symbol": "USDC"},
        "GET /api/v1/account/limits/borrow",
        query={"symbol": "USDC"},
    ),
    Case(
        "get_max_order_quantity",
        {"symbol": "BTC_USDC_PERP", "side": "Bid"},
        "GET /api/v1/account/limits/order",
        query={"symbol": "BTC_USDC_PERP", "side": "Bid"},
    ),
    Case(
        "get_max_withdrawal_quantity",
        {"symbol": "USDC"},
        "GET /api/v1/account/limits/withdrawal",
        query={"symbol": "USDC"},
    ),
    # Borrow lend.
    Case("get_borrow_lend_positions", {}, "GET /api/v1/borrowLend/positions"),
    Case(
        "get_borrow_history",
        {"limit": 10},
        "GET /wapi/v1/history/borrowLend",
        query={"limit": "10"},
    ),
    Case(
        "get_interest_history",
        {"limit": 10},
        "GET /wapi/v1/history/interest",
        query={"limit": "10"},
    ),
    Case(
        "get_borrow_position_history",
        {"limit": 10},
        "GET /wapi/v1/history/borrowLend/positions",
        query={"limit": "10"},
    ),
    # Capital.
    Case("get_balances", {}, "GET /api/v1/capital"),
    Case(
        "convert_dust",
        {"symbol": "SOL"},
        "POST /api/v1/account/convertDust",
        body={"symbol": "SOL"},
    ),
    Case("get_private_collateral", {}, "GET /api/v1/capital/collateral"),
    Case(
        "get_deposits",
        {"limit": 10},
        "GET /wapi/v1/capital/deposits",
        query={"limit": "10"},
    ),
    Case(
        "get_deposit_address",
        {"blockchain": "Solana"},
        "GET /wapi/v1/capital/deposit/address",
        query={"blockchain": "Solana"},
    ),
    Case(
        "get_withdrawals",
        {"limit": 10},
        "GET /wapi/v1/capital/withdrawals",
        query={"limit": "10"},
    ),
    Case(
        "get_dust_conversion_history",
        {"limit": 10},
        "GET /wapi/v1/history/dust",
        query={"limit": "10"},
    ),
    Case(
        "get_settlement_history",
        {"limit": 10},
        "GET /wapi/v1/history/settlement",
        query={"limit": "10"},
    ),
    # Orders.
    Case(
        "get_open_order",
        {"product_symbol": PERP, "orderId": "111"},
        "GET /api/v1/order",
        query={"symbol": "BTC_USDC_PERP", "orderId": "111"},
    ),
    Case(
        "place_order",
        {
            "product_symbol": PERP,
            "side": "Bid",
            "orderType": "Limit",
            "quantity": "1",
            "price": "100",
        },
        "POST /api/v1/order",
        body={"symbol": "BTC_USDC_PERP", "side": "Bid", "orderType": "Limit", "price": "100"},
    ),
    Case(
        "place_market_order",
        {"product_symbol": PERP, "side": "Ask", "quantity": "1"},
        "POST /api/v1/order",
        body={"symbol": "BTC_USDC_PERP", "side": "Ask", "orderType": "Market"},
    ),
    Case(
        "place_limit_order",
        {"product_symbol": SPOT, "side": "Bid", "quantity": "1", "price": "100"},
        "POST /api/v1/order",
        body={"symbol": "BTC_USDC", "orderType": "Limit", "timeInForce": "GTC"},
    ),
    Case(
        "cancel_order",
        {"product_symbol": PERP, "orderId": "111"},
        "DELETE /api/v1/order",
        body={"symbol": "BTC_USDC_PERP", "orderId": "111"},
    ),
    Case(
        "place_batch_orders",
        {
            "orders": [
                {
                    "product_symbol": PERP,
                    "side": "Bid",
                    "orderType": "Limit",
                    "quantity": "1",
                    "price": "100",
                }
            ]
        },
        "POST /api/v1/orders",
    ),
    Case(
        "get_open_orders",
        {"product_symbol": PERP},
        "GET /api/v1/orders",
        query={"symbol": "BTC_USDC_PERP"},
    ),
    Case(
        "cancel_open_orders",
        {"product_symbol": PERP},
        "DELETE /api/v1/orders",
        body={"symbol": "BTC_USDC_PERP"},
    ),
    Case(
        "get_fill_history",
        {"limit": 10},
        "GET /wapi/v1/history/fills",
        query={"limit": "10"},
    ),
    Case(
        "get_order_history",
        {"limit": 10},
        "GET /wapi/v1/history/orders",
        query={"limit": "10"},
    ),
    # Positions.
    Case("get_open_positions", {}, "GET /api/v1/position"),
    Case(
        "get_funding_payments",
        {"limit": 10},
        "GET /wapi/v1/history/funding",
        query={"limit": "10"},
    ),
    Case(
        "get_position_history",
        {"limit": 10},
        "GET /wapi/v1/history/position",
        query={"limit": "10"},
    ),
    # RFQ.
    Case("get_rfqs", {}, "GET /api/v1/rfqs"),
    Case(
        "submit_rfq",
        {"product_symbol": RFQ, "side": "Bid", "quantity": "1"},
        "POST /api/v1/rfq",
        body={"symbol": "AAPL.US_USDC_RFQ", "side": "Bid", "quantity": "1"},
    ),
    Case(
        "accept_rfq_quote",
        {"quote_id": "q1", "rfq_id": "r1"},
        "POST /api/v1/rfq/accept",
        body={"quoteId": "q1", "rfqId": "r1"},
    ),
    Case(
        "refresh_rfq",
        {"rfq_id": "r1"},
        "POST /api/v1/rfq/refresh",
        body={"rfqId": "r1"},
    ),
    Case(
        "cancel_rfq",
        {"rfq_id": "r1"},
        "POST /api/v1/rfq/cancel",
        body={"rfqId": "r1"},
    ),
    Case(
        "get_rfq_history",
        {"limit": 10},
        "GET /wapi/v1/history/rfq",
        query={"limit": "10"},
    ),
    Case(
        "get_quote_history",
        {"limit": 10},
        "GET /wapi/v1/history/quote",
        query={"limit": "10"},
    ),
    Case(
        "get_rfq_fill_history",
        {"limit": 10},
        "GET /wapi/v1/history/rfq/fill",
        query={"limit": "10"},
    ),
    Case(
        "get_quote_fill_history",
        {"limit": 10},
        "GET /wapi/v1/history/quote/fill",
        query={"limit": "10"},
    ),
)

# get_rfq_constraints post-processes /api/v1/securities, so it needs a
# securities-shaped response rather than the generic `{}`.
SECURITIES = [{"asset": "AAPL.US", "sessions": [{"name": "Regular", "minQuantity": "1"}]}]


@contextmanager
def _capture_server(
    payload: object = None,
) -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    encoded = json.dumps({} if payload is None else payload).encode()

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            received.put(
                {
                    "method": self.command,
                    "path": self.path,
                    "headers": {key.lower(): value for key, value in self.headers.items()},
                    "body": self.rfile.read(length).decode() if length else "",
                }
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _handle  # noqa: N815

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "api_key": base64.b64encode(b"2" * 32).decode(),
        "api_secret": base64.b64encode(b"1" * 32).decode(),
        "base_url": base_url,
        "preload_product_table": False,
        "timeout": 5,
    }


def _fail_if_native_is_stale(exc: ValueError, case: Case) -> None:
    """Fail when the installed ``dcex._native`` build predates this dispatch name."""
    message = str(exc)
    if "unsupported Backpack" in message and "method" in message:
        pytest.fail(
            f"installed dcex._native does not know {case.method_name!r}; "
            "rebuild the extension (maturin develop) to exercise it"
        )
    raise exc


def _assert_request(case: Case, received: queue.Queue[dict[str, Any]]) -> None:
    request = received.get_nowait()
    assert received.empty(), f"{case.method_name} sent more than one request"
    method, path = case.route.split(" ", 1)
    parts = urlsplit(request["path"])
    assert (request["method"], parts.path) == (method, path)
    query = dict(parse_qsl(parts.query))
    for key, value in case.query.items():
        assert query.get(key) == value, f"{case.method_name} query {query!r}"
    if method != "GET":
        body = json.loads(request["body"])
        assert isinstance(body, dict | list)
        if isinstance(body, dict):
            assert "product_symbol" not in body
        for key, value in case.body.items():
            assert body.get(key) == value, f"{case.method_name} body {body!r}"
    headers = request["headers"]
    if case.signed:
        assert headers.get("x-api-key") == _client_kwargs("")["api_key"]
        assert len(base64.b64decode(headers["x-signature"])) == 64
        assert headers.get("x-timestamp")
        assert headers.get("x-window") == "5000"
        if case.method_name in {"create_withdrawal", "submit_rfq_quote"}:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

            assert json.loads(request["body"]) == case.body
            instruction = "withdraw" if case.method_name == "create_withdrawal" else "quoteSubmit"
            fields = {
                key: str(value).lower() if isinstance(value, bool) else str(value)
                for key, value in case.body.items()
                if key != "recipientInformation"
            }
            message = (
                f"instruction={instruction}&{urlencode(sorted(fields.items()))}"
                f"&timestamp={headers['x-timestamp']}&window=5000"
            )
            key = Ed25519PrivateKey.from_private_bytes(
                base64.b64decode(_client_kwargs("")["api_secret"])
            )
            key.public_key().verify(base64.b64decode(headers["x-signature"]), message.encode())
    else:
        assert "x-signature" not in headers


def _wrapper_names(mode: str) -> set[str]:
    base = ROOT / "dcex" / ("async_support" if mode == "async" else "") / "backpack"
    module = "dcex.async_support.backpack.client" if mode == "async" else "dcex.backpack.client"
    client_cls = __import__(module, fromlist=["Client"]).Client
    files = {str(path) for path in base.glob("_*_http.py") if path.name != "_http_manager.py"}
    return {
        name
        for name, member in inspect.getmembers(client_cls, inspect.isfunction)
        if not name.startswith("_")
        and name not in {"close", "async_init"}
        and inspect.getsourcefile(member) in files
    }


@pytest.mark.parametrize("mode", ["sync", "async"])
def test_every_backpack_wrapper_has_a_route_case(mode: str) -> None:
    covered = {case.method_name for case in CASES} | {"get_rfq_constraints"}
    missing = _wrapper_names(mode) - covered
    assert not missing, f"add route cases for: {sorted(missing)}"


@pytest.mark.parametrize("case", CASES, ids=[case.method_name for case in CASES])
def test_sync_backpack_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.backpack.client import Client

    with _capture_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            result = getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _fail_if_native_is_stale(exc, case)
        finally:
            client.close()
        assert result == {}
        _assert_request(case, received)


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[case.method_name for case in CASES])
async def test_async_backpack_wrapper_hits_documented_route(case: Case) -> None:
    from dcex.async_support.backpack.client import Client

    with _capture_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        await client.async_init()
        try:
            result = await getattr(client, case.method_name)(**case.kwargs)
        except ValueError as exc:
            _fail_if_native_is_stale(exc, case)
        finally:
            await client.close()
        assert result == {}
        _assert_request(case, received)


def test_sync_backpack_rfq_constraints_reads_securities_session() -> None:
    from dcex.backpack.client import Client

    with _capture_server(SECURITIES) as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            result = client.get_rfq_constraints(product_symbol=RFQ, session_name="Regular")
        finally:
            client.close()
    request = received.get_nowait()
    assert (request["method"], urlsplit(request["path"]).path) == ("GET", "/api/v1/securities")
    assert result["symbol"] == "AAPL.US_USDC_RFQ"
    assert result["session"]["minQuantity"] == "1"


@pytest.mark.asyncio
async def test_async_backpack_rfq_constraints_reads_securities_session() -> None:
    from dcex.async_support.backpack.client import Client

    with _capture_server(SECURITIES) as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        await client.async_init()
        try:
            result = await client.get_rfq_constraints(product_symbol=RFQ, session_name="Regular")
        finally:
            await client.close()
    request = received.get_nowait()
    assert (request["method"], urlsplit(request["path"]).path) == ("GET", "/api/v1/securities")
    assert result["asset"] == "AAPL.US"
    assert result["session"]["name"] == "Regular"


def test_get_funding_payments_has_no_undocumented_subaccount_id() -> None:
    from dcex.async_support.backpack.client import Client as AsyncClient
    from dcex.backpack.client import Client

    for client_cls in (Client, AsyncClient):
        assert "subaccountId" not in inspect.signature(client_cls.get_funding_payments).parameters


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        (
            "create_strategy",
            {"product_symbol": "BTC-USDC-SWAP", "side": "Ask", "duration": 61, "interval": 10},
        ),
        (
            "create_strategy",
            {
                "product_symbol": "BTC-USDC-SWAP",
                "side": "Ask",
                "post_only": True,
                "time_in_force": "IOC",
            },
        ),
        (
            "create_strategy",
            {"product_symbol": "BTC-USDC-SWAP", "side": "Ask", "client_strategy_id": 4294967296},
        ),
        ("create_strategy", {"product_symbol": "BTC-USDC-SWAP", "side": "Ask", "quantity": "NaN"}),
        ("cancel_strategy", {"product_symbol": "BTC-USDC-SWAP"}),
    ],
)
async def test_new_risk_controls_reject_invalid_input_before_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    """Invalid trading parameters fail locally in both public Python interfaces."""
    import importlib

    module = importlib.import_module(
        ("dcex.async_support." if mode == "async" else "dcex.") + "backpack.client"
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
