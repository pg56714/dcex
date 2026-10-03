"""Offline-only verification of previews and exact same-owner transfer routes."""

import importlib
import inspect
from contextlib import asynccontextmanager
from copy import deepcopy
from decimal import Decimal as D

import pytest

from scripts.live import check_clean
from scripts.live import prepare_balances as funding
from scripts.live.accounts import Snapshot, collect
from tests.stateful_adapters import CexAdapter
from tests.stateful_lifecycle import MarketUnavailable
from tests.unit.test_stateful_adapters import EXCHANGES, ExchangeMock


def snapshot(exchange):
    values = {
        "kraken": (
            {"spot_USDT": D(0), "flex_USDT": D(25), "cash_USDT": D(0), "swap_USD": D(0)},
            {"spot_USDT": D(5), "flex_USDT": D(5)},
        ),
        "binance": (
            {"funding_USDC": D(25), "funding_USDT": D(25), "spot_USDC": D(0), "swap_USDT": D(0)},
            {"spot_USDC": D(5), "swap_USDT": D(5)},
        ),
        "bybit": ({"FUND": D(15), "UNIFIED": D(0)}, {"UNIFIED": D(10)}),
        "mexc": ({"spot": D(12), "contract": D(0)}, {"spot": D(3), "contract": D(5)}),
        "kucoin": (
            {"main": D(12), "trade": D(0), "futures": D(0)},
            {"trade": D(3), "futures": D(5)},
        ),
        "hyperliquid": (
            {"spot": D("11.8"), "perp": D("9")},
            {"spot": D("10.5"), "perp": D("10.3")},
        ),
        "aster": ({"futures": D(12), "spot": D(0)}, {"spot": D(3), "futures": D(5)}),
        "bingx": ({"fund": D("13.23"), "spot": D(0), "swap": D(0)}, {"spot": D(3), "swap": D(10)}),
    }
    balances, required = values[exchange]
    return Snapshot(balances=balances, required=required)


class TransferMock:
    def __init__(self, exchange, state):
        self.exchange, self.state = exchange, state
        self.calls = []
        self.cls = importlib.import_module("dcex." + exchange + ".client").Client
        self.wallet_address = "fixture-owner"

    def __getattr__(self, method):
        signature = inspect.signature(getattr(self.cls, method))

        def call(**kw):
            signature.bind(None, **kw)
            self.calls.append((method, kw))
            if method == "user_role":
                return {"role": "user"}
            if method == "get_spot_meta":
                return {"tokens": [{"name": "USDC", "tokenId": "0x" + "1" * 32}]}
            if method == "get_private_collateral":
                return {
                    "borrowLiability": "0",
                    "collateral": [
                        {"symbol": "USDC", "lendQuantity": str(self.state.balances["lend"])}
                    ],
                }
            if self.exchange == "bingx":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "bingx"
                    and r.source
                    == {"fund": "fund", "spot": "spot", "USDTMPerp": "swap"}[kw["from_account"]]
                    and r.destination == ("spot" if kw["to_account"] == "spot" else "swap")
                )
            elif self.exchange == "kucoin":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "kucoin"
                    and r.source
                    == {"MAIN": "main", "TRADE": "trade", "CONTRACT": "futures"}[
                        kw["fromAccountType"]
                    ]
                    and r.destination == ("trade" if kw["toAccountType"] == "TRADE" else "futures")
                )
            elif self.exchange == "aster":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "aster"
                    and r.stage == ("spot" if kw["kindType"] == "FUTURE_SPOT" else "perp")
                )
            elif self.exchange == "binance":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "binance"
                    and r.stage == ("spot" if kw["type_"] == "FUNDING_MAIN" else "perp")
                )
            elif self.exchange == "kraken":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "kraken"
                    and r.stage
                    == ("spot" if method == "withdraw_futures_to_spot_wallet" else "perp")
                )
            elif self.exchange == "mexc":
                route = next(
                    r
                    for r in funding.ROUTES
                    if r.exchange == "mexc"
                    and r.stage == ("spot" if kw["toAccountType"] == "SPOT" else "perp")
                )
            else:
                route = next(r for r in funding.ROUTES if r.exchange == self.exchange)
            amount = D(kw.get("amount", kw.get("quantity")))
            self.state.balances[route.source] -= amount
            self.state.balances[route.destination] += amount
            return {
                "kraken": {"result": "success", "uid": "transfer-fixture"}
                if method == "withdraw_futures_to_spot_wallet"
                else {"error": [], "result": {"refid": "transfer-fixture"}},
                "binance": {"tranId": "transfer-fixture"},
                "bybit": {"retCode": 0, "result": {"status": "SUCCESS"}},
                "kucoin": {"code": "200000", "data": {"orderId": "transfer-fixture"}},
                "mexc": {"tranId": "transfer-fixture"},
                "aster": {"tranId": "transfer-fixture"},
                "hyperliquid": {"status": "ok"},
                "backpack": None,
                "bingx": {"code": 0, "data": {"tranId": "transfer-fixture"}},
            }[self.exchange]

        return call


@pytest.mark.parametrize(
    "available,expected",
    [("27", "20"), ("19.12345678", "19.123456"), ("20.0000009", "20"), ("0", "0")],
)
def test_stage_cap_and_entire_small_source(available, expected):
    state = snapshot("mexc")
    state.balances["spot"] = D(available)
    transfers, after = funding.plan_transfers("mexc", state, "perp")
    assert sum((amount for _, amount in transfers), D(0)) == D(expected)
    assert after["spot"] == D(available) - D(expected)


@pytest.mark.parametrize("current,minimum", [(20, 5), (25, 25)])
def test_sufficient_destination_skips(current, minimum):
    state = snapshot("bybit")
    state.balances["UNIFIED"] = D(current)
    state.required["UNIFIED"] = D(minimum)
    assert funding.plan_transfers("bybit", state, "spot")[0] == []
    assert funding.plan_transfers("bybit", state, "perp")[0] == []


@pytest.mark.parametrize("exchange", ["okx", "bitget", "lighter", "extended", "ondo", "arcus"])
@pytest.mark.parametrize("stage", ["spot", "perp"])
def test_shared_wallets_never_propose_transfers(exchange, stage):
    state = Snapshot(balances={"shared": D(12)}, required={"shared": D(5)})
    assert funding.plan_transfers(exchange, state, stage) == ([], state.balances)


@pytest.mark.asyncio
async def test_kucoin_multiple_sources_share_one_stage_cap(monkeypatch):
    state = snapshot("kucoin")
    state.balances.update(main=D(5), trade=D(25))
    client = TransferMock("kucoin", state)

    async def read(*_):
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare("kucoin", [(client, "", "")], stage="perp", execute=True)
    assert [D(row["amount"]) for row in report["executed"]] == [D(5), D(15)]
    assert state.balances == {"main": D(0), "trade": D(10), "futures": D(20)}


@pytest.mark.asyncio
async def test_final_location_table_is_observed_not_projected(monkeypatch, capsys):
    state = snapshot("binance")

    @asynccontextmanager
    async def clients(_):
        yield []

    async def read(*_):
        return deepcopy(state)

    monkeypatch.setattr(funding, "clients_for", clients)
    monkeypatch.setattr(funding, "collect", read)
    monkeypatch.setattr(funding, "load_dotenv", lambda: None)
    assert await funding.run_cli("binance", False, "spot") == 0
    output = capsys.readouterr().out
    assert "binance | funding_USDC | USDC | 25" in output
    assert "binance | spot_USDC | USDC | 0" in output
    assert "no restore" in output


@pytest.mark.parametrize("stage", ["", "restore", "swap", "external"])
def test_invalid_stages_are_rejected(stage):
    with pytest.raises(ValueError, match="stage"):
        funding.plan_transfers("kucoin", snapshot("kucoin"), stage)


@pytest.mark.parametrize(
    "exchange,stage",
    [
        ("binance", "spot"),
        ("binance", "perp"),
        ("kraken", "spot"),
        ("kraken", "perp"),
        ("bybit", "spot"),
        ("bybit", "perp"),
        ("mexc", "perp"),
        ("mexc", "contract->spot"),
        ("kucoin", "spot"),
        ("kucoin", "futures->spot"),
        ("kucoin", "perp"),
        ("hyperliquid", "perp"),
        ("aster", "spot"),
        ("aster", "perp"),
        ("bingx", "spot"),
        ("bingx", "swap->spot"),
        ("bingx", "perp"),
    ],
)
@pytest.mark.asyncio
async def test_preview_is_read_only_and_execute_only_uses_owned_routes(
    monkeypatch, exchange, stage
):
    state = snapshot(exchange)
    reverse = "->" in stage
    if reverse:
        # After a perp stage everything sits in the contract account (no restore).
        source = stage.split("->")[0]
        for key in state.balances:
            state.balances[key] = D(0)
        state.balances[source] = D("13.2")
        stage = "spot"
    if stage == "perp" and exchange in {"aster", "bingx"}:
        state.balances["spot"] = D(12)
        state.balances["futures" if exchange == "aster" else "swap"] = D(0)
    if exchange == "kraken" and stage == "perp":
        state.balances.update(spot_USDT=D(25), flex_USDT=D(0))
    client = TransferMock(exchange, state)

    async def read(*_):
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare(exchange, [(client, "spot", "fixture")], stage=stage)
    assert report["mode"] == "preview"
    assert not client.calls
    assert report["proposed"]
    result = await funding.prepare(
        exchange, [(client, "spot", "fixture")], stage=stage, execute=True
    )
    writes = [
        (method, params)
        for method, params in client.calls
        if not method.startswith("get_") and method != "user_role"
    ]
    assert len(writes) == 1
    expected = {
        "kraken": "withdraw_futures_to_spot_wallet"
        if stage == "spot"
        else "wallet_transfer_to_futures",
        "binance": "create_universal_transfer",
        "bybit": "create_internal_transfer",
        "mexc": "user_universal_transfer",
        "kucoin": "flex_transfer",
        "hyperliquid": "transfer_between_dexes",
        "aster": "transfer_spot_futures",
        "bingx": "asset_transfer",
    }
    assert all(name == expected[exchange] for name, _ in writes)
    for _, params in writes:
        assert not set(params) & {
            "address",
            "fromUserId",
            "toUserId",
            "toMemberId",
            "subAccount",
            "destination",
        }
        if exchange == "kucoin":
            assert params["transfer_type"] == "INTERNAL"
            assert params["fromAccountType"] == (
                "CONTRACT" if reverse else "MAIN" if stage == "spot" else params["fromAccountType"]
            )
            assert params["fromAccountType"] in {"MAIN", "TRADE", "CONTRACT"}
        if exchange == "mexc":
            assert (params["fromAccountType"], params["toAccountType"]) == (
                ("FUTURES", "SPOT") if reverse else ("SPOT", "FUTURES")
            )
        if exchange == "hyperliquid":
            assert params["token"] == "USDC:0x" + "1" * 32
        if exchange == "bingx":
            expected_source = "USDTMPerp" if reverse else "fund" if stage == "spot" else "spot"
            assert params["from_account"] == expected_source
            assert params["to_account"] in {"spot", "USDTMPerp"}
    assert result["fund_locations"] == funding.fund_locations(exchange, state)
    assert sum(D(row["amount"]) for row in result["executed"]) <= 20


@pytest.mark.parametrize("destination", ["external", "subaccount", "other-user", "withdraw"])
def test_non_internal_route_rejected_without_any_client_call(destination):
    state = snapshot("kucoin")
    client = TransferMock("kucoin", state)
    with pytest.raises(ValueError, match="non-allowlisted"):
        funding.submit_transfer(
            client, funding.Route("kucoin", "main", destination, "USDT", D(4)), D(1)
        )
    assert not client.calls


@pytest.mark.parametrize("amount", ["NaN", "Infinity", "-1", "0", "1000000"])
def test_invalid_or_oversized_amount_rejected(amount):
    route = funding.ROUTES[0]
    with pytest.raises(ValueError):
        funding.submit_transfer(None, route, D(amount))


def test_less_than_twenty_moves_all_without_reserving_previous_stage():
    state = snapshot("kucoin")
    state.balances["main"] = D(5)
    transfers, after = funding.plan_transfers("kucoin", state, "spot")
    assert transfers[0][1] == 5
    assert after["main"] == 0
    assert after["trade"] == 5


def test_hyperliquid_perp_stage_moves_all_spot_collateral():
    transfers, after = funding.plan_transfers("hyperliquid", snapshot("hyperliquid"), "perp")
    assert transfers[0][1] == D("11.8")
    assert after["spot"] == 0


@pytest.mark.asyncio
async def test_changed_balance_blocks_before_mutation(monkeypatch):
    state = snapshot("mexc")
    client = TransferMock("mexc", state)
    count = 0

    async def read(*_):
        nonlocal count
        count += 1
        value = deepcopy(state)
        if count > 1:
            value.balances["spot"] = D(2)
        return value

    monkeypatch.setattr(funding, "collect", read)
    with pytest.raises(ValueError):
        await funding.prepare("mexc", [(client, "", "")], stage="perp", execute=True)
    assert not client.calls


@pytest.mark.asyncio
async def test_uncertain_acknowledgement_is_not_retried(monkeypatch):
    state = snapshot("bybit")

    async def read(*_):
        return state

    monkeypatch.setattr(funding, "collect", read)
    attempts = []

    def send(*_):
        attempts.append(1)
        raise TimeoutError("ambiguous response")

    monkeypatch.setattr(funding, "submit_transfer", send)
    with pytest.raises(TimeoutError):
        await funding.prepare("bybit", [(None, "", "")], stage="spot", execute=True)
    assert len(attempts) == 1


@pytest.mark.parametrize(
    "exchange", [ex for ex in EXCHANGES if ex not in {"bybit", "backpack", "binance", "kraken"}]
)
@pytest.mark.asyncio
async def test_account_snapshot_calls_only_read_operations(exchange):
    client = ExchangeMock(exchange, True, "sync")
    state = await collect(exchange, [(client, "spot", "BTC-USDT-SPOT")])
    assert state.markets[0]["status"] == "clean"
    assert all(method.startswith("get_") for method, _ in client.calls)


@pytest.mark.asyncio
async def test_binance_funding_snapshot_reads_each_quote_asset_free_balance():
    class Client(ExchangeMock):
        def payload(self, method, kw):
            if method == "get_funding_wallet":
                return [{"asset": "USDC", "free": "12.5"}, {"asset": "USDT", "free": "21"}]
            return super().payload(method, kw)

    client = Client("binance", True, "sync")
    state = await collect("binance", [(client, "spot", "BTC-USDT-SPOT")])
    assert state.balances["funding_USDC"] == D("12.5")
    assert state.balances["funding_USDT"] == D(21)
    assert state.assets["funding_USDC"] == "USDC"
    assert all(method.startswith("get_") for method, _ in client.calls)


@pytest.mark.asyncio
async def test_kraken_transfer_amount_uses_available_token_quantity_not_margin():
    class Client(ExchangeMock):
        def payload(self, method, kw):
            if method == "get_futures_accounts":
                return {
                    "accounts": {
                        "flex": {
                            "availableMargin": "999",
                            "currencies": {"USDT": {"quantity": "17", "available": "12"}},
                        },
                        "cash": {"balances": {"usdt": "3"}},
                    }
                }
            return super().payload(method, kw)

    client = Client("kraken", True, "sync")
    state = await collect("kraken", [(client, "spot", "DOGE-USDT-SPOT")])
    assert state.balances["flex_USDT"] == 12
    assert state.balances["cash_USDT"] == 3
    state.balances["spot_USDT"] = D(0)
    assert funding.plan_transfers("kraken", state, "spot")[0][0][1] == 12


@pytest.mark.asyncio
async def test_kraken_missing_wallet_endpoint_is_manual_skip(monkeypatch):
    async def read(*_):
        return snapshot("kraken")

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare("kraken", [(object(), "", "")], stage="spot")
    assert not report["proposed"]
    assert "Manual funding required" in report["notes"][0]


@pytest.mark.asyncio
async def test_kraken_unexpected_cash_credit_stops_and_reports_actual_location(monkeypatch, capsys):
    state = snapshot("kraken")
    state.assets.update(cash_USDT="USDT", swap_USD="USD")
    state.balances.update(spot_USDT=D(12), flex_USDT=D(0))
    client = TransferMock("kraken", state)
    calls = []

    def cash_credit(**kw):
        calls.append(kw)
        state.balances["spot_USDT"] -= D(kw["amount"])
        state.balances["cash_USDT"] += D(kw["amount"])
        return {"error": [], "result": {"refid": "transfer-fixture"}}

    client.wallet_transfer_to_futures = cash_credit

    @asynccontextmanager
    async def clients(_):
        yield [(client, "", "")]

    async def read(*_):
        return deepcopy(state)

    monkeypatch.setattr(funding, "clients_for", clients)
    monkeypatch.setattr(funding, "collect", read)
    monkeypatch.setattr(funding, "load_dotenv", lambda: None)
    assert await funding.run_cli("kraken", True, "perp") == 1
    assert len(calls) == 1
    output = capsys.readouterr().out
    assert "kraken | cash_USDT | USDT | 12" in output
    assert "cash -> flex in the Kraken UI" in output


@pytest.mark.asyncio
async def test_kraken_asynchronous_credit_is_polled_before_failing(monkeypatch):
    state = snapshot("kraken")
    state.balances.update(spot_USDT=D(12), flex_USDT=D(0))
    client = TransferMock("kraken", state)
    pending = []

    def delayed(**kw):
        pending.append(D(kw["amount"]))
        state.balances["spot_USDT"] -= D(kw["amount"])
        return {"error": [], "result": {"refid": "transfer-fixture"}}

    client.wallet_transfer_to_futures = delayed
    reads = 0

    async def read(*_):
        nonlocal reads
        reads += 1
        if reads == 5 and pending:
            state.balances["flex_USDT"] += pending.pop()
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    monkeypatch.setattr(funding, "KRAKEN_CONFIRM_DELAY", 0)
    report = await funding.prepare("kraken", [(client, "", "")], stage="perp", execute=True)
    assert [D(row["amount"]) for row in report["executed"]] == [D(12)]
    assert state.balances["flex_USDT"] == 12


@pytest.mark.asyncio
async def test_kraken_never_credited_stops_after_short_poll_without_retry(monkeypatch):
    state = snapshot("kraken")
    state.balances.update(spot_USDT=D(12), flex_USDT=D(0))
    client = TransferMock("kraken", state)
    sends = []
    client.wallet_transfer_to_futures = lambda **kw: (
        sends.append(kw) or {"error": [], "result": {"refid": "transfer-fixture"}}
    )
    reads = []

    async def read(*_):
        reads.append(1)
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    monkeypatch.setattr(funding, "KRAKEN_CONFIRM_DELAY", 0)
    with pytest.raises(ValueError, match="not confirmed; do not retry"):
        await funding.prepare("kraken", [(client, "", "")], stage="perp", execute=True)
    assert len(sends) == 1
    assert len(reads) == 2 + funding.KRAKEN_CONFIRM_POLLS


@pytest.mark.asyncio
async def test_execute_allows_small_source_growth_but_sends_previewed_amount(monkeypatch):
    state = snapshot("bybit")
    state.balances["FUND"] = D("12.5")
    client = TransferMock("bybit", state)
    reads = 0

    async def read(*_):
        nonlocal reads
        reads += 1
        if reads == 2:
            state.balances["FUND"] += D("0.000003")  # source grew slightly after preview
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare("bybit", [(client, "", "")], stage="spot", execute=True)
    assert [row["amount"] for row in report["executed"]] == ["12.5"]
    assert state.balances["FUND"] == D("0.000003")


def test_rounding_is_down_to_exchange_step_and_never_exceeds_cap():
    assert funding.round_down("kraken", D("12.123456789")) == D("12.12345678")
    assert funding.round_down("bingx", D("13.2399999")) == D("13.239999")
    assert funding.round_down("hyperliquid", D("11.8")) == D("11.8")
    state = snapshot("kraken")
    state.balances.update(flex_USDT=D("25.123456789"))
    transfers, _ = funding.plan_transfers("kraken", state, "spot")
    assert transfers[0][1] == 20
    state.balances.update(flex_USDT=D("19.999999999"))
    assert funding.plan_transfers("kraken", state, "spot")[0][0][1] == D("19.99999999")
    client = TransferMock("mexc", snapshot("mexc"))
    route = next(r for r in funding.ROUTES if r.exchange == "mexc")
    funding.submit_transfer(client, route, D("5.1234569"))
    assert client.calls[0][1]["amount"] == "5.123456"
    with pytest.raises(ValueError, match="rounds to zero"):
        funding.submit_transfer(client, route, D("0.0000009"))


@pytest.mark.parametrize("exchange,source,destination", [("bybit", "FUND", "UNIFIED")])
def test_need_only_threshold_and_single_transfer_across_stages(exchange, source, destination):
    state = Snapshot(balances={source: D(30), destination: D(12)}, required={destination: D(10)})
    assert funding.plan_transfers(exchange, state, "spot")[0] == []
    assert funding.plan_transfers(exchange, state, "perp")[0] == []
    state.balances[destination] = D(4)
    transfers, after = funding.plan_transfers(exchange, state, "spot")
    assert [amount for _, amount in transfers] == [D(20)]
    state.balances.update(after)
    assert funding.plan_transfers(exchange, state, "perp")[0] == []
    small = Snapshot(balances={source: D(7), destination: D(4)}, required={destination: D(10)})
    assert [q for _, q in funding.plan_transfers(exchange, small, "spot")[0]] == [D(7)]


def test_cli_requires_stage_before_constructing_clients(monkeypatch):
    monkeypatch.setattr("sys.argv", ["prepare_balances.py"])
    with pytest.raises(SystemExit) as error:
        funding.main()
    assert error.value.code == 2


@pytest.mark.asyncio
async def test_check_clean_only_reads_and_reports_dirty_state(monkeypatch, capsys):
    state = Snapshot(
        markets=[{"status": "dirty", "open_orders": [{"id": "fixture"}], "positions": []}]
    )

    @asynccontextmanager
    async def clients(_):
        yield []

    async def read(*_):
        return state

    monkeypatch.setattr(check_clean, "clients_for", clients)
    monkeypatch.setattr(check_clean, "collect", read)
    monkeypatch.setattr(check_clean, "load_dotenv", lambda: None)
    assert await check_clean.run_cli("binance") == 1
    assert "dirty" in capsys.readouterr().out


@pytest.mark.asyncio
async def test_arcus_has_no_automatic_transfer_routes():
    state = await collect("arcus", [])
    assert not state.blocked
    assert funding.plan_transfers("arcus", state, "perp") == ([], {})


@pytest.mark.asyncio
async def test_preview_cli_returns_nonzero_for_blocked_protocol(monkeypatch, capsys):
    @asynccontextmanager
    async def clients(_):
        yield []

    async def blocked(*_):
        return Snapshot(blocked=["fixture blocked protocol"])

    monkeypatch.setattr(funding, "clients_for", clients)
    monkeypatch.setattr(funding, "collect", blocked)
    monkeypatch.setattr(funding, "load_dotenv", lambda: None)
    assert await funding.run_cli("arcus", False, "perp") == 1
    assert "blocked" in capsys.readouterr().out
    with pytest.raises(ValueError, match="blocked protocol"):
        await funding.prepare("arcus", [], stage="perp", execute=True)


def test_hyperliquid_missing_token_id_never_transfers():
    class Client:
        wallet_address = "fixture-owner"

        def user_role(self, *, user):
            return {"role": "user"}

        def get_spot_meta(self):
            return {"tokens": []}

    route = next(r for r in funding.ROUTES if r.exchange == "hyperliquid")
    with pytest.raises(ValueError, match="metadata"):
        funding.submit_transfer(Client(), route, D(1))


@pytest.mark.parametrize(
    "role",
    [
        {"role": "agent", "data": {"user": "fixture-owner"}},
        {"role": "user", "data": {"user": "different-owner"}},
        {"role": "missing"},
    ],
)
def test_hyperliquid_agent_or_mismatched_owner_never_transfers(role):
    client = TransferMock("hyperliquid", snapshot("hyperliquid"))
    client.user_role = lambda *, user: role
    route = next(r for r in funding.ROUTES if r.exchange == "hyperliquid")
    with pytest.raises(ValueError, match="owner"):
        funding.submit_transfer(client, route, D(1))
    assert not client.calls


@pytest.mark.parametrize("exchange", ["bybit"])
@pytest.mark.asyncio
async def test_funding_snapshot_reads_explicit_fund_fields(exchange):
    class Client(ExchangeMock):
        def payload(self, method, kw):
            if method == "get_coin_balance":
                return {"balance": {"transferBalance": "15"}}
            return super().payload(method, kw)

    client = Client(exchange, True, "sync")
    result = await collect(exchange, [(client, "spot", "BTC-USDT-SPOT")])
    assert result.balances["FUND"] == D(15)
    assert all(method.startswith("get_") for method, _ in client.calls)


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{"balance": {}}, {"assets": [{"asset": "USDT"}]}])
async def test_bingx_missing_assets_or_free_fails_closed(payload):
    class Client(ExchangeMock):
        def payload(self, method, kwargs):
            if method == "get_fund_account_balance":
                return payload
            return super().payload(method, kwargs)

    client = Client("bingx", True, "sync")
    with pytest.raises(KeyError):
        await collect("bingx", [(client, "spot", "BTC-USDT-SPOT")])
    assert not any(method == "asset_transfer" for method, _ in client.calls)


@pytest.mark.asyncio
async def test_bingx_fund_available_uses_assets_free():
    client = ExchangeMock("bingx", True, "sync")
    state = await collect("bingx", [(client, "spot", "BTC-USDT-SPOT")])
    assert state.balances["fund"] == D("13.23")
    assert not state.blocked


@pytest.fixture
def unavailable_aster_spot(monkeypatch):
    """Make the Aster spot order test unavailable while its balances stay readable."""
    original = CexAdapter.prepare

    async def prepare(self):
        if self.exchange == "aster" and self.spot:
            raise MarketUnavailable("aster spot: simulated unavailable market")
        return await original(self)

    monkeypatch.setattr(CexAdapter, "prepare", prepare)


def aster_clients(spot_has_order=False):
    spot = ExchangeMock("aster", True, "sync")
    spot.placed = spot_has_order
    swap = ExchangeMock("aster", False, "sync")
    return [(spot, "spot", "USDC-USDT-SPOT"), (swap, "swap", "BTC-USDT-SWAP")]


@pytest.mark.usefixtures("unavailable_aster_spot")
@pytest.mark.asyncio
async def test_unavailable_market_is_reported_and_does_not_block_other_stage():
    state = await collect("aster", aster_clients())
    assert not state.blocked
    assert len(state.unavailable) == 1 and "unavailable" in state.unavailable[0]
    spot = next(row for row in state.markets if row["market"] == "spot")
    assert spot["status"] == "unavailable" and spot["minimum_order"] == "N/A"
    assert state.balances["spot"] == D(20) and "spot" not in state.required
    state.balances["futures"] = D(0)
    transfers, after = funding.plan_transfers("aster", state, "perp")
    assert [(r.source, r.destination, q) for r, q in transfers] == [("spot", "futures", D(20))]
    assert after["futures"] == D(20)
    assert funding.plan_transfers("aster", state, "spot")[0] == []


@pytest.mark.usefixtures("unavailable_aster_spot")
@pytest.mark.asyncio
async def test_unavailable_market_open_orders_are_reported_and_block_transfers():
    state = await collect("aster", aster_clients(spot_has_order=True))
    spot = next(row for row in state.markets if row["market"] == "spot")
    assert spot["status"] == "dirty" and spot["open_orders"]
    with pytest.raises(ValueError, match="Existing orders"):
        funding.plan_transfers("aster", state, "perp")


@pytest.mark.usefixtures("unavailable_aster_spot")
@pytest.mark.asyncio
@pytest.mark.parametrize(("spot_has_order", "expected"), [(False, 0), (True, 1)])
async def test_check_clean_exit_reflects_dirty_state_not_unavailable_markets(
    monkeypatch, capsys, spot_has_order, expected
):
    @asynccontextmanager
    async def clients(_):
        yield aster_clients(spot_has_order)

    monkeypatch.setattr(check_clean, "clients_for", clients)
    monkeypatch.setattr(check_clean, "load_dotenv", lambda: None)
    assert await check_clean.run_cli("aster") == expected
    assert "unavailable" in capsys.readouterr().out


@pytest.mark.usefixtures("unavailable_aster_spot")
@pytest.mark.asyncio
async def test_preview_and_execute_fund_perp_stage_when_spot_is_unavailable(monkeypatch):
    state = await collect("aster", aster_clients())
    state.balances["futures"] = D(0)
    client = TransferMock("aster", state)

    async def read(*_):
        return deepcopy(state)

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare("aster", [(client, "swap", "fixture")], stage="perp")
    assert report["unavailable"] == state.unavailable and not report["blocked"]
    assert report["proposed"] and not client.calls
    result = await funding.prepare(
        "aster", [(client, "swap", "fixture")], stage="perp", execute=True
    )
    assert [name for name, _ in client.calls] == ["transfer_spot_futures"]
    assert result["executed"][0]["amount"] == "20"


@pytest.mark.asyncio
async def test_hyperliquid_unified_account_preview_notes_shared_collateral(monkeypatch):
    state = snapshot("hyperliquid")
    state.shared["perp"] = "unified account: spot USDC is perp collateral"

    async def read(*_):
        return state

    monkeypatch.setattr(funding, "collect", read)
    report = await funding.prepare("hyperliquid", [(None, "", "")], stage="perp", execute=True)
    assert report["proposed"] == [] and report["executed"] == []
    assert "unified account: spot USDC is perp collateral" in report["notes"]
