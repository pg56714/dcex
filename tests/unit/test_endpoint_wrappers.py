"""Offline coverage for exchange endpoint wrapper methods."""
# ruff: noqa: ANN401, D101, D102, D103

from __future__ import annotations

import ast
import inspect
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest

from dcex.registry import ASYNC_EXCHANGES, SYNC_EXCHANGES
from dcex.utils.common import Common

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT_FILE_SUFFIXES = (
    "_account_http.py",
    "_asset_http.py",
    "_market_http.py",
    "_position_http.py",
    "_public_http.py",
    "_trade_http.py",
    "_trading_http.py",
)


@dataclass(frozen=True)
class EndpointCase:
    mode: str
    exchange: str
    method_name: str

    @property
    def id(self) -> str:
        return f"{self.mode}-{self.exchange}-{self.method_name}"


class FakePTM:
    """Product table stand-in with enough behavior for endpoint wrapper tests."""

    def get_exchange_symbol(self, exchange: Common | str, product_symbol: str | None = None) -> str:
        if exchange == Common.HYPERLIQUID or str(exchange) == Common.HYPERLIQUID.value:
            return '["BTC",0]'
        if exchange == Common.GATEIO or str(exchange) == Common.GATEIO.value:
            return "BTC_USDT"
        if exchange == Common.OKX or str(exchange) == Common.OKX.value:
            return product_symbol or "BTC-USDT-SWAP"
        if exchange == Common.BITMEX or str(exchange) == Common.BITMEX.value:
            return "XBTUSDT"
        return "BTCUSDT"

    def get_product_type(self, exchange: Common | str, product_symbol: str | None = None) -> str:
        if product_symbol and "SPOT" in product_symbol:
            return "spot"
        return "swap"

    def get_exchange_type(self, exchange: Common | str, product_symbol: str | None = None) -> str:
        if exchange == Common.OKX or str(exchange) == Common.OKX.value:
            return "SPOT" if product_symbol and "SPOT" in product_symbol else "SWAP"
        if exchange == Common.BINANCE or str(exchange) == Common.BINANCE.value:
            return "spot" if product_symbol and "SPOT" in product_symbol else "future"
        if exchange == Common.BYBIT or str(exchange) == Common.BYBIT.value:
            return "spot" if product_symbol and "SPOT" in product_symbol else "linear"
        return "swap"


class FakeAsyncResponse:
    def json(self) -> dict[str, str]:
        return {"listenKey": "test-listen-key"}


class FakeAsyncSession:
    is_closed = False

    async def post(self, *args: object, **kwargs: object) -> FakeAsyncResponse:
        return FakeAsyncResponse()


class FakeSyncHyperliquidMarket:
    def get_meta_and_asset_ctxs(self) -> list[Any]:
        return [{}, [{"midPx": "100.0"}]]


class FakeAsyncHyperliquidMarket:
    async def async_init(self) -> FakeAsyncHyperliquidMarket:
        return self

    async def get_meta_and_asset_ctxs(self) -> list[Any]:
        return [{}, [{"midPx": "100.0"}]]


def _endpoint_method_names(mode: str, exchange: str) -> list[str]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    exchange_dir = base / exchange

    names: list[str] = []
    for path in sorted(exchange_dir.glob("*.py")):
        if not path.name.endswith(ENDPOINT_FILE_SUFFIXES):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
            for node in cls.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not node.name.startswith("_") and node.name not in {"async_init", "close"}:
                        names.append(node.name)
    return sorted(set(names))


def _cases(mode: str, exchanges: tuple[str, ...]) -> list[EndpointCase]:
    return [
        EndpointCase(mode=mode, exchange=exchange, method_name=name)
        for exchange in exchanges
        for name in _endpoint_method_names(mode, exchange)
    ]


SYNC_CASES = _cases("sync", SYNC_EXCHANGES)
ASYNC_CASES = _cases("async", ASYNC_EXCHANGES)


def _client_class(mode: str, exchange: str) -> type:
    module_name = f"dcex.{exchange}.client"
    if mode == "async":
        module_name = f"dcex.async_support.{exchange}.client"
    return import_module(module_name).Client


def _client_kwargs(exchange: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"preload_product_table": False}
    if exchange in {"binance", "bingx", "bitmex", "bybit", "gateio"}:
        kwargs.update(api_key="api-key", api_secret="api-secret")
    elif exchange == "bitmart":
        kwargs.update(api_key="api-key", api_secret="api-secret", memo="memo")
    elif exchange in {"okx", "kucoin"}:
        kwargs.update(api_key="api-key", api_secret="api-secret", passphrase="passphrase")
    elif exchange == "hyperliquid":
        kwargs.update(
            wallet_address="0x0000000000000000000000000000000000000001",
            private_key="0x" + "1" * 64,
        )
    return kwargs


def _wire_sync(client: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    client.ptm = FakePTM()

    def fake_request(
        method: str,
        path: object,
        query: Any = None,
        body: Any = None,
        **kwargs: object,
    ) -> dict[str, Any]:
        calls.append(
            {"method": method, "path": path, "query": query, "body": body, "kwargs": kwargs}
        )
        return {"ok": True}

    client._request = fake_request
    return calls


def _wire_async(client: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    client.ptm = FakePTM()
    client.session = FakeAsyncSession()

    async def fake_request(
        method: str,
        path: object,
        query: Any = None,
        body: Any = None,
        **kwargs: object,
    ) -> dict[str, Any]:
        calls.append(
            {"method": method, "path": path, "query": query, "body": body, "kwargs": kwargs}
        )
        return {"ok": True}

    client._request = fake_request
    return calls


def _product_symbol(exchange: str, method_name: str) -> str:
    if exchange == "bitmex":
        return "XBT-USDT-SWAP"
    if exchange == "hyperliquid":
        return "BTC-USD-SWAP"
    if "spot" in method_name:
        return "BTC-USDT-SPOT"
    return "BTC-USDT-SWAP"


def _sample_order(exchange: str) -> dict[str, Any]:
    if exchange == "gateio":
        return {"product_symbol": "BTC-USDT-SWAP", "size": 1, "price": "100"}
    if exchange == "kucoin":
        return {
            "symbol": "BTC-USDT-SPOT",
            "type": "limit",
            "side": "buy",
            "size": "1",
            "price": "1",
        }
    if exchange == "okx":
        return {
            "instId": "BTC-USDT-SWAP",
            "tdMode": "cross",
            "side": "buy",
            "ordType": "limit",
            "sz": "1",
            "px": "100",
        }
    return {"symbol": "BTCUSDT", "side": "Buy", "orderType": "Limit", "qty": "1", "price": "1"}


def _sample_value(case: EndpointCase, parameter: inspect.Parameter) -> Any:
    name = parameter.name
    method_name = case.method_name

    if name == "product_symbol":
        return _product_symbol(case.exchange, method_name)
    if name in {"product_symbols"}:
        return [_product_symbol(case.exchange, method_name)]
    if name in {"side"}:
        if case.exchange == "bitmart" and "contract" in method_name:
            return 1
        if case.exchange in {"bybit", "bitmex"}:
            return "Buy"
        return "buy"
    if name in {"isBuy", "reduceOnly", "isCross", "randomize", "dual_mode"}:
        return True
    if name in {"type", "type_"}:
        return "limit"
    if name in {"orderType"}:
        return "Limit"
    if name in {"tdMode", "mgnMode"}:
        return "cross"
    if name in {"ordType"}:
        return "limit"
    if name in {"category"}:
        return "linear"
    if name in {"instType"}:
        return "SPOT"
    if name in {"ccy", "currency", "coin", "quoteCoin", "baseCoin"}:
        return "USDT"
    if name in {"settleCoin"}:
        return "USDT"
    if name in {"symbol"}:
        return "XBT-USDT-SWAP" if case.exchange == "bitmex" else "BTCUSDT"
    if name in {"contract"}:
        return "BTC_USDT"
    if name in {"path"}:
        return "futures"
    if name in {"tif", "timeInForce"}:
        return "GTC"
    if name in {"posMode"}:
        return "net_mode"
    if name in {"greeksType"}:
        return "PA"
    if name in {"spotMarginMode", "marginType"}:
        return "REGULAR_MARGIN"
    if name in {"cancelReplaceMode"}:
        return "STOP_ON_FAILURE"
    if name in {"positionSide"}:
        return "LONG"
    if name in {"dualSidePosition"}:
        return "true"
    if name in {"status", "state"}:
        return "open"
    if name in {"timeframe"}:
        return "1m"
    if name in {"user", "wallet_address"}:
        return "0x0000000000000000000000000000000000000001"
    if name in {"request", "orders", "batchOrders"}:
        return [_sample_order(case.exchange)]
    if name in {"modifies"}:
        return [{"oid": 1, "order": {"a": 0, "b": True, "p": "100", "s": "1", "r": False}}]
    if name in {"orderId", "order_id", "ordId", "orderID", "clientOrderId", "clOrdID", "cloid"}:
        return "test-order-id"
    if name in {"oid", "twap_id", "positionId", "id", "page", "limit", "size", "qty", "quantity"}:
        return 1
    if name in {"orderQty", "leverage", "lever", "ntli", "minutes"}:
        return 1
    if name in {"amount", "notional", "price", "px", "sz", "funds"}:
        return "1"
    if name in {"from_", "to", "transId", "wdId"}:
        return "test-id"
    if name in {"chain", "addr", "dest", "fee", "toAddr"}:
        return "test"
    if name in {"amt"}:
        return "1"
    if name in {"startTime", "endTime", "start_time", "end_time", "begin", "end", "timestamp"}:
        return 1
    if name in {"interval", "bar", "binSize"}:
        return "1m"
    if name in {"filter"}:
        return {}
    if name in {"columns"}:
        return "symbol"
    return "test"


def _required_kwargs(case: EndpointCase, method: Any) -> dict[str, Any]:
    signature = inspect.signature(method)
    kwargs: dict[str, Any] = {}
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}:
            continue
        if parameter.default is inspect.Parameter.empty:
            kwargs[parameter.name] = _sample_value(case, parameter)
    return kwargs


def _case_kwargs(case: EndpointCase, method: Any) -> dict[str, Any]:
    kwargs = _required_kwargs(case, method)
    if case.exchange == "bitmex" and case.method_name == "amend_order":
        kwargs["orderID"] = "test-order-id"
    if case.exchange == "bitmart" and case.method_name == "post_withdraw_apply":
        kwargs["address"] = "test-address"
    return kwargs


def _sample_okx_orders() -> dict[str, list[dict[str, str]]]:
    return {
        "data": [
            {
                "instId": "BTC-USDT-SWAP",
                "ordId": "test-order-id",
                "clOrdId": "test-client-order-id",
            }
        ]
    }


def _sample_bitmart_positions() -> list[dict[str, int | str]]:
    return [
        {"position_type": 1, "current_amount": "1"},
        {"position_type": 2, "current_amount": "1"},
    ]


def _patch_sync_case(client: Any, case: EndpointCase) -> None:
    if case.exchange == "okx" and case.method_name == "cancel_all_orders":
        client.get_order_list = lambda *args, **kwargs: _sample_okx_orders()
    if case.exchange == "bitmart" and case.method_name in {
        "place_contract_post_only_buy_order",
        "place_contract_post_only_sell_order",
    }:
        client.get_contract_position = lambda *args, **kwargs: _sample_bitmart_positions()


def _patch_async_case(client: Any, case: EndpointCase) -> None:
    if case.exchange == "okx" and case.method_name == "cancel_all_orders":

        async def fake_get_order_list(
            *args: object, **kwargs: object
        ) -> dict[str, list[dict[str, str]]]:
            return _sample_okx_orders()

        client.get_order_list = fake_get_order_list

    if case.exchange == "bitmart" and case.method_name in {
        "place_contract_post_only_buy_order",
        "place_contract_post_only_sell_order",
    }:

        async def fake_get_contract_position(
            *args: object, **kwargs: object
        ) -> list[dict[str, int | str]]:
            return _sample_bitmart_positions()

        client.get_contract_position = fake_get_contract_position


def _patch_hyperliquid_market(monkeypatch: pytest.MonkeyPatch) -> None:
    sync_trade = import_module("dcex.hyperliquid._trade_http")
    async_trade = import_module("dcex.async_support.hyperliquid._trade_http")
    monkeypatch.setattr(sync_trade, "MarketHTTP", FakeSyncHyperliquidMarket)
    monkeypatch.setattr(async_trade, "MarketHTTP", FakeAsyncHyperliquidMarket)


@pytest.mark.parametrize("case", SYNC_CASES, ids=[case.id for case in SYNC_CASES])
def test_sync_endpoint_wrapper_is_reachable(
    case: EndpointCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class(case.mode, case.exchange)(**_client_kwargs(case.exchange))
    calls = _wire_sync(client)
    _patch_sync_case(client, case)

    method = getattr(client, case.method_name)
    result = method(**_case_kwargs(case, method))

    assert result is not None
    if case.method_name != "get_listen_key":
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


def test_sync_bitmart_withdraw_apply_payload_matches_docs() -> None:
    client = _client_class("sync", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_sync(client)

    result = client.post_withdraw_apply(
        currency="USDT",
        amount="1",
        address="test-address",
        address_memo="memo",
        destination="wallet",
    )

    assert result == {"ok": True}
    assert calls[0]["query"] == {
        "currency": "USDT",
        "amount": "1",
        "address": "test-address",
        "address_memo": "memo",
        "destination": "wallet",
    }


def test_sync_bitmart_withdraw_apply_requires_destination() -> None:
    client = _client_class("sync", "bitmart")(**_client_kwargs("bitmart"))
    _wire_sync(client)

    with pytest.raises(ValueError, match="Withdraw requires address"):
        client.post_withdraw_apply(currency="USDT", amount="1")


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
    assert calls[0]["query"]["timeInForce"] == "PostOnly"
    assert calls[0]["query"]["positionIdx"] == "1"


@pytest.mark.parametrize("case", ASYNC_CASES, ids=[case.id for case in ASYNC_CASES])
@pytest.mark.asyncio
async def test_async_endpoint_wrapper_is_reachable(
    case: EndpointCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class(case.mode, case.exchange)(**_client_kwargs(case.exchange))
    calls = _wire_async(client)
    _patch_async_case(client, case)

    method = getattr(client, case.method_name)
    result = await method(**_case_kwargs(case, method))

    assert result is not None
    if case.method_name not in {"get_listen_key"}:
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

    action = calls[0]["query"]["action"]
    assert result == {"ok": True}
    assert action["builder"] == {"b": builder_address, "f": 10}
    assert "feeTenBp" not in action


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
async def test_async_bitmart_withdraw_apply_payload_matches_docs() -> None:
    client = _client_class("async", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_async(client)

    result = await client.post_withdraw_apply(
        currency="USDT",
        amount="1",
        address="test-address",
        address_memo="memo",
        destination="wallet",
    )

    assert result == {"ok": True}
    assert calls[0]["query"] == {
        "currency": "USDT",
        "amount": "1",
        "address": "test-address",
        "address_memo": "memo",
        "destination": "wallet",
    }


@pytest.mark.asyncio
async def test_async_bitmart_withdraw_apply_requires_destination() -> None:
    client = _client_class("async", "bitmart")(**_client_kwargs("bitmart"))
    _wire_async(client)

    with pytest.raises(ValueError, match="Withdraw requires address"):
        await client.post_withdraw_apply(currency="USDT", amount="1")
