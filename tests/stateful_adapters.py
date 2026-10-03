"""Explicit exchange adapters for the existing opt-in order tests."""

import inspect
from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from scripts.live.redaction import redact
from tests.stateful_lifecycle import (
    LifecycleError,
    MarketUnavailable,
    Order,
    Rules,
    decimal,
    plan_order,
)


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
            code = value.get(field, "missing") if isinstance(value, dict) else "missing"
            message = (
                value.get("msg", value.get("retMsg", value.get("message", "rejected")))
                if isinstance(value, dict)
                else "invalid response"
            )
            error = LifecycleError(f"{exchange}: code={redact(code)} {redact(message)}")
            error.code = str(code)
            raise error
    if isinstance(value, dict) and exchange in {"binance", "aster", "mexc"}:
        if ("code" in value and str(value["code"]) != "0") or value.get("success") is False:
            error = LifecycleError(
                f"{exchange}: code={redact(value.get('code'))} {redact(value.get('msg', value.get('message', 'rejected')))}"
            )
            error.code = str(value.get("code", "missing"))
            raise error
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
                raise LifecycleError(
                    f"okx: code={redact(row['sCode'])} {redact(row.get('sMsg', 'rejected'))}"
                )
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
        self.client_order_id = (
            str(uuid4().int & 0xFFFFFFFF)
            if exchange == "backpack"
            else str(uuid4())
            if exchange == "kraken"
            else "0" + uuid4().hex[:31]
        )

    async def recover_order(self):
        """Find only this test's client ID after an uncertain placement response."""
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
            if str(row.get(client_field, "")) == self.client_order_id
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
            code = redact(getattr(error, "code", getattr(error, "status_code", "")))
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
            reported = LifecycleError(f"{self.exchange} {method}: {label}code={code} {message}")
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
        bids, asks = (data["b"], data["a"]) if ex == "bybit" else (data["bids"], data["asks"])
        return decimal(bids[0][0]), decimal(asks[0][0])

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
            data = await self.call("get_balances")
            return decimal(data[coin]["available"]) if coin in data else Decimal(0)
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
                    # The spot spec defines index-price bands but exposes no
                    # index-price endpoint. Last trade/VWAP are not substitutes.
                    raise MarketUnavailable(
                        "aster spot: documented index-price source for percentage bands is unavailable"
                    )
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
                (await self.call("get_uta_positions", category=self.category))["list"],
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
        if ex == "binance":
            data = await self.call(
                "place_order",
                **kw,
                type_="LIMIT_MAKER" if self.spot else "LIMIT",
                newClientOrderId=self.client_order_id,
                side="BUY",
                quantity=size,
                price=price,
                **({} if self.spot else {"timeInForce": "GTX", "positionSide": self.position_side}),
            )
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
                timeInForce="GTX",
                **({} if self.spot else {"positionSide": self.position_side}),
            )
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
                timeInForce="PostOnly",
                **({} if self.spot else {"positionIdx": self.position_index}),
            )
            return checked_id(data["orderId"])
        if ex == "okx":
            data = await self.call(
                "place_order",
                **kw,
                tdMode="cash" if self.spot else "cross",
                clOrdId=self.client_order_id,
                side="buy",
                ordType="post_only",
                sz=size,
                px=price,
                **({} if self.spot else {"posSide": self.position_side}),
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
                time_in_force="post_only",
                **({} if self.position_side is None else {"pos_side": self.position_side}),
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
                time_in_force="PostOnly",
                **({} if self.spot else {"position_side": self.position_side}),
            )
            return checked_id(data["orderId"] if self.spot else data["order"]["orderId"])
        if ex == "mexc":
            if self.spot:
                data = await self.call(
                    "place_spot_order",
                    **kw,
                    side="BUY",
                    type_="LIMIT_MAKER",
                    quantity=size,
                    price=price,
                    newClientOrderId=self.client_order_id,
                )
                return checked_id(data["orderId"])
            return checked_id(
                await self.call(
                    "place_contract_order",
                    **kw,
                    side=1,
                    type_=2,
                    openType=2,
                    vol=size,
                    price=price,
                    externalOid=self.client_order_id,
                )
            )
        if ex == "kucoin":
            data = await self.call(
                "place_spot_order" if self.spot else "place_futures_order",
                **kw,
                side="buy",
                type_="limit",
                size=size,
                price=price,
                timeInForce="GTC",
                postOnly=True,
                clientOid=self.client_order_id,
                **({} if self.spot else {"leverage": "1"}),
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
                timeInForce="GTC",
                postOnly=True,
                autoBorrow=False,
                autoLend=False,
                autoLendRedeem=False,
            )
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
                    timeinforce="GTC",
                    oflags="post",
                    cl_ord_id=self.client_order_id,
                )
                return checked_id(data["txid"][0])
            data = await self.call(
                "place_futures_order",
                **kw,
                side="buy",
                orderType="post",
                cliOrdId=self.client_order_id,
                size=size,
                limitPrice=price,
            )
            if data["sendStatus"]["status"] != "placed":
                raise LifecycleError("kraken: futures order was not placed")
            return checked_id(data["sendStatus"]["order_id"])
        raise LifecycleError("unsupported placement adapter")

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
            data = await self.call(
                "get_spot_order" if self.spot else "get_futures_order",
                **({**kw, "order_id": identifier} if self.spot else {"orderId": identifier}),
            )
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
            "cancelled" if data["status"] == "canceled" else data["status"],
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
            "cancelled"
            if data["status"] == "CANCELLED"
            else "open"
            if data["status"] == "ENTERED_BOOK"
            else data["status"],
        )
    else:
        raise LifecycleError("unsupported order response")
    if exchange != "kucoin":
        values = [data[key] for key in fields]
    oid, symbol, side, kind, price, size, filled, state = values
    state = str(state).lower()
    state = (
        "open"
        if state in ({"live"} if exchange == "bitget" else {"new", "live", "open"})
        else "cancelled"
        if state in {"canceled", "cancelled"}
        else state
    )
    side, kind = str(side).lower(), str(kind).lower()
    if kind in {"limit_maker", "post_only"}:
        kind = "limit"
    if exchange == "backpack":
        side = "buy" if side == "bid" else "sell" if side == "ask" else side
    if exchange == "mexc" and not spot:
        side = "buy" if side == "1" else side
        kind = "limit" if kind in {"1", "2"} else kind
        state = {"2": "open", "4": "cancelled"}.get(state, state)
    return Order(
        str(oid), symbol, side, kind, decimal(price), decimal(size), decimal(filled), state
    )
