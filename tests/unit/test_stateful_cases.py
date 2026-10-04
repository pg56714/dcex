"""Offline IOC, FOK, reduce-only and amend order cases against real client signatures."""

import importlib
import inspect
from decimal import Decimal
from types import SimpleNamespace

import pytest

from tests.stateful_adapters import CexAdapter
from tests.stateful_arcus import ArcusAdapter
from tests.stateful_dex import ExtendedAdapter, HyperliquidAdapter, LighterAdapter, OndoAdapter
from tests.stateful_lifecycle import (
    CASES,
    TAKER_MAX_BID_FRACTION,
    LifecycleError,
    NotApplicable,
    OrderRejected,
    Plan,
    Rules,
    explicit_rejection,
    not_applicable,
    order_state,
    run_lifecycle,
)
from tests.stateful_reporting import RESULT_FIELDS, initial_result, update_report
from tests.stateful_runner import MARKETS, run_case
from tests.unit.test_stateful_adapters import EXCHANGES, ExchangeMock
from tests.unit.test_stateful_arcus import ArcusMock
from tests.unit.test_stateful_dex import DexMock

FILL_KEYS = {
    "executedQty",
    "cumExecQty",
    "accFillSz",
    "dealVol",
    "dealSize",
    "executedQuantity",
    "vol_exec",
    "filled",
}
ID_KEYS = {"orderId", "ordId", "id"}
AMEND_METHODS = {
    "cancel_replace_spot_order",
    "amend_futures_order",
    "modify_futures_order",
    "amend_order",
    "modify_uta_order",
    "replace_spot_order",
    "replace_swap_order",
    "amend_contract_limit_order",
    "alter_spot_order",
    "amend_spot_order",
    "edit_futures_order",
}
# Cancel-replace venues give the amended order a new ID.
REPLACING = {("binance", True), ("bingx", True), ("bingx", False), ("kucoin", True)}


def walk(value, keys, change):
    """Rewrite the named fields anywhere inside a mock response."""
    if isinstance(value, dict):
        return {
            key: change(item) if key in keys else walk(item, keys, change)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [walk(item, keys, change) for item in value]
    return value


class CaseMock(ExchangeMock):
    """ExchangeMock plus IOC kills, fills, reduce-only rejections and amendments."""

    def __init__(self, exchange, spot, mode, case):
        super().__init__(exchange, spot, mode)
        self.case = case
        self.fill = "0"
        self.place_fill = None
        self.reject = False
        self.replaced = False
        self.omit_new_id = False
        self.place_status = "placed"

    def requested(self, kw):
        for key in ("orderId", "ordId", "order_id", "txid"):
            if kw.get(key) is not None:
                return str(kw[key])
        if kw.get("orderIds"):
            return str(kw["orderIds"][0])
        return None

    def payload(self, method, kw):
        ex, spot = self.exchange, self.spot
        if method.startswith("place_"):
            if self.reject:
                error = RuntimeError("reduce-only order would not reduce a position")
                error.code = "110017"
                raise error
            data = super().payload(method, kw)
            if self.case in {"ioc", "fok"}:
                self.cancelled = True  # Killed unfilled: not open, nothing to cancel.
            if self.place_fill is not None and isinstance(data, dict):
                data = dict(data, executedQty=self.place_fill)
            if ex == "kraken" and not spot:
                data = {"sendStatus": dict(data["sendStatus"], status=self.place_status)}
            return data
        if method in AMEND_METHODS:
            old = self.price
            self.price = kw.get("price", kw.get("newPx", kw.get("newPrice")))
            self.price = self.price or kw.get("limit_price", kw.get("limitPrice"))
            assert self.price != old
            self.replaced = (ex, spot) in REPLACING
            new = "456" if self.replaced else "123"
            if self.omit_new_id:
                return {}
            return {
                "cancel_replace_spot_order": {
                    "cancelResult": "SUCCESS",
                    "newOrderResult": "SUCCESS",
                    "newOrderResponse": {"orderId": 456},
                },
                "replace_spot_order": {"orderOpenResponse": {"orderId": new}},
                "replace_swap_order": {"newOrderResponse": {"orderId": new}},
                "alter_spot_order": {"newOrderId": new},
                "amend_order": [{"ordId": new, "sCode": "0"}] if ex == "okx" else {"orderId": new},
                "amend_spot_order": {"amend_id": "fixture-amend"},
                "edit_futures_order": {"editStatus": {"status": "edited"}},
                "amend_contract_limit_order": new,
            }.get(method, {"orderId": new})
        requested = self.requested(kw)
        if self.replaced and requested == "123" and not method.startswith("cancel_"):
            # The replaced order: closed, at the original identity.
            saved = self.cancelled
            self.cancelled = True
            try:
                return super().payload(method, kw)
            finally:
                self.cancelled = saved
        data = super().payload(method, kw)
        if self.fill != "0":
            data = walk(data, FILL_KEYS, lambda value: self.fill if value == "0" else value)
        if self.replaced:
            data = walk(data, ID_KEYS, lambda value: "456" if str(value) == "123" else value)
        return data


def market(spot):
    return "spot" if spot else "swap"


def cex_adapter(client, exchange, spot):
    market = "spot" if spot else "swap"
    return CexAdapter(client, exchange, market, "BTC-USDT-" + ("SPOT" if spot else "SWAP"))


def place_kwargs(client):
    calls = [kw for name, kw in client.calls if name.startswith("place_")]
    assert len(calls) == 1
    return calls[0]


def tif_params(exchange, spot, tif):
    """The documented IOC/FOK parameter of each exchange's order endpoint."""
    if exchange in {"binance", "aster"}:
        return {"type_": "LIMIT", "timeInForce": tif}
    if exchange == "bybit":
        return {"orderType": "Limit", "timeInForce": tif}
    if exchange == "okx":
        return {"ordType": tif.lower()}
    if exchange == "bitget":
        return {"time_in_force": tif.lower()}
    if exchange == "bingx":
        return {"type_": "LIMIT", "time_in_force": tif}
    if exchange == "mexc":
        if spot:
            return {"type_": {"IOC": "IMMEDIATE_OR_CANCEL", "FOK": "FILL_OR_KILL"}[tif]}
        return {"type_": {"IOC": 3, "FOK": 4}[tif]}
    if exchange in {"kucoin", "backpack"}:
        return {"timeInForce": tif}
    if spot:
        return {"timeinforce": tif}
    return {"orderType": tif.lower()}


REDUCE_PARAMS = {
    "binance": {"reduceOnly": "true", "timeInForce": "GTX"},
    "aster": {"reduceOnly": True, "timeInForce": "GTX"},
    "bybit": {"reduceOnly": True, "timeInForce": "PostOnly"},
    "okx": {"reduceOnly": True, "ordType": "post_only"},
    "bitget": {"reduce_only": "yes", "time_in_force": "post_only"},
    "bingx": {"reduce_only": "true", "time_in_force": "PostOnly"},
    "mexc": {"side": 2, "type_": 2, "openType": 1},
    "kucoin": {"reduceOnly": True, "postOnly": True},
    "backpack": {"reduceOnly": True, "postOnly": True},
    "kraken": {"reduceOnly": True, "orderType": "post"},
}
AMEND_CALLS = {
    ("binance", True): (
        "cancel_replace_spot_order",
        {"cancel_replace_mode": "STOP_ON_FAILURE", "order_type": "LIMIT_MAKER"},
    ),
    ("binance", False): ("amend_futures_order", {"order_id": 123, "side": "BUY"}),
    ("aster", False): ("modify_futures_order", {"orderId": 123}),
    ("bybit", True): ("amend_order", {"orderId": "123"}),
    ("bybit", False): ("amend_order", {"orderId": "123"}),
    ("okx", True): ("amend_order", {"ordId": "123"}),
    ("okx", False): ("amend_order", {"ordId": "123"}),
    ("bitget", True): ("modify_uta_order", {"order_id": "123", "category": "SPOT"}),
    ("bitget", False): ("modify_uta_order", {"order_id": "123", "category": "USDT-FUTURES"}),
    ("bingx", True): ("replace_spot_order", {"cancel_order_id": 123, "time_in_force": "PostOnly"}),
    ("bingx", False): (
        "replace_swap_order",
        {"cancel_order_id": "123", "time_in_force": "PostOnly", "position_side": "BOTH"},
    ),
    ("mexc", False): ("amend_contract_limit_order", {"orderId": "123"}),
    ("kucoin", True): ("alter_spot_order", {"orderId": "123"}),
    ("kraken", True): ("amend_spot_order", {"txid": "123", "post_only": True}),
    ("kraken", False): ("edit_futures_order", {"orderId": "123"}),
}
CEX_MATRIX = [
    (exchange, spot, mode)
    for exchange in EXCHANGES
    for spot in (True, False)
    for mode in ("sync", "async")
]


def ids(params):
    exchange, spot, mode = params
    return f"{exchange}-{'spot' if spot else 'swap'}-{mode}"


@pytest.mark.parametrize("case", ["ioc", "fok"])
@pytest.mark.parametrize("params", CEX_MATRIX, ids=ids)
@pytest.mark.asyncio
async def test_cex_ioc_fok_send_exact_params_and_end_unfilled(params, case):
    exchange, spot, mode = params
    client = CaseMock(exchange, spot, mode, case)
    result = {}
    if not_applicable(exchange, market(spot), case):
        with pytest.raises(NotApplicable, match="N/A: " + exchange):
            await run_lifecycle(cex_adapter(client, exchange, spot), result, case=case)
        assert client.calls == [] and result["stage"] == "not_applicable"
        return
    await run_lifecycle(cex_adapter(client, exchange, spot), result, poll_delay=0, case=case)
    kw = place_kwargs(client)
    tif = case.upper()
    assert {key: kw.get(key) for key in tif_params(exchange, spot, tif)} == tif_params(
        exchange, spot, tif
    )
    # Never a maker/post-only flag on an IOC/FOK order, never reduce-only.
    assert not {"postOnly", "oflags", "reduceOnly", "reduce_only"} & set(kw)
    assert Decimal(kw.get("price", kw.get("px", kw.get("limitPrice")))) < 100
    assert result["stage"] == "complete" and result["case"] == case
    assert "with zero fill" in result["cleanup"]
    assert not any(name.startswith("cancel_") for name, _ in client.calls)


@pytest.mark.parametrize(
    "exchange,spot,case",
    [
        (exchange, spot, case)
        for exchange in EXCHANGES
        for spot in (True, False)
        for case in ("ioc", "fok")
        if not not_applicable(exchange, market(spot), case)
    ],
)
@pytest.mark.asyncio
async def test_cex_ioc_fok_fill_is_unexpected(exchange, spot, case):
    client = CaseMock(exchange, spot, "sync", case)
    client.fill = ".01"
    result = {}
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(cex_adapter(client, exchange, spot), result, poll_delay=0, case=case)
    assert result["stage"] == "query_final"
    assert sum(name.startswith("place_") for name, _ in client.calls) == 1


@pytest.mark.parametrize("case", ["ioc", "fok", "reduce_only", "lifecycle"])
@pytest.mark.asyncio
async def test_place_response_fill_is_unexpected(case):
    client = CaseMock("binance", False, "sync", case)
    client.place_fill = "0.01"
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(cex_adapter(client, "binance", False), {}, poll_delay=0, case=case)


@pytest.mark.asyncio
async def test_unqueryable_ioc_passes_only_with_zero_fill_in_place_response():
    client = CaseMock("binance", True, "sync", "ioc")
    client.place_fill = "0"
    adapter = cex_adapter(client, "binance", True)

    async def missing(identifier):
        return None

    adapter.order = missing
    result = {}
    await run_lifecycle(adapter, result, poll_delay=0, case="ioc")
    assert "not queryable; placement reported zero fill" in result["cleanup"]
    # Without a fill quantity in the placement response the same run fails closed.
    client = CaseMock("binance", True, "sync", "ioc")
    adapter = cex_adapter(client, "binance", True)
    adapter.order = missing
    with pytest.raises(LifecycleError, match="not found"):
        await run_lifecycle(adapter, {}, poll_delay=0, case="ioc")


@pytest.mark.asyncio
async def test_ioc_still_resting_fails_and_is_cancelled():
    client = CaseMock("bybit", False, "sync", "ioc")
    original = client.payload

    def payload(method, kw):
        data = original(method, kw)
        if method == "place_order":
            client.cancelled = False  # The venue left it resting: forbidden for IOC.
        return data

    client.payload = payload
    result = {}
    with pytest.raises(LifecycleError, match="still resting"):
        await run_lifecycle(cex_adapter(client, "bybit", False), result, poll_delay=0, case="ioc")
    assert [name for name, _ in client.calls if name.startswith("cancel_")] == ["cancel_order"]
    assert "cleanup cancellation acknowledged" in result["cleanup"]


@pytest.mark.parametrize(
    ("status", "outcome"),
    [("iocWouldNotExecute", "ended at placement unfilled"), ("filled", "UNEXPECTED FILL")],
)
@pytest.mark.asyncio
async def test_kraken_futures_ioc_send_status(status, outcome):
    client = CaseMock("kraken", False, "async", "ioc")
    client.place_status = status
    result = {}
    adapter = cex_adapter(client, "kraken", False)
    if outcome == "UNEXPECTED FILL":
        with pytest.raises(LifecycleError, match=outcome):
            await run_lifecycle(adapter, result, poll_delay=0, case="ioc")
        return
    await run_lifecycle(adapter, result, poll_delay=0, case="ioc")
    assert outcome in result["cleanup"] and not result.get("order_id")
    assert not any(name == "get_futures_order_status" for name, _ in client.calls)


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("rejected", [True, False], ids=["rejected", "accepted"])
@pytest.mark.asyncio
async def test_cex_reduce_only_rejected_or_cancelled_when_resting(exchange, mode, rejected):
    client = CaseMock(exchange, False, mode, "reduce_only")
    client.reject = rejected
    result = {}
    await run_lifecycle(
        cex_adapter(client, exchange, False), result, poll_delay=0, case="reduce_only"
    )
    kw = [kw for name, kw in client.calls if name.startswith("place_")][0]
    assert {key: kw.get(key) for key in REDUCE_PARAMS[exchange]} == REDUCE_PARAMS[exchange]
    assert result["stage"] == "complete"
    cancels = [name for name, _ in client.calls if name.startswith("cancel_")]
    if rejected:
        assert "reduce-only order rejected" in result["cleanup"] and cancels == []
        assert result["error_code"] == "110017"
    else:
        assert "accepted resting (pass with note)" in result["cleanup"] and len(cancels) == 1


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.asyncio
async def test_reduce_only_is_na_on_spot_without_any_call(exchange):
    client = CaseMock(exchange, True, "sync", "reduce_only")
    result = {}
    with pytest.raises(NotApplicable, match=f"N/A: {exchange} spot has no reduce-only"):
        await run_lifecycle(cex_adapter(client, exchange, True), result, case="reduce_only")
    assert client.calls == []


@pytest.mark.asyncio
async def test_reduce_only_ambiguous_error_is_not_a_pass():
    client = CaseMock("okx", False, "sync", "reduce_only")
    original = client.payload

    def payload(method, kw):
        if method == "place_order":
            raise TimeoutError("response timeout")
        return original(method, kw)

    client.payload = payload
    result = {}
    with pytest.raises(LifecycleError, match="timeout"):
        await run_lifecycle(
            cex_adapter(client, "okx", False), result, poll_delay=0, case="reduce_only"
        )
    assert "placement uncertain" in result["error_message"]


@pytest.mark.parametrize("params", CEX_MATRIX, ids=ids)
@pytest.mark.asyncio
async def test_cex_amend_moves_one_tick_and_tracks_ids(params):
    exchange, spot, mode = params
    client = CaseMock(exchange, spot, mode, "amend")
    result = {}
    adapter = cex_adapter(client, exchange, spot)
    if not_applicable(exchange, market(spot), "amend"):
        with pytest.raises(NotApplicable, match="has no order amendment"):
            await run_lifecycle(adapter, result, case="amend")
        assert client.calls == []
        return
    first_client_id = adapter.client_order_id
    await run_lifecycle(adapter, result, poll_delay=0, case="amend")
    method, expected = AMEND_CALLS[exchange, spot]
    calls = [kw for name, kw in client.calls if name == method]
    assert len(calls) == 1
    assert {key: calls[0].get(key) for key in expected} == expected
    placed = place_kwargs(client)
    assert Decimal(client.price) == Decimal(
        placed.get("price", placed.get("px", placed.get("limitPrice")))
    ) - Decimal(".1")
    assert result["price"] == "89.9" and result["stage"] == "complete"
    cancels = [
        kw for name, kw in client.calls if name.startswith("cancel_") and name not in AMEND_METHODS
    ]
    assert len(cancels) == 1
    if (exchange, spot) in REPLACING:
        assert result["order_id"] == "123->456"
        assert "456" in {str(value) for value in cancels[0].values()}
        assert adapter.client_order_id != first_client_id or exchange == "kucoin"
        assert result["prior_client_order_ids"].split(",")[-1] == adapter.client_order_id
    else:
        assert result["order_id"] == "123"


@pytest.mark.parametrize("spot", [True, False], ids=["spot", "swap"])
@pytest.mark.asyncio
async def test_bingx_replace_without_new_id_resolves_by_client_id(spot):
    client = CaseMock("bingx", spot, "sync", "amend")
    client.omit_new_id = True
    original = client.payload
    field = "clientOrderID" if spot else "clientOrderId"
    adapter = cex_adapter(client, "bingx", spot)

    def payload(method, kw):
        data = original(method, kw)
        if method in {"get_spot_open_orders", "get_open_orders"} and client.replaced:
            data = walk(
                data,
                {"orders"},
                lambda rows_: [dict(row, **{field: adapter.client_order_id}) for row in rows_],
            )
        return data

    client.payload = payload
    result = {}
    await run_lifecycle(adapter, result, poll_delay=0, case="amend")
    assert result["order_id"] == "123->456" and result["stage"] == "complete"


def failing_cancel_replace(confirm_cleanup):
    """Binance spot cancel-replace that times out after replacing the order under 456."""
    client = CaseMock("binance", True, "sync", "amend")
    original = client.payload
    adapter = cex_adapter(client, "binance", True)

    def payload(method, kw):
        if method == "cancel_replace_spot_order":
            assert adapter.held_client_ids == [kw["new_client_order_id"]]  # Recorded first.
            client.replaced = True
            client.price = kw["price"]
            raise TimeoutError("cancel-replace response timeout")
        if method == "cancel_order" and str(kw["orderId"]) == "123" and client.replaced:
            client.calls.append((method, kw))
            return {"code": -2011, "msg": "Unknown order sent."}
        if method == "cancel_order" and not confirm_cleanup:
            client.calls.append((method, kw))
            return {"code": -1003, "msg": "Too many requests."}
        data = original(method, kw)
        if method == "get_open_orders" and client.replaced:
            data = [dict(row, clientOrderId=adapter.held_client_ids[-1]) for row in data]
        return data

    client.payload = payload
    return client, adapter


@pytest.mark.asyncio
async def test_failed_cancel_replace_sweeps_every_held_id():
    client, adapter = failing_cancel_replace(confirm_cleanup=True)
    result = {}
    with pytest.raises(LifecycleError, match="timeout"):
        await run_lifecycle(adapter, result, poll_delay=0, case="amend")
    cancelled = [str(kw["orderId"]) for name, kw in client.calls if name == "cancel_order"]
    assert cancelled[0] == "123" and "456" in cancelled and set(cancelled) <= {"123", "456"}
    assert result["cleanup"].startswith("amend cleanup: every held order ID and client ID")


@pytest.mark.asyncio
async def test_unconfirmed_amend_cleanup_fails_loudly_with_every_id():
    client, adapter = failing_cancel_replace(confirm_cleanup=False)
    result = {}
    with pytest.raises(LifecycleError, match="AMEND CLEANUP UNCONFIRMED") as raised:
        await run_lifecycle(adapter, result, poll_delay=0, case="amend")
    message = str(raised.value)
    assert "timeout" in message and "123" in message and "456" in message
    assert adapter.held_client_ids[-1] in message and result["prior_client_order_ids"] in message


@pytest.mark.asyncio
async def test_amend_replaced_old_order_still_open_fails():
    client = CaseMock("kucoin", True, "sync", "amend")
    original = client.payload

    def payload(method, kw):
        if method == "get_spot_order" and kw.get("order_id") == "123" and client.replaced:
            client.replaced = False
            data = original(method, kw)  # The old ID still reported active.
            client.replaced = True
            return walk(data, {"price"}, lambda _: "90")
        return original(method, kw)

    client.payload = payload
    with pytest.raises(LifecycleError, match="still open after amendment"):
        await run_lifecycle(cex_adapter(client, "kucoin", True), {}, poll_delay=0, case="amend")


# DEX and Arcus fixtures ---------------------------------------------------------------


class DexCaseMock(DexMock):
    def __init__(self, exchange, mode, case):
        super().__init__(exchange, mode)
        self.case = case
        self.hl_status = None
        self.new_oid = 123
        self.client_index = None
        self.cloid = None

    def response(self, method, kw):
        ex = self.exchange
        if method in {"place_order", "place_limit_order", "create_order"}:
            data = super().response(method, kw)
            if ex == "hyperliquid" and self.hl_status is not None:
                self.placed = False
                data["response"]["data"]["statuses"] = [self.hl_status]
            elif self.case in {"ioc", "fok"}:
                self.cancelled = True
            return data
        if method == "modify_order":
            self.price = kw["price"] if ex == "hyperliquid" else str(kw["price"] / 10)
            if ex == "hyperliquid":
                self.new_oid = 456
                return {"status": "ok", "response": {"type": "default"}}
            return {}
        if ex == "hyperliquid" and method == "order_status":
            if not self.placed:
                return {"status": "unknownOid"}
            data = super().response(method, kw)
            if str(kw["oid"]) == "123" and self.new_oid == 456:
                data["order"]["status"] = "canceled"
            else:
                data["order"]["order"]["oid"] = self.new_oid
            return data
        if ex == "hyperliquid" and method == "open_orders":
            live = self.placed and not self.cancelled
            return [{"oid": self.new_oid, "cloid": self.cloid}] if live else []
        return super().response(method, kw)


def dex_adapter(client, adapter_type, exchange, market, symbol):
    adapter = adapter_type(client, exchange, market, symbol)
    client.cloid = adapter.client_order_id
    return adapter


DEX = [
    ("extended", ExtendedAdapter, "swap", "BTC-USD-SWAP"),
    ("ondo", OndoAdapter, "swap", "BTC-USD-SWAP"),
    ("hyperliquid", HyperliquidAdapter, "spot", "BTC-USDC-SPOT"),
    ("hyperliquid", HyperliquidAdapter, "swap", "BTC-USD-SWAP"),
    ("lighter", LighterAdapter, "mainnet", "ETH"),
    ("lighter", LighterAdapter, "robinhood", "ETH"),
]
PLACE = {"extended": "place_limit_order", "lighter": "create_order"}
DEX_IOC = {
    "extended": {"time_in_force": "IOC", "post_only": False},
    "ondo": {"timeInForce": "IOC"},
    "lighter": {"time_in_force": 0, "order_expiry": 0, "reduce_only": False},
}
DEX_REDUCE = {
    "extended": {"reduce_only": True, "post_only": True, "time_in_force": "GTT"},
    "ondo": {"reduceOnly": True, "postOnly": True, "timeInForce": "GTC"},
    "hyperliquid": {"reduceOnly": True, "tif": "Alo"},
    "lighter": {"reduce_only": True, "time_in_force": 2},
}


def dex_place(client, exchange):
    calls = [kw for name, kw in client.calls if name == PLACE.get(exchange, "place_order")]
    assert len(calls) == 1
    return calls[0]


@pytest.mark.parametrize("case", CASES[1:])
@pytest.mark.parametrize("exchange,adapter_type,market_,symbol", DEX)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_dex_cases(exchange, adapter_type, market_, symbol, mode, case):
    client = DexCaseMock(exchange, mode, case)
    adapter = dex_adapter(client, adapter_type, exchange, market_, symbol)
    result = {}
    if not_applicable(exchange, market_, case):
        with pytest.raises(NotApplicable, match="N/A: " + exchange):
            await run_lifecycle(adapter, result, case=case)
        assert client.calls == []
        return
    if exchange == "hyperliquid" and case == "ioc":
        client.hl_status = {"error": "Order could not immediately match against any resting"}
    await run_lifecycle(adapter, result, poll_delay=0, case=case)
    assert result["stage"] == "complete"
    kw = dex_place(client, exchange)
    if case == "ioc":
        expected = DEX_IOC.get(exchange, {"tif": "Ioc", "reduceOnly": False})
        assert {key: kw.get(key) for key in expected} == expected
        assert "postOnly" not in kw and not kw.get("post_only")
        assert "zero fill" in result["cleanup"] or "placement unfilled" in result["cleanup"]
    elif case == "reduce_only":
        expected = DEX_REDUCE[exchange]
        assert {key: kw.get(key) for key in expected} == expected
        assert "accepted resting" in result["cleanup"] and client.cancelled
    else:
        modify = [kw for name, kw in client.calls if name == "modify_order"]
        assert len(modify) == 1
        if exchange == "hyperliquid":
            assert modify[0]["tif"] == "Alo" and modify[0]["cloid"] == adapter.client_order_id
            assert result["order_id"] == "123->456"
        else:
            assert modify[0]["order_index"] == 123 and modify[0]["price"] == 899
            assert modify[0]["base_amount"] == int(Decimal(client.size) * 100)
        cancelled = [kw for name, kw in client.calls if name == "cancel_order"]
        assert len(cancelled) == 1
        assert cancelled[0].get("oid", cancelled[0].get("order_index")) == (
            456 if exchange == "hyperliquid" else 123
        )


@pytest.mark.parametrize(
    "status,match",
    [
        ({"filled": {"totalSz": "0.01", "avgPx": "90", "oid": 1}}, "UNEXPECTED FILL"),
        ({"error": "Order has invalid price."}, "invalid price"),
    ],
)
@pytest.mark.asyncio
async def test_hyperliquid_ioc_fill_or_other_rejection_fails(status, match):
    client = DexCaseMock("hyperliquid", "sync", "ioc")
    client.hl_status = status
    adapter = dex_adapter(client, HyperliquidAdapter, "hyperliquid", "swap", "BTC-USD-SWAP")
    with pytest.raises(LifecycleError, match=match):
        await run_lifecycle(adapter, {}, poll_delay=0, case="ioc")


@pytest.mark.asyncio
async def test_hyperliquid_reduce_only_rejection_passes():
    client = DexCaseMock("hyperliquid", "async", "reduce_only")
    client.hl_status = {"error": "Reduce only order would increase position."}
    adapter = dex_adapter(client, HyperliquidAdapter, "hyperliquid", "swap", "BTC-USD-SWAP")
    result = {}
    await run_lifecycle(adapter, result, poll_delay=0, case="reduce_only")
    assert "reduce-only order rejected" in result["cleanup"]
    assert not any(name == "cancel_order" for name, _ in client.calls)


@pytest.mark.parametrize("exchange,adapter_type,market_,symbol", DEX)
@pytest.mark.asyncio
async def test_dex_ioc_fill_is_unexpected(exchange, adapter_type, market_, symbol):
    client = DexCaseMock(exchange, "sync", "ioc")
    if exchange == "hyperliquid":
        client.hl_status = {"filled": {"totalSz": "0.01"}}
    client.fill = ".01"
    adapter = dex_adapter(client, adapter_type, exchange, market_, symbol)
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(adapter, {}, poll_delay=0, case="ioc")


class ArcusCaseMock(ArcusMock):
    def __init__(self, mode, case):
        super().__init__(mode)
        self.case = case
        self.reject_reduce = False

    def payload(self, name, kwargs):
        if name == "place_order" and self.reject_reduce:
            self.calls.append((name, kwargs))
            self.order_kwargs = kwargs
            return {"status": "REJECTED", "rejectionReason": "ReduceOnly", "filledSize": "0"}
        if name == "modify_order":
            self.calls.append((name, kwargs))
            self.order_kwargs = dict(self.order_kwargs, price=kwargs["price"])
            return {"orderId": "arcus-order-1", "marketDisplayName": "BTC-USD", "status": "ACK"}
        data = super().payload(name, kwargs)
        if name == "place_order" and self.case in {"ioc", "fok"}:
            self.cancelled = True
            self.cancel_pending = False
        return data


@pytest.mark.parametrize("case", CASES[1:])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_arcus_cases(mode, case):
    client = ArcusCaseMock(mode, case)
    result = {}
    await run_lifecycle(
        ArcusAdapter(client, "arcus", "swap", "BTC-USD"), result, poll_delay=0, case=case
    )
    assert result["stage"] == "complete"
    place = [kw for name, kw in client.calls if name == "place_order"][0]
    assert place["time_in_force"] == {"ioc": "IOC", "fok": "FOK"}.get(case, "ALO")
    assert place.get("reduce_only", False) is (case == "reduce_only")
    if case == "amend":
        modify = [kw for name, kw in client.calls if name == "modify_order"]
        assert len(modify) == 1 and modify[0]["order_id"] == "arcus-order-1"
        assert (modify[0]["time_in_force"], modify[0]["reduce_only"]) == ("ALO", False)
        assert Decimal(modify[0]["price"]) == Decimal(place["price"]) - Decimal(".1")
        assert modify[0]["good_til_time"] == place["good_til_time"]
    cancels = [kw for name, kw in client.calls if name == "cancel_order"]
    assert len(cancels) == (0 if case in {"ioc", "fok"} else 1)


@pytest.mark.asyncio
async def test_arcus_reduce_only_rejection_and_ioc_fill():
    client = ArcusCaseMock("sync", "reduce_only")
    client.reject_reduce = True
    result = {}
    adapter = ArcusAdapter(client, "arcus", "swap", "BTC-USD")
    await run_lifecycle(adapter, result, poll_delay=0, case="reduce_only")
    assert "rejected" in result["cleanup"] and "ReduceOnly" in result["cleanup"]
    client = ArcusCaseMock("sync", "ioc")
    client.filled = ".001"
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(
            ArcusAdapter(client, "arcus", "swap", "BTC-USD"), {}, poll_delay=0, case="ioc"
        )


# Support matrix, runner gating and reporting -------------------------------------------


def test_support_matrix_marks_documented_gaps_na():
    na = {
        (exchange, market_, case)
        for exchange, markets in MARKETS.items()
        for market_, _ in markets
        for case in CASES
        if not_applicable(exchange, market_, case)
    }
    assert ("hyperliquid", "swap", "fok") in na and ("kucoin", "swap", "fok") in na
    assert ("kucoin", "spot", "fok") not in na and ("kraken", "swap", "fok") not in na
    assert ("mexc", "spot", "amend") in na and ("mexc", "swap", "amend") not in na
    assert all(case != "lifecycle" and case != "ioc" for _, _, case in na)
    assert not_applicable("binance", "spot", "reduce_only") == (
        "N/A: binance spot has no reduce-only orders"
    )
    with pytest.raises(ValueError):
        not_applicable("binance", "spot", "unknown")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_runner_na_skips_before_credentials(mode, monkeypatch):
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr(
        "tests.stateful_runner.load_dotenv", lambda: pytest.fail("must not load credentials")
    )
    result = {}
    with pytest.raises(pytest.skip.Exception, match="N/A: hyperliquid futures has no FOK"):
        await run_case("hyperliquid", mode, "swap", "BTC-USD-SWAP", result, case="fok")
    row = update_report(result, SimpleNamespace(skipped=True, longrepr="N/A"))
    assert (row["status"], row["case"]) == ("N/A", "fok")


@pytest.mark.asyncio
async def test_runner_gate_still_applies_to_new_cases(monkeypatch):
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", False)
    result = {}
    with pytest.raises(pytest.skip.Exception, match="RUN_LIVE_TRADING_TESTS"):
        await run_case("binance", "sync", "spot", "BTC-USDC-SPOT", result, case="ioc")


@pytest.mark.parametrize(
    "name,case",
    [
        ("test_limit_order_lifecycle", "lifecycle"),
        ("test_ioc_never_fills", "ioc"),
        ("test_fok_never_fills", "fok"),
        ("test_reduce_only_cannot_open", "reduce_only"),
        ("test_amend_price", "amend"),
    ],
)
def test_result_rows_carry_case(name, case):
    assert "case" in RESULT_FIELDS
    row = initial_result(f"tests/sync_support/okx/test_stateful_trade.py::{name}[spot-X]")
    assert row["case"] == case


def test_states_normalize_and_unknown_states_stay_visible():
    assert order_state("EXPIRED_IN_MATCH") == "expired"
    assert order_state("canceled-post-only") == "cancelled"
    assert order_state("ENTERED_BOOK") == "open"
    assert order_state("PartiallyFilledCanceled") == "partiallyfilledcanceled"
    assert order_state("CANCEL_PENDING") == "cancel_pending"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    "exchange,method",
    sorted({(exchange, method) for (exchange, _), (method, _) in AMEND_CALLS.items()})
    + [("hyperliquid", "modify_order"), ("lighter", "modify_order"), ("arcus", "modify_order")],
)
def test_amend_methods_exist_on_real_clients(exchange, method, mode):
    module = "dcex." + ("async_support." if mode == "async" else "") + exchange + ".client"
    signature = inspect.signature(getattr(importlib.import_module(module).Client, method))
    assert "price" in signature.parameters or {
        "newPx",
        "newPrice",
        "limit_price",
        "limitPrice",
    } & set(signature.parameters)


# Review hardening: taker distance, reduce-only rejection codes, hedge sides ---------------


@pytest.mark.parametrize(
    ("price", "lower", "error", "match"),
    [
        ("96", None, NotApplicable, "price band too tight for a safe IOC/FOK"),
        ("90", "91", LifecycleError, "outside the price band"),
    ],
)
@pytest.mark.parametrize("case", ["ioc", "fok"])
@pytest.mark.asyncio
async def test_taker_price_refused_before_sending(price, lower, error, match, case):
    client = CaseMock("binance", False, "sync", case)
    adapter = cex_adapter(client, "binance", False)
    rules = Rules(
        Decimal(".1"),
        Decimal(".01"),
        Decimal(".01"),
        Decimal(0),
        lower_price=None if lower is None else Decimal(lower),
    )

    async def prepare():
        return Plan(
            "BTCUSDT", Decimal(price), Decimal(".12"), Decimal(price) * Decimal(".12"), rules
        ), Decimal(100)

    adapter.prepare = prepare
    result = {}
    with pytest.raises(error, match=match):
        await run_lifecycle(adapter, result, poll_delay=0, case=case)
    assert not any(name.startswith("place_") for name, _ in client.calls)
    if error is NotApplicable:
        assert result["stage"] == "not_applicable"
        row = update_report(result, SimpleNamespace(skipped=True, longrepr="N/A"))
        assert row["status"] == "N/A"


@pytest.mark.parametrize("case", ["ioc", "fok"])
@pytest.mark.asyncio
async def test_arcus_taker_price_capped_and_ladder_disabled(case):
    client = ArcusCaseMock("sync", case)
    client.price_rejections = 1
    result = {}
    with pytest.raises(NotApplicable, match="price band too tight"):
        await run_lifecycle(
            ArcusAdapter(client, "arcus", "swap", "BTC-USD"), result, poll_delay=0, case=case
        )
    places = [kw for name, kw in client.calls if name == "place_order"]
    assert len(places) == 1 and Decimal(places[0]["price"]) <= Decimal("95")
    assert result["stage"] == "not_applicable"
    # A higher oracle no longer lifts an IOC/FOK price above 95% of the bid.
    client = ArcusCaseMock("sync", case)
    client.info["oraclePrice"] = "120"
    taker = ArcusAdapter(client, "arcus", "swap", "BTC-USD")
    taker.case = case
    plan, _ = await taker.prepare()
    assert plan.price <= Decimal("100") * TAKER_MAX_BID_FRACTION


def coded(message, code):
    error = LifecycleError(message)
    error.code = code
    return error


@pytest.mark.parametrize(
    ("exchange", "error", "expected"),
    [
        (
            "binance",
            coded("binance place_order: code=-2022 ReduceOnly Order is rejected.", "-2022"),
            True,
        ),
        (
            "binance",
            coded('HTTP 400: {"code":-2022,"msg":"ReduceOnly Order is rejected."}', "400"),
            True,
        ),
        ("bybit", coded("bybit place_order: code=110017 position is zero", "110017"), True),
        ("okx", coded("okx: code=51169 no position", "51169"), True),
        ("kucoin", coded("kucoin: code=300009 No open positions to close.", "300009"), True),
        ("mexc", coded("mexc: code=2009 Position is nonexistent or closed", "2009"), True),
        ("mexc", coded('HTTP 200: {"success":false,"code":2008}', ""), True),
        ("mexc", coded("mexc: code=8917 reduce-only insufficient margin", "8917"), False),
        ("mexc", coded("mexc: code=2005 Insufficient balance", "2005"), False),
        ("extended", coded('HTTP 400: {"error":{"code":"REDUCE_ONLY_FAILED"}}', "400"), True),
        ("backpack", coded("backpack: code=4000 Reduce only order not reduced", "4000"), True),
        (
            "hyperliquid",
            OrderRejected("hyperliquid: Reduce only order would increase position."),
            True,
        ),
        ("kraken", OrderRejected("kraken: wouldNotReducePosition"), True),
        ("arcus", OrderRejected("arcus: order acknowledgement rejected (ReduceOnly)"), True),
        ("okx", coded("okx: code=51008 Order failed. Insufficient balance", "51008"), False),
        ("binance", coded("binance: code=-1003 Too many requests", "-1003"), False),
        (
            "binance",
            coded("binance: code=-1102 Mandatory parameter reduceOnly missing", "-1102"),
            False,
        ),
        (
            "bitget",
            coded("bitget: code=503 Service Unavailable; reduce only rejected", "503"),
            False,
        ),
        ("bybit", coded("bybit place_order: code= response timeout", ""), False),
        ("hyperliquid", OrderRejected("hyperliquid: Order has invalid price."), False),
        ("okx", TimeoutError("reduce only rejected"), False),
    ],
)
def test_only_documented_reduce_only_rejections_pass(exchange, error, expected):
    assert explicit_rejection(error, exchange) is expected


@pytest.mark.parametrize(
    ("message", "code"),
    [("Margin is insufficient.", "-2019"), ("Service Unavailable", "503"), ("Bad gateway", "")],
)
@pytest.mark.asyncio
async def test_reduce_only_non_reduce_errors_fail(message, code):
    client = CaseMock("binance", False, "sync", "reduce_only")
    original = client.payload

    def payload(method, kw):
        if method == "place_order":
            error = RuntimeError(message)
            error.code = code
            raise error
        return original(method, kw)

    client.payload = payload
    result = {}
    with pytest.raises(LifecycleError, match=message):
        await run_lifecycle(
            cex_adapter(client, "binance", False), result, poll_delay=0, case="reduce_only"
        )
    assert result["stage"] != "complete"


@pytest.mark.asyncio
async def test_reduce_only_rejected_id_is_swept_when_run_does_not_complete():
    client = CaseMock("bybit", False, "sync", "reduce_only")
    client.reject = True
    adapter = cex_adapter(client, "bybit", False)
    swept = []
    original_recover = adapter.recover_client_order

    async def recover(client_id):
        swept.append(client_id)
        return await original_recover(client_id)

    adapter.recover_client_order = recover
    original_positions = adapter.positions
    calls = []

    async def positions():
        calls.append(1)
        return [{"size": "1"}] if len(calls) > 1 else await original_positions()

    adapter.positions = positions
    result = {}
    with pytest.raises(LifecycleError, match="UNEXPECTED POSITION"):
        await run_lifecycle(adapter, result, poll_delay=0, case="reduce_only")
    assert adapter.client_order_id in swept


@pytest.mark.asyncio
async def test_reduce_only_order_appearing_after_rejection_is_cancelled():
    client = CaseMock("bybit", False, "sync", "reduce_only")
    client.reject = True
    adapter = cex_adapter(client, "bybit", False)
    polls = []

    async def recover():
        polls.append(1)
        if len(polls) < 3:
            return None
        client.placed = True  # The order shows up late after all.
        return "123"

    adapter.recover_order = recover
    result = {}
    await run_lifecycle(adapter, result, poll_delay=0, case="reduce_only")
    assert "accepted despite error" in result["cleanup"]
    assert [name for name, _ in client.calls if name == "cancel_order"] == ["cancel_order"]


HEDGE = {
    "binance": (
        "get_futures_position_mode",
        {"dualSidePosition": True},
        {"positionSide": "SHORT"},
        "reduceOnly",
    ),
    "aster": (
        "get_futures_position_mode",
        {"dualSidePosition": True},
        {"positionSide": "SHORT"},
        "reduceOnly",
    ),
    "okx": (
        "get_account_config",
        [{"posMode": "long_short_mode"}],
        {"posSide": "short"},
        "reduceOnly",
    ),
    "bitget": (
        "get_uta_settings",
        {"holdMode": "hedge_mode"},
        {"pos_side": "short"},
        "reduce_only",
    ),
    "bingx": (
        "get_position_mode",
        {"dualSidePosition": "true"},
        {"position_side": "SHORT"},
        "reduce_only",
    ),
    "bybit": (
        "get_positions",
        {"list": [{"positionIdx": 1, "size": "0"}, {"positionIdx": 2, "size": "0"}]},
        {"positionIdx": 2, "reduceOnly": True},
        None,
    ),
}


@pytest.mark.parametrize("exchange", sorted(HEDGE))
@pytest.mark.asyncio
async def test_hedge_mode_reduce_only_buy_targets_the_short_side(exchange):
    method, mode, expected, flag = HEDGE[exchange]
    client = CaseMock(exchange, False, "async", "reduce_only")
    original = client.payload
    client.payload = lambda name, kw: mode if name == method else original(name, kw)
    result = {}
    await run_lifecycle(
        cex_adapter(client, exchange, False), result, poll_delay=0, case="reduce_only"
    )
    kw = place_kwargs(client)
    assert {key: kw.get(key) for key in expected} == expected
    assert flag is None or flag not in kw
    assert "accepted resting" in result["cleanup"]


@pytest.mark.parametrize(
    ("mode", "extra"),
    [(1, {}), (2, {"reduceOnly": True, "positionMode": 2})],
    ids=["hedge", "one-way"],
)
@pytest.mark.asyncio
async def test_mexc_reduce_only_follows_position_mode(mode, extra):
    client = CaseMock("mexc", False, "sync", "reduce_only")
    client.position_mode = mode
    await run_lifecycle(cex_adapter(client, "mexc", False), {}, poll_delay=0, case="reduce_only")
    kw = place_kwargs(client)
    assert (kw["side"], kw["openType"], kw["leverage"]) == (2, 1, 15)  # positionType 2 row
    assert {key: kw[key] for key in ("reduceOnly", "positionMode") if key in kw} == extra


@pytest.mark.parametrize("mode", [None, 3, "hedge"])
@pytest.mark.asyncio
async def test_mexc_unknown_position_mode_fails_before_sending(mode):
    client = CaseMock("mexc", False, "sync", "reduce_only")
    client.position_mode = mode
    with pytest.raises(LifecycleError, match="unknown contract position mode"):
        await run_lifecycle(
            cex_adapter(client, "mexc", False), {}, poll_delay=0, case="reduce_only"
        )
    assert not any(name.startswith("place_") for name, _ in client.calls)


@pytest.mark.asyncio
async def test_unconfirmed_rejected_id_sweep_fails_even_when_case_is_na():
    client = ArcusCaseMock("sync", "ioc")
    client.price_rejections = 1
    adapter = ArcusAdapter(client, "arcus", "swap", "BTC-USD")

    async def broken(client_id):
        raise LifecycleError("open orders unavailable")

    adapter.recover_client_order = broken
    result = {}
    with pytest.raises(LifecycleError, match="REJECTED CLIENT ID CLEANUP UNCONFIRMED"):
        await run_lifecycle(adapter, result, poll_delay=0, case="ioc")
    assert result["stage"] == "cleanup"
    row = update_report(result, SimpleNamespace(skipped=False, failed=True, longrepr=None))
    assert row["status"] == "failed"


@pytest.mark.asyncio
async def test_arcus_unqueryable_ioc_passes_on_zero_fill_acknowledgement():
    client = ArcusCaseMock("sync", "ioc")
    original = client.payload

    def payload(name, kwargs):
        data = original(name, kwargs)
        if name == "place_order":
            data = dict(data, filledSize="0")
        if name == "get_order_status":
            raise RuntimeError("HTTP 404: Order not found")
        return data

    client.payload = payload
    result = {}
    await run_lifecycle(
        ArcusAdapter(client, "arcus", "swap", "BTC-USD"), result, poll_delay=0, case="ioc"
    )
    assert "not queryable; placement reported zero fill" in result["cleanup"]


@pytest.mark.parametrize(("exchange", "market_"), [("extended", "swap"), ("kucoin", "swap")])
def test_library_gaps_are_named(exchange, market_):
    assert "library has no order amendment" in not_applicable(exchange, market_, "amend")
