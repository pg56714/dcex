"""Arcus perpetual lifecycle using the official REST OpenAPI response fields.

Sources: https://docs.arcus.xyz/api-reference/exchange/place-order.md and
https://docs.arcus.xyz/api-reference/public/get-order-status.md (2026-10-03).
"""

import time
import re
from decimal import Decimal
from uuid import uuid4

from tests.stateful_adapters import CexAdapter, checked_id, rows
from tests.stateful_lifecycle import (
    LifecycleError,
    MarketUnavailable,
    Order,
    PriceBandRejected,
    Rules,
    decimal,
    plan_order,
)

ARCUS_SPOT_NA = "Arcus spot is N/A: RFQ execution always trades; no resting-order lifecycle. Only get_balances is checked."


class ArcusAdapter(CexAdapter):
    def __init__(self, client, exchange, market, symbol):
        self.client = client
        self.exchange = exchange
        self.market = market
        self.native = symbol
        self.spot = False
        self.client_order_id = "0" + uuid4().hex[:31]
        self.price_step = 0

    async def next_price_plan(self):
        if self.price_step == 3:
            raise LifecycleError("arcus: price range rejected (OracleDeviation) at 0.5%; stopped")
        self.price_step += 1
        self.client_order_id = "0" + uuid4().hex[:31]
        return await self.prepare()

    async def book(self):
        data = await self.call("get_bbo", market=self.native)
        return decimal(data["bestBid"]["price"]), decimal(data["bestAsk"]["price"])

    async def positions(self):
        data = await self.call("get_positions")
        return [row for row in data["positions"].values() if decimal(row["size"]) != 0]

    async def open_orders(self):
        return rows(await self.call("get_open_orders"), "orders")

    async def recover_order(self):
        return await self.recover_client_order(self.client_order_id)

    async def recover_client_order(self, client_order_id):
        matching = [
            row for row in await self.open_orders() if row.get("clientId") == client_order_id
        ]
        if len(matching) > 1:
            raise LifecycleError("arcus: ambiguous client ID; manual reconciliation required")
        return checked_id(matching[0]["orderId"]) if matching else None

    async def prepare(self):
        markets = rows(await self.call("get_markets"), "markets")
        info = next(row for row in markets if row["marketDisplayName"] == self.native)
        if info["status"] != "ONLINE" or info["type"] != "PERPETUAL":
            raise MarketUnavailable("arcus: perpetual market is not online")
        bid, ask = await self.book()
        reference = decimal(info.get("oraclePrice") or info.get("markPrice"))
        if reference <= 0:
            raise LifecycleError("arcus: invalid oracle/mark reference price")
        lower = info["lowerTradingBound"]
        upper = info["upperTradingBound"]
        band_start = Decimal(0)
        plan = None
        for tier in rows(info["tickTiers"]):
            band_end = decimal(tier["upToPrice"]) if "upToPrice" in tier else None
            if band_end is not None and band_end <= band_start:
                raise LifecycleError("arcus: invalid tick tier bounds")
            candidate = plan_order(
                self.native,
                bid,
                ask,
                Rules(
                    decimal(tier["tick"]),
                    decimal(info["stepSize"]),
                    decimal(info["minOrderSize"]),
                    max(Decimal(5), decimal(info["minOrderNotional"])),
                    lower_price=None if lower is None else decimal(lower),
                    upper_price=None if upper is None else decimal(upper),
                ),
                # Move inward only after a definitive rejection, retaining ALO.
                target_price=min(
                    reference * Decimal(("0.95", "0.98", "0.99", "0.995")[self.price_step]),
                    bid - decimal(tier["tick"]),
                ),
            )
            if candidate.price >= band_start and (band_end is None or candidate.price < band_end):
                plan = candidate
                break
            if band_end is None:
                break
            band_start = band_end
        if plan is None:
            raise LifecycleError("arcus: no valid price in the documented tick tiers")
        if plan.size > decimal(info["maxOrderSize"]):
            raise MarketUnavailable("arcus: minimum notional exceeds maxOrderSize")
        return plan, await self.available()

    async def available(self):
        return decimal((await self.call("get_account"))["freeCollateral"])

    async def place(self, plan):
        data = await self.call(
            "place_order",
            product_symbol=self.native,
            side="BUY",
            price=str(plan.price),
            quantity=str(plan.size),
            order_type="LIMIT",
            time_in_force="ALO",
            good_til_time=int(time.time() * 1_000_000) + 32 * 86400 * 1_000_000,
            client_order_id=self.client_order_id,
        )
        if decimal(data.get("filledSize", "0")) != 0:
            raise LifecycleError("UNEXPECTED FILL: stop; no automatic close")
        if data.get("rejectionReason") == "OracleDeviation" and data.get("status") == "REJECTED":
            raise PriceBandRejected("arcus: price range rejected (OracleDeviation)")
        if data["status"] not in {"ACK", "PENDING", "OPEN"}:
            raise LifecycleError("arcus: order acknowledgement rejected")
        if data["marketDisplayName"] != self.native or data["clientId"] != self.client_order_id:
            raise LifecycleError("arcus: acknowledgement identity mismatch")
        return checked_id(data["orderId"])

    async def order(self, identifier):
        try:
            data = await self.call("get_order_status", order_id=identifier)
        except LifecycleError as error:
            if (
                str(getattr(error, "code", "")) == "404" or re.search(r"\b404\b", str(error))
            ) and "order not found" in str(error).lower():
                return None
            raise
        original = decimal(data["originalSize"])
        filled = (
            decimal(data["filledSize"])
            if "filledSize" in data
            else original - decimal(data["remainingSize"])
        )
        if filled == 0 and data["status"] in {
            "ACK",
            "PENDING",
            "CANCEL_PENDING",
            "CANCEL_ACKNOWLEDGED",
        }:
            return None
        return Order(
            checked_id(data["orderId"]),
            data["marketDisplayName"],
            data["side"].lower(),
            data["type"].lower(),
            decimal(data["price"]),
            original,
            filled,
            {"OPEN": "open", "CANCELED": "cancelled"}.get(data["status"], data["status"]),
        )

    async def cancel(self, identifier):
        data = await self.call("cancel_order", product_symbol=self.native, order_id=identifier)
        if decimal(data.get("filledSize", "0")) != 0:
            raise LifecycleError("UNEXPECTED FILL: stop; no automatic close")
        if (
            checked_id(data["orderId"]) != identifier
            or data["marketDisplayName"] != self.native
            or data["status"] not in {"CANCEL_ACKNOWLEDGED", "CANCELED"}
        ):
            raise LifecycleError("arcus: cancellation acknowledgement rejected or mismatched")
