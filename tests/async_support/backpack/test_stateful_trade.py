"""Opt-in non-fill order tests: lifecycle, IOC, FOK, reduce-only and amend cases."""

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_limit_order_lifecycle(market, symbol, stateful_result):
    await run_case("backpack", "async", market, symbol, stateful_result)


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_ioc_never_fills(market, symbol, stateful_result):
    await run_case("backpack", "async", market, symbol, stateful_result, case="ioc")


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_fok_never_fills(market, symbol, stateful_result):
    await run_case("backpack", "async", market, symbol, stateful_result, case="fok")


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_reduce_only_cannot_open(market, symbol, stateful_result):
    await run_case("backpack", "async", market, symbol, stateful_result, case="reduce_only")


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_amend_price(market, symbol, stateful_result):
    await run_case("backpack", "async", market, symbol, stateful_result, case="amend")
