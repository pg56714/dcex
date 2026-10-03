"""DEX lifecycle fixtures using the documented native response fields."""

import importlib
import inspect
import json
from decimal import Decimal
from types import SimpleNamespace

import pytest

from tests.stateful_dex import ExtendedAdapter, HyperliquidAdapter, LighterAdapter, OndoAdapter
from tests.stateful_lifecycle import LifecycleError, MarketUnavailable, run_lifecycle
from tests.stateful_runner import run_case


class DexMock:
    def __init__(self, exchange, mode):
        self.exchange, self.mode = exchange, mode
        self.cls = importlib.import_module(
            "dcex." + ("async_support." if mode == "async" else "") + exchange + ".client"
        ).Client
        self.calls = []
        self.cancelled = self.placed = False
        self.fill = "0"
        self.rfq = False
        self.price = self.size = None
        self.account_index = 1
        self.wallet_address = "fixture-owner"
        self.abstraction = "disabled"
        native = (
            json.dumps(["BTC", 0])
            if exchange == "hyperliquid"
            else "BTC-USD.P"
            if exchange == "ondo"
            else "BTC-USD"
        )
        self.ptm = SimpleNamespace(
            get_exchange_symbol=lambda *args: native,
            get_trading_details=lambda *args: dict(
                price_precision=".1",
                size_precision=".01",
                min_size=".01",
                min_notional="10",
                size_per_contract="1",
            ),
        )

    def __getattr__(self, method):
        signature = inspect.signature(getattr(self.cls, method))

        def call(**kw):
            signature.bind(None, **kw)
            self.calls.append((method, kw))
            data = self.response(method, kw)
            if self.exchange == "extended":
                return {"status": "OK", "data": data}
            if self.exchange == "ondo":
                return {"success": True, "result": data}
            if self.exchange == "lighter":
                return {"code": 200, **data}
            return data

        if self.mode == "sync":
            return call

        async def acall(**kw):
            return call(**kw)

        return acall

    def response(self, method, kw):
        ex = self.exchange
        if method == "get_markets":
            return [
                {
                    "name": "BTC-USD",
                    "status": "ACTIVE",
                    "isRfq": self.rfq,
                    "isOffHours": False,
                    "marketStats": {"markPrice": "100", "indexPrice": "100"},
                    "tradingConfig": {
                        "limitPriceFloor": ".15",
                        "limitPriceCap": ".15",
                        "minPriceChange": ".1",
                        "minOrderSizeChange": ".01",
                        "minOrderSize": ".12",
                    },
                }
            ]
        if method == "get_order_book_details":
            return {
                "order_book_details": [
                    {
                        "symbol": "ETH",
                        "status": "active",
                        "market_id": 7,
                        "price_decimals": 1,
                        "size_decimals": 2,
                        "min_base_amount": ".01",
                        "min_quote_amount": "10",
                    }
                ]
            }
        if method == "user_role":
            return {"role": "user"}
        if method == "get_user_abstraction":
            return self.abstraction
        if method == "clearinghouse_state":
            return {"assetPositions": [], "withdrawable": "20"}
        if method == "spot_clearinghouse_state":
            return {"balances": [{"coin": "USDC", "total": "20", "hold": "0"}]}
        if method == "get_account":
            return {"accounts": [{"positions": [], "available_balance": "20"}]}
        if method == "get_balance":
            return (
                {"availableForTrade": "20", "balance": "20", "collateralReservedForSpotOrders": "0"}
                if ex == "extended"
                else {"availableMargin": "20"}
            )
        if method in {"get_positions", "get_open_orders", "open_orders"}:
            return []
        if method == "get_account_active_orders":
            return {"orders": []}
        if method == "get_order_book":
            return {"bid": [{"price": "100"}], "ask": [{"price": "101"}]}
        if method == "get_depth":
            return {"bids": [["100", "1"]], "asks": [["101", "1"]]}
        if method == "get_l2book":
            return {"levels": [[{"px": "100"}], [{"px": "101"}]]}
        if method == "get_order_book_orders":
            return {"bids": [{"price": "100"}], "asks": [{"price": "101"}]}
        if method in {"place_order", "place_limit_order", "create_order"}:
            self.placed = True
            self.price = kw["price"]
            self.size = kw.get("size", kw.get("qty"))
            if ex == "lighter":
                self.client_index = kw["client_order_index"]
                self.price = str(kw["price"] / 10)
                self.size = str(kw["base_amount"] / 100)
                return {"tx_hash": "fixture-transaction"}
            if ex == "hyperliquid":
                return {
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {"statuses": [{"resting": {"oid": 123}}]},
                    },
                }
            return {"id" if ex == "extended" else "orderId": "123"}
        if method == "cancel_order":
            self.cancelled = True
            return (
                {"status": "ok", "response": {"type": "cancel", "data": {"statuses": ["success"]}}}
                if ex == "hyperliquid"
                else {}
            )
        if method == "get_order":
            if ex == "extended":
                return {
                    "id": "123",
                    "market": "BTC-USD",
                    "side": "BUY",
                    "type": "LIMIT",
                    "price": self.price,
                    "qty": self.size,
                    "filledQty": self.fill,
                    "status": "CANCELLED" if self.cancelled else "NEW",
                }
            return {
                "orderId": "123",
                "market": "BTC-USD.P",
                "side": "buy",
                "type": "limit",
                "price": self.price,
                "size": self.size,
                "filledSize": self.fill,
                "status": "canceled" if self.cancelled else "open",
            }
        if method == "order_status":
            return {
                "status": "order",
                "order": {
                    "status": "canceled" if self.cancelled else "open",
                    "order": {
                        "oid": 123,
                        "coin": "BTC",
                        "side": "B",
                        "orderType": "Limit",
                        "limitPx": self.price,
                        "origSz": self.size,
                        "sz": "0" if self.cancelled else self.size,
                    },
                },
            }
        if method == "user_fills_by_time":
            return [{"oid": 123, "sz": self.fill}]
        if method == "get_account_orders":
            return {
                "orders": [
                    {
                        "order_index": 123,
                        "client_order_index": self.client_index,
                        "market_index": 7,
                        "is_ask": False,
                        "type": "limit",
                        "price": self.price,
                        "initial_base_amount": self.size,
                        "filled_base_amount": self.fill,
                        "status": "canceled" if self.cancelled else "open",
                    }
                ]
            }
        raise AssertionError("Unexpected mock call: " + method)


CASES = [
    ("extended", ExtendedAdapter, "spot", "BTC-USD-SPOT"),
    ("extended", ExtendedAdapter, "swap", "BTC-USD-SWAP"),
    ("ondo", OndoAdapter, "swap", "BTC-USD-SWAP"),
    ("hyperliquid", HyperliquidAdapter, "spot", "BTC-USDC-SPOT"),
    ("hyperliquid", HyperliquidAdapter, "swap", "BTC-USD-SWAP"),
    ("lighter", LighterAdapter, "mainnet", "ETH"),
    ("lighter", LighterAdapter, "robinhood", "ETH"),
]


@pytest.mark.parametrize("exchange,adapter_type,market,symbol", CASES)
@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.asyncio
async def test_dex_lifecycle_signatures_and_responses(exchange, adapter_type, market, symbol, mode):
    client = DexMock(exchange, mode)
    result = {}
    await run_lifecycle(adapter_type(client, exchange, market, symbol), result, poll_delay=0)
    assert result["stage"] == "complete"
    assert client.cancelled
    assert not any(
        "transfer" in name or "withdraw" in name or name.startswith("set_")
        for name, _ in client.calls
    )


@pytest.mark.parametrize("exchange,adapter_type,market,symbol", CASES)
@pytest.mark.asyncio
async def test_dex_fill_stops_and_only_cancels(exchange, adapter_type, market, symbol):
    client = DexMock(exchange, "sync")
    client.fill = ".01"
    with pytest.raises(LifecycleError, match="UNEXPECTED FILL"):
        await run_lifecycle(adapter_type(client, exchange, market, symbol), {}, poll_delay=0)
    assert client.cancelled
    assert (
        sum(
            name in {"create_order", "place_order", "place_limit_order"} for name, _ in client.calls
        )
        == 1
    )


@pytest.mark.asyncio
async def test_extended_rfq_market_skips_before_order():
    client = DexMock("extended", "sync")
    client.rfq = True
    with pytest.raises(MarketUnavailable, match="RFQ"):
        await run_lifecycle(ExtendedAdapter(client, "extended", "spot", "BTC-USD-SPOT"), {})
    assert not client.placed


@pytest.mark.asyncio
async def test_arcus_unverified_or_incompatible_protocol_cannot_initialize_client(monkeypatch):
    monkeypatch.setenv("RUN_LIVE_TRADING_TESTS", "1")
    monkeypatch.setattr("tests.live_gate.LIVE_TRADING_ENABLED", True)
    monkeypatch.setattr(
        "tests.stateful_runner.load_dotenv", lambda: pytest.fail("must not read credentials")
    )
    result = {}
    with pytest.raises(pytest.skip.Exception, match="Arcus"):
        await run_case("arcus", "sync", "spot", "", result)
    assert result["stage"] == "not_applicable"
    assert result["status"] == "N/A"
    assert result["skip_reason"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("market", "details", "book", "tick", "step"),
    [
        # PURR-like spot: szDecimals=0 -> 8 decimals cap, 5 significant figures at 0.164.
        ("spot", ("1e-08", "1"), ("0.164", "0.165"), "0.00001", "1"),
        # BTC-like perp: szDecimals=5 -> 1 decimal cap, 5 significant figures at 60000.
        ("swap", ("0.1", "0.00001"), ("60000", "60001"), "1", "0.00001"),
    ],
)
async def test_hyperliquid_tick_combines_decimal_cap_and_significant_figures(
    market, details, book, tick, step
):
    from decimal import Decimal

    adapter = HyperliquidAdapter.__new__(HyperliquidAdapter)
    adapter.native = "PURR/USDC" if market == "spot" else "BTC"
    adapter.details = {
        "price_precision": details[0],
        "size_precision": details[1],
        "min_size": details[1],
        "min_notional": "10",
    }
    bid, ask = (Decimal(value) for value in book)

    async def fixed_book():
        return bid, ask

    async def available():
        return Decimal(100)

    adapter.book, adapter.available = fixed_book, available
    plan, _ = await adapter.prepare()
    assert plan.price < bid
    assert plan.price % Decimal(tick) == 0
    assert (
        len(plan.price.normalize().as_tuple().digits) <= 5 or plan.price == plan.price.to_integral()
    )
    assert -plan.price.normalize().as_tuple().exponent <= max(
        0, -Decimal(details[0]).as_tuple().exponent
    )
    assert plan.size % Decimal(step) == 0


def test_best_reads_top_of_book_regardless_of_level_order():
    from tests.stateful_dex import best

    bids = [["99", "1"], ["101", "1"], ["100", "1"]]
    asks = [["105", "1"], ["102", "1"], ["103", "1"]]
    assert best(bids, asks, lambda row: row[0]) == (Decimal(101), Decimal(102))


@pytest.mark.parametrize(("bids", "asks"), [([], [["1", "1"]]), ([["1", "1"]], None)])
def test_best_rejects_an_empty_book_side(bids, asks):
    from tests.stateful_dex import best
    from tests.stateful_lifecycle import LifecycleError

    with pytest.raises(LifecycleError, match="empty side"):
        best(bids, asks, lambda row: row[0])


@pytest.mark.asyncio
async def test_extended_spot_market_closed_to_clients_skips_without_recovery():
    client = DexMock("extended", "sync")
    original = client.response

    def response(method, kw):
        if method == "place_limit_order":
            raise RuntimeError(
                'HTTP 400: {"status":"ERROR","error":{"code":1153,'
                '"message":"Market is not allowed for clients"}}'
            )
        return original(method, kw)

    client.response = response
    result = {}
    with pytest.raises(MarketUnavailable, match="1153"):
        await run_lifecycle(ExtendedAdapter(client, "extended", "spot", "BTC-USD-SPOT"), result)
    assert "skip_reason" in result
    # An explicit rejection created no order, so no client-ID recovery is attempted.
    assert not any(name in {"get_order_by_external_id", "cancel_order"} for name, _ in client.calls)


@pytest.mark.asyncio
async def test_extended_not_found_after_cancel_is_polled_again():
    client = DexMock("extended", "async")
    original = client.response
    misses = []

    def response(method, kw):
        if method == "get_order" and client.cancelled and len(misses) < 2:
            misses.append(1)
            error = RuntimeError('HTTP 404: {"status":"ERROR","error":{"message":"Not Found"}}')
            error.status_code = 404
            raise error
        return original(method, kw)

    client.response = response
    result = {}
    adapter = ExtendedAdapter(client, "extended", "swap", "BTC-USD-SWAP")
    await run_lifecycle(adapter, result, poll_delay=0)
    assert result["stage"] == "complete" and len(misses) == 2


@pytest.mark.asyncio
async def test_extended_other_order_query_errors_still_raise():
    client = DexMock("extended", "sync")

    def response(method, kw):
        raise RuntimeError("HTTP 500: internal error")

    client.response = response
    with pytest.raises(LifecycleError, match="500"):
        await ExtendedAdapter(client, "extended", "swap", "BTC-USD-SWAP").order("123")


@pytest.mark.parametrize(
    ("abstraction", "expected"),
    [("unifiedAccount", Decimal(15)), ("portfolioMargin", Decimal(15)), ("disabled", Decimal(0))],
)
@pytest.mark.asyncio
async def test_hyperliquid_unified_perp_margin_is_spot_usdc_of_resolved_owner(
    abstraction, expected
):
    client = DexMock("hyperliquid", "sync")
    client.wallet_address = "fixture-agent"
    client.abstraction = abstraction
    original = client.response

    def response(method, kw):
        if method == "user_role":
            return {"role": "agent", "data": {"user": "fixture-owner"}}
        if method == "clearinghouse_state":
            return {"assetPositions": [], "withdrawable": "0"}
        if method == "spot_clearinghouse_state":
            return {"balances": [{"coin": "USDC", "total": "20", "hold": "5"}]}
        return original(method, kw)

    client.response = response
    adapter = HyperliquidAdapter(client, "hyperliquid", "swap", "BTC-USD-SWAP")
    assert await adapter.available() == expected
    reads = [kw["user"] for name, kw in client.calls if name != "user_role"]
    assert reads and set(reads) == {"fixture-owner"}


@pytest.mark.parametrize("abstraction", ["unifiedAccount", "disabled"])
@pytest.mark.asyncio
async def test_hyperliquid_unified_account_skips_spot_to_perp_transfer(abstraction):
    from scripts.live import prepare_balances as funding
    from scripts.live.accounts import collect

    client = DexMock("hyperliquid", "sync")
    client.abstraction = abstraction
    clients = [(client, "spot", "BTC-USDC-SPOT"), (client, "swap", "BTC-USD-SWAP")]
    snapshot = await collect("hyperliquid", clients)
    snapshot.balances["perp"] = Decimal(0)  # Non-unified: perp needs funding from spot.
    transfers, _ = funding.plan_transfers("hyperliquid", snapshot, "perp")
    unified = abstraction == "unifiedAccount"
    assert bool(transfers) is not unified
    assert ("perp" in snapshot.shared) is unified
    assert not any("transfer" in name for name, _ in client.calls)
