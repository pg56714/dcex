"""Opt-in non-fill order lifecycle; unsupported markets report explicit skips."""

import asyncio

import pytest

from tests.stateful_runner import MARKETS, run_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["extended"])
def test_limit_order_lifecycle(market, symbol, stateful_result):
    asyncio.run(run_case("extended", "sync", market, symbol, stateful_result))
