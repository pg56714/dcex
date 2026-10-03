"""Opt-in non-crossing limit order, query, cancel and confirmation tests."""

import asyncio

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["binance"])
def test_limit_order_lifecycle(market, symbol, stateful_result):
    asyncio.run(run_case("binance", "sync", market, symbol, stateful_result))
