"""Read-only asynchronous Arcus live reference-data checks."""

import pytest

from dcex.async_support.arcus.client import Client
from dcex.async_support.arcus.spot import SpotClient

pytestmark = [pytest.mark.live, pytest.mark.asyncio]


async def test_perpetual_reference_data():
    client = Client(timeout=20)
    try:
        assert isinstance(await client.get_markets(), dict | list)
        assert isinstance(await client.get_spot_assets(), dict | list)
    finally:
        await client.close()


async def test_spot_reference_data():
    client = SpotClient(timeout=20)
    try:
        assert isinstance(await client.get_tokens(), dict | list)
    finally:
        await client.close()
