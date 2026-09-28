"""Canonical generated names preserve legacy signatures and request dispatch."""

import importlib
import inspect

import pytest

from scripts.wrapper_codegen import METHOD_ALIASES
from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_orders import invoke


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "exchange,canonical,legacy",
    [(ex, new, old) for ex, aliases in METHOD_ALIASES.items() for new, old in aliases.items()],
)
def test_canonical_names_keep_original_signatures(asynchronous, exchange, canonical, legacy):
    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.{exchange}.client").Client
    assert getattr(cls, canonical) is getattr(cls, legacy)
    assert inspect.signature(getattr(cls, canonical)) == inspect.signature(getattr(cls, legacy))


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "name",
    [
        "close_copy_futures_follower_positions",
        "close_copy_futures_trader_positions",
        *METHOD_ALIASES["bitget"].values(),
    ],
)
@pytest.mark.parametrize(
    "scope",
    [
        {},
        {"symbol": "BTCUSDT"},
        {"tracking_no": "123"},
        {"all_symbols": True},
        {"symbol": "BTCUSDT", "all_symbols": True},
    ],
)
async def test_copy_position_closes_require_explicit_scope(asynchronous, name, scope):
    from tests.unit.test_bitget_endpoint_coverage import _client_kwargs

    prefix = "dcex.async_support" if asynchronous else "dcex"
    cls = importlib.import_module(f"{prefix}.bitget.client").Client
    with _http_server({"code": "00000", "data": {}}) as (base, received):
        client = cls(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            if not scope or len(scope) > 1:
                with pytest.raises(ValueError, match="exclusively"):
                    await invoke(client, name, product_type="USDT-FUTURES", **scope)
                assert received.empty()
            else:
                await invoke(client, name, product_type="USDT-FUTURES", **scope)
                request = received.get_nowait()
                assert request["method"] == "POST"
                assert "all_symbols" not in request["body"]
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
