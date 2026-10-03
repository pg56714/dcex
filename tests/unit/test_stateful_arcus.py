"""Offline Arcus fixtures from the published REST OpenAPI; no real clients."""

import importlib
import inspect
from decimal import Decimal
from types import SimpleNamespace

import pytest

from scripts.live.accounts import collect
from tests.stateful_arcus import ArcusAdapter
from tests.stateful_lifecycle import (
    InsufficientBalance,
    LifecycleError,
    MarketUnavailable,
    run_lifecycle,
)
from tests.stateful_reporting import update_report
from tests.stateful_runner import run_case


class ArcusMock:
    def __init__(self, mode="sync"):
        self.mode = mode
        self.cls = importlib.import_module(
            "dcex." + ("async_support." if mode == "async" else "") + "arcus.client"
        ).Client
        self.calls = []
        self.placed = False
        self.cancelled = False
        self.query_pending = True
        self.query_missing = False
        self.cancel_pending = True
        self.filled = "0"
        self.available = "12"
        self.bid = "100"
        self.order_kwargs = {}
        self.place_error = None
        self.price_rejections = 0
        self.place_status = "ACK"
        self.extra_orders = []
        self.rejected_but_open = False
        self.after_rejection_orders = []
        self.info = {
            "oraclePrice": "100",
            "markPrice": "101",
            "marketDisplayName": "BTC-USD",
            "status": "ONLINE",
            "type": "PERPETUAL",
            "stepSize": ".001",
            "tickSize": ".01",
            "minOrderSize": ".001",
            "minOrderNotional": "5",
            "maxOrderSize": "100",
            "tickTiers": [{"upToPrice": "90", "tick": ".01"}, {"tick": ".1"}],
            "lowerTradingBound": None,
            "upperTradingBound": None,
        }

    def record(self):
        return {
            "orderId": "arcus-order-1",
            "clientId": self.order_kwargs["client_order_id"],
            "marketDisplayName": "BTC-USD",
            "marketId": 1,
            "side": "BUY",
            "type": "LIMIT",
            "price": self.order_kwargs["price"],
            "originalSize": self.order_kwargs["quantity"],
            "remainingSize": str(Decimal(self.order_kwargs["quantity"]) - Decimal(self.filled)),
            "filledSize": self.filled,
            "status": "CANCELED" if self.cancelled else "OPEN",
        }

    def payload(self, name, kwargs):
        self.calls.append((name, kwargs))
        if name == "get_markets":
            return {"markets": [self.info]}
        if name == "get_bbo":
            return {
                "bestBid": {"price": self.bid, "size": "1"},
                "bestAsk": {"price": "101", "size": "1"},
            }
        if name == "get_positions":
            return {"positions": {}, "total": 0}
        if name == "get_account":
            return {
                "equity": self.available,
                "freeCollateral": self.available,
                "netQuoteBalance": self.available,
                "positions": {},
            }
        if name == "get_open_orders":
            values = (
                ([self.record()] + self.extra_orders) if self.placed and not self.cancelled else []
            ) + self.after_rejection_orders
            return {"orders": values, "total": len(values)}
        if name == "place_order":
            self.order_kwargs = kwargs
            if self.price_rejections:
                self.price_rejections -= 1
                if self.rejected_but_open:
                    self.after_rejection_orders.append(
                        {"clientId": kwargs["client_order_id"], "orderId": "arcus-ghost-1"}
                    )
                return {
                    "status": "REJECTED",
                    "rejectionReason": "OracleDeviation",
                    "filledSize": "0",
                }
            self.placed = True
            if self.place_error:
                raise self.place_error
            return {
                "orderId": "arcus-order-1",
                "clientId": kwargs["client_order_id"],
                "marketDisplayName": "BTC-USD",
                "status": self.place_status,
            }
        if name == "get_order_status":
            if self.query_missing:
                self.query_missing = False
                raise RuntimeError("HTTP 404: Order not found")
            result = self.record()
            if self.cancelled and self.cancel_pending:
                self.cancel_pending = False
                result["status"] = "CANCEL_PENDING"
            elif not self.cancelled and self.query_pending:
                self.query_pending = False
                result["status"] = "PENDING"
            return result
        if name == "cancel_order" and kwargs["order_id"] == "arcus-ghost-1":
            self.after_rejection_orders = [
                row for row in self.after_rejection_orders if row["orderId"] != "arcus-ghost-1"
            ]
            return {
                "orderId": "arcus-ghost-1",
                "marketDisplayName": "BTC-USD",
                "status": "CANCEL_ACKNOWLEDGED",
            }
        if name == "cancel_order":
            assert kwargs["order_id"] == "arcus-order-1"
            self.cancelled = True
            return {
                "orderId": "arcus-order-1",
                "marketDisplayName": "BTC-USD",
                "status": "CANCEL_ACKNOWLEDGED",
            }
        raise AssertionError("unexpected method: " + name)

    def __getattr__(self, name):
        def call(**kwargs):
            inspect.signature(getattr(self.cls, name)).bind(self, **kwargs)
            return self.payload(name, kwargs)

        async def async_call(**kwargs):
            return call(**kwargs)

        return async_call if self.mode == "async" else call


def adapter(client):
    return ArcusAdapter(client, "arcus", "swap", "BTC-USD")


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("status", ["ACK", "OPEN"])
@pytest.mark.asyncio
async def test_arcus_acknowledgement_requires_final_queries(mode, status, monkeypatch):
    monkeypatch.setattr("tests.stateful_arcus.time.time", lambda: 1_800_000_000)
    client = ArcusMock(mode)
    client.place_status = status
    result = {}
    await run_lifecycle(adapter(client), result, poll_delay=0)
    assert result["stage"] == "complete"
    assert sum(name == "get_order_status" for name, _ in client.calls) == 4
    args = client.order_kwargs
    assert args["time_in_force"] == "ALO"
    assert args["order_type"] == "LIMIT"
    assert args["good_til_time"] == (1_800_000_000 + 32 * 86400) * 1_000_000
    assert Decimal(args["price"]) == Decimal("95")
    assert Decimal(args["quantity"]) == Decimal(".053")
    assert args["client_order_id"] == result["client_order_id"]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_arcus_uncertain_acceptance_recovers_only_own_client_id(mode):
    client = ArcusMock(mode)
    client.place_error = TimeoutError("mock response timeout")
    client.extra_orders = [{"clientId": "someone-else", "orderId": "unrelated-order"}]
    result = {}
    with pytest.raises(LifecycleError, match="timeout"):
        await run_lifecycle(adapter(client), result, poll_delay=0)
    assert client.cancelled
    assert result["order_id"] == "arcus-order-1"
    assert "client order ID" in result["error_message"]
    assert [(name, args["order_id"]) for name, args in client.calls if name == "cancel_order"] == [
        ("cancel_order", "arcus-order-1")
    ]


@pytest.mark.asyncio
async def test_arcus_detects_fill_even_in_pending_query():
    client = ArcusMock()
    client.filled = ".001"
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(adapter(client), {}, poll_delay=0)
    assert client.cancelled


@pytest.mark.asyncio
async def test_arcus_oracle_rejection_is_price_range_issue():
    client = ArcusMock()
    client.price_rejections = 4
    result = {}
    with pytest.raises(LifecycleError, match="price range"):
        await run_lifecycle(adapter(client), result, poll_delay=0)
    assert "price range" in result["error_message"]
    assert not result.get("skip_reason")
    assert sum(name == "place_order" for name, _ in client.calls) == 4
    assert Decimal(result["price"]) == Decimal("99.5")
    assert not client.placed
    assert not client.cancelled


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("rejections", [0, 1, 2, 3])
@pytest.mark.asyncio
async def test_arcus_moves_inward_only_after_definitive_rejection(mode, rejections):
    client = ArcusMock(mode)
    client.price_rejections = rejections
    result = {}
    await run_lifecycle(adapter(client), result, poll_delay=0)
    attempts = [args for name, args in client.calls if name == "place_order"]
    expected = [Decimal(x) for x in ("95", "98", "99", "99.5")][: rejections + 1]
    assert [Decimal(args["price"]) for args in attempts] == expected
    assert all(args["time_in_force"] == "ALO" for args in attempts)
    assert len({args["client_order_id"] for args in attempts}) == len(attempts)
    assert sum(name == "get_account" for name, _ in client.calls) == len(attempts)
    assert sum(name == "get_bbo" for name, _ in client.calls) == 2 * len(attempts)
    assert Decimal(result["price"]) == expected[-1]
    assert (
        Decimal(
            update_report(result, SimpleNamespace(passed=True, failed=False, skipped=False))[
                "price"
            ]
        )
        == expected[-1]
    )


@pytest.mark.parametrize("ours", [True, False])
@pytest.mark.asyncio
async def test_arcus_open_order_after_rejection_stops_and_cleans_only_own_ids(ours):
    client = ArcusMock()
    client.price_rejections = 1
    client.rejected_but_open = ours
    unrelated = {"clientId": "someone-else", "orderId": "unrelated-order"}
    original = client.payload

    def payload(name, kwargs):
        data = original(name, kwargs)
        if name == "place_order" and not ours:
            client.after_rejection_orders.append(unrelated)
        return data

    client.payload = payload
    result = {}
    with pytest.raises(LifecycleError, match="after rejected placement"):
        await run_lifecycle(adapter(client), result, poll_delay=0)
    assert sum(name == "place_order" for name, _ in client.calls) == 1
    cancels = [args["order_id"] for name, args in client.calls if name == "cancel_order"]
    assert cancels == (["arcus-ghost-1"] if ours else [])
    assert ("cancelled" in result.get("cleanup", "")) is ours
    if not ours:
        assert client.after_rejection_orders == [unrelated]


@pytest.mark.asyncio
async def test_arcus_reports_every_client_id_used_without_env_masking(monkeypatch):
    client = ArcusMock()
    client.price_rejections = 2
    result = {}
    await run_lifecycle(adapter(client), result, poll_delay=0)
    used = [args["client_order_id"] for name, args in client.calls if name == "place_order"]
    assert len(used) == 3
    assert result["prior_client_order_ids"].split(",") == used
    assert result["client_order_id"] == used[-1]
    monkeypatch.setenv("MOCK_API_SECRET", used[0])
    row = update_report(result, SimpleNamespace(passed=True, failed=False, skipped=False))
    assert row["prior_client_order_ids"].split(",") == used


@pytest.mark.parametrize(
    "error", [TimeoutError("OracleDeviation response timeout"), RuntimeError("OracleDeviation")]
)
@pytest.mark.asyncio
async def test_arcus_uncertain_rejection_text_never_retries(error):
    client = ArcusMock()
    client.price_rejections = 1
    client.place_error = error
    result = {}
    with pytest.raises(LifecycleError, match="OracleDeviation"):
        await run_lifecycle(adapter(client), result, poll_delay=0)
    assert sum(name == "place_order" for name, _ in client.calls) == 2
    assert client.cancelled


@pytest.mark.asyncio
async def test_arcus_retry_rechecks_collateral():
    client = ArcusMock()
    client.price_rejections = 1
    original = client.payload

    def payload(name, kwargs):
        data = original(name, kwargs)
        if name == "place_order":
            client.available = "0"
        return data

    client.payload = payload
    with pytest.raises(InsufficientBalance):
        await run_lifecycle(adapter(client), {}, poll_delay=0)
    assert sum(name == "place_order" for name, _ in client.calls) == 1


@pytest.mark.parametrize(
    "rule,value,error",
    [
        ("maxOrderSize", ".01", MarketUnavailable),
        ("status", "OFFLINE", MarketUnavailable),
        ("lowerTradingBound", "100", LifecycleError),
        ("stepSize", "0", LifecycleError),
        ("tickTiers", [], LifecycleError),
    ],
)
@pytest.mark.asyncio
async def test_arcus_invalid_market_rules_never_place(rule, value, error):
    client = ArcusMock()
    client.info[rule] = value
    with pytest.raises(error):
        await run_lifecycle(adapter(client), {}, poll_delay=0)
    assert not client.placed


@pytest.mark.asyncio
async def test_arcus_insufficient_collateral_skips_before_order():
    client = ArcusMock()
    client.available = "3"
    with pytest.raises(InsufficientBalance, match="requires.*available 3"):
        await run_lifecycle(adapter(client), {}, poll_delay=0)
    assert not client.placed


@pytest.mark.asyncio
async def test_arcus_collect_checks_perps_and_only_reads_spot_balances():
    reads = []

    def balances(**kwargs):
        reads.append(kwargs)
        return {"balances": [{"symbol": "USDG", "balance": "3000000", "decimals": 6}]}

    spot = SimpleNamespace(get_balances=balances)
    perp = ArcusMock()
    state = await collect("arcus", [(spot, "spot", ""), (perp, "swap", "BTC-USD")])
    assert not state.blocked
    assert state.balances == {"spot": Decimal(3), "perp": Decimal(12)}
    assert [row["status"] for row in state.markets] == ["N/A", "clean"]
    assert reads == [{"include_wrapped": False}]
    assert all(name.startswith("get_") for name, _ in perp.calls)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_arcus_spot_na_does_not_construct_clients(mode, monkeypatch):
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr(
        "tests.stateful_runner.load_dotenv", lambda: pytest.fail("must not load credentials")
    )
    result = {}
    with pytest.raises(pytest.skip.Exception, match="N/A"):
        await run_case("arcus", mode, "spot", "", result)
    report = update_report(result, SimpleNamespace(skipped=True, longrepr="RFQ only"))
    assert report["status"] == "N/A"


@pytest.mark.asyncio
async def test_arcus_uses_tick_in_selected_price_tier():
    client = ArcusMock()
    client.bid = "100.03"
    client.info["oraclePrice"] = "90.12"
    plan, _ = await adapter(client).prepare()
    assert plan.price == Decimal("85.62")
    assert plan.price % Decimal(".01") == 0


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_arcus_transient_order_not_found_continues_polling(mode):
    client = ArcusMock(mode)
    client.query_missing = True
    result = {}
    await run_lifecycle(adapter(client), result, poll_delay=0)
    assert result["stage"] == "complete"
    assert sum(name == "get_order_status" for name, _ in client.calls) == 5


@pytest.mark.parametrize("message", ["HTTP 401: Order not found", "HTTP 404: Market not found"])
@pytest.mark.asyncio
async def test_arcus_does_not_hide_other_query_errors(message):
    client = ArcusMock()
    a = adapter(client)

    async def failed(*_, **__):
        raise LifecycleError(message)

    a.call = failed
    with pytest.raises(LifecycleError, match=message):
        await a.order("order-1")


@pytest.mark.asyncio
async def test_arcus_mark_reference_and_bid_clamp():
    client = ArcusMock()
    client.info.pop("oraclePrice")
    plan, _ = await adapter(client).prepare()
    assert plan.price == Decimal("96.0")
    assert plan.price < Decimal(client.bid)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_arcus_runner_constructs_correct_adapter_and_closes(mode, monkeypatch):
    client = ArcusMock(mode)
    client.query_pending = client.cancel_pending = False
    closed = []
    if mode == "async":

        async def init():
            return client

        async def close():
            closed.append(True)

        client.async_init = init
    else:

        def close():
            closed.append(True)

    client.close = close
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr("tests.stateful_runner.load_dotenv", lambda: None)
    monkeypatch.setattr("tests.stateful_runner.client_options", lambda _: {})
    monkeypatch.setattr(
        "tests.stateful_runner.importlib.import_module",
        lambda _: SimpleNamespace(Client=lambda **_: client),
    )
    result = {}
    await run_case("arcus", mode, "swap", "BTC-USD", result)
    assert result["stage"] == "complete"
    assert closed == [True]
