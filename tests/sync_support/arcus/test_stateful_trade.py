"""Opt-in non-fill order lifecycle; unsupported markets report explicit skips."""

import asyncio

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["arcus"])
def test_limit_order_lifecycle(market, symbol, stateful_result):
    asyncio.run(run_case("arcus", "sync", market, symbol, stateful_result))


@pytest.mark.parametrize("market,symbol", MARKETS["arcus"])
def test_ioc_never_fills(market, symbol, stateful_result):
    asyncio.run(run_case("arcus", "sync", market, symbol, stateful_result, case="ioc"))


@pytest.mark.parametrize("market,symbol", MARKETS["arcus"])
def test_fok_never_fills(market, symbol, stateful_result):
    asyncio.run(run_case("arcus", "sync", market, symbol, stateful_result, case="fok"))


@pytest.mark.parametrize("market,symbol", MARKETS["arcus"])
def test_reduce_only_cannot_open(market, symbol, stateful_result):
    asyncio.run(run_case("arcus", "sync", market, symbol, stateful_result, case="reduce_only"))


@pytest.mark.parametrize("market,symbol", MARKETS["arcus"])
def test_amend_price(market, symbol, stateful_result):
    asyncio.run(run_case("arcus", "sync", market, symbol, stateful_result, case="amend"))
