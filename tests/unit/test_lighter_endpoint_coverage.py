"""
Offline coverage for every Lighter sync and async HTTP wrapper.

Each case checks that the Python wrapper forwards the documented native method
name with the exact parameters, and then replays those parameters through the
real Rust client against a local HTTP server to confirm they reach the official
REST path (or, for signed transactions, the official ``sendTx`` tx_type).
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, Mock
from urllib.parse import parse_qsl, urlsplit

import pytest

from dcex.async_support.lighter.client import Client as AsyncClient
from dcex.lighter.client import Client
from tests.unit.native_http_helpers import _http_server

ACCOUNT = 12
API_KEY = 3
PRIVATE_KEY = "01" + "00" * 39
TOKEN = "test-token"
ORDER_DEFAULTS = [
    ("reduce_only", "false"),
    ("trigger_price", "0"),
    ("order_expiry", "-1"),
    ("integrator_account_index", "0"),
    ("integrator_taker_fee", "0"),
    ("integrator_maker_fee", "0"),
    ("self_trade_behavior_mode", "0"),
    ("self_trade_equality_mode", "0"),
    ("skip_nonce", "0"),
]
MODIFY_DEFAULTS = [
    ("trigger_price", "0"),
    ("integrator_account_index", "0"),
    ("integrator_taker_fee", "0"),
    ("integrator_maker_fee", "0"),
    ("self_trade_behavior_mode", "0"),
    ("self_trade_equality_mode", "0"),
    ("skip_nonce", "0"),
]
ORDER_ARGS = (1, 42, 1000, 250000, True, 0, 1)
ORDER_PARAMS = [
    ("market_index", "1"),
    ("client_order_index", "42"),
    ("base_amount", "1000"),
    ("price", "250000"),
    ("is_ask", "true"),
    ("order_type", "0"),
    ("time_in_force", "1"),
    *ORDER_DEFAULTS,
    ("nonce", "5"),
]
MODIFY_ARGS = (1, 99, 20, 101)
MODIFY_PARAMS = [
    ("market_index", "1"),
    ("order_index", "99"),
    ("base_amount", "20"),
    ("price", "101"),
    *MODIFY_DEFAULTS,
    ("nonce", "5"),
]


@dataclass(frozen=True)
class WrapperCase:
    """One wrapper call, its native dispatch, and the official route or tx_type."""

    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    kind: str
    params: list[tuple[str, str]]
    route: str | int

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return self.method


def _case(
    kind: str,
    method: str,
    args: tuple[Any, ...],
    params: list[tuple[str, str]],
    route: str | int,
    **kwargs: Any,  # noqa: ANN401
) -> WrapperCase:
    return WrapperCase(method, args, kwargs, kind, params, route)


def _series(market_id: int = 1, resolution: str = "1h") -> list[tuple[str, str]]:
    return [
        ("market_id", str(market_id)),
        ("resolution", resolution),
        ("start_timestamp", "1000"),
        ("end_timestamp", "2000"),
        ("count_back", "5"),
    ]


GROUP_ORDERS = [
    {
        "market_index": 1,
        "client_order_index": 100 + i,
        "base_amount": 1000,
        "price": 250000,
        "is_ask": True,
        "order_type": kind,
        "time_in_force": 0,
        "reduce_only": True,
        "trigger_price": trigger,
        "order_expiry": 1900000000000,
    }
    for i, (kind, trigger) in enumerate([(2, 240000), (4, 260000)])
]
GROUP_PARAMS = [
    ("grouping_type", "2"),
    *ORDER_DEFAULTS[3:],
    ("nonce", "5"),
    ("orders", json.dumps(GROUP_ORDERS, separators=(",", ":"))),
]

WRAPPER_CASES = [
    _case("private", "create_sub_account", (), [("skip_nonce", "0"), ("nonce", "5")], 9, nonce=5),
    _case("sign", "sign_create_sub_account", (), [("skip_nonce", "0"), ("nonce", "5")], 9, nonce=5),
    _case(
        "private",
        "change_api_key_signed",
        (
            "01000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "0x111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111b",
            5,
        ),
        [
            (
                "new_pubkey",
                "01000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
            (
                "l1_signature",
                "0x111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111b",
            ),
            ("nonce", "5"),
            ("skip_nonce", "0"),
        ],
        8,
    ),
    _case(
        "sign",
        "sign_change_api_key_signed",
        (
            "01000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "0x111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111b",
            5,
        ),
        [
            (
                "new_pubkey",
                "01000000000000000000000000000000000000000000000000000000000000000000000000000000",
            ),
            (
                "l1_signature",
                "0x111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111b",
            ),
            ("nonce", "5"),
            ("skip_nonce", "0"),
        ],
        8,
    ),
    _case(
        "private",
        "change_account_tier",
        (),
        [("account_index", "12"), ("new_tier", "premium"), ("authorization", "test-token")],
        "/api/v1/changeAccountTier",
        **{"account_index": 12, "new_tier": "premium", "authorization": "test-token"},
    ),
    _case(
        "private",
        "create_read_only_token",
        (),
        [
            ("name", "reporting"),
            ("account_index", "12"),
            ("expiry", "1800000000"),
            ("sub_account_access", "false"),
            ("authorization", "test-token"),
        ],
        "/api/v1/tokens/create",
        **{
            "name": "reporting",
            "account_index": 12,
            "expiry": 1800000000,
            "sub_account_access": False,
            "authorization": "test-token",
        },
    ),
    _case(
        "private",
        "revoke_read_only_token",
        (),
        [("token_id", "1"), ("account_index", "12"), ("authorization", "test-token")],
        "/api/v1/tokens/revoke",
        **{"token_id": 1, "account_index": 12, "authorization": "test-token"},
    ),
    _case(
        "public",
        "get_transaction",
        (),
        [("by", "hash"), ("value", "abc")],
        "/api/v1/tx",
        **{"by": "hash", "value": "abc"},
    ),
    _case(
        "public",
        "get_transaction_by_l1_hash",
        (),
        [("hash", "0x1111111111111111111111111111111111111111111111111111111111111111")],
        "/api/v1/txFromL1TxHash",
        **{"hash": "0x1111111111111111111111111111111111111111111111111111111111111111"},
    ),
    _case(
        "private",
        "acknowledge_notification",
        (),
        [("notif_id", "notification-1"), ("account_index", "12"), ("authorization", "test-token")],
        "/api/v1/notification/ack",
        **{"notif_id": "notification-1", "account_index": 12, "authorization": "test-token"},
    ),
    _case(
        "public",
        "create_deposit_intent_address",
        (),
        [
            ("chain_id", "42161"),
            ("from_addr", "0x2222222222222222222222222222222222222222"),
            ("amount", "1"),
        ],
        "/api/v1/createIntentAddress",
        **{
            "chain_id": "42161",
            "from_addr": "0x2222222222222222222222222222222222222222",
            "amount": "1",
        },
    ),
    _case(
        "public",
        "get_latest_deposit",
        (),
        [("l1_address", "0x2222222222222222222222222222222222222222")],
        "/api/v1/deposit/latest",
        **{"l1_address": "0x2222222222222222222222222222222222222222"},
    ),
    _case(
        "private",
        "update_account_config",
        (1,),
        [("account_trading_mode", "1"), ("skip_nonce", "0"), ("nonce", "5")],
        41,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_update_account_config",
        (1,),
        [("account_trading_mode", "1"), ("skip_nonce", "0"), ("nonce", "5")],
        41,
        nonce=5,
    ),
    _case(
        "private",
        "update_account_asset_config",
        (1, 1),
        [("asset_index", "1"), ("asset_margin_mode", "1"), ("skip_nonce", "0"), ("nonce", "5")],
        42,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_update_account_asset_config",
        (1, 1),
        [("asset_index", "1"), ("asset_margin_mode", "1"), ("skip_nonce", "0"), ("nonce", "5")],
        42,
        nonce=5,
    ),
    _case("sign", "sign_create_grouped_orders", (2, GROUP_ORDERS), GROUP_PARAMS, 28, nonce=5),
    _case("private", "create_grouped_orders", (2, GROUP_ORDERS), GROUP_PARAMS, 28, nonce=5),
    # Public market and account data.
    _case("public", "get_status", (), [], "/"),
    _case("public", "get_info", (), [], "/info"),
    _case("public", "get_announcement", (), [], "/api/v1/announcement"),
    _case("public", "get_system_config", (), [], "/api/v1/systemConfig"),
    _case("public", "get_layer1_basic_info", (), [], "/api/v1/layer1BasicInfo"),
    _case(
        "public",
        "get_order_book_details",
        (),
        [("market_id", "1"), ("filter", "perp")],
        "/api/v1/orderBookDetails",
        market_id=1,
        filter="perp",
    ),
    _case(
        "public", "get_order_books", (), [("filter", "spot")], "/api/v1/orderBooks", filter="spot"
    ),
    _case(
        "public",
        "get_order_book_orders",
        (1, 10),
        [("market_id", "1"), ("limit", "10")],
        "/api/v1/orderBookOrders",
    ),
    _case(
        "public",
        "get_recent_trades",
        (1, 10),
        [("market_id", "1"), ("limit", "10")],
        "/api/v1/recentTrades",
    ),
    _case(
        "public",
        "get_trades",
        ("timestamp", 10),
        [("sort_by", "timestamp"), ("limit", "10"), ("market_id", "1"), ("type_", "trade")],
        "/api/v1/trades",
        market_id=1,
        type_="trade",
    ),
    _case("public", "get_candles", (1, "1h", 1000, 2000, 5), _series(), "/api/v1/candles"),
    _case(
        "public",
        "get_mark_price_candles",
        (1, "1h", 1000, 2000, 5),
        _series(),
        "/api/v1/markPriceCandles",
    ),
    _case(
        "public",
        "get_market_price_charts",
        ([1, 2],),
        [("market_ids", "1"), ("market_ids", "2")],
        "/api/v1/marketPriceCharts",
    ),
    _case(
        "public",
        "get_synthetic_spot_info",
        ("AAPL",),
        [("symbol", "AAPL")],
        "/api/v1/syntheticSpotInfo",
    ),
    _case("public", "get_funding_rates", (), [], "/api/v1/funding-rates"),
    _case("public", "get_fundings", (1, "1h", 1000, 2000, 5), _series(), "/api/v1/fundings"),
    _case("public", "get_exchange_stats", (), [], "/api/v1/exchangeStats"),
    _case("public", "get_execute_stats", ("d",), [("period", "d")], "/api/v1/executeStats"),
    _case(
        "public",
        "get_exchange_metrics",
        ("d", "volume"),
        [("period", "d"), ("kind", "volume")],
        "/api/v1/exchangeMetrics",
    ),
    _case("public", "get_deposit_networks", (), [], "/api/v1/deposit/networks"),
    _case("public", "get_fastbridge_info", (), [], "/api/v1/fastbridge/info"),
    _case("public", "get_lease_options", (), [], "/api/v1/leaseOptions"),
    _case("public", "get_withdrawal_delay", (), [], "/api/v1/withdrawalDelay"),
    _case(
        "public",
        "get_account",
        ("index", "12"),
        [("by", "index"), ("value", "12")],
        "/api/v1/account",
    ),
    _case(
        "public",
        "get_accounts_by_l1_address",
        ("0xabc",),
        [("l1_address", "0xabc")],
        "/api/v1/accountsByL1Address",
    ),
    _case(
        "public",
        "get_account_metadata",
        ("index", "12"),
        [("by", "index"), ("value", "12"), ("authorization", TOKEN)],
        "/api/v1/accountMetadata",
        authorization=TOKEN,
    ),
    _case("public", "get_api_keys", (12,), [("account_index", "12")], "/api/v1/apikeys"),
    _case(
        "public",
        "get_public_pools_metadata",
        (0, 10),
        [("index", "0"), ("limit", "10")],
        "/api/v1/publicPoolsMetadata",
    ),
    _case(
        "public",
        "get_pnl",
        ("index", "12", "1h", 1000, 2000, 5),
        [
            ("by", "index"),
            ("value", "12"),
            ("resolution", "1h"),
            ("start_timestamp", "1000"),
            ("end_timestamp", "2000"),
            ("count_back", "5"),
        ],
        "/api/v1/pnl",
    ),
    _case(
        "public", "get_asset_details", (), [("asset_id", "1")], "/api/v1/assetDetails", asset_id=1
    ),
    _case("public", "get_tokens", (12,), [("account_index", "12")], "/api/v1/tokens"),
    _case("public", "get_token_list", (), [], "/api/v1/tokenlist"),
    # Authenticated account data.
    _case("private", "get_account_limits", (), [], "/api/v1/accountLimits"),
    _case(
        "private",
        "get_account_active_orders",
        (),
        [("market_id", "1")],
        "/api/v1/accountActiveOrders",
        market_id=1,
    ),
    _case(
        "private",
        "get_account_inactive_orders",
        (50,),
        [("limit", "50"), ("market_id", "1")],
        "/api/v1/accountInactiveOrders",
        market_id=1,
    ),
    _case(
        "private",
        "get_account_orders",
        ("1,2",),
        [("client_order_indexes", "1,2")],
        "/api/v1/accountOrders",
    ),
    _case(
        "private",
        "get_deposit_history",
        ("0xabc",),
        [("l1_address", "0xabc"), ("filter", "pending")],
        "/api/v1/deposit/history",
        filter="pending",
    ),
    _case(
        "private",
        "get_export",
        ("trade",),
        [("type_", "trade"), ("market_id", "1")],
        "/api/v1/export",
        market_id=1,
    ),
    _case("private", "get_fastwithdraw_info", (), [], "/api/v1/fastwithdraw/info"),
    _case(
        "private",
        "get_l1_metadata",
        ("0xabc",),
        [("l1_address", "0xabc")],
        "/api/v1/l1Metadata",
    ),
    _case("private", "get_liquidations", (10,), [("limit", "10")], "/api/v1/liquidations"),
    _case("private", "get_referral_points", (), [], "/api/v1/referral/points"),
    _case(
        "private",
        "get_referral_user_referrals",
        ("0xabc",),
        [("l1_address", "0xabc"), ("limit", "20")],
        "/api/v1/referral/userReferrals",
        limit=20,
    ),
    _case(
        "private",
        "get_transfer_history",
        (),
        [("type_", "L2Transfer"), ("type_", "L2BurnShares")],
        "/api/v1/transfer/history",
        type_=["L2Transfer", "L2BurnShares"],
    ),
    _case(
        "private",
        "get_transfer_fee_info",
        (),
        [("to_account_index", "13")],
        "/api/v1/transferFeeInfo",
        to_account_index=13,
    ),
    _case("private", "get_withdraw_history", (), [], "/api/v1/withdraw/history"),
    _case(
        "private",
        "get_position_funding",
        (10,),
        [("limit", "10"), ("side", "long")],
        "/api/v1/positionFunding",
        side="long",
    ),
    _case("private", "get_leases", (), [("limit", "10")], "/api/v1/leases", limit=10),
    _case(
        "private",
        "get_partner_stats",
        (),
        [("start_timestamp", "1000"), ("end_timestamp", "2000")],
        "/api/v1/partnerStats",
        start_timestamp=1000,
        end_timestamp=2000,
    ),
    _case("private", "get_maker_only_api_keys", (), [], "/api/v1/getMakerOnlyApiKeys"),
    _case("private", "get_next_nonce", (), [], "/api/v1/nextNonce"),
    # RFQ.
    _case(
        "private",
        "create_rfq",
        (1, 0),
        [("market_index", "1"), ("direction", "0"), ("base_amount", "0.1")],
        "/api/v1/rfq/create",
        base_amount="0.1",
    ),
    _case("private", "get_rfq", (10,), [("rfq_id", "10")], "/api/v1/rfq/get"),
    _case("private", "list_rfqs", (), [("limit", "20")], "/api/v1/rfq/list", limit=20),
    _case(
        "private",
        "update_rfq",
        (10, "CANCELED"),
        [("rfq_id", "10"), ("status", "CANCELED")],
        "/api/v1/rfq/update",
    ),
    # Raw and signed transactions.
    _case(
        "private",
        "send_tx",
        (14, '{"Nonce":1}'),
        [("tx_type", "14"), ("tx_info", '{"Nonce":1}'), ("price_protection", "false")],
        "/api/v1/sendTx",
        price_protection=False,
    ),
    _case(
        "private",
        "send_tx_batch",
        ("[14,15]", "[{},{}]"),
        [("tx_types", "[14,15]"), ("tx_infos", "[{},{}]")],
        "/api/v1/sendTxBatch",
    ),
    _case("private", "create_order", ORDER_ARGS, ORDER_PARAMS, 14, nonce=5),
    _case("private", "place_order", ORDER_ARGS, ORDER_PARAMS, 14, nonce=5),
    _case("sign", "sign_create_order", ORDER_ARGS, ORDER_PARAMS, 14, nonce=5),
    _case(
        "private",
        "cancel_order",
        (1, 99),
        [("market_index", "1"), ("order_index", "99"), ("skip_nonce", "0"), ("nonce", "5")],
        15,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_cancel_order",
        (1, 99),
        [("market_index", "1"), ("order_index", "99"), ("skip_nonce", "0"), ("nonce", "5")],
        15,
        nonce=5,
    ),
    _case("private", "modify_order", MODIFY_ARGS, MODIFY_PARAMS, 17, nonce=5),
    _case("sign", "sign_modify_order", MODIFY_ARGS, MODIFY_PARAMS, 17, nonce=5),
    _case(
        "private",
        "cancel_all_orders",
        (0, 0),
        [
            ("time_in_force", "0"),
            ("timestamp_ms", "0"),
            ("cancel_all_market_index", "255"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        16,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_cancel_all_orders",
        (1, 1900000000000),
        [
            ("time_in_force", "1"),
            ("timestamp_ms", "1900000000000"),
            ("cancel_all_market_index", "255"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        16,
        nonce=5,
    ),
    _case(
        "private",
        "update_leverage",
        (1, 500, 0),
        [
            ("market_index", "1"),
            ("fraction", "500"),
            ("margin_mode", "0"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        20,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_update_leverage",
        (1, 500, 1),
        [
            ("market_index", "1"),
            ("fraction", "500"),
            ("margin_mode", "1"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        20,
        nonce=5,
    ),
    _case(
        "private",
        "update_margin",
        (1, 1500000, 1),
        [
            ("market_index", "1"),
            ("usdc_amount", "1500000"),
            ("direction", "1"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        29,
        nonce=5,
    ),
    _case(
        "sign",
        "sign_update_margin",
        (1, -1500000, 0),
        [
            ("market_index", "1"),
            ("usdc_amount", "-1500000"),
            ("direction", "0"),
            ("skip_nonce", "0"),
            ("nonce", "5"),
        ],
        29,
        nonce=5,
    ),
]

# Wrappers that do not map to a single REST endpoint or signed transaction.
NON_ENDPOINT_METHODS = {"async_init", "check_client", "close", "create_auth_token", "from_env"}


def _public_methods(cls: type) -> set[str]:
    return {
        name
        for name, member in inspect.getmembers(cls, callable)
        if not name.startswith("_") and not inspect.isclass(member)
    } - NON_ENDPOINT_METHODS


def test_every_lighter_wrapper_has_a_coverage_case() -> None:
    """New sync or async wrappers must be added to this offline coverage table."""
    covered = {case.method for case in WRAPPER_CASES}
    assert _public_methods(Client) == covered
    assert _public_methods(AsyncClient) == covered


def _mocks(asynchronous: bool) -> dict[str, Mock]:
    factory = AsyncMock if asynchronous else Mock
    return {
        "public": factory(return_value={"ok": True}),
        "private": factory(return_value={"ok": True}),
        "sign": factory(return_value=(14, "{}", "00", None)),
    }


def _install(client: Any, mocks: dict[str, Mock]) -> None:  # noqa: ANN401
    client._native_public = mocks["public"]
    client._native_private = mocks["private"]
    client._native_sign = mocks["sign"]


@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
def test_sync_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Sync wrappers call the documented native dispatch name with exact params."""
    client = object.__new__(Client)
    mocks = _mocks(asynchronous=False)
    _install(client, mocks)
    getattr(client, case.method)(*case.args, **case.kwargs)
    native_name = "create_order" if case.method == "place_order" else case.method
    for kind, mock in mocks.items():
        if kind == case.kind:
            mock.assert_called_once_with(native_name, case.params)
        else:
            mock.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
async def test_async_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Async wrappers call the same native dispatch name with exact params."""
    client = object.__new__(AsyncClient)
    mocks = _mocks(asynchronous=True)
    _install(client, mocks)
    await getattr(client, case.method)(*case.args, **case.kwargs)
    native_name = "create_order" if case.method == "place_order" else case.method
    for kind, mock in mocks.items():
        if kind == case.kind:
            mock.assert_awaited_once_with(native_name, case.params)
        else:
            mock.assert_not_called()


def _signing_native(base_url: str) -> Any:  # noqa: ANN401
    native = pytest.importorskip("dcex._native")
    return native.LighterHttpClient(
        timeout=2,
        base_url=base_url,
        account_index=ACCOUNT,
        api_key_index=API_KEY,
        api_private_key=PRIVATE_KEY,
        chain_id=304,
    )


@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
def test_wrapper_params_reach_official_route(case: WrapperCase) -> None:
    """The Rust client accepts the wrapper params and emits the official route."""
    native_name = "create_order" if case.method == "place_order" else case.method
    if case.kind == "sign":
        tx_type, tx_info, tx_hash, error = _signing_native("http://127.0.0.1:1").sign_request(
            native_name, case.params
        )
        assert (tx_type, error) == (case.route, None)
        assert json.loads(tx_info)["Nonce"] == 5
        assert len(tx_hash) == 80
        return
    with _http_server({"code": 200, "nonce": 5}) as (base_url, received):
        client = _signing_native(base_url)
        request = (
            client.public_request_json if case.kind == "public" else client.private_request_json
        )
        request(native_name, case.params)
    requests = []
    while not received.empty():
        requests.append(received.get_nowait())
    assert len(requests) == 1
    url = urlsplit(requests[0]["path"])
    query = parse_qsl(url.query)
    assert not any(key in {"authorization", "product_symbol", "type_", "from_"} for key, _ in query)
    if isinstance(case.route, int):
        assert url.path == "/api/v1/sendTx"
        body = dict(parse_qsl(requests[0]["body"]))
        assert int(body["tx_type"]) == case.route
        info = json.loads(body["tx_info"])
        assert (info["AccountIndex"], info["ApiKeyIndex"], info["Nonce"]) == (ACCOUNT, API_KEY, 5)
        assert info["Sig"]
        return
    assert url.path == case.route


@pytest.mark.parametrize("market_index", [256, 2048, 4095, 32767])
def test_native_signing_accepts_market_ids_outside_legacy_ranges(market_index: int) -> None:
    """lighter-go allows market ids up to 32767 (255 is the nil sentinel); 4095 is live."""
    params = [(k, str(market_index) if k == "market_index" else v) for k, v in ORDER_PARAMS]
    tx_type, tx_info, _, error = _signing_native("http://127.0.0.1:1").sign_request(
        "sign_create_order", params
    )
    assert (tx_type, error) == (14, None)
    assert json.loads(tx_info)["MarketIndex"] == market_index


@pytest.mark.parametrize(("order_type", "time_in_force"), [(1, 0), (0, 0)])
def test_native_market_and_ioc_orders_default_to_zero_expiry(
    order_type: int, time_in_force: int
) -> None:
    """Market and IOC orders use expiry 0 by default, like lighter-python create_market_order."""
    overrides = {"order_type": str(order_type), "time_in_force": str(time_in_force)}
    params = [(k, overrides.get(k, v)) for k, v in ORDER_PARAMS]
    tx_type, tx_info, _, error = _signing_native("http://127.0.0.1:1").sign_request(
        "sign_create_order", params
    )
    assert (tx_type, error) == (14, None)
    assert json.loads(tx_info)["OrderExpiry"] == 0
