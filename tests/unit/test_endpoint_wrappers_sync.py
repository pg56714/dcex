# ruff: noqa: D100, D103, F403, F405

from tests.unit.endpoint_wrapper_helpers import *


@pytest.mark.parametrize("case", SYNC_CASES, ids=[case.id for case in SYNC_CASES])
def test_sync_endpoint_wrapper_is_reachable(
    case: EndpointCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class(case.mode, case.exchange)(**_client_kwargs(case.exchange))
    _patch_lighter_signer(client)
    calls = _wire_sync(client)
    _patch_sync_case(client, case)

    method = getattr(client, case.method_name)
    result = method(**_case_kwargs(case, method))

    if case.method_name != "check_client":
        assert result is not None
    if case.method_name not in NO_REQUEST_METHODS:
        assert calls


def test_sync_hyperliquid_builder_fee_payload_matches_docs() -> None:
    client = _client_class("sync", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_sync(client)
    builder_address = "0x0000000000000000000000000000000000000002"

    result = client.place_order(
        product_symbol="BTC-USD-SWAP",
        isBuy=True,
        price="100",
        size="1",
        reduceOnly=False,
        builder_address=builder_address,
        fee_ten_bp=10,
    )

    action = calls[0]["query"]["action"]
    assert result == {"ok": True}
    assert action["builder"] == {"b": builder_address, "f": 10}
    assert "feeTenBp" not in action


def test_sync_hyperliquid_builder_fee_requires_address_and_fee() -> None:
    client = _client_class("sync", "hyperliquid")(**_client_kwargs("hyperliquid"))
    _wire_sync(client)

    with pytest.raises(ValueError, match="builder_address and fee_ten_bp"):
        client.place_order(
            product_symbol="BTC-USD-SWAP",
            isBuy=True,
            price="100",
            size="1",
            reduceOnly=False,
            builder_address="0x0000000000000000000000000000000000000002",
        )


def test_sync_hyperliquid_builder_fee_requires_fee_when_address_given() -> None:
    client = _client_class("sync", "hyperliquid")(**_client_kwargs("hyperliquid"))
    _wire_sync(client)

    with pytest.raises(ValueError, match="builder_address and fee_ten_bp"):
        client.place_order(
            product_symbol="BTC-USD-SWAP",
            isBuy=True,
            price="100",
            size="1",
            reduceOnly=False,
            fee_ten_bp=10,
        )


def test_sync_hyperliquid_market_order_uses_ioc_limit_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class("sync", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_sync(client)

    client.place_future_market_buy_order(product_symbol="BTC-USD-SWAP", size="1")

    order = calls[0]["query"]["action"]["orders"][0]
    assert order["p"] == "103"
    assert order["t"] == {"limit": {"tif": "Ioc"}}


def test_sync_bybit_post_only_forwards_position_idx() -> None:
    client = _client_class("sync", "bybit")(**_client_kwargs("bybit"))
    calls = _wire_sync(client)

    result = client.place_post_only_limit_buy_order(
        product_symbol="BTC-USDT-SWAP",
        qty="1",
        price="100",
        positionIdx=1,
    )

    assert result == {"ok": True}
    assert calls[0]["method"] == "NATIVE_PRIVATE"
    assert calls[0]["path"] == "place_post_only_limit_buy_order"
    assert dict(calls[0]["query"])["positionIdx"] == "1"


def test_sync_bitmart_modify_limit_order_uses_documented_payload_types() -> None:
    client = _client_class("sync", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_sync(client)

    result = client.modify_limit_order(
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
def test_sync_okx_deposit_withdraw_status_validates_query(
    kwargs: dict[str, str], message: str
) -> None:
    client = _client_class("sync", "okx")(**_client_kwargs("okx"))
    _wire_sync(client)

    with pytest.raises(ValueError, match=message):
        client.get_deposit_withdraw_status(**kwargs)
