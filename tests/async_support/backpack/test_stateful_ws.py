"""Opt-in private WebSocket order-update check around the non-filling limit lifecycle."""

import pytest

from tests.stateful_runner import MARKETS
from tests.stateful_ws import run_ws_case

pytestmark = [pytest.mark.private, pytest.mark.stateful]


@pytest.mark.parametrize("market,symbol", MARKETS["backpack"])
@pytest.mark.asyncio
async def test_order_stream_reports_lifecycle(market, symbol, stateful_result):
    await run_ws_case("backpack", market, symbol, stateful_result)
