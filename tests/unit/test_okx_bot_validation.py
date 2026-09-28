"""Offline coverage for okx bot validation."""
# ruff: noqa: ANN001, ANN201, D103

import pytest

from tests.unit.native_http_helpers import _http_server


@pytest.mark.parametrize(
    "method,kwargs",
    [
        ("trading_bot_grid_close_position", {"algo_id": "1", "mkt_close": False}),
        ("trading_bot_grid_close_position", {"algo_id": "1", "mkt_close": False, "sz": "1"}),
        (
            "trading_bot_signal_sub_order",
            {
                "inst_id": "BTC-USDT-SWAP",
                "algo_id": "1",
                "side": "buy",
                "ord_type": "limit",
                "sz": "1",
            },
        ),
    ],
)
def test_okx_bot_conditional_required_fields(method, kwargs):
    from dcex.okx.client import Client
    from tests.unit.test_okx_endpoint_coverage import _client_kwargs

    with _http_server({"code": "0", "data": []}) as (base, received):
        client = Client(**_client_kwargs(base))
        try:
            with pytest.raises(ValueError):
                getattr(client, method)(**kwargs)
        finally:
            client.close()
        assert received.empty()
