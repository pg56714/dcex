"""Read-only asynchronous Arcus live reference-data checks."""

import pytest

from dcex.async_support.arcus.client import Client
from dcex.async_support.arcus.spot import SpotClient

pytestmark = [pytest.mark.live, pytest.mark.asyncio]


async def test_perpetual_reference_data():
    async with Client(timeout=20) as client:
        assert isinstance(await client.get_markets(), dict | list)
        assert isinstance(await client.get_spot_assets(), dict | list)


async def test_spot_reference_data():
    async with SpotClient(timeout=20) as client:
        assert isinstance(await client.get_tokens(), dict | list)
