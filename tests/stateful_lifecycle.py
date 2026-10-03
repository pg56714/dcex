"""One non-crossing limit-order lifecycle shared by sync and async live tests."""

import asyncio
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Protocol

from scripts.live.redaction import redact


class LifecycleError(Exception):
    """An unsafe precondition, failed exchange operation, or unexpected fill."""


class PriceBandRejected(LifecycleError):
    """An explicit rejection confirming that no order was accepted."""


class InsufficientBalance(Exception):
    """The selected account cannot fund the smallest permitted order."""


class MarketUnavailable(Exception):
    """The documented market cannot perform this non-fill lifecycle."""


def decimal(value: object) -> Decimal:
    """Reject missing, non-finite, and malformed numeric response fields."""
    try:
        number = Decimal(str(value))
    except Exception:
        raise LifecycleError("missing or invalid numeric response field") from None
    if not number.is_finite():
        raise LifecycleError("non-finite numeric response field")
    return number


@dataclass(frozen=True)
class Rules:
    tick: Decimal
    step: Decimal
    min_size: Decimal
    min_notional: Decimal
    multiplier: Decimal = Decimal(1)
    lower_price: Decimal | None = None
    upper_price: Decimal | None = None


@dataclass(frozen=True)
class Plan:
    symbol: str
    price: Decimal
    size: Decimal
    notional: Decimal


@dataclass(frozen=True)
class Order:
    identifier: str
    symbol: str
    side: str
    kind: str
    price: Decimal
    size: Decimal
    filled: Decimal
    state: str


def plan_order(
    symbol: str, bid: Decimal, ask: Decimal, rules: Rules, *, target_price: Decimal | None = None
) -> Plan:
    """Choose a distant bid within known bands and the smallest valid size."""
    values = (bid, ask, rules.tick, rules.step, rules.multiplier)
    if any(not value.is_finite() or value <= 0 for value in values) or bid >= ask:
        raise LifecycleError("invalid book, tick, step, or contract multiplier")
    if any(not value.is_finite() or value < 0 for value in (rules.min_size, rules.min_notional)):
        raise LifecycleError("invalid minimum order rule")
    lower = rules.lower_price
    if lower is not None and (not lower.is_finite() or lower < 0):
        raise LifecycleError("invalid lower price band")
    margin = None
    if target_price is not None:
        # Caller-chosen ladder (Arcus); only kept one tick above any floor.
        target = decimal(target_price)
        if lower is not None:
            target = max(rules.tick, lower + rules.tick, target)
        price = (target / rules.tick).to_integral_value(rounding=ROUND_CEILING) * rules.tick
    else:
        # Rest far below the bid, but a quarter of the way into any band so a small
        # reference move cannot push the order below the exchange floor.
        target = bid * Decimal("0.90")
        if lower is not None:
            margin = lower + (bid - lower) * Decimal("0.25")
            target = max(target, margin)
        price = (target / rules.tick).to_integral_value(rounding=ROUND_FLOOR) * rules.tick
        if margin is not None and price < margin:
            price = (margin / rules.tick).to_integral_value(rounding=ROUND_CEILING) * rules.tick
    if rules.upper_price is not None:
        if not rules.upper_price.is_finite() or rules.upper_price <= 0:
            raise LifecycleError("invalid upper price band")
        price = min(
            price,
            (rules.upper_price / rules.tick).to_integral_value(rounding=ROUND_FLOOR) * rules.tick,
        )
    if margin is not None and (price < margin or price >= bid):
        raise LifecycleError("price band too tight: no buy price safely inside it below the bid")
    if price <= 0 or price >= bid or price >= ask:
        raise LifecycleError("no valid non-crossing buy price inside the permitted band")
    if lower is not None and price < lower:
        raise LifecycleError("price bands do not contain a valid limit price")
    minimum = max(rules.min_size, rules.step, rules.min_notional / (price * rules.multiplier))
    size = (minimum / rules.step).to_integral_value(rounding=ROUND_CEILING) * rules.step
    return Plan(symbol, price, size, price * size * rules.multiplier)


class Adapter(Protocol):
    client_order_id: str
    """Only the six operations needed for one isolated order are exposed."""

    async def prepare(self) -> tuple[Plan, Decimal]: ...
    async def book(self) -> tuple[Decimal, Decimal]: ...
    async def positions(self) -> list[object]: ...
    async def open_orders(self) -> list[object]: ...
    async def place(self, plan: Plan) -> str: ...
    async def order(self, identifier: str) -> Order | None: ...
    async def cancel(self, identifier: str) -> None: ...
    async def recover_order(self) -> str | None: ...


def validate_order(order: Order, plan: Plan, identifier: str) -> None:
    """Validate identity and every order field, rejecting any execution immediately."""
    if order.filled != 0 or not order.filled.is_finite():
        raise LifecycleError("UNEXPECTED FILL: stop; position was not automatically closed")
    expected = (identifier, plan.symbol, "buy", "limit", plan.price, plan.size)
    actual = (order.identifier, order.symbol, order.side, order.kind, order.price, order.size)
    if actual != expected:
        raise LifecycleError(
            "queried order does not match the submitted ID/symbol/side/type/price/size"
        )


async def run_lifecycle(
    adapter: Adapter, result: dict[str, str], *, poll_delay: float = 0.25
) -> None:
    """Retry only explicit price rejections; cancel only the accepted test order."""
    identifier = None
    cancelled = False
    placement_started = False
    client_ids: list[str] = []
    rejected_ids: list[str] = []
    try:
        result["stage"] = "preflight"
        if await adapter.positions():
            raise LifecycleError("existing position: manual reconciliation required")
        if await adapter.open_orders():
            raise LifecycleError("existing open orders: no order was submitted")
        plan, available = await adapter.prepare()
        while True:
            if not available.is_finite() or available < 0:
                raise LifecycleError("invalid available balance")
            if available < plan.notional:
                raise InsufficientBalance(
                    f"{result.get('exchange')} {result.get('market')}: "
                    f"requires {plan.notional:f} quote units; available {available:f}"
                )
            bid, ask = await adapter.book()
            if plan.price >= bid or plan.price >= ask or bid >= ask:
                raise LifecycleError(
                    "book moved: planned price is no longer safely below the market"
                )
            result["stage"] = "place"
            result["client_order_id"] = adapter.client_order_id
            if adapter.client_order_id not in client_ids:
                client_ids.append(adapter.client_order_id)
            result["prior_client_order_ids"] = ",".join(client_ids)
            result["price"] = str(plan.price)
            placement_started = True
            try:
                identifier = await adapter.place(plan)
                break
            except MarketUnavailable:
                # An explicit exchange rejection: no order was created, nothing to recover.
                placement_started = False
                raise
            except PriceBandRejected:
                placement_started = False
                rejected_ids.append(adapter.client_order_id)
                next_plan = getattr(adapter, "next_price_plan", None)
                if next_plan is None:
                    raise
                if await adapter.open_orders():
                    raise LifecycleError(
                        "open order present after rejected placement; stopped without retry"
                    ) from None
                plan, available = await next_plan()
        if not identifier:
            raise LifecycleError("exchange acknowledged no order ID; do not retry placement")
        result["order_id"] = redact(identifier, mask_environment=False)
        result["stage"] = "query_open"
        for attempt in range(20):
            order = await adapter.order(identifier)
            if order is not None:
                validate_order(order, plan, identifier)
                if order.state != "open":
                    raise LifecycleError("new limit order is not resting open")
                break
            if attempt == 19:
                raise LifecycleError("order ID was not found after placement")
            await asyncio.sleep(poll_delay)
        result["stage"] = "cancel"
        await adapter.cancel(identifier)
        result["stage"] = "query_cancelled"
        for attempt in range(20):
            order = await adapter.order(identifier)
            if order is not None:
                validate_order(order, plan, identifier)
                if order.state == "cancelled":
                    cancelled = True
                    break
                if order.state != "open":
                    raise LifecycleError("unexpected order status after cancellation")
            if attempt == 19:
                raise LifecycleError("cancellation was not confirmed by order query")
            await asyncio.sleep(poll_delay)
        result["stage"] = "verify_clean"
        if await adapter.open_orders():
            raise LifecycleError("open orders remain after cancellation")
        if await adapter.positions():
            raise LifecycleError("UNEXPECTED POSITION: stop; no automatic close was attempted")
        result["cleanup"] = "cancellation confirmed; no open orders or positions remain"
        result["stage"] = "complete"
    except (InsufficientBalance, MarketUnavailable) as error:
        result["skip_reason"] = redact(error)
        raise
    except Exception as error:
        result["error_code"] = redact(getattr(error, "code", ""))
        result["error_message"] = redact(error)
        raise LifecycleError(result["error_message"]) from None
    finally:
        if placement_started and not identifier:
            result["cleanup"] = "placement unresolved; inspect client order ID manually"
            result["error_message"] = result.get("error_message", "") + (
                "; placement uncertain; inspect client order ID " + adapter.client_order_id
            )
            try:
                for attempt in range(20):
                    identifier = await adapter.recover_order()
                    if identifier:
                        result["order_id"] = redact(identifier, mask_environment=False)
                        break
                    if attempt < 19:
                        await asyncio.sleep(poll_delay)
            except Exception:
                result["error_message"] += (
                    "; client-ID recovery failed; manual reconciliation required"
                )
        if identifier and not cancelled:
            try:
                await adapter.cancel(identifier)
                for attempt in range(20):
                    if not await adapter.open_orders():
                        break
                    if attempt == 19:
                        raise LifecycleError("open orders remain after cleanup cancellation")
                    await asyncio.sleep(poll_delay)
                result["cleanup"] = "cleanup cancellation acknowledged; no open orders remain"
            except Exception:
                result["cleanup"] = (
                    "cleanup cancellation unconfirmed; inspect test order ID and client ID manually"
                )
        if rejected_ids and result.get("stage") != "complete":
            # Only this run's explicitly rejected client IDs; never other open orders.
            await cleanup_client_ids(adapter, rejected_ids, result, poll_delay)
        if placement_started and not cancelled:
            try:
                remaining_positions = await adapter.positions()
            except Exception:
                result["cleanup"] += "; position check unconfirmed; manual reconciliation required"
            else:
                if remaining_positions:
                    warning = "UNEXPECTED POSITION: stop; no automatic close was attempted"
                    result["cleanup"] += "; " + warning
                    result["error_message"] = result.get("error_message", "") + "; " + warning
                    raise LifecycleError(result["error_message"])


async def cleanup_client_ids(
    adapter: Adapter, client_ids: list[str], result: dict[str, str], poll_delay: float
) -> None:
    """Cancel any still-open order carrying one of this run's rejected client IDs."""
    recover = getattr(adapter, "recover_client_order", None)
    notes = []
    for client_id in client_ids:
        try:
            if recover is None:
                raise LifecycleError("client-ID recovery unavailable")
            found = await recover(client_id)
            if not found:
                continue
            await adapter.cancel(found)
            for attempt in range(20):
                if not await recover(client_id):
                    break
                if attempt == 19:
                    raise LifecycleError("order remains open after cleanup cancellation")
                await asyncio.sleep(poll_delay)
            notes.append("rejected-attempt client ID " + client_id + " cancelled")
        except Exception:
            notes.append(
                "rejected-attempt client ID " + client_id + " unconfirmed; inspect manually"
            )
    if notes:
        result["cleanup"] = "; ".join(filter(None, (result.get("cleanup", ""), *notes)))
