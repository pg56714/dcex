"""Offline coverage for aster prediction validation."""
# ruff: noqa: ANN001, ANN201, D103

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.parametrize("quantity", ["1e-3", "+0.01", "NaN", "inf"])
def test_aster_prediction_requires_plain_decimals(quantity):
    from dcex.aster.client import Client
    from tests.unit.test_aster_endpoint_coverage import _client_kwargs

    with _http_server() as (base, received):
        client = Client(**_client_kwargs(base))
        try:
            with pytest.raises(ValueError):
                client.create_prediction_mint(symbol="BTCUP", quantity=quantity)
        finally:
            client.close()
        assert received.empty()
