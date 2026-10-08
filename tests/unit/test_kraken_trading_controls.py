"""Offline coverage for kraken trading controls."""
# ruff: noqa: ANN001, ANN201, D103

import pytest


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"margin_mode": "isolated"},
        {"margin_mode": "cross", "max_leverage": "3"},
        {"margin_mode": "invalid"},
    ],
)
def test_kraken_leverage_mode_must_be_explicit_and_consistent(kwargs):
    from dcex.kraken.client import Client
    from tests.unit.test_kraken_endpoint_coverage import _client_kwargs, _route_server

    with _route_server() as (base, received):
        client = Client(**_client_kwargs(base))
        try:
            # A missing margin_mode fails at the call (required argument); others locally.
            with pytest.raises(TypeError if not kwargs else ValueError):
                client.set_futures_leverage_preference("BTC-USD-SWAP", **kwargs)
        finally:
            client.close()
        assert received.empty()


def test_kraken_take_profit_batch_allows_market_trigger():
    from dcex.kraken.client import Client
    from tests.unit.test_kraken_endpoint_coverage import _client_kwargs, _route_server

    with _route_server() as (base, received):
        client = Client(**_client_kwargs(base))
        try:
            client.manage_futures_batch_orders(
                [
                    {
                        "order": "send",
                        "symbol": "PF_XBTUSD",
                        "order_tag": "take-profit",
                        "side": "sell",
                        "size": 1,
                        "orderType": "take_profit",
                        "stopPrice": 100000,
                    }
                ]
            )
        finally:
            client.close()
        assert received.get(timeout=10)["method"] == "POST"
