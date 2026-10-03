"""Opt-in non-fill order lifecycle; unsupported markets report explicit skips."""

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["hyperliquid"])
@pytest.mark.asyncio
async def test_limit_order_lifecycle(market, symbol, stateful_result):
    await run_case("hyperliquid", "async", market, symbol, stateful_result)
