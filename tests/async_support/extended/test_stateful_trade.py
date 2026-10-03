"""Opt-in non-fill order lifecycle; unsupported markets report explicit skips."""

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["extended"])
@pytest.mark.asyncio
async def test_limit_order_lifecycle(market, symbol, stateful_result):
    await run_case("extended", "async", market, symbol, stateful_result)
