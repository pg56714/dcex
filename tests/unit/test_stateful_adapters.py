"""Offline exchange response fixtures and public-method signature checks."""

import importlib
import inspect
from decimal import Decimal
from types import SimpleNamespace

import pytest

from tests.stateful_adapters import CexAdapter, normalize_order, response_data
from tests.stateful_lifecycle import LifecycleError, run_lifecycle

EXCHANGES = (
    "binance",
    "aster",
    "bybit",
    "okx",
    "bitget",
    "bingx",
    "mexc",
    "kucoin",
    "backpack",
    "kraken",
)


def order_record(exchange, spot, cancelled=False, price="90", size=".12"):
    state = "CANCELED" if cancelled else "NEW"
    common = dict(
        orderId="123",
        symbol="BTCUSDT",
        side="BUY",
        type="LIMIT",
        price=price,
        origQty=size,
        executedQty="0",
        status=state,
    )
    if exchange in {"binance", "aster", "bingx"} or (exchange == "mexc" and spot):
        return common
    if exchange in {"bybit", "bitget"}:
        return dict(
            orderId="123",
            symbol="BTCUSDT",
            side="Buy",
            orderType="Limit",
            price=price,
            qty=size,
            cumExecQty="0",
            orderStatus=("Cancelled" if cancelled else "New")
            if exchange == "bybit"
            else ("cancelled" if cancelled else "live"),
        )
    if exchange == "okx":
        return dict(
            ordId="123",
            instId="BTCUSDT",
            side="buy",
            ordType="limit",
            px=price,
            sz=size,
            accFillSz="0",
            state="canceled" if cancelled else "live",
        )
    if exchange == "mexc":
        return dict(
            orderId="123",
            symbol="BTCUSDT",
            side=1,
            orderType=2,
            price=price,
            vol=size,
            dealVol="0",
            state=4 if cancelled else 2,
        )
    if exchange == "kucoin":
        return dict(
            id="123",
            symbol="BTCUSDT",
            side="buy",
            type="limit",
            price=price,
            size=size,
            dealSize="0",
            cancelExist=cancelled,
            **(
                {"active": not cancelled, "inOrderBook": not cancelled}
                if spot
                else {"isActive": not cancelled}
            ),
        )
    if exchange == "backpack":
        return dict(
            id="123",
            symbol="BTCUSDT",
            side="Bid",
            orderType="Limit",
            price=price,
            quantity=size,
            executedQuantity="0",
            status="Cancelled" if cancelled else "New",
        )
    if spot:
        return dict(
            descr=dict(pair="BTCUSDT", type="buy", ordertype="limit", price=price),
            vol=size,
            vol_exec="0",
            status="canceled" if cancelled else "open",
        )
    return dict(
        order=dict(
            orderId="123",
            symbol="BTCUSDT",
            side="buy",
            type="ORDER",
            limitPrice=price,
            quantity=size,
            filled="0",
        ),
        status="CANCELLED" if cancelled else "ENTERED_BOOK",
    )


class ExchangeMock:
    """No sockets or actual Client instances; bind calls against actual signatures."""

    def __init__(self, exchange, spot, mode):
        self.exchange, self.spot, self.mode = exchange, spot, mode
        module = "dcex." + ("async_support." if mode == "async" else "") + exchange + ".client"
        self.cls = importlib.import_module(module).Client
        self.ptm = SimpleNamespace(
            get_exchange_symbol=lambda *args: "BTCUSDT",
            get_trading_details=lambda *args: dict(
                price_precision=".1",
                size_precision=".01",
                min_size=".01",
                min_notional="10",
                size_per_contract="1",
            ),
        )
        self.calls = []
        self.placed = self.cancelled = False
        self.price, self.size = "90", ".12"

    def __getattr__(self, method):
        signature = inspect.signature(getattr(self.cls, method))

        def call(**kwargs):
            signature.bind(None, **kwargs)
            self.calls.append((method, kwargs))
            payload = self.payload(method, kwargs)
            ex = self.exchange
            if ex == "bybit":
                return dict(retCode=0, result=payload)
            if ex == "okx":
                return dict(code="0", data=payload)
            if ex in {"bitget", "kucoin", "bingx"}:
                return dict(
                    code={"bitget": "00000", "kucoin": "200000", "bingx": 0}[ex], data=payload
                )
            if ex == "mexc" and not self.spot:
                return dict(success=True, code=0, data=payload)
            if ex == "kraken":
                return (
                    dict(error=[], result=payload)
                    if self.spot
                    else dict(result="success", **payload)
                )
            return payload

        if self.mode == "sync":
            return call

        async def async_call(**kwargs):
            return call(**kwargs)

        return async_call

    def payload(self, method, kw):
        ex, spot = self.exchange, self.spot
        if method.startswith("place_"):
            self.placed = True
            self.price = kw.get("price", kw.get("px", kw.get("limitPrice")))
            self.size = kw.get(
                "quantity",
                kw.get("qty", kw.get("sz", kw.get("vol", kw.get("volume", kw.get("size"))))),
            )
            return {
                "binance": {"orderId": "123"},
                "aster": {"orderId": "123"},
                "bybit": {"orderId": "123"},
                "okx": [{"ordId": "123", "sCode": "0"}],
                "bitget": {"orderId": "123"},
                "bingx": {"orderId": "123"} if spot else {"order": {"orderId": "123"}},
                "mexc": {"orderId": "123"} if spot else "123",
                "kucoin": {"orderId": "123"},
                "backpack": {"id": "123"},
                "kraken": {"txid": ["123"]}
                if spot
                else {"sendStatus": {"status": "placed", "order_id": "123"}},
            }[ex]
        if method.startswith("cancel_"):
            self.cancelled = True
            if ex == "kraken":
                return {"count": 1} if spot else {"cancelStatus": {"status": "cancelled"}}
            if ex == "okx":
                return [{"ordId": "123", "sCode": "0"}]
            if ex == "mexc" and not spot:
                return [{"orderId": "123", "errorCode": 0}]
            return {}
        record = order_record(ex, spot, self.cancelled, self.price, self.size)
        if method in {
            "get_order",
            "get_spot_order",
            "get_futures_order",
            "get_order_detail",
            "get_contract_order",
            "get_uta_order",
            "get_futures_order_status",
            "get_spot_orders",
            "get_order_history",
        } or (method == "get_open_orders" and kw.get("orderId")):
            if ex == "bybit":
                return {"list": [record]}
            if ex == "okx":
                return [record]
            if ex == "bingx" and not spot:
                return {"order": record}
            if ex == "backpack":
                return [record]
            if ex == "kraken":
                return {"123": record} if spot else {"orders": [record]}
            return record
        if method in {
            "get_open_orders",
            "get_spot_open_orders",
            "get_futures_open_orders",
            "get_uta_open_orders",
            "get_contract_open_orders",
            "get_futures_order_list",
            "get_order_list",
        }:
            orders = [record] if self.placed and not self.cancelled else []
            if ex in {"bybit", "bitget"}:
                return {"list": orders}
            if ex == "kucoin":
                return {"items": orders}
            if ex == "bingx":
                return {"orders": orders}
            if ex == "kraken":
                return (
                    {"open": dict.fromkeys(["123"], record) if orders else {}}
                    if spot
                    else {"openOrders": orders}
                )
            return orders
        if "orderbook" in method or method == "get_order_book_depth":
            book = {"bids": [["100", "1"]], "asks": [["101", "1"]]}
            if ex in {"bybit", "bitget"}:
                return {"b": book["bids"], "a": book["asks"]}
            if ex == "okx":
                return [book]
            if ex == "kraken":
                return {"BTCUSDT": book} if spot else {"orderBook": book}
            return book
        if method == "get_contract_ticker":
            return dict(bid1="100", ask1="101")
        if method == "get_uta_instruments":
            return [{"symbol": "BTCUSDT", "buyLimitPriceRatio": "0.2"}]
        if method == "get_uta_tickers":
            return [{"symbol": "BTCUSDT", "lastPrice": "100", "markPrice": "100"}]
        if method == "get_market":
            band = {"minMultiplier": ".8", "maxMultiplier": "1.2"}
            return {"filters": {"price": {"meanMarkPriceBand": band}}}
        if method == "get_ticker":
            return {"lastPrice": "100"}
        if method == "get_mark_prices":
            return [{"markPrice": "100"}]
        if method in {"get_spot_exchange_info", "get_futures_exchange_info"}:
            return {"symbols": [{"symbol": "BTCUSDT", "filters": []}]}
        if method == "get_price_limit":
            return [{"enabled": True, "buyLmt": "120"}]
        if method == "get_order_price_limit":
            return {"buyLmt": "120"}
        if method in {"get_futures_position_mode", "get_position_mode"}:
            return {"dualSidePosition": False}
        if method == "get_futures_margin_mode":
            return {"symbol": "BTCUSDTM", "marginMode": "CROSS"}
        if method == "get_futures_cross_margin_leverage":
            return {"symbol": "BTCUSDTM", "leverage": "3"}
        if method == "get_contract_leverage":
            return [
                {"positionType": 1, "openType": 1, "leverage": 20},
                {"positionType": 2, "openType": 1, "leverage": 15},
            ]
        if method == "get_contract_position_mode":
            return getattr(self, "position_mode", 1)
        if method == "get_account_config":
            return [{"posMode": "net_mode"}]
        if method == "get_uta_settings":
            return {"holdMode": "one_way_mode"}
        if "position" in method:
            if ex in {"bybit", "bitget"}:
                return {"list": []}
            if ex == "kraken":
                return {"openPositions": []}
            return []
        wallet = [{"asset": "USDT", "free": "20", "availableBalance": "20"}]
        if ex in {"binance", "aster", "mexc"}:
            if spot:
                return {"balances": wallet}
            if ex == "aster":
                return {"assets": wallet}
            return wallet if ex == "binance" else {"availableBalance": "20"}
        if ex == "bybit":
            return {
                "list": [
                    {
                        "coin": [
                            {
                                "coin": "USDT",
                                "walletBalance": "20",
                                "locked": "0",
                                "totalPositionIM": "0",
                                "totalOrderIM": "0",
                            }
                        ]
                    }
                ]
            }
        if ex == "okx":
            return [{"details": [{"ccy": "USDT", "availBal": "20"}]}]
        if ex == "bitget":
            return {"assets": [{"coin": "USDT", "available": "20"}]}
        if ex == "bingx":
            if method == "get_fund_account_balance":
                return {"assets": [{"asset": "USDT", "free": "13.23", "locked": "0"}]}
            return {"balances": wallet} if spot else {"balance": {"availableMargin": "20"}}
        if ex == "kucoin":
            return [{"currency": "USDT", "available": "20"}] if spot else {"availableBalance": "20"}
        if ex == "backpack":
            # Orders use autoLendRedeem, so the adapter reads wallet plus lent quantity.
            return {
                "borrowLiability": "0",
                "collateral": [{"symbol": "USDT", "availableQuantity": "5", "lendQuantity": "15"}],
            }
        if ex == "kraken":
            return {"USDT": "20"} if spot else {"accounts": {"flex": {"availableMargin": "20"}}}
        raise AssertionError(method)


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("spot", [True, False], ids=["spot", "swap"])
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_exchange_lifecycle_against_method_signatures(exchange, spot, mode):
    client = ExchangeMock(exchange, spot, mode)
    adapter = CexAdapter(
        client, exchange, "spot" if spot else "swap", "BTC-USDT-" + ("SPOT" if spot else "SWAP")
    )
    result = {"exchange": exchange, "market": adapter.market}
    await run_lifecycle(adapter, result, poll_delay=0)
    assert result["stage"] == "complete"
    assert sum(name.startswith("place_") for name, _ in client.calls) == 1
    assert sum(name.startswith("cancel_") for name, _ in client.calls) == 1
    assert not any(
        "transfer" in name or "withdraw" in name or name.startswith("set_")
        for name, _ in client.calls
    )


@pytest.mark.parametrize("exchange", EXCHANGES)
@pytest.mark.parametrize("spot", [True, False])
def test_queried_order_fields_are_not_defaulted(exchange, spot):
    record = order_record(exchange, spot)
    order = normalize_order(exchange, spot, record, "123")
    assert (order.identifier, order.symbol, order.side, order.kind, order.filled, order.state) == (
        "123",
        "BTCUSDT",
        "buy",
        "limit",
        Decimal(0),
        "open",
    )
    with pytest.raises((KeyError, LifecycleError)):
        normalize_order(exchange, spot, {}, "123")


@pytest.mark.parametrize(
    "exchange,payload",
    [
        ("bybit", {"retCode": 10001}),
        ("okx", {"code": "51000"}),
        ("bitget", {"code": "40085"}),
        ("kucoin", {"code": "400100"}),
        ("bingx", {"code": 100001}),
        ("binance", {"code": -1013}),
        ("aster", {"code": -1013}),
        ("mexc", {"success": False, "code": 1002}),
        ("kraken", {"error": ["EOrder:Invalid order"]}),
    ],
)
def test_http_success_with_exchange_rejection_fails(exchange, payload):
    with pytest.raises(LifecycleError):
        response_data(exchange, payload)


def test_unbooked_orders_are_not_resting():
    # Bitget "new" is a resting state (seen live on a far-from-market post-only order).
    record = order_record("kucoin", True)
    record["inOrderBook"] = False
    assert normalize_order("kucoin", True, record, "123").state != "open"


@pytest.mark.parametrize(
    "exchange,spot,label",
    [
        ("mexc", False, "exchange permission issue"),
        ("extended", True, "account eligibility issue"),
    ],
)
@pytest.mark.parametrize("transport_error", [True, False])
@pytest.mark.asyncio
async def test_rejections_are_classified_for_exceptions_and_response_codes(
    exchange, spot, label, transport_error
):
    client = ExchangeMock("mexc", spot, "sync")

    def reject():
        if transport_error:
            raise RuntimeError("Permission denied")
        if exchange == "mexc":
            return {"success": False, "code": 1002, "message": "Permission denied"}
        return {"status": "ERROR", "message": "Spot not enabled"}

    client.reject = reject
    adapter = CexAdapter(client, exchange, "spot" if spot else "swap", "BTC-USDT-SPOT")
    with pytest.raises(LifecycleError, match=label):
        await adapter.call("reject")


@pytest.mark.asyncio
async def test_bingx_doge_swap_plans_with_integer_quantity_step():
    # BingX DOGE-USDT swap: quantityPrecision=0 -> size step "1", pricePrecision=5 -> "1e-05".
    client = ExchangeMock("bingx", False, "async")
    client.ptm = SimpleNamespace(
        get_exchange_symbol=lambda *args: "DOGE-USDT",
        get_trading_details=lambda *args: dict(
            price_precision="1e-05",
            size_precision="1",
            min_size="1",
            min_notional="2",
            size_per_contract="1",
        ),
    )
    adapter = CexAdapter(client, "bingx", "swap", "DOGE-USDT-SWAP")
    plan, _ = await adapter.prepare()
    assert plan.size > 0 and plan.size % 1 == 0
    assert plan.price % Decimal("0.00001") == 0


@pytest.mark.asyncio
async def test_bitget_null_position_list_means_no_positions():
    # Live Bitget UTA returns {"list": null} when the account holds no positions.
    client = ExchangeMock("bitget", False, "async")
    original = client.payload

    def payload(method, kw):
        if method == "get_uta_positions":
            return {"list": None}
        return original(method, kw)

    client.payload = payload
    adapter = CexAdapter(client, "bitget", "swap", "BTC-USDT-SWAP")
    assert await adapter.positions() == []


@pytest.mark.parametrize(
    ("exchange", "status"),
    [("bingx", "PENDING"), ("bingx", "NEW"), ("bitget", "live"), ("bitget", "new")],
)
def test_documented_resting_states_are_open(exchange, status):
    from tests.stateful_adapters import normalize_order

    if exchange == "bingx":
        data = dict(
            orderId="1",
            symbol="DOGE-USDT",
            side="BUY",
            type="LIMIT",
            price="0.08",
            origQty="10",
            executedQty="0",
            status=status,
        )
    else:
        data = dict(
            orderId="1",
            symbol="DOGEUSDT",
            side="buy",
            orderType="limit",
            price="0.08",
            qty="10",
            cumExecQty="0",
            orderStatus=status,
        )
    assert normalize_order(exchange, True, data, "1").state == "open"


@pytest.mark.asyncio
async def test_kucoin_null_order_data_is_polled_again():
    client = ExchangeMock("kucoin", True, "async")
    original = client.payload

    def payload(method, kw):
        if method == "get_spot_order":
            return None
        return original(method, kw)

    client.payload = payload
    adapter = CexAdapter(client, "kucoin", "spot", "BTC-USDT-SPOT")
    assert await adapter.order("123") is None


@pytest.mark.asyncio
async def test_backpack_orders_redeem_lent_funds_but_never_borrow():
    client = ExchangeMock("backpack", True, "async")
    adapter = CexAdapter(client, "backpack", "spot", "BTC-USDT-SPOT")
    plan, available = await adapter.prepare()
    assert available == Decimal(20)  # 5 in the wallet plus 15 lent
    await adapter.place(plan)
    params = next(kw for name, kw in client.calls if name == "place_limit_order")
    assert params["autoLendRedeem"] is True and params["autoBorrow"] is False


@pytest.mark.asyncio
async def test_backpack_existing_debt_stops_before_any_order():
    client = ExchangeMock("backpack", True, "async")
    original = client.payload

    def payload(method, kw):
        if method == "get_private_collateral":
            return {"borrowLiability": "1", "collateral": []}
        return original(method, kw)

    client.payload = payload
    adapter = CexAdapter(client, "backpack", "spot", "BTC-USDT-SPOT")
    with pytest.raises(LifecycleError, match="borrow liability"):
        await adapter.available()
    assert not any(name.startswith("place_") for name, _ in client.calls)


@pytest.mark.parametrize(
    ("mode", "leverage"), [("CROSS", "3"), ("ISOLATED", "1")], ids=["cross", "isolated"]
)
@pytest.mark.asyncio
async def test_kucoin_futures_order_uses_current_margin_mode(mode, leverage):
    # Live 330005: the order's margin mode must match the symbol's current one (default ISOLATED).
    client = ExchangeMock("kucoin", False, "async")
    original = client.payload

    def payload(method, kw):
        if method == "get_futures_margin_mode":
            return {"symbol": "DOGEUSDTM", "marginMode": mode}
        return original(method, kw)

    client.payload = payload
    adapter = CexAdapter(client, "kucoin", "swap", "DOGE-USDT-SWAP")
    plan, _ = await adapter.prepare()
    await adapter.place(plan)
    params = next(kw for name, kw in client.calls if name == "place_futures_order")
    assert (params["marginMode"], params["leverage"]) == (mode, leverage)
    assert ("get_futures_cross_margin_leverage" in {n for n, _ in client.calls}) == (
        mode == "CROSS"
    )
    assert not any(name.startswith(("set_", "modify_")) for name, _ in client.calls)


@pytest.mark.asyncio
async def test_mexc_contract_order_uses_current_long_open_type_and_leverage():
    client = ExchangeMock("mexc", False, "async")
    adapter = CexAdapter(client, "mexc", "swap", "BTC-USDT-SWAP")
    plan, _ = await adapter.prepare()
    await adapter.place(plan)
    params = next(kw for name, kw in client.calls if name == "place_contract_order")
    assert (params["openType"], params["leverage"]) == (1, 20)  # the positionType 1 row
    assert not any(name.startswith(("set_", "change_")) for name, _ in client.calls)


@pytest.mark.parametrize(
    "rows_", [[], [{"positionType": 1, "leverage": 20}]], ids=["no-long-row", "no-open-type"]
)
@pytest.mark.asyncio
async def test_mexc_missing_leverage_setting_fails_before_any_order(rows_):
    client = ExchangeMock("mexc", False, "async")
    original = client.payload
    client.payload = lambda method, kw: (
        rows_ if method == "get_contract_leverage" else original(method, kw)
    )
    adapter = CexAdapter(client, "mexc", "swap", "BTC-USDT-SWAP")
    plan, _ = await adapter.prepare()
    with pytest.raises(LifecycleError, match="openType/leverage unavailable"):
        await adapter.place(plan)
    assert not any(name.startswith("place_") for name, _ in client.calls)


@pytest.mark.asyncio
async def test_mexc_contract_order_id_may_be_wrapped_in_an_object():
    client = ExchangeMock("mexc", False, "async")
    original = client.payload

    def payload(method, kw):
        if method == "place_contract_order":
            client.placed = True
            return {"orderId": "861578920561512960", "ts": 1}
        return original(method, kw)

    client.payload = payload
    adapter = CexAdapter(client, "mexc", "swap", "BTC-USDT-SWAP")
    plan, _ = await adapter.prepare()
    assert await adapter.place(plan) == "861578920561512960"


@pytest.mark.asyncio
async def test_kucoin_futures_order_not_yet_visible_is_polled_again():
    client = ExchangeMock("kucoin", False, "async")

    def reject(**_):
        raise RuntimeError("KUCOIN API Error: [100001] error.getOrder.orderNotExist")

    client.get_futures_order = reject
    adapter = CexAdapter(client, "kucoin", "swap", "BTC-USDT-SWAP")
    assert await adapter.order("496075506332991488") is None
