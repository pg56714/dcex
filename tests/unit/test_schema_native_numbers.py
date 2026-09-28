"""Native catalog validation must reject bad decimals without an HTTP request."""

import pytest

from tests.unit.native_http_helpers import _http_server

CASES = [
    (
        "bitget",
        "stock_plus_orders_place_order",
        "submittedQuantity",
        {
            "symbol": "AAPL",
            "orderType": "LIMIT",
            "side": "BUY",
            "submittedQuantity": "1",
            "submittedPrice": "100",
            "timeInForce": "DAY",
        },
    ),
    (
        "bitget",
        "stock_plus_orders_place_order",
        "submittedPrice",
        {
            "symbol": "AAPL",
            "orderType": "LIMIT",
            "side": "BUY",
            "submittedQuantity": "1",
            "submittedPrice": "100",
            "timeInForce": "DAY",
        },
    ),
    (
        "bitget",
        "broker_subaccount_withdrawal",
        "amount",
        {
            "subUid": "1",
            "coin": "USDT",
            "dest": "internal_transfer",
            "address": "2",
            "amount": "1",
        },
    ),
    (
        "bybit",
        "place_stock_order",
        "qty",
        {
            "symbol": "AAPL-US",
            "quoteToken": "USDC",
            "side": "BUY",
            "type": "LIMIT",
            "qty": "1",
            "limitPrice": "100",
            "timeInForce": "DAY",
            "orderTime": "1",
            "requestId": "id",
        },
    ),
    (
        "bybit",
        "place_stock_order",
        "limitPrice",
        {
            "symbol": "AAPL-US",
            "quoteToken": "USDC",
            "side": "BUY",
            "type": "LIMIT",
            "qty": "1",
            "limitPrice": "100",
            "timeInForce": "DAY",
            "orderTime": "1",
            "requestId": "id",
        },
    ),
    (
        "bybit",
        "create_fgridbot",
        "total_investment",
        {
            "symbol": "BTCUSDT",
            "grid_mode": "1",
            "min_price": "50000",
            "max_price": "60000",
            "cell_number": "10",
            "leverage": "5",
            "grid_type": "1",
            "total_investment": "1000",
        },
    ),
]


@pytest.mark.parametrize("exchange,method,key,valid", CASES)
@pytest.mark.parametrize("invalid", ["1e-5", "-3", "abc", "NaN"])
def test_native_catalog_rejects_bad_decimal_before_transport(exchange, method, key, valid, invalid):
    from dcex.bitget.client import Client as BitgetClient
    from tests.unit.test_bitget_endpoint_coverage import _client_kwargs
    from tests.unit.test_bybit_endpoint_coverage import _native_client

    with _http_server() as (base, received):
        if exchange == "bitget":
            wrapper = BitgetClient(**_client_kwargs(base))
            client = wrapper._native_client
        else:
            wrapper = None
            client = _native_client(base)
        values = {**valid, key: invalid}
        try:
            with pytest.raises(ValueError, match=key):
                client.private_request_json(method, list(values.items()))
            assert received.empty()
        finally:
            if wrapper is not None:
                wrapper.close()
