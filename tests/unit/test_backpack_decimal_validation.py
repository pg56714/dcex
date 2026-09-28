"""Offline coverage for backpack decimal validation."""
# ruff: noqa: ANN001, ANN201, D103

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.parametrize("quantity", ["1e-3", "+0.01", "NaN", "inf"])
@pytest.mark.parametrize("method", ["vault_mint", "vault_redeem", "create_strategy"])
def test_backpack_requires_plain_decimals(method, quantity):
    from dcex.backpack.client import Client
    from tests.unit.test_backpack_endpoint_coverage import _client_kwargs

    with _http_server() as (base, received):
        client = Client(**_client_kwargs(base))
        kwargs = (
            {"vault_id": 1, "symbol": "USDC", "quantity": quantity}
            if method == "vault_mint"
            else {"vault_id": 1, "vault_token_quantity": quantity}
            if method == "vault_redeem"
            else {
                "product_symbol": "BTC-USDC-SPOT",
                "side": "Bid",
                "quantity": quantity,
                "duration": 60,
                "interval": 10,
            }
        )
        try:
            with pytest.raises(ValueError):
                getattr(client, method)(**kwargs)
        finally:
            client.close()
        assert received.empty()
