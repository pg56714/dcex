# ruff: noqa: D103
"""
Offline wire coverage for every Extended sync and async endpoint wrapper.

The generic endpoint suite replaces the transport with a fake and never reaches
the native dispatcher.  These tests drive each public wrapper through the real
Rust client against a local HTTP server and assert that the documented Extended
path (https://api.docs.extended.exchange/) and query arrive on the wire, that
private calls carry ``X-Api-Key``, and that pre-signed bodies are forwarded
verbatim.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from tests.unit.wire_expectations import EXPECTED_VERBS as _ALL_VERBS

EXPECTED_VERBS = _ALL_VERBS["extended"]

from dcex.async_support.extended.client import Client as AsyncClient
from dcex.extended.client import Client
from dcex.utils.errors import FailedRequestError
from tests.unit.native_http_helpers import _http_server

API_KEY = "extended-key"
STARK_PRIVATE_KEY = "0x1"
STARK_PUBLIC_KEY = "0x1ef15c18599971b7beced415a40f0c7deacfd9b0d1819e03d723d8bc943cfca"
VAULT = 4272448241247734333
RUST_DIR = (
    Path(__file__).resolve().parents[2] / "crates" / "dcex" / "src" / "exchanges" / "extended"
)
RUST_SOURCE = "\n".join(
    path.read_text(encoding="utf-8")
    for path in [*RUST_DIR.glob("*.rs"), *(RUST_DIR / "schemas").glob("*.json")]
)

# One payload that satisfies the market-config and fee lookups used while
# auto-signing orders, and is a valid ``status: OK`` body for every other call.
PAYLOAD: dict[str, Any] = {
    "status": "OK",
    "data": [
        {
            "name": "BTC-USD",
            "market": "BTC-USD",
            "makerFeeRate": "0.0001",
            "takerFeeRate": "0.00025",
            "l2Config": {
                "collateralId": "0x555344430000000000000000000000",
                "collateralResolution": 1000000,
                "syntheticId": "0x4254432d31300000000000000000000",
                "syntheticResolution": 100000000,
            },
        }
    ],
}


def _presigned_order(order_type: str = "LIMIT", time_in_force: str = "GTT") -> dict[str, Any]:
    return {
        "id": "order-1",
        "market": "BTC-USD",
        "type": order_type,
        "side": "BUY",
        "qty": "0.001",
        "price": "10000",
        "reduceOnly": False,
        "postOnly": False,
        "timeInForce": time_in_force,
        "expiryEpochMillis": int(time.time() * 1000) + 3_600_000,
        "fee": "0.00025",
        "nonce": "1",
        "selfTradeProtectionLevel": "ACCOUNT",
        "settlement": {
            "signature": {"r": "0x1", "s": "0x2"},
            "starkKey": "0x3",
            "collateralPosition": "4",
        },
    }


TRANSFER = {
    "fromAccount": 3004,
    "toAccount": 7349,
    "amount": "1000",
    "transferredAsset": "USD",
    "settlement": {
        "amount": 1000000000,
        "assetId": "0x1",
        "expirationTimestamp": 478932,
        "nonce": 758978120,
        "receiverPositionId": 104350,
        "receiverPublicKey": "0x2",
        "senderPositionId": 100005,
        "senderPublicKey": "0x2",
        "signature": {"r": "abc", "s": "def"},
    },
}

RFQ_ORDER = {**_presigned_order("MARKET", "IOC"), "market": "AAPL-USD", "rfqStartPrice": "199"}


@dataclass(frozen=True)
class WireCase:
    """One wrapper call and the request line target it must produce."""

    method: str
    kwargs: dict[str, Any]
    target: str
    private: bool
    body: dict[str, Any] | None = None

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return self.method


def pub(method: str, target: str, **kwargs: Any) -> WireCase:  # noqa: ANN401
    """Build a public wire case."""
    return WireCase(method, kwargs, target, private=False)


def priv(
    method: str,
    target: str,
    expect_body: dict[str, Any] | None = None,
    **kwargs: Any,  # noqa: ANN401
) -> WireCase:
    """Build a private wire case."""
    return WireCase(method, kwargs, target, private=True, body=expect_body)


PRESIGNED = _presigned_order()
WITHDRAWAL = {
    "accountId": "100006",
    "amount": "2",
    "chainId": "STRK",
    "asset": "USD",
    "settlement": {
        "recipient": "0x123",
        "positionId": 300006,
        "collateralId": "0x456",
        "amount": "2000000",
        "expiration": {"seconds": 1900000000},
        "salt": 93763903,
        "signature": {"r": "123", "s": "456"},
    },
}

CASES = [
    priv(
        "create_withdrawal_signed",
        "/api/v1/user/withdrawal",
        expect_body=WITHDRAWAL,
        body=WITHDRAWAL,
    ),
    priv("get_affiliate_data", "/api/v1/user/affiliate"),
    priv("get_referral_status", "/api/v1/user/referrals/status"),
    priv("get_referral_links", "/api/v1/user/referrals/links"),
    priv("get_referral_dashboard", "/api/v1/user/referrals/dashboard?period=WEEK", period="WEEK"),
    priv(
        "use_referral_code", "/api/v1/user/referrals/use", expect_body={"code": "TEST"}, code="TEST"
    ),
    priv(
        "create_referral_code",
        "/api/v1/user/referrals",
        expect_body={"id": "TEST", "isDefault": True, "hiddenAtUi": False},
        id="TEST",
        is_default=True,
        hidden_at_ui=False,
    ),
    priv(
        "update_referral_code",
        "/api/v1/user/referrals",
        expect_body={"id": "TEST", "isDefault": False, "hiddenAtUi": True},
        id="TEST",
        is_default=False,
        hidden_at_ui=True,
    ),
    priv("commit_bridge_quote", "/api/v1/user/bridge/quote?id=quote-1", quote_id="quote-1"),
    pub("get_vault_performance", "/api/v1/vault/public/performance?interval=WEEK", interval="WEEK"),
    pub("get_vault_summary", "/api/v1/vault/public/summary"),
    priv("get_earned_points", "/api/v1/user/rewards/earned"),
    priv("get_points_leaderboard_stats", "/api/v1/user/rewards/leaderboard/stats"),
    priv(
        "get_account_equity_history",
        "/api/v1/portfolio/charts/equities?accountId=1000&accountId=1001&interval=WEEK",
        account_id=[1000, 1001],
        interval="WEEK",
    ),
    priv(
        "get_account_pnl_history",
        "/api/v1/portfolio/charts/pnl?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&instrumentType=SPOT",
        account_id=[1000, 1001],
        interval="WEEK",
        pnl_type="TOTAL_PNL",
        instrument_type="SPOT",
    ),
    priv(
        "get_account_pnl_percentage_history",
        "/api/v1/portfolio/charts/pnl/percentage?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&priceMarket=BTC-USD&priceMarket=ETH-USD&instrumentType=SPOT",
        account_id=[1000, 1001],
        interval="WEEK",
        pnl_type="TOTAL_PNL",
        price_market=["BTC-USD", "ETH-USD"],
        instrument_type="SPOT",
    ),
    priv(
        "get_cumulative_account_pnl_history",
        "/api/v1/portfolio/charts/pnl/cumulative?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&instrumentType=SPOT",
        account_id=[1000, 1001],
        interval="WEEK",
        pnl_type="TOTAL_PNL",
        instrument_type="SPOT",
    ),
    priv(
        "get_cumulative_account_pnl_percentage_history",
        "/api/v1/portfolio/charts/pnl/cumulative/percentage?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&priceMarket=BTC-USD&priceMarket=ETH-USD&instrumentType=SPOT",
        account_id=[1000, 1001],
        interval="WEEK",
        pnl_type="TOTAL_PNL",
        price_market=["BTC-USD", "ETH-USD"],
        instrument_type="SPOT",
    ),
    priv(
        "get_account_vault_equity_history",
        "/api/v1/portfolio/charts/vault-equities?accountId=1000&accountId=1001&interval=WEEK",
        account_id=[1000, 1001],
        interval="WEEK",
    ),
    priv(
        "get_account_max_drawdown_history",
        "/api/v1/portfolio/charts/max-drawdown?accountId=1000&accountId=1001&interval=WEEK",
        account_id=[1000, 1001],
        interval="WEEK",
    ),
    priv(
        "get_account_funding_chart",
        "/api/v1/portfolio/charts/funding?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD",
        account_id=[1000, 1001],
        interval="WEEK",
        market=["BTC-USD", "ETH-USD"],
    ),
    priv(
        "get_account_portfolio_summary",
        "/api/v1/portfolio/accounts/summary?accountId=1000&accountId=1001&interval=WEEK&instrumentType=SPOT",
        account_id=[1000, 1001],
        interval="WEEK",
        instrument_type="SPOT",
    ),
    priv(
        "get_account_performance",
        "/api/v1/portfolio/accounts/performance?accountId=1000&accountId=1001&interval=WEEK&marketType=PERPS",
        account_id=[1000, 1001],
        interval="WEEK",
        market_type="PERPS",
    ),
    priv(
        "get_account_funding_stats",
        "/api/v1/portfolio/funding/stats?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD",
        account_id=[1000, 1001],
        interval="WEEK",
        market=["BTC-USD", "ETH-USD"],
    ),
    priv(
        "get_account_funding_history",
        "/api/v1/portfolio/funding/history?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD&cursor=1&limit=50",
        account_id=[1000, 1001],
        interval="WEEK",
        market=["BTC-USD", "ETH-USD"],
        cursor=1,
        limit=50,
    ),
    pub(
        "get_interest_rate_curves_history",
        "/api/v1/interest/info/rate-curves?interval=WEEK",
        interval="WEEK",
    ),
    pub(
        "get_latest_interest_rate_curve",
        "/api/v1/interest/info/latest-rate-curves",
    ),
    priv(
        "get_interest_key_metrics",
        "/api/v1/interest/key-metrics?accountId=1000&accountId=1001",
        account_id=[1000, 1001],
    ),
    priv(
        "get_interest_daily_metrics",
        "/api/v1/interest/daily-metrics?accountId=1000&accountId=1001&interval=WEEK",
        account_id=[1000, 1001],
        interval="WEEK",
    ),
    priv(
        "get_interest_payment_chart",
        "/api/v1/interest/payment-chart?accountId=1000&accountId=1001&interval=WEEK&bucket=DAILY",
        account_id=[1000, 1001],
        interval="WEEK",
        bucket="DAILY",
    ),
    priv(
        "get_interest_payments_history",
        "/api/v1/interest/payments?accountId=1000&accountId=1001&interval=WEEK",
        account_id=[1000, 1001],
        interval="WEEK",
    ),
    pub(
        "get_markets",
        "/api/v1/info/markets?market=BTC-USD&market=ETH-USD",
        market=["BTC-USD", "ETH-USD"],
    ),
    pub(
        "get_assets",
        "/api/v1/info/assets?asset=BTC&type=SPOT&collateral=false",
        asset="BTC",
        type="SPOT",
        collateral=False,
    ),
    pub("get_asset_index_price", "/api/v1/info/assets/BTC/price", asset="BTC"),
    pub("get_market_statistics", "/api/v1/info/markets/BTC-USD/stats", market="BTC-USD"),
    pub("get_order_book", "/api/v1/info/markets/BTC-USD/orderbook", market="BTC-USD"),
    pub("get_trades", "/api/v1/info/markets/BTC-USD/trades", market="BTC-USD"),
    pub(
        "get_candles",
        "/api/v1/info/candles/BTC-USD/mark-prices?interval=PT1M&limit=50&endTime=123",
        market="BTC-USD",
        interval="PT1M",
        candleType="mark-prices",
        limit=50,
        endTime=123,
    ),
    pub(
        "get_funding",
        "/api/v1/info/BTC-USD/funding?startTime=1&endTime=2&limit=3",
        market="BTC-USD",
        startTime=1,
        endTime=2,
        limit=3,
    ),
    pub(
        "get_open_interest",
        "/api/v1/info/BTC-USD/open-interests?interval=P1H&startTime=1&endTime=2",
        market="BTC-USD",
        interval="P1H",
        startTime=1,
        endTime=2,
    ),
    priv("get_account_details", "/api/v1/user/account/info"),
    priv("get_sub_accounts", "/api/v1/user/accounts"),
    priv("get_balance", "/api/v1/user/balance"),
    priv(
        "get_spot_balances", "/api/v1/user/spot/balances?accountId=1&accountId=2", accountId=[1, 2]
    ),
    priv(
        "get_asset_operations",
        "/api/v1/user/assetOperations?type=DEPOSIT&status=COMPLETED&limit=5",
        type="DEPOSIT",
        status="COMPLETED",
        limit=5,
    ),
    priv("submit_internal_transfer", "/api/v1/user/transfer", expect_body=TRANSFER, body=TRANSFER),
    priv("get_account_health", "/api/v1/portfolio/accounts/health?accountId=7", accountId=7),
    priv(
        "get_positions",
        "/api/v1/user/positions?market=BTC-USD&side=LONG",
        market="BTC-USD",
        side="LONG",
    ),
    priv(
        "get_positions_history",
        "/api/v1/user/positions/history?cursor=1&limit=2",
        cursor=1,
        limit=2,
    ),
    priv(
        "get_trades_history",
        "/api/v1/user/trades?market=BTC-USD&type=TRADE&side=BUY",
        market="BTC-USD",
        type="TRADE",
        side="BUY",
    ),
    priv(
        "get_funding_payments",
        "/api/v1/user/funding/history?market=BTC-USD&startTime=100",
        startTime=100,
        market="BTC-USD",
    ),
    priv("get_leverage", "/api/v1/user/leverage?market=BTC-USD", market="BTC-USD"),
    priv("get_fees", "/api/v1/user/fees?market=BTC-USD&builderId=5", market="BTC-USD", builderId=5),
    priv("get_rebates", "/api/v1/user/rebates/stats"),
    priv("get_builder_dashboard", "/api/v1/info/builder/dashboard"),
    priv("get_builder_trades", "/api/v1/builder/trades?cursor=1&limit=10", cursor=1, limit=10),
    priv("get_bridge_config", "/api/v1/user/bridge/config"),
    priv(
        "get_bridge_quote",
        "/api/v1/user/bridge/quote?chainIn=ARB&chainOut=STRK&amount=100",
        chainIn="ARB",
        chainOut="STRK",
        amount="100",
    ),
    priv(
        "get_open_orders",
        "/api/v1/user/orders?market=BTC-USD&type=TPSL",
        market="BTC-USD",
        type="TPSL",
    ),
    priv(
        "get_orders_history",
        "/api/v1/user/orders/history?id=1&id=2&sort=ID",
        id=[1, 2],
        sort="ID",
    ),
    priv("get_order", "/api/v1/user/orders/42", id=42),
    priv("get_order_by_external_id", "/api/v1/user/orders/external/cid-1", externalId="cid-1"),
    priv("get_order_by_external_id", "/api/v1/user/orders/external/cid-2", externalId="cid-2"),
    priv("place_order", "/api/v1/user/order", expect_body=PRESIGNED, body=PRESIGNED),
    priv("place_rfq_order", "/api/v1/user/order/rfq", expect_body=RFQ_ORDER, body=RFQ_ORDER),
    priv("cancel_order", "/api/v1/user/order/42", id=42),
    priv("cancel_order_by_external_id", "/api/v1/user/order?externalId=cid-1", externalId="cid-1"),
    priv(
        "mass_cancel",
        "/api/v1/user/order/massCancel",
        expect_body={"markets": ["BTC-USD"]},
        body={"markets": ["BTC-USD"]},
    ),
    priv("set_deadmanswitch", "/api/v1/user/deadmanswitch?countdownTime=60", countdownTime=60),
]

# Wrappers that auto-sign and therefore issue lookups before the final request.
SIGNING_METHODS = {"place_limit_order", "sign_create_order"}
# Wrappers sent with PATCH, which the shared recording server does not accept;
# they are covered by the dedicated tests at the end of this module.
PATCH_METHODS = {"update_leverage"}


def _client_kwargs(base_url: str) -> dict[str, Any]:
    return {
        "base_url": base_url,
        "api_key": API_KEY,
        "stark_private_key": STARK_PRIVATE_KEY,
        "stark_public_key": STARK_PUBLIC_KEY,
        "vault_number": VAULT,
        "preload_product_table": False,
    }


@pytest.fixture(scope="module")
def server() -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    """Share one recording server across the module to keep the suite fast."""
    with _http_server(PAYLOAD) as (base_url, received):
        yield base_url, received


def _drain(received: queue.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    while not received.empty():
        requests.append(received.get_nowait())
    return requests


def _fail_if_native_is_stale(method: str, error: Exception) -> None:
    if "unsupported Extended" not in str(error) or f'"{method}"' not in RUST_SOURCE:
        raise error
    pytest.fail(f"installed dcex._native predates Rust dispatch {method!r}; rebuild needed")


def _assert_request(case: WireCase, requests: list[dict[str, Any]]) -> None:
    assert len(requests) == 1, requests
    request = requests[0]
    from tests.unit.wire_contracts import assert_wire_contract
    assert_wire_contract("extended", case.method, request)
    assert request["method"] == EXPECTED_VERBS[case.method]
    assert request["path"] == case.target
    if case.method == "update_referral_code":
        assert request["method"] == "PUT"
    elif case.method in {"create_withdrawal_signed", "use_referral_code", "create_referral_code"}:
        assert request["method"] == "POST"
    if case.private:
        assert request.get("extended_x-api-key") == API_KEY
    if case.body is not None:
        assert json.loads(request["body"]) == case.body


def _wrapper_names() -> set[str]:
    names: set[str] = set()
    for base in Client.__mro__:
        module = getattr(base, "__module__", "")
        if (
            module.startswith("dcex.extended._")
            and module.endswith("_http")
            and "manager" not in module
        ):
            names.update(
                name
                for name, value in vars(base).items()
                if not name.startswith("_") and callable(value)
            )
    return names


def test_every_endpoint_wrapper_has_a_wire_case() -> None:
    covered = {case.method for case in CASES} | SIGNING_METHODS | PATCH_METHODS
    assert _wrapper_names() - covered == set()
    for name in covered:
        assert f'"{name}"' in RUST_SOURCE, name


@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_sync_wrapper_reaches_documented_route(
    case: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        result = getattr(client, case.method)(**case.kwargs)
    except (ValueError, FailedRequestError) as error:
        _fail_if_native_is_stale(case.method, error)
    finally:
        client.close()
    assert result == PAYLOAD
    _assert_request(case, _drain(received))


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
async def test_async_wrapper_reaches_documented_route(
    case: WireCase, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = AsyncClient(**_client_kwargs(base_url))
    await client.async_init()
    try:
        result = await getattr(client, case.method)(**case.kwargs)
    except (ValueError, FailedRequestError) as error:
        _fail_if_native_is_stale(case.method, error)
    finally:
        await client.close()
    assert result == PAYLOAD
    _assert_request(case, _drain(received))


def _order_kwargs() -> dict[str, Any]:
    return {"market": "BTC-USD", "side": "BUY", "qty": "0.001", "price": "10000", "nonce": 7}


def _assert_signed_order_flow(requests: list[dict[str, Any]], *, posted: bool) -> None:
    paths = [request["path"] for request in requests]
    expected = ["/api/v1/info/markets?market=BTC-USD", "/api/v1/user/fees?market=BTC-USD"]
    if posted:
        expected.append("/api/v1/user/order")
    assert paths == expected
    assert [request["method"] for request in requests] == (
        ["GET", "GET", "POST"] if posted else ["GET", "GET"]
    )
    if posted:
        order = json.loads(requests[-1]["body"])
        assert order["market"] == "BTC-USD"
        assert order["type"] == "LIMIT"
        assert order["timeInForce"] == "GTT"
        assert order["fee"] == "0.00025"
        assert order["nonce"] == "7"
        assert order["settlement"]["signature"]["r"].startswith("0x")


@pytest.mark.parametrize("method", ["place_limit_order", "place_order"])
def test_sync_auto_signed_order_fetches_market_and_fee(
    method: str, server: tuple[str, queue.Queue[dict[str, Any]]]
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        getattr(client, method)(**_order_kwargs())
    finally:
        client.close()
    _assert_signed_order_flow(_drain(received), posted=True)


@pytest.mark.asyncio
async def test_async_auto_signed_order_fetches_market_and_fee(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = AsyncClient(**_client_kwargs(base_url))
    await client.async_init()
    try:
        await client.place_limit_order(**_order_kwargs())
    finally:
        await client.close()
    _assert_signed_order_flow(_drain(received), posted=True)


def test_sign_create_order_does_not_post(server: tuple[str, queue.Queue[dict[str, Any]]]) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    try:
        signed = client.sign_create_order(**_order_kwargs())
    finally:
        client.close()
    _assert_signed_order_flow(_drain(received), posted=False)
    assert signed["order"]["side"] == "BUY"
    assert signed["orderHash"].startswith("0x")


@pytest.mark.asyncio
async def test_async_sign_create_order_does_not_post(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = AsyncClient(**_client_kwargs(base_url))
    await client.async_init()
    try:
        signed = await client.sign_create_order(**_order_kwargs(), fee="0.0005")
    finally:
        await client.close()
    paths = [request["path"] for request in _drain(received)]
    assert paths == ["/api/v1/info/markets?market=BTC-USD"]
    assert signed["order"]["fee"] == "0.0005"


def test_unsafe_requests_are_rejected_before_the_wire(
    server: tuple[str, queue.Queue[dict[str, Any]]],
) -> None:
    base_url, received = server
    _drain(received)
    client = Client(**_client_kwargs(base_url))
    errors = (ValueError, FailedRequestError)
    try:
        with pytest.raises(errors):
            client.place_limit_order(**_order_kwargs(), type_="MARKET")
        with pytest.raises(errors):
            client.place_limit_order(**_order_kwargs(), time_in_force="FOK")
        with pytest.raises(errors):
            client.place_order(body=_presigned_order("MARKET", "GTT"))
        with pytest.raises(errors):
            client.mass_cancel(body={})
        with pytest.raises(errors):
            client.get_candles(market="BTC-USD", interval="1m", limit=1)
        with pytest.raises(errors):
            client.get_order_by_external_id(externalId="../escape")
    finally:
        client.close()
    assert _drain(received) == []


@contextmanager
def _patch_server() -> Iterator[tuple[str, list[dict[str, Any]]]]:
    """Record PATCH requests, which the shared helper server does not handle."""
    received: list[dict[str, Any]] = []

    class Handler(BaseHTTPRequestHandler):
        def do_PATCH(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            received.append(
                {
                    "method": self.command,
                    "path": self.path,
                    "api_key": self.headers.get("X-Api-Key"),
                    "body": self.rfile.read(length).decode() if length else "",
                }
            )
            body = json.dumps({"status": "OK", "data": {"market": "BTC-USD", "leverage": "10"}})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, _format: str, *_args: object) -> None:
            return

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(
        target=httpd.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    try:
        host, port = httpd.server_address
        yield f"http://{host}:{port}", received
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=10)


def _assert_update_leverage(result: Any, received: list[dict[str, Any]]) -> None:  # noqa: ANN401
    assert result["data"]["leverage"] == "10"
    assert len(received) == 1, received
    request = received[0]
    assert request["method"] == "PATCH"
    assert request["path"] == "/api/v1/user/leverage"
    assert request["api_key"] == API_KEY
    assert json.loads(request["body"]) == {"market": "BTC-USD", "leverage": "10"}


def test_sync_update_leverage_patches_documented_body() -> None:
    with _patch_server() as (base_url, received):
        client = Client(**_client_kwargs(base_url))
        try:
            result = client.update_leverage(market="BTC-USD", leverage=10)
        except (ValueError, FailedRequestError) as error:
            _fail_if_native_is_stale("update_leverage", error)
        finally:
            client.close()
        _assert_update_leverage(result, received)


@pytest.mark.asyncio
async def test_async_update_leverage_patches_documented_body() -> None:
    with _patch_server() as (base_url, received):
        client = AsyncClient(**_client_kwargs(base_url))
        await client.async_init()
        try:
            result = await client.update_leverage(market="BTC-USD", leverage="10")
        except (ValueError, FailedRequestError) as error:
            _fail_if_native_is_stale("update_leverage", error)
        finally:
            await client.close()
        _assert_update_leverage(result, received)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("get_account_equity_history", {"account_id": [], "interval": "WEEK"}),
        ("get_account_equity_history", {"account_id": [1, -1], "interval": "WEEK"}),
        ("get_account_pnl_history", {"account_id": [1], "interval": "WEEK", "pnl_type": "INVALID"}),
        ("get_account_funding_history", {"account_id": [1], "interval": "WEEK", "limit": 501}),
        (
            "get_interest_payment_chart",
            {"account_id": [1], "interval": "WEEK", "bucket": "MONTHLY"},
        ),
    ],
)
async def test_new_risk_controls_reject_invalid_input_before_transport(
    method: str, kwargs: dict[str, Any], mode: str
) -> None:
    """Invalid trading parameters fail locally in both public Python interfaces."""
    import importlib

    module = importlib.import_module(
        ("dcex.async_support." if mode == "async" else "dcex.") + "extended.client"
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
