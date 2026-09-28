"""Read-only Arcus live reference-data checks."""

import pytest

from dcex.arcus.client import Client
from dcex.arcus.spot import SpotClient

pytestmark = pytest.mark.live


def test_perpetual_reference_data():
    with Client(timeout=20) as client:
        assert isinstance(client.get_markets(), dict | list)
        assert isinstance(client.get_spot_assets(), dict | list)


def test_spot_reference_data():
    with SpotClient(timeout=20) as client:
        assert isinstance(client.get_tokens(), dict | list)
