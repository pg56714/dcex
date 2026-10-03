"""Exercise the entire order lifecycle with in-memory exchange responses."""

from dataclasses import replace
from decimal import Decimal as D

import pytest

from tests.stateful_lifecycle import (
    InsufficientBalance,
    LifecycleError,
    Order,
    PriceBandRejected,
    Rules,
    plan_order,
    run_lifecycle,
)


class MockAdapter:
    def __init__(self):
        self.plan = plan_order("BTCUSDT", D(100), D(101), Rules(D(".1"), D(".01"), D(".01"), D(10)))
        self.available = D(20)
        self.cancelled = False
        self.calls = []
        self.existing_positions = []
        self.change = {}
        self.client_order_id = "unique-test-client-id"

    async def recover_order(self):
        self.calls.append("recover")
        return "123"

    async def prepare(self):
        self.calls.append("prepare")
        return self.plan, self.available

    async def book(self):
        return D(100), D(101)

    async def positions(self):
        return self.existing_positions

    async def open_orders(self):
        return []

    async def place(self, plan):
        self.calls.append("place")
        return "123"

    async def order(self, identifier):
        self.calls.append("query_cancelled" if self.cancelled else "query_open")
        row = Order(
            identifier,
            self.plan.symbol,
            "buy",
            "limit",
            self.plan.price,
            self.plan.size,
            D(0),
            "cancelled" if self.cancelled else "open",
        )
        return replace(row, **self.change)

    async def cancel(self, identifier):
        assert identifier == "123"
        self.calls.append("cancel")
        self.cancelled = True


@pytest.mark.asyncio
async def test_complete_lifecycle_checks_query_after_cancel():
    adapter = MockAdapter()
    result = {}
    await run_lifecycle(adapter, result, poll_delay=0)
    assert adapter.calls == ["prepare", "place", "query_open", "cancel", "query_cancelled"]
    assert result["stage"] == "complete"
    assert result["order_id"] == "123"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "field,value",
    [
        ("identifier", "456"),
        ("symbol", "ETHUSDT"),
        ("side", "sell"),
        ("kind", "market"),
        ("price", D(1)),
        ("size", D(1)),
        ("filled", D(".01")),
        ("state", "filled"),
    ],
)
async def test_wrong_fields_or_fills_fail_and_only_cancel_the_test_order(field, value):
    adapter = MockAdapter()
    adapter.change = {field: value}
    result = {}
    with pytest.raises(LifecycleError):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert adapter.calls.count("place") == 1
    assert adapter.calls[-1] == "cancel"
    assert result["stage"] == "query_open"


@pytest.mark.asyncio
async def test_existing_position_fails_before_placing():
    adapter = MockAdapter()
    adapter.existing_positions = [object()]
    with pytest.raises(LifecycleError, match="existing position"):
        await run_lifecycle(adapter, {}, poll_delay=0)
    assert not adapter.calls


@pytest.mark.asyncio
async def test_insufficient_balance_skips_without_mutation():
    adapter = MockAdapter()
    adapter.available = D(3)
    result = {"exchange": "arcus", "market": "spot"}
    with pytest.raises(InsufficientBalance, match="available 3"):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert adapter.calls == ["prepare"]
    assert "arcus spot" in result["skip_reason"]


@pytest.mark.asyncio
async def test_cancel_ack_without_cancelled_query_is_not_success():
    adapter = MockAdapter()
    adapter.change = {"state": "open"}
    with pytest.raises(LifecycleError, match="not confirmed"):
        await run_lifecycle(adapter, {}, poll_delay=0)
    assert adapter.calls.count("place") == 1


def test_price_band_and_contract_multiplier_produce_smallest_valid_order():
    rules = Rules(D(".5"), D(1), D(1), D(10), D(".01"), D(80), D(120))
    plan = plan_order("BTC_USDT", D(100), D(101), rules)
    assert plan.price == D(90)
    assert plan.notional >= 10
    assert plan.price * (plan.size - rules.step) * rules.multiplier < 10


def test_near_lower_band_rests_a_quarter_of_the_way_into_the_band():
    rules = Rules(D(".5"), D(1), D(1), D(10), lower_price=D(95))
    plan = plan_order("BTC_USDT", D(100), D(101), rules)
    # 95 + (100 - 95) / 4 = 96.25, rounded up to the next tick rather than toward the floor.
    assert plan.price == D("96.5")


def test_price_band_too_tight_is_rejected():
    rules = Rules(D(".5"), D(1), D(1), D(10), lower_price=D(95), upper_price=D(96))
    with pytest.raises(LifecycleError, match="price band too tight"):
        plan_order("BTC_USDT", D(100), D(101), rules)


def test_explicit_target_ladder_is_unchanged_by_band_margin():
    rules = Rules(D(".1"), D(1), D(1), D(10), lower_price=D(90))
    plan = plan_order("BTC_USDT", D(100), D(101), rules, target_price=D(95))
    assert plan.price == D(95)


@pytest.mark.parametrize("bid,ask", [(D(101), D(100)), (D(0), D(1)), (D("NaN"), D(1))])
def test_invalid_books_are_rejected(bid, ask):
    with pytest.raises(LifecycleError):
        plan_order("BTC", bid, ask, Rules(D(1), D(1), D(1), D(1)))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [TimeoutError(), ConnectionError(), KeyError("orderId"), LifecycleError("invalid order ID")],
)
async def test_accepted_order_is_recovered_after_placement_failure(failure):
    adapter = MockAdapter()

    async def accepted_then_failed(plan):
        adapter.calls.append("place")
        raise failure

    adapter.place = accepted_then_failed
    result = {}
    with pytest.raises(LifecycleError):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert adapter.calls == ["prepare", "place", "recover", "cancel"]
    assert result["client_order_id"] == adapter.client_order_id
    assert adapter.client_order_id in result["error_message"]
    assert result["order_id"] == "123"


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_fails", [False, True])
async def test_cleanup_failure_is_separate_from_original_error(cancel_fails):
    adapter = MockAdapter()
    adapter.change = {"kind": "market"}
    result = {}
    if cancel_fails:

        async def cancel(identifier):
            raise ConnectionError("lost cancel response")

        adapter.cancel = cancel
    else:

        async def open_orders():
            return [object()] if adapter.cancelled else []

        adapter.open_orders = open_orders
    with pytest.raises(LifecycleError, match="does not match"):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert "does not match" in result["error_message"]
    assert "unconfirmed" in result["cleanup"]


@pytest.mark.asyncio
async def test_cleanup_waits_for_asynchronous_cancellation():
    adapter = MockAdapter()
    adapter.change = {"kind": "market"}
    polls = []

    async def pending_orders():
        if not adapter.cancelled:
            return []
        polls.append(True)
        return [object()] if len(polls) < 3 else []

    adapter.open_orders = pending_orders
    result = {}
    with pytest.raises(LifecycleError, match="does not match"):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert len(polls) == 3
    assert "unconfirmed" not in result["cleanup"]
    assert adapter.calls.count("cancel") == 1


@pytest.mark.parametrize("recovered", [False, True])
@pytest.mark.asyncio
async def test_uncertain_placement_checks_positions_even_without_an_open_order(recovered):
    adapter = MockAdapter()

    async def place(plan):
        adapter.calls.append("place")
        raise TimeoutError("lost order response")

    async def recover():
        return "123" if recovered else None

    async def positions():
        return [object()] if "place" in adapter.calls else []

    adapter.place, adapter.recover_order, adapter.positions = place, recover, positions
    result = {}
    with pytest.raises(LifecycleError, match="UNEXPECTED POSITION"):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert "UNEXPECTED POSITION" in result["cleanup"]
    assert "lost order response" in result["error_message"]


@pytest.mark.asyncio
async def test_price_rejection_retries_only_when_no_open_orders_remain():
    adapter = MockAdapter()
    leftover = []

    async def place(plan):
        adapter.calls.append("place")
        leftover.append({"clientId": adapter.client_order_id})
        raise PriceBandRejected("mock price band")

    async def next_price_plan():
        adapter.calls.append("next")
        return adapter.plan, adapter.available

    async def open_orders():
        return leftover

    adapter.place = place
    adapter.next_price_plan = next_price_plan
    adapter.open_orders = open_orders
    result = {}
    with pytest.raises(LifecycleError, match="after rejected placement"):
        await run_lifecycle(adapter, result, poll_delay=0)
    assert adapter.calls == ["prepare", "place"]
    assert result["prior_client_order_ids"] == "unique-test-client-id"
    # No client-ID recovery method: report for manual inspection, never cancel blindly.
    assert "unique-test-client-id unconfirmed" in result["cleanup"]
    assert "cancel" not in adapter.calls
