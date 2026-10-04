"""One non-crossing limit-order lifecycle shared by sync and async live tests."""

import asyncio
import re
from dataclasses import dataclass, field, replace
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from typing import Protocol

from scripts.live.redaction import redact


class LifecycleError(Exception):
    """An unsafe precondition, failed exchange operation, or unexpected fill."""


class PriceBandRejected(LifecycleError):
    """An explicit rejection confirming that no order was accepted."""


class OrderRejected(LifecycleError):
    """The exchange explicitly refused the order, so it was never accepted."""


class OrderClosed(LifecycleError):
    """The exchange reports an IOC/FOK order ended at placement, unfilled and not resting."""


class InsufficientBalance(Exception):
    """The selected account cannot fund the smallest permitted order."""


class MarketUnavailable(Exception):
    """The documented market cannot perform this non-fill lifecycle."""


class NotApplicable(MarketUnavailable):
    """The exchange has no such order feature on this market; reported as N/A."""


CASES = ("lifecycle", "ioc", "fok", "reduce_only", "amend")
OPEN_STATES = frozenset({"new", "live", "open", "pending", "entered_book"})
TERMINAL_UNFILLED = frozenset({"cancelled", "expired", "rejected"})
FEATURES = {"ioc": "IOC orders", "fok": "FOK orders", "reduce_only": "reduce-only orders"}
FEATURES["amend"] = "order amendment"


def not_applicable(exchange: str, market: str, case: str) -> str | None:
    """Unsupported exchange/market/case combinations; never silently fall back."""
    spot = market == "spot"
    label = exchange + (" spot" if spot else " futures")
    unsupported = False
    if case == "reduce_only":
        unsupported = spot
    elif case == "fok":
        unsupported = exchange in {"hyperliquid", "lighter", "extended", "ondo"} or (
            exchange == "kucoin" and not spot
        )
    elif case == "amend":
        unsupported = (
            exchange in {"backpack", "extended", "ondo"}
            or (exchange in {"mexc", "aster"} and spot)
            or (exchange == "kucoin" and not spot)
        )
    elif case not in CASES:
        raise ValueError("unknown order-test case: " + case)
    if case == "amend" and (exchange == "extended" or (exchange == "kucoin" and not spot)):
        # The venue can amend (Extended cancelId replace, KuCoin UTA) but this library
        # exposes no such method for the tested account type.
        return f"N/A: {label} library has no {FEATURES[case]}"
    return f"N/A: {label} has no {FEATURES[case]}" if unsupported else None


# IOC/FOK have no post-only protection: only distance below the bid keeps them unfilled.
TAKER_MAX_BID_FRACTION = Decimal("0.95")
TAKER_BAND_NA = "N/A: price band too tight for a safe IOC/FOK"


def check_taker_price(plan: "Plan", bid: Decimal) -> None:
    """Refuse an IOC/FOK price above 95% of the bid or outside the known bands."""
    rules = plan.rules
    if rules is not None and (
        (rules.lower_price is not None and plan.price < rules.lower_price)
        or (rules.upper_price is not None and plan.price > rules.upper_price)
    ):
        raise LifecycleError("IOC/FOK price is outside the price band; nothing was sent")
    if plan.price > bid * TAKER_MAX_BID_FRACTION:
        raise NotApplicable(
            f"{TAKER_BAND_NA} (price {plan.price:f} above 95% of bid {bid:f}); nothing was sent"
        )


# Documented reduce-only business rejections (code, or message fragment when no code is
# documented). Anything else - balance, parameter, rate limit, transport - fails.
REDUCE_ONLY_CODES = {
    "binance": {"-2022"},  # ReduceOnly Order is rejected.
    "aster": {"-2022"},
    "bybit": {"110017"},  # Reduce-only rule not satisfied / position is zero.
    "okx": {"51169", "51170"},  # No position in this direction to reduce / same direction.
    "bitget": {"22002", "25227"},  # No position to close / no position available to close.
    "kucoin": {"300009"},  # No open positions to close.
    "mexc": {"2009"},  # Position nonexistent or closed.
    "extended": {"1137"},  # Position is missing for reduce-only order.
}
REDUCE_ONLY_MESSAGE = re.compile(
    r"reduce[ _-]?only\b.*\b(reject|not|would|cannot|can't|invalid|fail)"
    r"|reject\w*\W+.*reduce[ _-]?only|would (not )?(increase|reduce)"
    r"|wouldnotreduceposition|no (open )?position",
    re.IGNORECASE,
)
# "code=N", "code": N or the "[N]" prefix the HTTP layer gives exchange errors.
EXCHANGE_CODE = r'(?:code"?\s*[=:]\s*"?|\[)'


def explicit_rejection(error: Exception, exchange: str = "") -> bool:
    """Only a documented reduce-only business rejection counts; others fail for diagnosis."""
    if not isinstance(error, LifecycleError) or isinstance(error, PriceBandRejected):
        return False
    code, message = str(getattr(error, "code", "")).strip(), str(error)
    codes = REDUCE_ONLY_CODES.get(exchange, set())
    if code in codes or any(
        re.search(EXCHANGE_CODE + re.escape(known) + r"(?!\d)", message)
        or (not known.lstrip("-").isdigit() and known in message)
        for known in codes
    ):
        return True
    # A bare HTTP status or a transport failure is not a business rejection by itself.
    business_code = bool(code) and not re.fullmatch(r"[1-5]\d\d", code)
    business_code = business_code or bool(re.search(EXCHANGE_CODE + r"-?\d{4,}", message))
    if not isinstance(error, OrderRejected) and not business_code:
        return False
    return bool(REDUCE_ONLY_MESSAGE.search(message))


def order_state(value: object) -> str:
    """Normalize venue order statuses; unknown values stay visible and fail closed."""
    state = str(value).strip().lower()
    if state in OPEN_STATES:
        return "open"
    if "cancel" in state and "pending" not in state and "partial" not in state:
        return "cancelled"
    if "expire" in state:
        return "expired"
    if "reject" in state:
        return "rejected"
    return state


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
    rules: Rules | None = field(default=None, compare=False)


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
    return Plan(symbol, price, size, price * size * rules.multiplier, rules)


def amend_plans(plan: Plan) -> tuple[Plan, Plan]:
    """One size valid at both prices: rest at the planned price, then amend one tick lower."""
    rules = plan.rules
    if rules is None:
        raise LifecycleError("amend requires the planned price rules")
    price = plan.price - rules.tick
    if price <= 0 or (rules.lower_price is not None and price < rules.lower_price):
        raise LifecycleError("no room to amend one tick lower inside the price band")
    minimum = max(plan.size, rules.min_notional / (price * rules.multiplier))
    size = (minimum / rules.step).to_integral_value(rounding=ROUND_CEILING) * rules.step
    first = replace(plan, size=size, notional=plan.price * size * rules.multiplier)
    return first, replace(first, price=price, notional=price * size * rules.multiplier)


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


async def query_order(
    adapter: Adapter, identifier: str, plan: Plan, poll_delay: float, *, final: bool = False
) -> Order:
    """Poll until the order is visible; with final, until it leaves the open state."""
    order = None
    for attempt in range(20):
        order = await adapter.order(identifier)
        if order is not None:
            validate_order(order, plan, identifier)
            if not final or order.state != "open":
                return order
        if attempt < 19:
            await asyncio.sleep(poll_delay)
    if order is not None:
        raise LifecycleError("order is still resting open; it must not rest")
    raise LifecycleError("order ID was not found after placement")


async def cancel_confirmed(
    adapter: Adapter, identifier: str, plan: Plan, poll_delay: float
) -> None:
    """Cancel only this order and confirm the cancellation by order query."""
    await adapter.cancel(identifier)
    for attempt in range(20):
        order = await adapter.order(identifier)
        if order is not None:
            validate_order(order, plan, identifier)
            if order.state == "cancelled":
                return
            if order.state != "open":
                raise LifecycleError("unexpected order status after cancellation")
        if attempt == 19:
            raise LifecycleError("cancellation was not confirmed by order query")
        await asyncio.sleep(poll_delay)


def check_unfilled(order: Order) -> None:
    if order.filled != 0 or not order.filled.is_finite():
        raise LifecycleError("UNEXPECTED FILL: stop; position was not automatically closed")


async def confirm_replaced(adapter: Adapter, previous: str, poll_delay: float) -> None:
    """A cancel-replace amendment must leave the previous order ID closed and unfilled."""
    for attempt in range(20):
        order = await adapter.order(previous)
        if order is not None:
            check_unfilled(order)
        if order is None or order.state != "open":
            return
        if attempt == 19:
            raise LifecycleError("replaced order ID is still open after amendment")
        await asyncio.sleep(poll_delay)


async def confirm_amended(
    adapter: Adapter,
    previous: str,
    identifier: str,
    plan: Plan,
    amended: Plan,
    poll_delay: float,
) -> None:
    """The order now rests at the new price with the same size; a replaced ID is closed."""
    for attempt in range(20):
        order = await adapter.order(identifier)
        if order is not None:
            check_unfilled(order)
            # An in-place amendment may briefly still show the previous price.
            stale = identifier == previous and order.price == plan.price
            if not (stale and order.state == "open"):
                validate_order(order, amended, identifier)
                if order.state != "open":
                    raise LifecycleError("amended order is not resting open")
                break
        if attempt == 19:
            raise LifecycleError("amended price was not confirmed by order query")
        await asyncio.sleep(poll_delay)
    if identifier != previous:
        await confirm_replaced(adapter, previous, poll_delay)


async def run_lifecycle(
    adapter: Adapter,
    result: dict[str, str],
    *,
    poll_delay: float = 0.25,
    case: str = "lifecycle",
) -> None:
    """Retry only explicit price rejections; cancel only the accepted test order.

    Cases (every price stays strictly below the bid, inside the price bands):
    "lifecycle" rests post-only and cancels; "ioc"/"fok" must end unfilled and not open;
    "reduce_only" (no position) must be rejected or end unfilled, and is cancelled if it
    rests; "amend" rests post-only, moves one tick lower, confirms, then cancels.
    """
    identifier = None
    cancelled = False
    placement_started = False
    amend_started = False
    replaced: list[str] = []
    client_ids: list[str] = []
    rejected_ids: list[str] = []
    outcome = ""
    result["case"] = case
    try:
        result["stage"] = "preflight"
        reason = not_applicable(
            str(getattr(adapter, "exchange", "")), str(getattr(adapter, "market", "")), case
        )
        if reason:
            result["stage"] = "not_applicable"
            raise NotApplicable(reason)
        adapter.case = case  # type: ignore[attr-defined]
        if await adapter.positions():
            raise LifecycleError("existing position: manual reconciliation required")
        if await adapter.open_orders():
            raise LifecycleError("existing open orders: no order was submitted")
        plan, available = await adapter.prepare()
        amended = plan
        while True:
            if case == "amend":
                plan, amended = amend_plans(plan)
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
            if case in {"ioc", "fok"}:
                try:
                    check_taker_price(plan, bid)
                except NotApplicable:
                    result["stage"] = "not_applicable"
                    raise
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
                if case in {"ioc", "fok"}:
                    # Never ladder a taker order toward the bid.
                    result["stage"] = "not_applicable"
                    raise NotApplicable(
                        TAKER_BAND_NA + " (exchange rejected the price band)"
                    ) from None
                next_plan = getattr(adapter, "next_price_plan", None)
                if next_plan is None:
                    raise
                if await adapter.open_orders():
                    raise LifecycleError(
                        "open order present after rejected placement; stopped without retry"
                    ) from None
                plan, available = await next_plan()
            except OrderClosed as error:
                if case not in {"ioc", "fok"}:
                    raise
                # The venue reported the order killed unfilled; nothing rests.
                placement_started = False
                outcome = f"{case} order ended at placement unfilled: {redact(error)}"
                break
            except LifecycleError as error:
                exchange = str(getattr(adapter, "exchange", ""))
                if case != "reduce_only" or not explicit_rejection(error, exchange):
                    raise
                # Cleanup sweeps this client ID unless the run completes.
                rejected_ids.append(adapter.client_order_id)
                # Confirm nothing with this client ID appears despite the refusal.
                for attempt in range(4):
                    identifier = await adapter.recover_order()
                    if identifier or attempt == 3:
                        break
                    await asyncio.sleep(poll_delay)
                if identifier:
                    outcome = "reduce-only order accepted despite error: " + redact(error)
                    break
                placement_started = False
                result["error_code"] = redact(getattr(error, "code", ""))
                outcome = "reduce-only order rejected: " + redact(error)
                break
        fill = getattr(adapter, "placed_fill", None)
        if fill is not None and (not decimal(fill).is_finite() or decimal(fill) != 0):
            raise LifecycleError("UNEXPECTED FILL: stop; position was not automatically closed")
        if identifier:
            result["order_id"] = redact(identifier, mask_environment=False)
        elif not outcome:
            raise LifecycleError("exchange acknowledged no order ID; do not retry placement")
        if identifier and case in {"ioc", "fok"}:
            result["stage"] = "query_final"
            try:
                order = await query_order(adapter, identifier, plan, poll_delay, final=True)
            except LifecycleError as error:
                if "not found" not in str(error) or fill is None:
                    raise
                # Not retained by the venue; the placement response proved a zero fill.
                outcome = f"{case} order not queryable; placement reported zero fill"
            else:
                if order.state not in TERMINAL_UNFILLED:
                    raise LifecycleError(f"unexpected {case} order status: {order.state}")
                outcome = f"{case} order ended {order.state} with zero fill"
            cancelled = True
        elif identifier and case == "reduce_only":
            result["stage"] = "query_open"
            order = await query_order(adapter, identifier, plan, poll_delay)
            if order.state == "open":
                note = "accepted resting (pass with note): reduce-only order cancelled"
                outcome = "; ".join(filter(None, (outcome, note)))
                result["stage"] = "cancel"
                await cancel_confirmed(adapter, identifier, plan, poll_delay)
            elif order.state in TERMINAL_UNFILLED:
                note = f"reduce-only order accepted, then {order.state} by the exchange"
                outcome = "; ".join(filter(None, (outcome, note)))
            else:
                raise LifecycleError("unexpected reduce-only order status: " + order.state)
            cancelled = True
        elif identifier:
            result["stage"] = "query_open"
            order = await query_order(adapter, identifier, plan, poll_delay)
            if order.state != "open":
                raise LifecycleError("new limit order is not resting open")
            if case == "amend":
                result["stage"] = "amend"
                previous = identifier
                amend_started = True
                new = await adapter.amend(identifier, amended)  # type: ignore[attr-defined]
                if not new:
                    raise LifecycleError("amendment acknowledged no order ID")
                amend_started = False
                if new != previous:
                    # Cancel-replace: track (and later cancel) the new ID from here on.
                    replaced.append(previous)
                    identifier = new
                    result["order_id"] = (
                        redact(previous, mask_environment=False)
                        + "->"
                        + redact(new, mask_environment=False)
                    )
                result["price"] = str(amended.price)
                result["stage"] = "query_amended"
                await confirm_amended(adapter, previous, identifier, plan, amended, poll_delay)
                plan = amended
                result["client_order_id"] = adapter.client_order_id
                if adapter.client_order_id not in client_ids:
                    client_ids.append(adapter.client_order_id)
                result["prior_client_order_ids"] = ",".join(client_ids)
                outcome = "amended one tick lower; new price and same size confirmed"
            result["stage"] = "cancel"
            await cancel_confirmed(adapter, identifier, plan, poll_delay)
            cancelled = True
        result["stage"] = "verify_clean"
        if await adapter.open_orders():
            raise LifecycleError("open orders remain after cancellation")
        if await adapter.positions():
            raise LifecycleError("UNEXPECTED POSITION: stop; no automatic close was attempted")
        result["cleanup"] = (
            outcome + "; no open orders or positions remain"
            if outcome
            else "cancellation confirmed; no open orders or positions remain"
        )
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
        if identifier and not cancelled and (replaced or amend_started):
            # A failed amendment may have replaced the order under an unknown ID: cancel
            # every order ID and client ID this run ever held, or fail loudly.
            held = [*client_ids, *getattr(adapter, "held_client_ids", [])]
            held.append(adapter.client_order_id)
            await cleanup_amend(adapter, [identifier, *replaced], held, result, poll_delay)
        elif identifier and not cancelled:
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
        sweep_error = None
        if rejected_ids and result.get("stage") != "complete":
            # Only this run's explicitly rejected client IDs; never other open orders.
            try:
                await cleanup_client_ids(adapter, rejected_ids, result, poll_delay)
            except LifecycleError as error:
                # Still run the position check below before failing.
                sweep_error = error
        if placement_started and not cancelled:
            try:
                remaining_positions = await adapter.positions()
            except Exception:
                result["cleanup"] = (
                    result.get("cleanup", "")
                    + "; position check unconfirmed; manual reconciliation required"
                )
            else:
                if remaining_positions:
                    warning = "UNEXPECTED POSITION: stop; no automatic close was attempted"
                    result["cleanup"] = result.get("cleanup", "") + "; " + warning
                    result["error_message"] = result.get("error_message", "") + "; " + warning
                    raise LifecycleError(result["error_message"])
        if sweep_error is not None:
            raise sweep_error


async def cleanup_amend(
    adapter: Adapter,
    identifiers: list[str],
    client_ids: list[str],
    result: dict[str, str],
    poll_delay: float,
) -> None:
    """Cancel every held order ID, sweep every held client ID with polling, then confirm."""
    order_ids = list(dict.fromkeys(identifiers))
    client_ids = list(dict.fromkeys(client_ids))
    for identifier in order_ids:
        try:
            await adapter.cancel(identifier)
        except Exception:
            pass  # A replaced ID is usually already cancelled.
    recover = getattr(adapter, "recover_client_order", None)
    confirmed = False
    for attempt in range(20):
        try:
            found = []
            if recover is not None:
                for client_id in client_ids:
                    order_id = await recover(client_id)
                    if order_id:
                        found.append(order_id)
                        order_ids.append(order_id)
                        await adapter.cancel(order_id)
            # Late replacements may still appear: require a few clean sweeps first.
            if not found and attempt >= 2 and not await adapter.open_orders():
                confirmed = recover is not None
                break
        except Exception:
            pass
        await asyncio.sleep(poll_delay)
    if not confirmed:
        message = (
            "AMEND CLEANUP UNCONFIRMED: inspect order IDs "
            + ",".join(redact(item, mask_environment=False) for item in dict.fromkeys(order_ids))
            + " and client IDs "
            + ",".join(client_ids)
            + " manually"
        )
        result["cleanup"] = message
        result["error_message"] = "; ".join(filter(None, (result.get("error_message"), message)))
        raise LifecycleError(result["error_message"])
    result["cleanup"] = (
        "amend cleanup: every held order ID and client ID cancelled; no open orders remain"
    )


async def cleanup_client_ids(
    adapter: Adapter, client_ids: list[str], result: dict[str, str], poll_delay: float
) -> None:
    """Cancel any still-open order carrying one of this run's rejected client IDs."""
    recover = getattr(adapter, "recover_client_order", None)
    notes = []
    unconfirmed = []
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
            unconfirmed.append(client_id)
            notes.append(
                "rejected-attempt client ID " + client_id + " unconfirmed; inspect manually"
            )
    if notes:
        result["cleanup"] = "; ".join(filter(None, (result.get("cleanup", ""), *notes)))
    if unconfirmed:
        # Never let an unconfirmed sweep end as N/A or skipped: fail loudly.
        message = "REJECTED CLIENT ID CLEANUP UNCONFIRMED: " + ",".join(unconfirmed)
        result["stage"] = "cleanup"
        result["error_message"] = "; ".join(filter(None, (result.get("error_message"), message)))
        raise LifecycleError(result["error_message"])
