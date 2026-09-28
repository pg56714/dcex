# ruff: noqa: ANN001, ANN201, D103
"""Offline regressions for the remaining endpoint review findings."""

from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_review import batch_client, invoke


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_binance_partial_cancel_replace_has_structured_outcomes(asynchronous):
    from dcex.utils.errors import FailedRequestError

    outcomes = {
        "cancelResult": "SUCCESS",
        "newOrderResult": "FAILURE",
        "cancelResponse": {"orderId": 1},
        "newOrderResponse": {"code": -2010, "msg": "Rejected"},
    }
    with _http_server({"code": -2021, "msg": "Partial failure", "data": outcomes}, 409) as (
        base,
        _,
    ):
        async with batch_client(asynchronous, base) as client:
            with pytest.raises(FailedRequestError) as caught:
                await invoke(
                    client,
                    "cancel_replace_spot_order",
                    product_symbol="BTC-USDT-SPOT",
                    side="BUY",
                    order_type="MARKET",
                    cancel_replace_mode="ALLOW_FAILURE",
                    quantity="1",
                    cancel_order_id=1,
                )
            assert caught.value.response_data == outcomes


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "method,kwargs,path",
    [
        ("wallet_dust_transfer", {"asset": ["ETH", "LTC"]}, "/sapi/v1/asset/dust"),
        (
            "place_spot_sor_order",
            {"symbol": "BTCUSDT", "side": "BUY", "order_type": "MARKET", "quantity": "1"},
            "/api/v3/sor/order",
        ),
        ("sign_futures_tradfi_perps_contract", {}, "/fapi/v1/stock/contract"),
        ("liquidate_margin_account", {"kind_type": "MARGIN"}, "/sapi/v1/margin/manual-liquidation"),
        (
            "set_coin_futures_leverage",
            {"product_symbol": "BTCUSD_PERP", "leverage": 3},
            "/dapi/v1/leverage",
        ),
        (
            "amend_futures_batch_orders",
            {
                "orders": [
                    {
                        "symbol": "BTCUSDT",
                        "side": "BUY",
                        "quantity": "1",
                        "price": "10",
                        "orderId": 1,
                    }
                ]
            },
            "/fapi/v1/batchOrders",
        ),
    ],
)
async def test_binance_review_names_and_fields(asynchronous, method, kwargs, path):
    payload = [{"orderId": 1}] if "batch" in method else {"ok": True}
    with _http_server(payload) as (base, received):
        async with batch_client(asynchronous, base) as client:
            await invoke(client, method, **kwargs)
        request = next(r for r in list(received.queue) if urlsplit(r["path"]).path == path)
    pairs = parse_qsl(urlsplit(request["path"]).query or request["body"])
    if method == "wallet_dust_transfer":
        assert [v for k, v in pairs if k == "asset"] == ["ETH", "LTC"]
    if method == "set_coin_futures_leverage":
        assert dict(pairs)["symbol"] == "BTCUSD_PERP"


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
            with pytest.raises(ValueError):
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
        assert received.get(timeout=2)["method"] == "POST"


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
        body = json.loads(received.get(timeout=2)["body"])
        assert body["category"] == "UTA_SPOT"
        assert body["postOnly"] == expected


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


@pytest.mark.parametrize(
    "method,limit",
    [
        ("get_crypto_loan_borrow_history", 100),
        ("get_crypto_loan_common_adjustment_history", 100),
        ("get_spot_lever_token_order_record", 500),
    ],
)
def test_bybit_endpoint_specific_page_limit(method, limit):
    from tests.unit.test_bybit_endpoint_coverage import CASES, _route_server, _sync_client

    case = next(c for c in CASES if c.method_name == method)
    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            getattr(client, method)(*case.args, **dict(case.kwargs, limit=limit))
        finally:
            client.close()
        assert dict(parse_qsl(urlsplit(received.get(timeout=2)["path"]).query))["limit"] == str(
            limit
        )


def test_bybit_max_loan_accepts_collateral_list():
    import json

    from tests.unit.test_bybit_endpoint_coverage import _route_server, _sync_client

    collateral = [{"ccy": "BTC", "amount": "1"}]
    with _route_server() as (base, received):
        client = _sync_client(base)
        try:
            client.crypto_loan_common_max_loan(currency="USDT", collateral_list=collateral)
        finally:
            client.close()
        assert json.loads(received.get(timeout=2)["body"])["collateralList"] == collateral


@pytest.mark.parametrize(
    "base_urls,expected",
    [
        ({}, "https://papi.asterdex.com"),
        (
            {
                "spot_base_url": "https://sapi.asterdex-testnet.com",
                "futures_base_url": "https://fapi.asterdex-testnet.com",
            },
            "https://papi.asterdex-testnet.com",
        ),
    ],
)
def test_aster_prediction_follows_network(base_urls, expected):
    from dcex.aster.client import Client

    client = Client(preload_product_table=False, **base_urls)
    try:
        assert client.prediction_base_url == expected
    finally:
        client.close()


@pytest.mark.parametrize("key", ["spot_base_url", "futures_base_url"])
def test_aster_rejects_mixed_network_defaults(key):
    from dcex.aster.client import Client

    with pytest.raises(ValueError, match="network"):
        Client(preload_product_table=False, **{key: "https://fapi.asterdex-testnet.com"})


def test_aster_nonce_reservations_are_unique_and_current():
    import time
    from concurrent.futures import ThreadPoolExecutor

    from dcex.aster.client import Client

    client = Client(preload_product_table=False)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            values = list(pool.map(lambda _: client.reserve_nonce(), range(100)))
        assert len(set(values)) == 100
        assert all(abs(time.time_ns() // 1000 - value) < 60_000_000 for value in values)
    finally:
        client.close()


def test_extended_commit_bridge_quote_uses_post_query():
    from dcex.extended.client import Client

    with _http_server({"status": "OK", "data": "commitment"}) as (base, received):
        client = Client(api_key="key", base_url=base, preload_product_table=False)
        try:
            client.commit_bridge_quote("quote-123")
        finally:
            client.close()
        request = received.get(timeout=2)
        assert request["method"] == "POST"
        assert urlsplit(request["path"]).path == "/api/v1/user/bridge/quote"
        assert dict(parse_qsl(urlsplit(request["path"]).query)) == {"id": "quote-123"}
        assert request["body"] == ""


@pytest.mark.parametrize(
    "trade_type,symbol,expected",
    [("MARGIN", "BTC-USDT-SPOT", "BTC-USDT"), ("FUTURES", "BTC-USDT-SWAP", "XBTUSDTM")],
)
def test_kucoin_leverage_uses_requested_market(trade_type, symbol, expected):
    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            client.get_uta_leverage(trade_type, product_symbol=symbol)
        finally:
            client.close()
        assert (
            dict(parse_qsl(urlsplit(received.get(timeout=2)["path"]).query))["symbol"] == expected
        )


def test_kucoin_stop_order_generates_client_id():
    import json

    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            client.place_spot_stop_order(
                "buy", "BTC-USDT-SPOT", "limit", "90", price="100", size="1"
            )
        finally:
            client.close()
        body = json.loads(received.get(timeout=2)["body"])
        assert isinstance(body["clientOid"], str) and len(body["clientOid"]) > 10


def test_kucoin_batch_cancel_rejects_both_identifier_lists():
    from dcex.kucoin.client import Client
    from tests.unit.test_kucoin_endpoint_coverage import _client_kwargs

    with _http_server({"code": "200000", "data": {}}) as (base, received):
        client = Client(**_client_kwargs(base, base))
        try:
            with pytest.raises(ValueError):
                client.cancel_futures_batch_orders(
                    order_ids=["1"], client_orders=[{"symbol": "XBTUSDTM", "clientOid": "mine"}]
                )
        finally:
            client.close()
        assert received.empty()


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
