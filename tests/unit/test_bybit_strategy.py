"""Offline coverage for bybit strategy."""
# ruff: noqa: ANN001, ANN201, D103

import pytest


@pytest.mark.parametrize(
    "symbol,category",
    [
        ("BTC-USDT-SPOT", "UTA_USDT"),
        ("BTC-USDT-SWAP", "UTA_SPOT"),
        ("BTC-USDC-SWAP", "UTA_USDT"),
        ("BTC-USD-SWAP", "UTA_USDT"),
    ],
)
def test_bybit_strategy_rejects_market_mismatch(symbol, category):
    from tests.unit.test_bybit_endpoint_coverage import _route_server, _sync_client

    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            with pytest.raises(ValueError, match="category"):
                client.create_strategy(category, symbol, "Buy", "twap", size="1", duration=600)
        finally:
            client.close()
        assert received.empty()


@pytest.mark.parametrize(
    "fields",
    [
        {"chase_distance": "1", "chase_percent_e4": 10},
        {"sub_size": "1", "order_count": 2},
        {"sub_size": "1", "sub_position_value": "10"},
    ],
)
def test_bybit_strategy_rejects_conflicting_controls(fields):
    from tests.unit.test_bybit_endpoint_coverage import _route_server, _sync_client

    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            with pytest.raises(ValueError):
                client.create_strategy(
                    "UTA_SPOT",
                    "BTC-USDT-SPOT",
                    "Buy",
                    "iceberg",
                    size="2",
                    **dict({"order_count": 2}, **fields),
                )
        finally:
            client.close()
        assert received.empty()


@pytest.mark.parametrize("maker_only,expected", [(True, 0), (False, 1)])
def test_bybit_strategy_derives_category_and_maker_encoding(maker_only, expected):
    import json

    from tests.unit.test_bybit_endpoint_coverage import _route_server, _sync_client

    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            client.create_strategy(
                product_symbol="BTC-USDT-SPOT",
                side="Buy",
                strategy_type="iceberg",
                size="2",
                order_count=2,
                maker_only=maker_only,
            )
        finally:
            client.close()
        body = json.loads(received.get(timeout=10)["body"])
        assert body["category"] == "UTA_SPOT"
        assert body["postOnly"] == expected
