# ruff: noqa: D100, D103, F403, F405

import asyncio

from tests.unit.endpoint_wrapper_helpers import *


@pytest.mark.parametrize("case", ASYNC_CASES, ids=[case.id for case in ASYNC_CASES])
@pytest.mark.asyncio
async def test_async_endpoint_wrapper_is_reachable(
    case: EndpointCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class(case.mode, case.exchange)(**_client_kwargs(case.exchange))
    _patch_lighter_native_client(client)
    calls = _wire_async(client)
    _patch_async_case(client, case)

    method = getattr(client, case.method_name)
    result = await method(**_case_kwargs(case, method))

    if case.method_name != "check_client":
        assert result is not None
    if case.method_name not in NO_REQUEST_METHODS:
        assert calls


@pytest.mark.asyncio
async def test_async_hyperliquid_builder_fee_payload_matches_docs() -> None:
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_async(client)
    builder_address = "0x0000000000000000000000000000000000000002"

    result = await client.place_order(
        product_symbol="BTC-USD-SWAP",
        isBuy=True,
        price="100",
        size="1",
        reduceOnly=False,
        builder_address=builder_address,
        fee_ten_bp=10,
    )

    assert result == {"ok": True}
    assert calls[0]["method"] == "NATIVE_PRIVATE"
    assert calls[0]["path"] == "place_order"
    params = dict(calls[0]["query"])
    assert params["builder_address"] == builder_address
    assert params["fee_ten_bp"] == "10"


@pytest.mark.asyncio
async def test_async_hyperliquid_builder_fee_requires_address_and_fee() -> None:
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    _wire_async(client)

    with pytest.raises(ValueError, match="builder_address and fee_ten_bp"):
        await client.place_order(
            product_symbol="BTC-USD-SWAP",
            isBuy=True,
            price="100",
            size="1",
            reduceOnly=False,
            builder_address="0x0000000000000000000000000000000000000002",
        )


@pytest.mark.asyncio
async def test_async_hyperliquid_builder_fee_requires_fee_when_address_given() -> None:
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    _wire_async(client)

    with pytest.raises(ValueError, match="builder_address and fee_ten_bp"):
        await client.place_order(
            product_symbol="BTC-USD-SWAP",
            isBuy=True,
            price="100",
            size="1",
            reduceOnly=False,
            fee_ten_bp=10,
        )


@pytest.mark.asyncio
async def test_async_hyperliquid_market_order_uses_ioc_limit_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_async(client)

    await client.place_future_market_buy_order(product_symbol="BTC-USD-SWAP", size="1")

    assert calls[0]["method"] == "NATIVE_PRIVATE"
    assert calls[0]["path"] == "place_future_market_buy_order"
    assert dict(calls[0]["query"]) == {
        "product_symbol": "BTC-USD-SWAP",
        "size": "1",
    }


@pytest.mark.asyncio
async def test_async_extended_place_limit_order_uses_native_signing_params() -> None:
    client = _client_class("async", "extended")(**_client_kwargs("extended"))
    calls = _wire_async(client)

    result = await client.place_limit_order(
        market="BTC-USD",
        side="BUY",
        qty="0.001",
        price="10000",
        post_only=True,
        type_="LIMIT",
    )

    assert result == {"ok": True}
    assert calls[0]["method"] == "NATIVE_PRIVATE"
    assert calls[0]["path"] == "place_limit_order"
    params = dict(calls[0]["query"])
    assert params["type"] == "LIMIT"
    assert params["post_only"] == "true"
    assert params["qty"] == "0.001"


@pytest.mark.parametrize(
    ("exchange", "method_name", "kwargs"),
    [
        (
            "aster",
            "place_spot_order",
            {
                "product_symbol": "ASTER-USDT-SPOT",
                "side": "BUY",
                "type_": "LIMIT",
            },
        ),
        (
            "kucoin",
            "place_futures_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "side": "buy",
                "type_": "limit",
                "size": "1",
            },
        ),
        (
            "mexc",
            "place_contract_order",
            {
                "product_symbol": "BTC-USDT-SWAP",
                "side": 1,
                "type_": 1,
                "openType": 1,
                "vol": "1",
            },
        ),
        (
            "mexc",
            "change_contract_margin",
            {
                "positionId": 1,
                "amount": "1",
                "type_": "ADD",
            },
        ),
    ],
)
@pytest.mark.asyncio
async def test_async_type_keyword_wrappers_send_native_type_key(
    exchange: str,
    method_name: str,
    kwargs: dict[str, object],
) -> None:
    client = _client_class("async", exchange)(**_client_kwargs(exchange))
    calls = _wire_async(client)

    result = await getattr(client, method_name)(**kwargs)

    assert result == {"ok": True}
    keys = [key for key, _value in calls[0]["query"]]
    assert "type" in keys
    assert "type_" not in keys


@pytest.mark.asyncio
async def test_async_bitmart_modify_limit_order_uses_documented_payload_types() -> None:
    client = _client_class("async", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_async(client)

    result = await client.modify_limit_order(
        product_symbol="BTC-USDT-SWAP",
        order_id="123456",
        price="100.1",
        size=1,
    )

    query = dict(calls[0]["query"])
    assert result == {"ok": True}
    assert calls[0]["method"] == "NATIVE_PRIVATE"
    assert calls[0]["path"] == "modify_limit_order"
    assert query["order_id"] == "123456"
    assert query["price"] == "100.1"
    assert query["size"] == "1"


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({}, "Exactly one of wdId or txId"),
        ({"wdId": "withdrawal-id", "txId": "transaction-id"}, "Exactly one of wdId or txId"),
        ({"txId": "transaction-id"}, "ccy, to, chain required"),
    ],
)
@pytest.mark.asyncio
async def test_async_okx_deposit_withdraw_status_validates_query(
    kwargs: dict[str, str], message: str
) -> None:
    client = _client_class("async", "okx")(**_client_kwargs("okx"))
    _wire_async(client)

    with pytest.raises(ValueError, match=message):
        await client.get_deposit_withdraw_status(**kwargs)


@pytest.mark.asyncio
async def test_async_bitmart_post_only_buy_reads_position_response_data() -> None:
    client = _client_class("async", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_async(client)

    async def fake_get_contract_position(*args: object, **kwargs: object) -> dict[str, Any]:
        return {"data": [{"position_type": 2, "current_amount": "1"}]}

    client.get_contract_position = fake_get_contract_position

    result = await client.place_contract_post_only_buy_order(
        product_symbol="BTC-USDT-SWAP",
        price="100.1",
        size=1,
    )

    assert result == {"ok": True}
    assert dict(calls[0]["query"])["side"] == "2"


@pytest.mark.parametrize(
    ("helper_name", "order_method_name", "position_type", "close_side", "open_side"),
    [
        ("place_contract_market_buy_order", "place_contract_market_order", 2, 2, 1),
        ("place_contract_market_sell_order", "place_contract_market_order", 1, 3, 4),
        ("place_contract_post_only_buy_order", "place_contract_post_only_order", 2, 2, 1),
        ("place_contract_post_only_sell_order", "place_contract_post_only_order", 1, 3, 4),
    ],
)
@pytest.mark.asyncio
async def test_async_bitmart_reverse_helpers_close_before_opening(
    helper_name: str,
    order_method_name: str,
    position_type: int,
    close_side: int,
    open_side: int,
) -> None:
    client = _client_class("async", "bitmart")(**_client_kwargs("bitmart"))
    close_completed = False
    sides: list[int] = []

    async def fake_get_contract_position(*args: object, **kwargs: object) -> dict[str, Any]:
        return {"data": [{"position_type": position_type, "current_amount": "1"}]}

    async def fake_place_order(*args: object, **kwargs: Any) -> dict[str, Any]:
        nonlocal close_completed
        side = kwargs["side"]
        sides.append(side)
        if side == close_side:
            await asyncio.sleep(0)
            close_completed = True
        else:
            assert close_completed
        return {"side": side}

    client.get_contract_position = fake_get_contract_position
    setattr(client, order_method_name, fake_place_order)
    kwargs: dict[str, Any] = {"product_symbol": "BTC-USDT-SWAP", "size": 2}
    if "post_only" in helper_name:
        kwargs["price"] = "100.1"

    result = await getattr(client, helper_name)(**kwargs)

    assert result == ({"side": close_side}, {"side": open_side})
    assert sides == [close_side, open_side]
