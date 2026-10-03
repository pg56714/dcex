"""Opt-in non-crossing limit order, query, cancel and confirmation tests."""

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["okx"])
@pytest.mark.asyncio
async def test_limit_order_lifecycle(market, symbol, stateful_result):
    await run_case("okx", "async", market, symbol, stateful_result)
