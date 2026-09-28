# ruff: noqa: ANN001, ANN201, D103
"""Regression tests for explicit consent and account-wide scope."""

import importlib
import inspect
from unittest.mock import AsyncMock, Mock

import pytest

CONFIRMED = [
    ("bitget", "upgrade_to_uta", {}),
    ("bitget", "upgrade_classic_account", {}),
    ("bitget", "uta_delete_sub", {"sub_uid": "123"}),
    ("bitget", "set_uta_account_mode", {"mode": "basic"}),
    ("bitget", "set_futures_asset_mode", {"product_type": "USDT-FUTURES", "asset_mode": "single"}),
    (
        "bitget",
        "move_uta_positions",
        {"from_uid": "1", "to_uid": "2", "category": "USDT-FUTURES", "position_list": []},
    ),
    (
        "bitget",
        "reverse_futures_position",
        {
            "product_symbol": "BTC-USDT-SWAP",
            "margin_coin": "USDT",
            "product_type": "USDT-FUTURES",
            "side": "buy",
        },
    ),
    ("bingx", "reverse_swap_position", {"type_": "MARKET", "product_symbol": "BTC-USDT-SWAP"}),
    ("bingx", "set_swap_asset_mode", {"assetMode": "singleAsset"}),
    ("bybit", "delete_api_key", {}),
    ("bybit", "modify_api_key", {"read_only": 1}),
    ("kucoin", "set_uta_account_mode", {"account_type": "UNIFIED"}),
    ("ondo", "delete_api_key", {"apiKeyID": "key"}),
    ("aster", "exchange_futures_assets", {}),
]
SCOPED = [
    ("bitget", "close_futures_positions", {"product_type": "USDT-FUTURES"}),
    ("bitget", "close_uta_positions", {"category": "USDT-FUTURES"}),
    ("bitget", "cancel_futures_plan_orders", {"product_type": "USDT-FUTURES"}),
    ("bitget", "cancel_spot_plan_orders", {}),
    ("bingx", "close_coin_swap_all_positions", {}),
    ("bingx", "cancel_coin_swap_all_orders", {}),
    ("mexc", "cancel_spot_all_orders", {}),
    ("kucoin", "cancel_spot_stop_orders", {}),
    ("kucoin", "cancel_futures_stop_orders", {}),
    ("kucoin", "cancel_spot_oco_orders", {}),
    ("kucoin", "cancel_margin_oco_orders", {}),
    ("backpack", "cancel_open_strategies", {}),
]


def stub_client(exchange, asynchronous):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    client = cls.__new__(cls)
    client._native_private = AsyncMock(return_value={}) if asynchronous else Mock(return_value={})
    return client


async def call(client, method, kwargs):
    value = getattr(client, method)(**kwargs)
    return await value if inspect.isawaitable(value) else value


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("exchange,method,kwargs", CONFIRMED)
@pytest.mark.parametrize("flag", [None, False, 1, "true"])
async def test_confirmation_required_before_dispatch(asynchronous, exchange, method, kwargs, flag):
    client = stub_client(exchange, asynchronous)
    kwargs = dict(kwargs)
    if flag is not None:
        kwargs["confirm"] = flag
    with pytest.raises(ValueError, match="confirm"):
        await call(client, method, kwargs)
    client._native_private.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("exchange,method,kwargs", CONFIRMED)
async def test_confirmation_is_keyword_only_and_reaches_rust(
    asynchronous, exchange, method, kwargs
):
    client = stub_client(exchange, asynchronous)
    parameter = inspect.signature(getattr(client, method)).parameters["confirm"]
    assert parameter.kind == inspect.Parameter.KEYWORD_ONLY
    await call(client, method, dict(kwargs, confirm=True))
    args, named = client._native_private.call_args
    params = named if exchange == "ondo" else dict(args[1])
    assert params["confirm"] in (True, "true")


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("exchange,method,kwargs", SCOPED)
async def test_scope_required_before_dispatch(asynchronous, exchange, method, kwargs):
    client = stub_client(exchange, asynchronous)
    with pytest.raises(ValueError, match="all_symbols"):
        await call(client, method, kwargs)
    client._native_private.assert_not_called()
    await call(client, method, dict(kwargs, all_symbols=True))
    assert dict(client._native_private.call_args.args[1])["all_symbols"] == "true"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_vault_full_redemption_is_explicit(asynchronous):
    client = stub_client("backpack", asynchronous)
    with pytest.raises(ValueError, match="all"):
        await call(client, "vault_redeem", {"vault_id": 1})
    client._native_private.assert_not_called()
    await call(client, "vault_redeem", {"vault_id": 1, "all": True})
    assert dict(client._native_private.call_args.args[1])["all"] == "true"
