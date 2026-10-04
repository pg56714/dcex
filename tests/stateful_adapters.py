"""Explicit exchange adapters for the existing opt-in order tests."""

import asyncio
import inspect
import re
from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from scripts.live.redaction import redact
from tests.stateful_lifecycle import (
    LifecycleError,
    NotApplicable,
    Order,
    OrderClosed,
    OrderRejected,
    Rules,
    decimal,
    order_state,
    plan_order,
)

DISPLAY_NAMES = {
    "binance": "Binance",
    "aster": "Aster",
    "bybit": "Bybit",
    "okx": "OKX",
    "bitget": "Bitget",
    "bingx": "BingX",
    "mexc": "MEXC",
    "kucoin": "KuCoin",
    "lighter": "Lighter",
    "extended": "Extended",
    "ondo": "Ondo",
}


def body_error(exchange: str, code: object, message: object) -> LifecycleError:
    """A business rejection inside a 2xx body, in the library's shared error format."""
    name = DISPLAY_NAMES.get(exchange, exchange)
    error = LifecycleError(f"{name} API Error: [{redact(code)}] {redact(message)}")
    error.code = str(code)
    return error


# Documented refusals of an IOC/FOK that cannot fill immediately (never recorded).
TAKER_KILLED_AT_PLACEMENT = {
    "binance": ("[-5021]",),  # FOK order rejected: could not be filled immediately.
    "aster": ("[-5021]",),
    "backpack": ("Fill or kill order would not complete fill immediately",),
    "kraken": ("[EOrder] Unfilled FOK precheck",),  # Spot FOK refused before booking.
}

# Documented executed-quantity fields of placement acknowledgements.
FILL_FIELDS = ("executedQty", "executedQuantity", "cumExecQty", "accFillSz", "filledSize")


def rows(value, key=None):
    if key is not None:
        value = value[key]
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise LifecycleError("expected an explicit list of response records")
    return value


def balance(items, currency, asset_key, available_key):
    matching = [row for row in rows(items) if row[asset_key] == currency]
    if not matching:
        return Decimal(0)
    return sum((decimal(row[available_key]) for row in matching), Decimal(0))


def checked_id(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, str))
        or not str(value).strip()
        or str(value) in {"0", "None"}
    ):
        raise LifecycleError("exchange response is missing an order ID")
    return str(value)


def response_data(exchange, value):
    """Require each exchange's documented success indicator when it has one."""
    codes = {
        "bybit": ("retCode", "0"),
        "okx": ("code", "0"),
        "bitget": ("code", "00000"),
        "kucoin": ("code", "200000"),
        "bingx": ("code", "0"),
        "extended": ("status", "OK"),
        "ondo": ("success", "True"),
        "lighter": ("code", "200"),
    }
    if exchange in codes:
        field, expected = codes[exchange]
        if not isinstance(value, dict) or str(value.get(field)) != expected:
            if not isinstance(value, dict):
                raise body_error(exchange, "missing", "invalid response")
            # Extended nests {"error": {"code", "message"}}; Ondo uses error_code/error.
            nested = value["error"] if isinstance(value.get("error"), dict) else {}
            code = nested.get("code", value.get("error_code", value.get(field, "missing")))
            message = nested.get("message") or next(
                (value[k] for k in ("msg", "retMsg", "message", "error") if value.get(k)),
                "rejected",
            )
            raise body_error(exchange, code, message)
    if isinstance(value, dict) and exchange in {"binance", "aster", "mexc"}:
        if ("code" in value and str(value["code"]) != "0") or value.get("success") is False:
            message = value.get("msg", value.get("message", "rejected"))
            raise body_error(exchange, value.get("code", "missing"), message)
    if exchange == "kraken":
        if not isinstance(value, dict) or (
            value.get("error") != [] and value.get("result") != "success"
        ):
            raise LifecycleError("kraken: response did not contain a successful result")
        return value["result"] if "error" in value else value
    if exchange == "bybit":
        return value["result"]
    if exchange == "ondo":
        return value["result"]
    if exchange in {"bingx", "bitget", "kucoin", "extended"}:
        return value["data"]
    if exchange == "okx":
        for row in rows(value["data"]):
            if "sCode" in row and str(row["sCode"]) != "0":
                raise body_error(exchange, row["sCode"], row.get("sMsg", "rejected"))
        return value["data"]
    if exchange == "mexc" and isinstance(value, dict) and "success" in value:
        if value["success"] is not True or str(value.get("code")) != "0":
            raise LifecycleError("mexc: contract response did not confirm success")
        return value["data"]
    return value


class CexAdapter:
    """Spot and linear-contract lifecycle for exchanges with standard REST books."""

    def __init__(self, client, exchange, market, symbol):
        self.client = client
        self.exchange = exchange
        self.market = market
        self.symbol = symbol
        self.spot = market == "spot"
        self.native = client.ptm.get_exchange_symbol(exchange, symbol)
        self.details = client.ptm.get_trading_details(exchange, symbol)
        self.currency = symbol.split("-")[1]
        self.category = "SPOT" if self.spot else "USDT-FUTURES"
        self.position_side = None
        self.position_index = 0
        self.client_order_id = self.fresh_client_id()
        # Order-test case (see run_lifecycle) and any fill quantity the placement reported.
        self.case = "lifecycle"
        self.placed_fill = None
        # Client IDs created for cancel-replace amendments, recorded before sending.
        self.held_client_ids = []

    def fresh_client_id(self):
        return (
            str(uuid4().int & 0xFFFFFFFF)
            if self.exchange == "backpack"
            else str(uuid4())
            if self.exchange == "kraken"
            else "0" + uuid4().hex[:31]
        )

    @property
    def tif(self):
        """IOC/FOK for those cases; None means the post-only (maker) default."""
        return {"ioc": "IOC", "fok": "FOK"}.get(self.case)

    @property
    def reduce(self):
        return self.case == "reduce_only"

    def hedge_reduce(self, short_side, field, value):
        """Reduce-only buy: in hedge mode close the short side (the reduce flag is one-way
        only there); in one-way mode send the documented reduce-only flag."""
        position_field = {
            "binance": "positionSide",
            "aster": "positionSide",
            "okx": "posSide",
            "bitget": "pos_side",
            "bingx": "position_side",
        }[self.exchange]
        hedged = self.position_side in {"LONG", "long"}
        return {position_field: short_side} if hedged else {field: value}

    def unsupported(self, feature):
        label = self.exchange + (" spot" if self.spot else " futures")
        return NotApplicable(f"N/A: {label} has no {feature}")

    def record_fill(self, data):
        """Keep a fill quantity the placement response reports; absent stays unknown."""
        if isinstance(data, dict):
            for key in FILL_FIELDS:
                if key in data and data[key] not in (None, ""):
                    self.placed_fill = decimal(data[key])
                    return

    async def recover_order(self):
        """Find only this test's client ID after an uncertain placement response."""
        return await self.recover_client_order(self.client_order_id)

    async def recover_client_order(self, client_order_id):
        """Return the open order carrying exactly this client ID, if any."""
        client_field, order_field = {
            "binance": ("clientOrderId", "orderId"),
            "aster": ("clientOrderId", "orderId"),
            "bybit": ("orderLinkId", "orderId"),
            "okx": ("clOrdId", "ordId"),
            "bitget": ("clientOid", "orderId"),
            "bingx": ("clientOrderID" if self.spot else "clientOrderId", "orderId"),
            "mexc": ("clientOrderId" if self.spot else "externalOid", "orderId"),
            "kucoin": ("clientOid", "id"),
            "backpack": ("clientId", "id"),
            "kraken": ("cl_ord_id" if self.spot else "cliOrdId", "id" if self.spot else "order_id"),
            "extended": ("externalId", "id"),
            "ondo": ("clientOrderId", "orderId"),
        }[self.exchange]
        matching = [
            row
            for row in await self.open_orders()
            if str(row.get(client_field, "")) == client_order_id
        ]
        if len(matching) > 1:
            raise LifecycleError("ambiguous client order ID; manual reconciliation required")
        return checked_id(matching[0][order_field]) if matching else None

    async def call(self, method, **kwargs):
        try:
            value = getattr(self.client, method)(**kwargs)
            if inspect.isawaitable(value):
                value = await value
            return response_data(self.exchange, value)
        except Exception as error:
            message = redact(getattr(error, "message", str(error)))
            # Every exchange error reads "{Exchange} API Error: [{code}] {message} (HTTP n)".
            shared = re.search(r"API Error: \[([^\]]+)\]", message)
            code = shared.group(1) if shared else redact(getattr(error, "code", ""))
            label = ""
            if (
                self.exchange == "mexc"
                and not self.spot
                and any(
                    word in message.lower()
                    for word in ("permission", "not support api", "not authorized")
                )
            ):
                label = "exchange permission issue: "
            if (
                self.exchange == "extended"
                and self.spot
                and any(
                    word in message.lower()
                    for word in (
                        "eligib",
                        "permission",
                        "not enabled",
                        "not allowed",
                        "not authorized",
                    )
                )
            ):
                label = "account eligibility issue: "
            killed = TAKER_KILLED_AT_PLACEMENT.get(self.exchange, ())
            if self.tif and method.startswith("place") and any(k in message for k in killed):
                # The venue refused an IOC/FOK that could not fill at once: nothing rests.
                raise OrderClosed(f"{self.exchange} {method}: {message}") from None
            reported = LifecycleError(f"{self.exchange} {method}: {label}{message}")
            reported.code = code
            raise reported from None

    async def book(self):
        ex = self.exchange
        kw = {"product_symbol": self.symbol}
        if ex in {"binance", "aster", "kucoin"}:
            data = await self.call(
                "get_spot_orderbook" if self.spot else "get_futures_orderbook", **kw
            )
        elif ex == "bitget":
            data = await self.call("get_uta_orderbook", category=self.category, **kw)
        elif ex in {"bybit", "okx"}:
            data = await self.call("get_orderbook", **kw)
            if ex == "okx":
                data = rows(data)[0]
        elif ex == "bingx":
            data = await self.call("get_spot_orderbook" if self.spot else "get_orderbook", **kw)
        elif ex == "mexc":
            if not self.spot:
                data = await self.call("get_contract_ticker", **kw)
                return decimal(data["bid1"]), decimal(data["ask1"])
            data = await self.call("get_spot_orderbook", **kw)
        elif ex == "backpack":
            data = await self.call("get_order_book_depth", **kw)
        elif ex == "kraken":
            data = await self.call(
                "get_spot_orderbook" if self.spot else "get_futures_orderbook", **kw
            )
            data = next(iter(data.values())) if self.spot else data["orderBook"]
        else:
            raise LifecycleError("unsupported book adapter")
        bids, asks = (
            (data["b"], data["a"]) if ex in {"bybit", "bitget"} else (data["bids"], data["asks"])
        )
        if not bids or not asks:
            raise LifecycleError("order book has an empty side")
        # Level order differs by venue (Backpack and Kraken Futures list bids ascending).
        return max(decimal(row[0]) for row in bids), min(decimal(row[0]) for row in asks)

    async def available(self):
        ex, coin = self.exchange, self.currency
        if ex == "binance":
            data = await self.call(
                "get_account_balance", market_type="spot" if self.spot else "swap"
            )
            return balance(
                data["balances"] if self.spot else data,
                coin,
                "asset",
                "free" if self.spot else "availableBalance",
            )
        if ex == "aster":
            data = await self.call("get_spot_account" if self.spot else "get_futures_account")
            return balance(
                data["balances"] if self.spot else data["assets"],
                coin,
                "asset",
                "free" if self.spot else "availableBalance",
            )
        if ex == "bybit":
            data = await self.call("get_wallet_balance", coin=coin)
            wallets = rows(data["list"])
            if len(wallets) != 1:
                raise LifecycleError("expected one unified wallet")
            row = next(row for row in rows(wallets[0]["coin"]) if row["coin"] == coin)
            free = decimal(row["walletBalance"]) - decimal(row["locked"])
            # Reserve both existing position and order initial margin in addition
            # to locked spot funds. Never substitute equity for spendable funds.
            for key in ("totalPositionIM", "totalOrderIM"):
                free -= decimal(row[key])
            return max(Decimal(0), free)
        if ex == "okx":
            data = await self.call("get_account_balance", ccy=[coin])
            return balance(rows(data)[0]["details"], coin, "ccy", "availBal")
        if ex == "bitget":
            data = await self.call("get_uta_account_assets")
            return balance(data["assets"], coin, "coin", "available")
        if ex == "bingx":
            data = await self.call(
                "get_spot_account_balance" if self.spot else "get_swap_account_balance"
            )
            if self.spot:
                return balance(data["balances"], coin, "asset", "free")
            if isinstance(data, list):
                return balance(data, coin, "asset", "availableMargin")
            return decimal(data["balance"]["availableMargin"])
        if ex == "mexc":
            if self.spot:
                data = await self.call("get_spot_account")
                return balance(data["balances"], coin, "asset", "free")
            return decimal(
                (await self.call("get_contract_asset", currency=coin))["availableBalance"]
            )
        if ex == "kucoin":
            if self.spot:
                data = await self.call("get_account_balance", currency=coin, type="trade")
                return balance(data, coin, "currency", "available")
            return decimal(
                (await self.call("get_futures_account", currency=coin))["availableBalance"]
            )
        if ex == "backpack":
            # Orders use autoLendRedeem, so lent USDC counts; any existing debt stops the test.
            data = await self.call("get_private_collateral")
            if decimal(data["borrowLiability"]) != 0:
                raise LifecycleError("backpack: existing borrow liability; no order was submitted")
            row = next((r for r in rows(data["collateral"]) if r["symbol"] == coin), None)
            if row is None:
                return Decimal(0)
            return decimal(row["availableQuantity"]) + decimal(row["lendQuantity"])
        if ex == "kraken":
            if self.spot:
                data = await self.call("get_spot_account_balance")
                return decimal(data.get(coin, data.get("Z" + coin, "0")))
            data = await self.call("get_futures_accounts")
            return decimal(data["accounts"]["flex"]["availableMargin"])
        raise LifecycleError("unsupported balance adapter")

    async def prepare(self):
        values = self.details
        rules = Rules(
            decimal(values["price_precision"]),
            decimal(values["size_precision"]),
            decimal(values["min_size"]),
            decimal(values["min_notional"]),
            decimal(values["size_per_contract"]),
        )
        bid, ask = await self.book()
        if self.exchange in {"binance", "aster"}:
            info = await self.call(
                "get_spot_exchange_info" if self.spot else "get_futures_exchange_info"
            )
            market = next(row for row in rows(info["symbols"]) if row["symbol"] == self.native)
            filters = {row["filterType"]: row for row in rows(market["filters"])}
            percent = filters.get("PERCENT_PRICE_BY_SIDE", filters.get("PERCENT_PRICE"))
            lower, upper = Decimal(0), None
            if percent:
                if self.exchange == "aster" and self.spot:
                    # Aster spot bands use an index price (PERCENT_PRICE) and a 5-minute
                    # average (PERCENT_PRICE_BY_SIDE) but expose neither. The best bid is the
                    # reference; take the tighter band. A wrong reference can only cause a
                    # rejection, never a fill, because the price stays below the bid.
                    bands = [
                        filters[name]
                        for name in ("PERCENT_PRICE", "PERCENT_PRICE_BY_SIDE")
                        if name in filters
                    ]
                    down = max(
                        decimal(band.get("bidMultiplierDown", band.get("multiplierDown")))
                        for band in bands
                    )
                    up = min(
                        decimal(band.get("bidMultiplierUp", band.get("multiplierUp")))
                        for band in bands
                    )
                    lower, upper = bid * down, bid * up
                else:
                    reference = await self.call(
                        "get_spot_average_price" if self.spot else "get_futures_premium_index",
                        product_symbol=self.symbol,
                    )
                    reference = decimal(reference["price"] if self.spot else reference["markPrice"])
                    lower = reference * decimal(
                        percent.get("bidMultiplierDown", percent.get("multiplierDown"))
                    )
                    upper = reference * decimal(
                        percent.get("bidMultiplierUp", percent.get("multiplierUp"))
                    )
            price_filter = filters.get("PRICE_FILTER", {})
            if price_filter.get("minPrice") and decimal(price_filter["minPrice"]) > 0:
                lower = max(lower, decimal(price_filter["minPrice"]))
            if price_filter.get("maxPrice") and decimal(price_filter["maxPrice"]) > 0:
                maximum = decimal(price_filter["maxPrice"])
                upper = maximum if upper is None else min(upper, maximum)
            rules = replace(rules, lower_price=lower or None, upper_price=upper)
        elif self.exchange == "okx":
            data = rows(await self.call("get_price_limit", product_symbol=self.symbol))[0]
            if str(data["enabled"]).lower() == "true":
                rules = replace(rules, upper_price=decimal(data["buyLmt"]))
        elif self.exchange == "bybit" and not self.spot:
            data = await self.call(
                "get_order_price_limit", product_symbol=self.symbol, category="linear"
            )
            rules = replace(rules, upper_price=decimal(data["buyLmt"]))
        elif self.exchange == "bitget":
            kw = {"category": self.category, "product_symbol": self.symbol}

            def matching(data):
                found = [row for row in rows(data) if row.get("symbol") == self.native]
                if len(found) != 1:
                    raise LifecycleError(f"bitget {self.native}: instrument not found exactly once")
                return found[0]

            ratio = decimal(
                matching(await self.call("get_uta_instruments", **kw))["buyLimitPriceRatio"]
            )
            ticker = matching(await self.call("get_uta_tickers", **kw))
            reference = decimal(ticker["lastPrice" if self.spot else "markPrice"])
            # Official UTA docs: buyLimitPriceRatio caps the highest buy price relative to the
            # market price; there is no documented lower bound for buys.
            rules = replace(rules, upper_price=reference * (1 + ratio))
        elif self.exchange == "backpack":
            market = await self.call("get_market", product_symbol=self.symbol)
            band = market["filters"]["price"].get("meanMarkPriceBand")
            if band:
                # Spot has no public mark price; the last price is the closest public reference.
                if self.spot:
                    data = await self.call("get_ticker", product_symbol=self.symbol)
                    reference = decimal(data["lastPrice"])
                else:
                    data = rows(await self.call("get_mark_prices", product_symbol=self.symbol))
                    reference = decimal(data[0]["markPrice"])
                rules = replace(
                    rules,
                    lower_price=reference * decimal(band["minMultiplier"]),
                    upper_price=reference * decimal(band["maxMultiplier"]),
                )
        return plan_order(self.native, bid, ask, rules), await self.available()

    async def positions(self):
        if self.spot:
            return []
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        if ex == "binance":
            mode = await self.call("get_futures_position_mode")
            if not isinstance(mode["dualSidePosition"], bool):
                raise LifecycleError("unrecognized Binance position mode")
            self.position_side = "LONG" if mode["dualSidePosition"] is True else "BOTH"
            data, key = await self.call("get_future_position"), "positionAmt"
        elif ex == "aster":
            mode = await self.call("get_futures_position_mode")
            if not isinstance(mode["dualSidePosition"], bool):
                raise LifecycleError("unrecognized Aster position mode")
            self.position_side = "LONG" if mode["dualSidePosition"] is True else "BOTH"
            data, key = await self.call("get_futures_position_risk"), "positionAmt"
        elif ex == "bybit":
            data, key = (await self.call("get_positions", category="linear", **kw))["list"], "size"
            self.position_index = 1 if any(row["positionIdx"] == 1 for row in rows(data)) else 0
        elif ex == "okx":
            mode = rows(await self.call("get_account_config"))[0]["posMode"]
            if mode not in {"long_short_mode", "net_mode"}:
                raise LifecycleError("unrecognized OKX position mode")
            self.position_side = "long" if mode == "long_short_mode" else "net"
            data, key = await self.call("get_positions"), "pos"
        elif ex == "bitget":
            data, key = (
                # Bitget returns "list": null when there are no positions.
                (await self.call("get_uta_positions", category=self.category))["list"] or [],
                "total",
            )
            mode = (await self.call("get_uta_settings"))["holdMode"]
            if mode not in {"hedge_mode", "one_way_mode"}:
                raise LifecycleError("unrecognized Bitget position mode")
            self.position_side = "long" if mode == "hedge_mode" else None
        elif ex == "bingx":
            mode = str((await self.call("get_position_mode"))["dualSidePosition"]).lower()
            if mode not in {"true", "false"}:
                raise LifecycleError("unrecognized BingX position mode")
            self.position_side = "LONG" if mode == "true" else "BOTH"
            data, key = await self.call("get_open_positions"), "positionAmt"
        elif ex == "mexc":
            data, key = await self.call("get_contract_open_positions"), "holdVol"
        elif ex == "kucoin":
            data, key = await self.call("get_futures_positions"), "currentQty"
        elif ex == "backpack":
            data, key = await self.call("get_open_positions"), "netQuantity"
        elif ex == "kraken":
            data, key = (await self.call("get_futures_open_positions"))["openPositions"], "size"
        else:
            raise LifecycleError("unsupported positions adapter")
        return [row for row in rows(data) if decimal(row[key]) != 0]

    async def open_orders(self):
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        if ex in {"binance", "backpack"}:
            return rows(await self.call("get_open_orders", **kw))
        if ex == "bybit":
            return rows(
                (
                    await self.call(
                        "get_open_orders", category="spot" if self.spot else "linear", **kw
                    )
                )["list"]
            )
        if ex == "okx":
            return rows(await self.call("get_order_list", **kw))
        if ex == "bitget":
            return rows(
                (await self.call("get_uta_open_orders", category=self.category, **kw))["list"]
            )
        if ex == "bingx":
            data = await self.call("get_spot_open_orders" if self.spot else "get_open_orders", **kw)
            return rows(data["orders"])
        if ex == "mexc":
            data = await self.call(
                "get_spot_open_orders" if self.spot else "get_contract_open_orders", **kw
            )
            return rows(data)
        if ex == "aster":
            return rows(
                await self.call(
                    "get_spot_open_orders" if self.spot else "get_futures_open_orders", **kw
                )
            )
        if ex == "kucoin":
            data = await self.call(
                "get_spot_open_orders" if self.spot else "get_futures_order_list",
                **kw,
                **({} if self.spot else {"status": "active"}),
            )
            return rows(data["items"])
        if ex == "kraken":
            if self.spot:
                return [
                    dict(row, id=identifier)
                    for identifier, row in (await self.call("get_spot_open_orders"))["open"].items()
                ]
            return rows((await self.call("get_futures_open_orders"))["openOrders"])
        raise LifecycleError("unsupported open-order adapter")

    async def place(self, plan):
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        price, size = format(plan.price, "f"), format(plan.size, "f")
        tif, reduce = self.tif, self.reduce
        if reduce and self.spot:
            raise self.unsupported("reduce-only orders")
        if ex == "binance":
            if self.spot:
                kind = {"type_": "LIMIT", "timeInForce": tif} if tif else {"type_": "LIMIT_MAKER"}
            else:
                kind = {
                    "type_": "LIMIT",
                    "timeInForce": tif or "GTX",
                    "positionSide": self.position_side,
                    **(self.hedge_reduce("SHORT", "reduceOnly", "true") if reduce else {}),
                }
            data = await self.call(
                "place_order",
                **kw,
                **kind,
                newClientOrderId=self.client_order_id,
                side="BUY",
                quantity=size,
                price=price,
            )
            self.record_fill(data)
            return checked_id(data["orderId"])
        if ex == "aster":
            data = await self.call(
                "place_spot_order" if self.spot else "place_futures_order",
                **kw,
                newClientOrderId=self.client_order_id,
                side="BUY",
                type_="LIMIT",
                quantity=size,
                price=price,
                timeInForce=tif or "GTX",
                **{
                    **({} if self.spot else {"positionSide": self.position_side}),
                    **(self.hedge_reduce("SHORT", "reduceOnly", True) if reduce else {}),
                },
            )
            self.record_fill(data)
            return checked_id(data["orderId"])
        if ex == "bybit":
            data = await self.call(
                "place_order",
                **kw,
                orderLinkId=self.client_order_id,
                side="Buy",
                orderType="Limit",
                qty=size,
                price=price,
                timeInForce=tif or "PostOnly",
                # Hedge mode: positionIdx 2 is the short side a reduce-only buy closes.
                **(
                    {}
                    if self.spot
                    else {
                        "positionIdx": 2
                        if reduce and self.position_index == 1
                        else self.position_index
                    }
                ),
                **({"reduceOnly": True} if reduce else {}),
            )
            return checked_id(data["orderId"])
        if ex == "okx":
            data = await self.call(
                "place_order",
                **kw,
                tdMode="cash" if self.spot else "cross",
                clOrdId=self.client_order_id,
                side="buy",
                ordType={"IOC": "ioc", "FOK": "fok"}.get(tif or "", "post_only"),
                sz=size,
                px=price,
                **{
                    **({} if self.spot else {"posSide": self.position_side}),
                    **(self.hedge_reduce("short", "reduceOnly", True) if reduce else {}),
                },
            )
            return checked_id(rows(data)[0]["ordId"])
        if ex == "bitget":
            data = await self.call(
                "place_uta_order",
                **kw,
                category=self.category,
                client_oid=self.client_order_id,
                side="buy",
                order_type="limit",
                qty=size,
                price=price,
                time_in_force=tif.lower() if tif else "post_only",
                **{
                    **({} if self.position_side is None else {"pos_side": self.position_side}),
                    **(self.hedge_reduce("short", "reduce_only", "yes") if reduce else {}),
                },
            )
            return checked_id(data["orderId"])
        if ex == "bingx":
            data = await self.call(
                "place_spot_order" if self.spot else "place_swap_order",
                **kw,
                **(
                    {"new_client_order_id": self.client_order_id}
                    if self.spot
                    else {"client_order_id": self.client_order_id}
                ),
                side="BUY",
                type_="LIMIT",
                quantity=size,
                price=price,
                time_in_force=tif or "PostOnly",
                **{
                    **({} if self.spot else {"position_side": self.position_side}),
                    **(self.hedge_reduce("SHORT", "reduce_only", "true") if reduce else {}),
                },
            )
            record = data if self.spot else data["order"]
            self.record_fill(record)
            return checked_id(record["orderId"])
        if ex == "mexc":
            if self.spot:
                data = await self.call(
                    "place_spot_order",
                    **kw,
                    side="BUY",
                    type_={"IOC": "IMMEDIATE_OR_CANCEL", "FOK": "FILL_OR_KILL"}.get(
                        tif or "", "LIMIT_MAKER"
                    ),
                    quantity=size,
                    price=price,
                    newClientOrderId=self.client_order_id,
                )
                return checked_id(data["orderId"])
            # Opening orders must carry the account's current long-side margin type and
            # leverage (read-only GET /api/v1/private/position/leverage); never change them.
            # A reduce-only test closes the (absent) short: side 2 with the short row.
            longs = [
                row
                for row in rows(await self.call("get_contract_leverage", **kw))
                if str(row.get("positionType")) == ("2" if reduce else "1")
            ]
            if len(longs) != 1 or str(longs[0].get("openType")) not in {"1", "2"}:
                raise LifecycleError(
                    "mexc: current long openType/leverage unavailable; no order was submitted"
                )
            closing = {}
            if reduce:
                # Official GET /api/v1/private/position/position_mode: 1 hedge, 2 one-way.
                # Hedge: side 2 closes the short. One-way: reduceOnly applies (one-way only).
                mode = str(await self.call("get_contract_position_mode"))
                if mode not in {"1", "2"}:
                    raise LifecycleError(
                        "mexc: unknown contract position mode; no order was submitted"
                    )
                if mode == "2":
                    closing = {"reduceOnly": True, "positionMode": 2}
            data = await self.call(
                "place_contract_order",
                **kw,
                # Official sides: 1 open long, 2 close short (a reduce-only buy).
                side=2 if reduce else 1,
                **closing,
                # Official order types: 2 post-only maker, 3 IOC, 4 FOK.
                type_={"IOC": 3, "FOK": 4}.get(tif or "", 2),
                openType=int(longs[0]["openType"]),
                leverage=int(decimal(longs[0]["leverage"])),
                vol=size,
                price=price,
                externalOid=self.client_order_id,
            )
            # MEXC returns either the order ID or {"orderId": ..., "ts": ...}.
            return checked_id(data["orderId"] if isinstance(data, dict) else data)
        if ex == "kucoin":
            margin = {}
            if not self.spot:
                # Orders must match the symbol's current margin mode (else 330005); KuCoin
                # defaults to ISOLATED. Read the mode and its leverage; never change them.
                mode = (await self.call("get_futures_margin_mode", **kw))["marginMode"]
                if mode not in {"ISOLATED", "CROSS"}:
                    raise LifecycleError(
                        "kucoin: unknown futures margin mode; no order was submitted"
                    )
                leverage = Decimal(1)
                if mode == "CROSS":
                    cross = await self.call("get_futures_cross_margin_leverage", **kw)
                    leverage = decimal(cross["leverage"])
                margin = {"marginMode": mode, "leverage": str(int(leverage))}
            data = await self.call(
                "place_spot_order" if self.spot else "place_futures_order",
                **kw,
                side="buy",
                type_="limit",
                size=size,
                price=price,
                **({"timeInForce": tif} if tif else {"timeInForce": "GTC", "postOnly": True}),
                clientOid=self.client_order_id,
                **margin,
                **({"reduceOnly": True} if reduce else {}),
            )
            return checked_id(data["orderId"])
        if ex == "backpack":
            data = await self.call(
                "place_limit_order",
                **kw,
                side="Bid",
                clientId=int(self.client_order_id),
                quantity=size,
                price=price,
                **({"timeInForce": tif} if tif else {"timeInForce": "GTC", "postOnly": True}),
                **({"reduceOnly": True} if reduce else {}),
                # Lent USDC may fund the order (Backpack redeems it); never borrow.
                autoBorrow=False,
                autoLend=False,
                autoLendRedeem=True,
            )
            self.record_fill(data)
            return checked_id(data["id"])
        if ex == "kraken":
            if self.spot:
                data = await self.call(
                    "place_spot_order",
                    **kw,
                    side="buy",
                    ordertype="limit",
                    volume=size,
                    price=price,
                    **({"timeinforce": tif} if tif else {"timeinforce": "GTC", "oflags": "post"}),
                    cl_ord_id=self.client_order_id,
                )
                return checked_id(data["txid"][0])
            data = await self.call(
                "place_futures_order",
                **kw,
                side="buy",
                orderType={"IOC": "ioc", "FOK": "fok"}.get(tif or "", "post"),
                cliOrdId=self.client_order_id,
                size=size,
                limitPrice=price,
                **({"reduceOnly": True} if reduce else {}),
            )
            status = data["sendStatus"]["status"]
            if status in {"iocWouldNotExecute", "fokWouldNotExecute"} and tif:
                raise OrderClosed("kraken: " + status)
            if status == "wouldNotReducePosition":
                raise OrderRejected("kraken: " + status)
            if status in {"filled", "partiallyFilled"}:
                raise LifecycleError("UNEXPECTED FILL: stop; position was not automatically closed")
            if status != "placed":
                raise LifecycleError(
                    "kraken: futures order was not placed (" + redact(status) + ")"
                )
            return checked_id(data["sendStatus"]["order_id"])
        raise LifecycleError("unsupported placement adapter")

    async def amended_id(self, data, *paths):
        """Resolve a cancel-replace's new order ID from the response or this client ID."""
        for path in paths:
            value = data
            for key in path:
                value = value.get(key) if isinstance(value, dict) else None
            if value not in (None, ""):
                return checked_id(value)
        for attempt in range(20):
            found = await self.recover_order()
            if found:
                return found
            await asyncio.sleep(0.25 if attempt else 0)
        raise LifecycleError("replacement order ID unresolved; inspect client order ID manually")

    async def amend(self, identifier, plan):
        """Amend the resting order's price; return the order ID now holding it."""
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        price, size = format(plan.price, "f"), format(plan.size, "f")
        if ex == "binance" and self.spot:
            # Cancel-replace: the new order gets a new ID and a fresh client ID.
            self.client_order_id = self.fresh_client_id()
            self.held_client_ids.append(self.client_order_id)
            data = await self.call(
                "cancel_replace_spot_order",
                **kw,
                side="BUY",
                order_type="LIMIT_MAKER",
                cancel_replace_mode="STOP_ON_FAILURE",
                quantity=size,
                price=price,
                cancel_order_id=int(identifier),
                new_client_order_id=self.client_order_id,
            )
            if data.get("cancelResult") != "SUCCESS" or data.get("newOrderResult") != "SUCCESS":
                raise LifecycleError("binance: cancel-replace did not succeed")
            return checked_id(data["newOrderResponse"]["orderId"])
        if ex == "binance":
            data = await self.call(
                "amend_futures_order",
                **kw,
                side="BUY",
                quantity=size,
                price=price,
                order_id=int(identifier),
            )
            return checked_id(data["orderId"])
        if ex == "aster" and not self.spot:
            data = await self.call(
                "modify_futures_order", **kw, quantity=size, price=price, orderId=int(identifier)
            )
            return checked_id(data["orderId"])
        if ex == "bybit":
            data = await self.call("amend_order", **kw, orderId=identifier, price=price)
            return checked_id(data["orderId"])
        if ex == "okx":
            data = await self.call("amend_order", **kw, ordId=identifier, newPx=price)
            return checked_id(rows(data)[0]["ordId"])
        if ex == "bitget":
            data = await self.call(
                "modify_uta_order",
                **kw,
                category=self.category,
                order_id=identifier,
                qty=size,
                price=price,
            )
            return checked_id(data.get("orderId") or identifier)
        if ex == "bingx":
            # Swap amend_swap_order changes quantity only; both markets use cancel-replace.
            self.client_order_id = self.fresh_client_id()
            self.held_client_ids.append(self.client_order_id)
            common = dict(
                kw,
                cancel_replace_mode="STOP_ON_FAILURE",
                side="BUY",
                type_="LIMIT",
                quantity=size,
                price=price,
                # Live: spot cancelReplace accepts only IOC/POC; swap uses PostOnly.
                time_in_force="POC" if self.spot else "PostOnly",
            )
            if self.spot:
                data = await self.call(
                    "replace_spot_order",
                    **common,
                    cancel_order_id=int(identifier),
                    new_client_order_id=self.client_order_id,
                )
                return await self.amended_id(data, ("orderOpenResponse", "orderId"))
            data = await self.call(
                "replace_swap_order",
                **common,
                position_side=self.position_side,
                cancel_order_id=identifier,
                client_order_id=self.client_order_id,
            )
            return await self.amended_id(data, ("newOrderResponse", "orderId"))
        if ex == "mexc" and not self.spot:
            data = await self.call(
                "amend_contract_limit_order", orderId=identifier, price=price, vol=size
            )
            if isinstance(data, dict):
                data = data.get("orderId")
            return checked_id(data if data not in (None, "", True) else identifier)
        if ex == "kucoin" and self.spot:
            data = await self.call(
                "alter_spot_order", **kw, orderId=identifier, newPrice=price, newSize=size
            )
            return checked_id(data["newOrderId"])
        if ex == "kraken" and self.spot:
            data = await self.call(
                "amend_spot_order", txid=identifier, limit_price=price, post_only=True
            )
            if not data.get("amend_id"):
                raise LifecycleError("kraken: amendment was not acknowledged")
            return identifier
        if ex == "kraken":
            data = await self.call(
                "edit_futures_order", orderId=identifier, size=size, limitPrice=price
            )
            if data["editStatus"]["status"] != "edited":
                raise LifecycleError("kraken: futures edit rejected")
            return identifier
        raise self.unsupported("order amendment")

    async def cancel(self, identifier):
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        if ex == "binance":
            await self.call("cancel_order", **kw, orderId=int(identifier))
        elif ex == "aster":
            await self.call(
                "cancel_spot_order" if self.spot else "cancel_futures_order",
                **kw,
                orderId=int(identifier),
            )
        elif ex in {"bybit", "backpack"}:
            await self.call("cancel_order", **kw, orderId=identifier)
        elif ex == "okx":
            await self.call("cancel_order", **kw, ordId=identifier)
        elif ex == "bitget":
            await self.call("cancel_uta_order", order_id=identifier, category=self.category)
        elif ex == "bingx":
            await self.call(
                "cancel_spot_order" if self.spot else "cancel_swap_order",
                **kw,
                order_id=int(identifier),
            )
        elif ex == "mexc":
            if self.spot:
                await self.call("cancel_spot_order", **kw, orderId=identifier)
            else:
                data = await self.call("cancel_contract_order", order_id=identifier)
                if not data or any(str(row["errorCode"]) != "0" for row in rows(data)):
                    raise LifecycleError("mexc: contract cancellation rejected")
        elif ex == "kucoin":
            await self.call(
                "cancel_spot_order" if self.spot else "cancel_futures_order",
                orderId=identifier,
                **(kw if self.spot else {}),
            )
        elif ex == "kraken":
            data = await self.call(
                "cancel_spot_order" if self.spot else "cancel_futures_order",
                **({"txid": identifier} if self.spot else {"order_id": identifier}),
            )
            if self.spot and data["count"] != 1:
                raise LifecycleError("kraken: cancellation did not cancel the test order")
            if not self.spot and data["cancelStatus"]["status"] != "cancelled":
                raise LifecycleError("kraken: futures cancellation rejected")
        else:
            raise LifecycleError("unsupported cancellation adapter")

    async def order(self, identifier):
        ex, kw = self.exchange, {"product_symbol": self.symbol}
        if ex == "binance":
            data = await self.call("get_order", **kw, orderId=int(identifier))
        elif ex == "aster":
            data = await self.call(
                "get_spot_order" if self.spot else "get_futures_order",
                **kw,
                orderId=int(identifier),
            )
        elif ex == "bybit":
            category = "spot" if self.spot else "linear"
            data = rows(
                (
                    await self.call(
                        "get_open_orders", **kw, category=category, orderId=identifier, openOnly=0
                    )
                )["list"]
            )
            if not data:
                data = rows(
                    (
                        await self.call(
                            "get_order_history", **kw, category=category, orderId=identifier
                        )
                    )["list"]
                )
            if not data:
                return None
            data = data[0]
        elif ex == "okx":
            data = rows(await self.call("get_order", **kw, ordId=identifier))[0]
        elif ex == "bitget":
            data = await self.call("get_uta_order", order_id=identifier)
        elif ex == "bingx":
            data = await self.call(
                "get_spot_order" if self.spot else "get_order_detail",
                **kw,
                order_id=int(identifier),
            )
            if not self.spot:
                data = data["order"]
        elif ex == "mexc":
            data = await self.call(
                "get_spot_order" if self.spot else "get_contract_order",
                **({**kw, "orderId": identifier} if self.spot else {"order_id": identifier}),
            )
        elif ex == "kucoin":
            try:
                data = await self.call(
                    "get_spot_order" if self.spot else "get_futures_order",
                    **({**kw, "order_id": identifier} if self.spot else {"orderId": identifier}),
                )
            except LifecycleError as error:
                # Futures orders can be invisible for a moment right after placement.
                if "orderNotExist" in str(error):
                    return None
                raise
            # KuCoin briefly returns "data": null while an order changes state; poll again.
            if data is None:
                return None
        elif ex == "backpack":
            data = rows(await self.call("get_open_orders", **kw))
            data = [row for row in data if str(row["id"]) == identifier]
            if not data:
                data = rows(await self.call("get_order_history", **kw, orderId=identifier))
            if not data:
                return None
            data = data[0]
        elif ex == "kraken":
            if self.spot:
                data = (await self.call("get_spot_orders", txid=identifier)).get(identifier)
            else:
                records = rows(
                    (await self.call("get_futures_order_status", orderIds=[identifier]))["orders"]
                )
                data = records[0] if records else None
            if data is None:
                return None
        else:
            raise LifecycleError("unsupported query adapter")
        return normalize_order(ex, self.spot, data, identifier)


# Limit orders whose venue type name carries their time-in-force.
LIMIT_KINDS = frozenset(
    {"limit_maker", "post_only", "ioc", "fok", "immediate_or_cancel", "fill_or_kill"}
)


def normalize_order(exchange, spot, data, identifier):
    """Read documented fields explicitly; absent fill/identity fields fail closed."""
    if exchange in {"binance", "aster", "bingx"} or (exchange == "mexc" and spot):
        fields = ("orderId", "symbol", "side", "type", "price", "origQty", "executedQty", "status")
    elif exchange == "bybit":
        fields = (
            "orderId",
            "symbol",
            "side",
            "orderType",
            "price",
            "qty",
            "cumExecQty",
            "orderStatus",
        )
    elif exchange == "okx":
        fields = ("ordId", "instId", "side", "ordType", "px", "sz", "accFillSz", "state")
    elif exchange == "bitget":
        fields = (
            "orderId",
            "symbol",
            "side",
            "orderType",
            "price",
            "qty",
            "cumExecQty",
            "orderStatus",
        )
    elif exchange == "mexc":
        fields = ("orderId", "symbol", "side", "orderType", "price", "vol", "dealVol", "state")
    elif exchange == "kucoin":
        fields = (
            "id",
            "symbol",
            "side",
            "type",
            "price",
            "size",
            "dealSize",
            "active" if spot else "isActive",
        )
        values = [data[key] for key in fields]
        values[-1] = (
            "open"
            if values[-1] is True and (not spot or data["inOrderBook"] is True)
            else "cancelled"
            if values[-1] is False and data["cancelExist"] is True
            else "closed"
        )
    elif exchange == "backpack":
        fields = (
            "id",
            "symbol",
            "side",
            "orderType",
            "price",
            "quantity",
            "executedQuantity",
            "status",
        )
    elif exchange == "kraken" and spot:
        return Order(
            identifier,
            data["descr"]["pair"],
            data["descr"]["type"].lower(),
            data["descr"]["ordertype"].lower(),
            decimal(data["descr"]["price"]),
            decimal(data["vol"]),
            decimal(data["vol_exec"]),
            order_state(data["status"]),
        )
    elif exchange == "kraken":
        row = data["order"]
        return Order(
            str(row["orderId"]),
            row["symbol"],
            row["side"].lower(),
            "limit" if row["type"] == "ORDER" and decimal(row["limitPrice"]) > 0 else row["type"],
            decimal(row["limitPrice"]),
            decimal(row["quantity"]),
            decimal(row["filled"]),
            order_state(data["status"]),
        )
    else:
        raise LifecycleError("unsupported order response")
    if exchange != "kucoin":
        values = [data[key] for key in fields]
    oid, symbol, side, kind, price, size, filled, state = values
    state = order_state(state)
    side, kind = str(side).lower(), str(kind).lower()
    if kind in LIMIT_KINDS:
        kind = "limit"
    if exchange == "backpack":
        side = "buy" if side == "bid" else "sell" if side == "ask" else side
    if exchange == "mexc" and not spot:
        side = "buy" if side in {"1", "2"} else side  # open long or close short
        # Order types 1 limit, 2 post-only, 3 IOC, 4 FOK; states 2 open, 4 cancelled, 5 invalid.
        kind = "limit" if kind in {"1", "2", "3", "4"} else kind
        state = {"2": "open", "4": "cancelled", "5": "rejected"}.get(state, state)
    return Order(
        str(oid), symbol, side, kind, decimal(price), decimal(size), decimal(filled), state
    )
