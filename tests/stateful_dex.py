"""Explicit DEX order protocols, verified against official API response schemas."""

import asyncio
import json
import re
import time
from decimal import Decimal
from uuid import uuid4

from scripts.live.redaction import redact
from tests.stateful_adapters import CexAdapter, checked_id, rows
from tests.stateful_lifecycle import (
    LifecycleError,
    MarketUnavailable,
    Order,
    OrderClosed,
    OrderRejected,
    Rules,
    decimal,
    order_state,
    plan_order,
)


def best(bids, asks, price):
    """Return the best bid and ask whatever order the venue lists its levels in."""
    if not bids or not asks:
        raise LifecycleError("order book has an empty side")
    return max(decimal(price(row)) for row in bids), min(decimal(price(row)) for row in asks)


class ExtendedAdapter(CexAdapter):
    async def book(self):
        data = await self.call("get_order_book", market=self.native)
        return best(data["bid"], data["ask"], lambda row: row["price"])

    async def positions(self):
        return [row for row in rows(await self.call("get_positions")) if decimal(row["size"]) != 0]

    async def open_orders(self):
        return rows(await self.call("get_open_orders"))

    async def available(self):
        data = await self.call("get_balance")
        available = decimal(data["availableForTrade"])
        if self.spot:
            available = min(
                available,
                decimal(data["balance"]) - decimal(data["collateralReservedForSpotOrders"]),
            )
        return available

    async def prepare(self):
        market = next(
            row
            for row in rows(await self.call("get_markets", market=self.native))
            if row["name"] == self.native
        )
        if market["status"] != "ACTIVE" or market["isRfq"] or market["isOffHours"]:
            raise MarketUnavailable(
                f"extended {self.market}: market inactive, RFQ-only, or outside trading hours"
            )
        config = market["tradingConfig"]
        reference = decimal(market["marketStats"]["indexPrice" if self.spot else "markPrice"])
        cap = decimal(config["limitPriceCap"])
        if reference <= 0 or cap < 0:
            raise LifecycleError("extended: invalid limit price bounds")
        rules = Rules(
            decimal(config["minPriceChange"]),
            decimal(config["minOrderSizeChange"]),
            decimal(config["minOrderSize"]),
            Decimal(0),
            # The official floor applies to short/sell orders, not this buy.
            upper_price=reference * (1 + cap),
        )
        bid, ask = await self.book()
        return plan_order(self.native, bid, ask, rules), await self.available()

    async def place(self, plan):
        try:
            data = await self.call(
                "place_limit_order",
                market=self.native,
                side="BUY",
                qty=str(plan.size),
                price=str(plan.price),
                # Extended supports GTT and IOC only; IOC cannot be post-only.
                post_only=self.tif is None,
                time_in_force=self.tif or "GTT",
                **({"reduce_only": True} if self.reduce else {}),
                expiry_epoch_millis=int(time.time() * 1000) + 300000,
                external_id=self.client_order_id,
            )
        except LifecycleError as error:
            # Extended 1153 "Market is not allowed for clients": an explicit rejection,
            # so no order exists. Spot markets are not open to clients yet.
            if self.spot and "1153" in str(error):
                raise MarketUnavailable(
                    "extended spot: market is not open to clients (code 1153)"
                ) from None
            raise
        return checked_id(data["id"])

    async def cancel(self, identifier):
        await self.call("cancel_order", id=identifier)

    async def order(self, identifier):
        try:
            data = await self.call("get_order", id=identifier)
        except LifecycleError as error:
            # Extended briefly answers 404 Not Found right after a cancel: not yet visible.
            if str(getattr(error, "code", "")) == "404" or re.search(r"\b404\b", str(error)):
                return None
            raise
        return Order(
            checked_id(data["id"]),
            data["market"],
            data["side"].lower(),
            data["type"].lower(),
            decimal(data["price"]),
            decimal(data["qty"]),
            decimal(data["filledQty"]),
            order_state(data["status"]),
        )


class OndoAdapter(CexAdapter):
    async def book(self):
        data = await self.call("get_depth", market=self.native, depth=5)
        return best(data["bids"], data["asks"], lambda row: row[0])

    async def positions(self):
        return [
            row
            for row in rows(await self.call("get_positions"))
            if decimal(row["netQuantity"]) != 0
        ]

    async def open_orders(self):
        return rows(await self.call("get_open_orders"))

    async def available(self):
        return decimal((await self.call("get_balance"))["availableMargin"])

    async def place(self, plan):
        data = await self.call(
            "place_order",
            market=self.native,
            side="buy",
            type="limit",
            price=str(plan.price),
            size=str(plan.size),
            # Live: Ondo accepts reduce-only only as IOC (reduce_only_invalid_tif).
            **(
                {"timeInForce": self.tif or "IOC"}
                if self.tif or self.reduce
                else {"timeInForce": "GTC", "postOnly": True}
            ),
            **({"reduceOnly": True} if self.reduce else {}),
            clientOrderId=self.client_order_id,
        )
        self.record_fill(data)
        return checked_id(data["orderId"])

    async def cancel(self, identifier):
        await self.call("cancel_order", orderID=identifier)

    async def order(self, identifier):
        data = await self.call("get_order", orderID=identifier)
        return Order(
            checked_id(data["orderId"]),
            data["market"],
            data["side"],
            data["type"],
            decimal(data["price"]),
            decimal(data["size"]),
            decimal(data["filledSize"]),
            order_state(data["status"]),
        )


# userAbstraction modes whose USDC perp collateral is the spot balance (official docs:
# trading/account-abstraction-modes); "disabled"/"default" keep separate perp balances.
UNIFIED_ABSTRACTIONS = frozenset({"unifiedAccount", "portfolioMargin"})


class HyperliquidAdapter(CexAdapter):
    def __init__(self, client, exchange, market, symbol):
        super().__init__(client, exchange, market, symbol)
        self.native = json.loads(self.native)[0]
        self.user = client.wallet_address
        self.client_order_id = "0x" + uuid4().hex
        self.started = int(time.time() * 1000)

    async def owner(self):
        """Resolve an API agent wallet to the account owner that holds the balances."""
        role = await self.call("user_role", user=self.user)
        if role["role"] == "agent":
            self.user = role["data"]["user"]
        return self.user

    async def unified(self):
        """Unified/portfolio-margin accounts keep perp collateral in the spot clearinghouse."""
        mode = await self.call("get_user_abstraction", user=await self.owner())
        return mode in UNIFIED_ABSTRACTIONS

    async def positions(self):
        data = await self.call("clearinghouse_state", user=await self.owner())
        return [row for row in rows(data["assetPositions"]) if decimal(row["position"]["szi"]) != 0]

    async def open_orders(self):
        return rows(await self.call("open_orders", user=self.user))

    async def book(self):
        data = await self.call("get_l2book", product_symbol=self.symbol)
        return best(data["levels"][0], data["levels"][1], lambda row: row["px"])

    async def available(self):
        if not self.spot and not await self.unified():
            return decimal((await self.call("clearinghouse_state", user=self.user))["withdrawable"])
        data = await self.call("spot_clearinghouse_state", user=await self.owner())
        return sum(
            (
                decimal(row["total"]) - decimal(row["hold"])
                for row in rows(data["balances"])
                if row["coin"] == "USDC"
            ),
            Decimal(0),
        )

    async def prepare(self):
        bid, ask = await self.book()
        d = self.details
        # price_precision is the MAX_DECIMALS - szDecimals cap; prices are also limited to five
        # significant figures. The coarser of both at the bid's magnitude stays valid below it.
        tick = max(decimal(d["price_precision"]), Decimal(1).scaleb(bid.adjusted() - 4))
        rules = Rules(
            tick,
            decimal(d["size_precision"]),
            decimal(d["min_size"]),
            max(Decimal(10), decimal(d["min_notional"])),
        )
        return plan_order(self.native, bid, ask, rules), await self.available()

    @staticmethod
    def acknowledgement(data, kind):
        if data["status"] != "ok" or data["response"]["type"] != kind:
            raise LifecycleError("hyperliquid: exchange rejected operation")
        statuses = data["response"]["data"]["statuses"]
        if len(statuses) != 1:
            raise LifecycleError("hyperliquid: expected one operation status")
        return statuses[0]

    async def place(self, plan):
        if self.tif == "FOK":
            raise self.unsupported("FOK orders")
        data = await self.call(
            "place_order",
            product_symbol=self.symbol,
            isBuy=True,
            price=str(plan.price),
            size=str(plan.size),
            reduceOnly=self.reduce,
            tif="Ioc" if self.tif == "IOC" else "Alo",
            cloid=self.client_order_id,
        )
        status = self.acknowledgement(data, "order")
        if isinstance(status, dict) and "filled" in status:
            raise LifecycleError("UNEXPECTED FILL: stop; position was not automatically closed")
        if isinstance(status, dict) and isinstance(status.get("error"), str):
            message = "hyperliquid: " + redact(status["error"])
            if self.tif and "could not immediately match" in status["error"].lower():
                raise OrderClosed(message)
            raise OrderRejected(message)
        if not isinstance(status, dict) or "resting" not in status:
            raise LifecycleError(
                "hyperliquid: order did not rest; unexpected fill or rejection; inspect account"
            )
        return checked_id(status["resting"]["oid"])

    async def amend(self, identifier, plan):
        """Modify keeps the client ID; the order may get a new oid, so resolve it by cloid."""
        data = await self.call(
            "modify_order",
            oid=int(identifier),
            product_symbol=self.symbol,
            isBuy=True,
            price=str(plan.price),
            size=str(plan.size),
            reduceOnly=False,
            tif="Alo",
            cloid=self.client_order_id,
        )
        if data.get("status") != "ok":
            raise LifecycleError("hyperliquid: modification was rejected")
        for _ in range(20):
            matching = [
                row for row in await self.open_orders() if row.get("cloid") == self.client_order_id
            ]
            if len(matching) > 1:
                raise LifecycleError("hyperliquid: ambiguous client ID after modification")
            if matching:
                return checked_id(matching[0]["oid"])
            await asyncio.sleep(0.25)
        raise LifecycleError("hyperliquid: modified order not found by client ID")

    async def recover_client_order(self, client_order_id):
        """Only an open order with this cloid; cleanup polls until none remains."""
        matching = [row for row in await self.open_orders() if row.get("cloid") == client_order_id]
        if len(matching) > 1:
            raise LifecycleError("hyperliquid: ambiguous client ID")
        return checked_id(matching[0]["oid"]) if matching else None

    async def recover_order(self):
        data = await self.call("order_status", user=self.user, oid=self.client_order_id)
        if data["status"] == "unknownOid":
            return None
        row = data["order"]["order"]
        if row.get("cloid") != self.client_order_id:
            raise LifecycleError("hyperliquid: recovered order has a different client ID")
        return checked_id(row["oid"])

    async def cancel(self, identifier):
        status = self.acknowledgement(
            await self.call("cancel_order", product_symbol=self.symbol, oid=int(identifier)),
            "cancel",
        )
        if status != "success":
            raise LifecycleError("hyperliquid: cancellation was rejected")

    async def order(self, identifier):
        data = await self.call("order_status", user=self.user, oid=int(identifier))
        if data["status"] == "unknownOid":
            return None
        if data["status"] != "order":
            raise LifecycleError("hyperliquid: unrecognized order response")
        details = data["order"]
        row = details["order"]
        fills = rows(await self.call("user_fills_by_time", user=self.user, start_time=self.started))
        filled = sum(
            (decimal(fill["sz"]) for fill in fills if str(fill["oid"]) == identifier), Decimal(0)
        )
        if len(fills) >= 2000:
            raise LifecycleError("hyperliquid: fill query reached its page limit")
        if details["status"] == "filled" and filled == 0:
            raise LifecycleError("UNEXPECTED FILL: exchange reports filled; no automatic close")
        return Order(
            checked_id(row["oid"]),
            row["coin"],
            {"B": "buy", "A": "sell"}[row["side"]],
            row["orderType"].lower(),
            decimal(row["limitPx"]),
            decimal(row["origSz"]),
            filled,
            order_state(details["status"]),
        )


class LighterAdapter(CexAdapter):
    def __init__(self, client, exchange, market, symbol):
        self.client, self.exchange, self.market, self.symbol = client, exchange, market, symbol
        self.market_id = None
        self.client_index = uuid4().int & ((1 << 48) - 1)
        self.client_order_id = str(self.client_index)
        self.spot = False
        self.case = "lifecycle"
        self.placed_fill = None

    async def account(self):
        accounts = rows(
            (await self.call("get_account", by="index", value=str(self.client.account_index)))[
                "accounts"
            ]
        )
        if len(accounts) != 1:
            raise LifecycleError("lighter: expected exactly one account")
        return accounts[0]

    async def positions(self):
        return [
            row
            for row in rows((await self.account())["positions"])
            if decimal(row["position"]) != 0
        ]

    async def open_orders(self):
        return rows((await self.call("get_account_active_orders"))["orders"])

    async def book(self):
        data = await self.call("get_order_book_orders", market_id=self.market_id, limit=5)
        return best(data["bids"], data["asks"], lambda row: row["price"])

    async def available(self):
        return decimal((await self.account())["available_balance"])

    async def prepare(self):
        markets = rows((await self.call("get_order_book_details"))["order_book_details"])
        candidates = [
            row for row in markets if row["symbol"] == self.symbol and row["status"] == "active"
        ]
        if len(candidates) != 1:
            raise MarketUnavailable(f"lighter {self.market}: selected market unavailable")
        d = candidates[0]
        self.market_id = int(d["market_id"])
        self.price_scale = Decimal(10) ** int(d["price_decimals"])
        self.size_scale = Decimal(10) ** int(d["size_decimals"])
        rules = Rules(
            1 / self.price_scale,
            1 / self.size_scale,
            decimal(d["min_base_amount"]),
            decimal(d["min_quote_amount"]),
        )
        bid, ask = await self.book()
        return plan_order(str(self.market_id), bid, ask, rules), await self.available()

    async def query(self):
        orders = rows(
            (await self.call("get_account_orders", client_order_indexes=str(self.client_index)))[
                "orders"
            ]
        )
        matching = [row for row in orders if int(row["client_order_index"]) == self.client_index]
        if len(matching) > 1:
            raise LifecycleError("lighter: ambiguous client order index")
        return matching[0] if matching else None

    async def place(self, plan):
        if self.tif == "FOK":
            raise self.unsupported("FOK orders")
        await self.call(
            "create_order",
            market_index=self.market_id,
            client_order_index=self.client_index,
            base_amount=int(plan.size * self.size_scale),
            price=int(plan.price * self.price_scale),
            is_ask=False,
            order_type=0,
            # Official time-in-force: 0 IOC (expiry must be 0), 2 post-only.
            time_in_force=0 if self.tif == "IOC" else 2,
            reduce_only=self.reduce,
            order_expiry=0 if self.tif else int(time.time() * 1000) + 28 * 24 * 60 * 60 * 1000,
        )
        for _ in range(20):
            row = await self.query()
            if row is not None:
                return checked_id(row["order_index"])
            await asyncio.sleep(0.25)
        if self.reduce and not await self.positions():
            # Live: the sequencer drops a reduce-only order with no position; no order
            # (active or inactive) is ever created for the client index.
            raise OrderRejected(
                f"lighter: reduce-only order not created with no position (client index {self.client_index})"
            )
        raise LifecycleError(
            f"lighter: acknowledgement could not be resolved to an order ID; inspect client index {self.client_index}; do not retry placement"
        )

    async def recover_order(self):
        row = await self.query()
        return checked_id(row["order_index"]) if row is not None else None

    async def recover_client_order(self, client_order_id):
        """Only an active order with this client index."""
        matching = [
            row
            for row in await self.open_orders()
            if str(row.get("client_order_index")) == str(client_order_id)
        ]
        if len(matching) > 1:
            raise LifecycleError("lighter: ambiguous client order index")
        return checked_id(matching[0]["order_index"]) if matching else None

    async def cancel(self, identifier):
        await self.call("cancel_order", market_index=self.market_id, order_index=int(identifier))

    async def amend(self, identifier, plan):
        """Modify in place: the order index and client index are unchanged."""
        await self.call(
            "modify_order",
            market_index=self.market_id,
            order_index=int(identifier),
            base_amount=int(plan.size * self.size_scale),
            price=int(plan.price * self.price_scale),
        )
        return identifier

    async def order(self, identifier):
        row = await self.query()
        if row is None:
            return None
        return Order(
            checked_id(row["order_index"]),
            str(row["market_index"]),
            "sell" if row["is_ask"] else "buy",
            row["type"],
            decimal(row["price"]),
            decimal(row["initial_base_amount"]),
            decimal(row["filled_base_amount"]),
            order_state(row["status"]),
        )
