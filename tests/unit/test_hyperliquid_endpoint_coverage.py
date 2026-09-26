"""
Offline coverage for every Hyperliquid sync and async HTTP wrapper.

Each case checks that the Python wrapper forwards the documented native method
name with the exact camelCase parameters, and then replays those parameters
through the real Rust client against a local HTTP server to confirm the wire
request uses the official ``/info`` request type or ``/exchange`` action type.
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest

from dcex.async_support.hyperliquid.client import Client as AsyncClient
from dcex.hyperliquid.client import Client
from tests.unit.native_http_helpers import _http_server

USER = "0x" + "ab" * 20
WALLET = "0x" + "22" * 20
ETH = '["ETH",1]'
BTC = '["BTC",0]'
CLOID = "0x1234567890abcdef1234567890abcdef"
META = [{"universe": [{"name": "BTC", "szDecimals": 5}]}, [{"midPx": "100.0"}]]
SIGNATURE = {"r": "0x" + "11" * 32, "s": "0x" + "22" * 32, "v": 27}
BATCH_ORDERS = [
    {"product_symbol": ETH, "isBuy": True, "price": "2000", "size": "0.1", "tif": "Gtc"},
    {
        "product_symbol": ETH,
        "isBuy": False,
        "price": "2200",
        "size": "0.1",
        "reduceOnly": True,
        "isMarket": True,
        "triggerPx": "2200",
        "tpsl": "tp",
    },
]
BATCH_CANCELS = [{"product_symbol": ETH, "oid": 7}, {"product_symbol": BTC, "oid": 8}]
BATCH_CLOID_CANCELS = [{"product_symbol": ETH, "cloid": CLOID}]
MODIFIES = [
    {
        "oid": 42,
        "order": {
            "a": 1,
            "b": True,
            "p": "2000",
            "s": "0.1",
            "r": False,
            "t": {"limit": {"tif": "Gtc"}},
        },
    }
]


@dataclass(frozen=True)
class WrapperCase:
    """One wrapper call, its native dispatch, and the official wire type."""

    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    kind: str
    native_name: str
    params: list[tuple[str, str]]
    wire_type: str

    @property
    def id(self) -> str:
        """Return the pytest id for this case."""
        return f"{self.method}-{self.wire_type}"


def _info(
    method: str,
    args: tuple[Any, ...],
    params: list[tuple[str, str]],
    wire_type: str,
    **kwargs: Any,  # noqa: ANN401
) -> WrapperCase:
    return WrapperCase(method, args, kwargs, "public", method, params, wire_type)


def _action(
    method: str,
    args: tuple[Any, ...],
    params: list[tuple[str, str]],
    wire_type: str,
    **kwargs: Any,  # noqa: ANN401
) -> WrapperCase:
    return WrapperCase(method, args, kwargs, "private", method, params, wire_type)


WRAPPER_CASES = [
    _info("get_spot_fee_rates", (USER,), [("user", USER)], "userFees"),
    _info("get_futures_fee_rates", (USER,), [("user", USER)], "userFees"),
    _info("get_meta", (), [("dex", "xyz")], "meta", dex="xyz"),
    _info("get_perp_dexs", (), [], "perpDexs"),
    _info("get_spot_meta", (), [], "spotMeta"),
    _info("get_meta_and_asset_ctxs", (), [], "metaAndAssetCtxs"),
    _info("get_spot_meta_and_asset_ctxs", (), [], "spotMetaAndAssetCtxs"),
    _info(
        "get_l2book",
        ("BTC",),
        [("product_symbol", "BTC"), ("nSigFigs", "5"), ("mantissa", "2")],
        "l2Book",
        nSigFigs=5,
        mantissa=2,
    ),
    _info(
        "get_candle_snapshot",
        ("BTC", "1h", 1000, 2000),
        [
            ("product_symbol", "BTC"),
            ("interval", "1h"),
            ("startTime", "1000"),
            ("endTime", "2000"),
        ],
        "candleSnapshot",
    ),
    _info(
        "get_funding_rate_history",
        ("BTC", 1000, 2000),
        [("product_symbol", "BTC"), ("startTime", "1000"), ("endTime", "2000")],
        "fundingHistory",
    ),
    _info(
        "clearinghouse_state",
        (USER,),
        [("user", USER), ("dex", "xyz")],
        "clearinghouseState",
        dex="xyz",
    ),
    _info("spot_clearinghouse_state", (USER,), [("user", USER)], "spotClearinghouseState"),
    _info("open_orders", (USER,), [("user", USER), ("dex", "xyz")], "openOrders", dex="xyz"),
    _info("user_fills", (USER,), [("user", USER), ("aggregateByTime", "false")], "userFills"),
    _info(
        "user_fills_by_time",
        (USER, 1000, 2000, True),
        [("user", USER), ("startTime", "1000"), ("endTime", "2000"), ("aggregateByTime", "true")],
        "userFillsByTime",
    ),
    _info(
        "user_funding",
        (USER, 1000, 2000),
        [("user", USER), ("startTime", "1000"), ("endTime", "2000")],
        "userFunding",
    ),
    _info(
        "user_non_funding_ledger_updates",
        (USER, 1000),
        [("user", USER), ("startTime", "1000")],
        "userNonFundingLedgerUpdates",
    ),
    _info("user_rate_limit", (USER,), [("user", USER)], "userRateLimit"),
    _info("order_status", (USER, 42), [("user", USER), ("oid", "42")], "orderStatus"),
    _info("historical_orders", (USER,), [("user", USER)], "historicalOrders"),
    _info("subaccounts", (USER,), [("user", USER)], "subAccounts"),
    _info("user_role", (USER,), [("user", USER)], "userRole"),
    _info("portfolio", (USER,), [("user", USER)], "portfolio"),
    _info("user_vault_equities", (USER,), [("user", USER)], "userVaultEquities"),
    _action(
        "transfer_between_dexes",
        ("", "xyz", "USDC", "1.5"),
        [("sourceDex", ""), ("destinationDex", "xyz"), ("token", "USDC"), ("amount", "1.5")],
        "agentSendAsset",
    ),
    _action(
        "place_order",
        (ETH, True, "2000", "0.1", False),
        [
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("price", "2000"),
            ("size", "0.1"),
            ("reduceOnly", "false"),
            ("tif", "Gtc"),
            ("cloid", CLOID),
            ("grouping", "na"),
            ("expiresAfter", "1700000001000"),
        ],
        "order",
        tif="Gtc",
        cloid=CLOID,
        expiresAfter=1700000001000,
    ),
    _action(
        "place_future_market_order",
        (BTC, False, "0.01"),
        [
            ("product_symbol", BTC),
            ("isBuy", "false"),
            ("size", "0.01"),
            ("reduceOnly", "true"),
            ("slippage", "0.01"),
            ("grouping", "na"),
        ],
        "order",
        reduceOnly=True,
        slippage=0.01,
    ),
    _action(
        "place_future_market_buy_order",
        (BTC, "0.01"),
        [
            ("product_symbol", BTC),
            ("size", "0.01"),
            ("reduceOnly", "false"),
            ("slippage", "0.05"),
            ("grouping", "na"),
        ],
        "order",
    ),
    _action(
        "place_future_market_sell_order",
        (BTC, "0.01"),
        [
            ("product_symbol", BTC),
            ("size", "0.01"),
            ("triggerPx", "90"),
            ("tpsl", "sl"),
            ("reduceOnly", "true"),
            ("slippage", "0.05"),
            ("grouping", "na"),
        ],
        "order",
        triggerPx="90",
        tpsl="sl",
        reduceOnly=True,
    ),
    _action(
        "place_future_limit_order",
        (ETH, True, "2000", "0.1", "Alo"),
        [
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("price", "2000"),
            ("size", "0.1"),
            ("tif", "Alo"),
            ("grouping", "na"),
        ],
        "order",
    ),
    _action(
        "place_future_limit_buy_order",
        (ETH, "2000", "0.1", "Gtc"),
        [
            ("product_symbol", ETH),
            ("price", "2000"),
            ("size", "0.1"),
            ("tif", "Gtc"),
            ("grouping", "na"),
            ("builder_address", WALLET),
            ("fee_ten_bp", "10"),
        ],
        "order",
        builder_address=WALLET,
        fee_ten_bp=10,
    ),
    _action(
        "place_future_limit_sell_order",
        (ETH, "2100", "0.1", "Ioc"),
        [
            ("product_symbol", ETH),
            ("price", "2100"),
            ("size", "0.1"),
            ("tif", "Ioc"),
            ("grouping", "na"),
            ("vaultAddress", WALLET),
        ],
        "order",
        vaultAddress=WALLET,
    ),
    _action("cancel_order", (ETH, 7), [("product_symbol", ETH), ("oid", "7")], "cancel"),
    _action(
        "cancel_order_by_cloid",
        (ETH, CLOID),
        [("product_symbol", ETH), ("cloid", CLOID)],
        "cancelByCloid",
    ),
    _action(
        "place_batch_orders",
        (BATCH_ORDERS,),
        [("orders", json.dumps(BATCH_ORDERS, separators=(",", ":"))), ("grouping", "normalTpsl")],
        "order",
        grouping="normalTpsl",
    ),
    _action(
        "cancel_batch_orders",
        (BATCH_CANCELS,),
        [("cancels", json.dumps(BATCH_CANCELS, separators=(",", ":")))],
        "cancel",
    ),
    _action(
        "cancel_batch_orders_by_cloid",
        (BATCH_CLOID_CANCELS,),
        [("cancels", json.dumps(BATCH_CLOID_CANCELS, separators=(",", ":")))],
        "cancelByCloid",
    ),
    _action("schedule_cancel", (), [], "scheduleCancel"),
    _action(
        "modify_order",
        (7, ETH, True, "2000", "0.1", False),
        [
            ("oid", "7"),
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("price", "2000"),
            ("size", "0.1"),
            ("reduceOnly", "false"),
            ("tif", "Gtc"),
        ],
        "modify",
        tif="Gtc",
    ),
    _action(
        "modify_batch_orders",
        (MODIFIES,),
        [("modifies", json.dumps(MODIFIES, separators=(",", ":")))],
        "batchModify",
    ),
    _action(
        "update_leverage",
        (ETH, True, 5),
        [("product_symbol", ETH), ("isCross", "true"), ("leverage", "5")],
        "updateLeverage",
    ),
    _action(
        "update_isolate_margin",
        (ETH, True, 1000000),
        [("product_symbol", ETH), ("isBuy", "true"), ("ntli", "1000000")],
        "updateIsolatedMargin",
    ),
    _action(
        "update_isolated_margin",
        (ETH, True, 1000000),
        [("product_symbol", ETH), ("isBuy", "true"), ("ntli", "1000000")],
        "updateIsolatedMargin",
    ),
    _action(
        "place_twap_order",
        (ETH, True, "1", False, 30, True),
        [
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("size", "1"),
            ("reduceOnly", "false"),
            ("minutes", "30"),
            ("randomize", "true"),
        ],
        "twapOrder",
    ),
    _action(
        "cancel_twap_order",
        (ETH, 9),
        [("product_symbol", ETH), ("twap_id", "9")],
        "twapCancel",
    ),
    _action(
        "transfer_usdc_spot_perp",
        ("1", True, 1700000000000, SIGNATURE, "0xa4b1"),
        [
            ("amount", "1"),
            ("toPerp", "true"),
            ("nonce", "1700000000000"),
            ("signature", json.dumps(SIGNATURE, separators=(",", ":"))),
            ("signatureChainId", "0xa4b1"),
        ],
        "usdClassTransfer",
    ),
]

NON_ENDPOINT_METHODS = {"async_init", "close"}


def _public_methods(cls: type) -> set[str]:
    return {
        name
        for name, member in inspect.getmembers(cls, callable)
        if not name.startswith("_") and not inspect.isclass(member)
    } - NON_ENDPOINT_METHODS


def test_every_hyperliquid_wrapper_has_a_coverage_case() -> None:
    """New sync or async wrappers must be added to this offline coverage table."""
    covered = {case.method for case in WRAPPER_CASES}
    assert _public_methods(Client) == covered
    assert _public_methods(AsyncClient) == covered


def _sync_client() -> tuple[Client, Mock, Mock]:
    client = object.__new__(Client)
    public = Mock(return_value={"ok": True})
    private = Mock(return_value={"ok": True})
    client._native_public = public
    client._native_private = private
    return client, public, private


@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
def test_sync_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Sync wrappers call the documented native dispatch name with exact params."""
    client, public, private = _sync_client()
    result = getattr(client, case.method)(*case.args, **case.kwargs)
    assert result == {"ok": True}
    called, idle = (public, private) if case.kind == "public" else (private, public)
    called.assert_called_once_with(case.native_name, case.params)
    idle.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
async def test_async_wrapper_forwards_native_name_and_params(case: WrapperCase) -> None:
    """Async wrappers call the same native dispatch name with exact params."""
    client = object.__new__(AsyncClient)
    public = AsyncMock(return_value={"ok": True})
    private = AsyncMock(return_value={"ok": True})
    client._native_public = public
    client._native_private = private
    result = await getattr(client, case.method)(*case.args, **case.kwargs)
    assert result == {"ok": True}
    called, idle = (public, private) if case.kind == "public" else (private, public)
    called.assert_awaited_once_with(case.native_name, case.params)
    idle.assert_not_called()


@pytest.mark.parametrize("case", WRAPPER_CASES, ids=lambda case: case.id)
def test_wrapper_params_reach_official_wire_type(case: WrapperCase) -> None:
    """The Rust client accepts the wrapper params and emits the official request type."""
    native = pytest.importorskip("dcex._native")
    with _http_server(META) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address=WALLET,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        request = (
            client.public_request_json if case.kind == "public" else client.private_request_json
        )
        request(case.native_name, case.params)
    requests = []
    while not received.empty():
        requests.append(received.get_nowait())
    assert requests
    last = requests[-1]
    payload = json.loads(last["body"])
    if case.kind == "public":
        assert last["path"] == "/info"
        assert payload["type"] == case.wire_type
        return
    assert last["path"] == "/exchange"
    assert payload["action"]["type"] == case.wire_type
    if case.wire_type == "usdClassTransfer":
        assert payload["signature"] == SIGNATURE
        assert payload["action"]["nonce"] == payload["nonce"] == 1700000000000
        assert payload["action"]["hyperliquidChain"] == "Mainnet"
    else:
        assert payload["signature"]["v"] in {27, 28}
    if case.method.startswith("place_future_market"):
        assert [json.loads(item["body"]) for item in requests[:-1]] == [
            {"type": "metaAndAssetCtxs"}
        ]


@pytest.mark.parametrize(
    "method",
    [
        "place_order",
        "place_future_market_order",
        "place_future_market_buy_order",
        "place_future_limit_order",
        "place_future_limit_buy_order",
    ],
)
def test_builder_fee_requires_address_and_fee_together(method: str) -> None:
    """Every order wrapper that accepts a builder fee rejects half-specified builders."""
    client, _public, private = _sync_client()
    case = next(case for case in WRAPPER_CASES if case.method == method)
    kwargs = {key: value for key, value in case.kwargs.items() if key != "fee_ten_bp"}
    kwargs["builder_address"] = WALLET
    with pytest.raises(ValueError, match="builder_address and fee_ten_bp"):
        getattr(client, method)(*case.args, **kwargs)
    private.assert_not_called()


def test_native_batch_orders_carry_all_orders_and_grouping() -> None:
    """place_batch_orders sends one ``order`` action like the SDK's ``bulk_orders``."""
    native = pytest.importorskip("dcex._native")
    with _http_server({"status": "ok"}) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address=WALLET,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        client.private_request_json(
            "place_batch_orders",
            [("orders", json.dumps(BATCH_ORDERS)), ("grouping", "normalTpsl")],
        )
    action = json.loads(received.get_nowait()["body"])["action"]
    assert action["grouping"] == "normalTpsl"
    assert [order["t"] for order in action["orders"]] == [
        {"limit": {"tif": "Gtc"}},
        {"trigger": {"isMarket": True, "triggerPx": "2200", "tpsl": "tp"}},
    ]
    assert [order["r"] for order in action["orders"]] == [False, True]
