"""Offline coverage for exchange endpoint wrapper methods."""
# ruff: noqa: ANN401, D101, D102, D103

from __future__ import annotations

import ast
import asyncio
import base64
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
NO_REQUEST_METHODS = {"check_client", "create_auth_token", "get_listen_key"}


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
        if exchange == Common.BACKPACK or str(exchange) == Common.BACKPACK.value:
            return "BTC_USDC" if product_symbol and "SPOT" in product_symbol else "BTC_USDC_PERP"
        if exchange == Common.HYPERLIQUID or str(exchange) == Common.HYPERLIQUID.value:
            return '["BTC",0]'
        if exchange == Common.GATEIO or str(exchange) == Common.GATEIO.value:
            return "BTC_USDT"
        if exchange == Common.OKX or str(exchange) == Common.OKX.value:
            return product_symbol or "BTC-USDT-SWAP"
        if exchange == Common.BITMEX or str(exchange) == Common.BITMEX.value:
            return "XBTUSDT"
        if exchange == Common.KRAKEN or str(exchange) == Common.KRAKEN.value:
            return "XBTUSDT" if product_symbol and "SPOT" in product_symbol else "PF_XBTUSD"
        if exchange == Common.LIGHTER or str(exchange) == Common.LIGHTER.value:
            return "0"
        if exchange == Common.MEXC or str(exchange) == Common.MEXC.value:
            return "BTCUSDT" if product_symbol and "SPOT" in product_symbol else "BTC_USDT"
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


class FakeSyncResponse:
    status_code = 200
    headers: dict[str, str] = {}

    def json(self) -> dict[str, str]:
        return {"listenKey": "test-listen-key"}


class FakeSyncSession:
    def post(self, *args: object, **kwargs: object) -> FakeSyncResponse:
        return FakeSyncResponse()

    def close(self) -> None:
        return None


class FakeAsyncSession:
    is_closed = False

    async def post(self, *args: object, **kwargs: object) -> FakeAsyncResponse:
        return FakeAsyncResponse()


class FakeSyncNativePublicClient:
    def __init__(self, calls: list[dict[str, Any]]) -> None:
        self.calls = calls

    def public_request(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append({"method": "NATIVE_PUBLIC", "path": method_name, "query": params})
        return 200, {"x-response": "native"}, b'{"ok":true}'


class FakeAsyncNativePublicClient:
    def __init__(self, calls: list[dict[str, Any]]) -> None:
        self.calls = calls

    async def public_request_async(
        self,
        method_name: str,
        params: list[tuple[str, str]],
    ) -> tuple[int, dict[str, str], bytes]:
        self.calls.append({"method": "NATIVE_PUBLIC", "path": method_name, "query": params})
        return 200, {"x-response": "native"}, b'{"ok":true}'


class FakeSyncHyperliquidMarket:
    def __init__(self, *args: object, **kwargs: object) -> None:
        return None

    def get_meta_and_asset_ctxs(self) -> list[Any]:
        return [{}, [{"midPx": "100.0"}]]

    def close(self) -> None:
        return None


class FakeAsyncHyperliquidMarket:
    def __init__(self, *args: object, **kwargs: object) -> None:
        return None

    async def async_init(self) -> FakeAsyncHyperliquidMarket:
        return self

    async def get_meta_and_asset_ctxs(self) -> list[Any]:
        return [{}, [{"midPx": "100.0"}]]

    async def close(self) -> None:
        return None


class FakeLighterSigner:
    """Signer stand-in for Lighter endpoint wrapper tests."""

    def create_auth_token_with_expiry(self, **kwargs: object) -> tuple[str, None]:
        return "test-auth-token", None

    def check_client(self) -> None:
        return None

    def check_client_data(self, data: object) -> None:
        return None

    def sign_create_order(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 1, "{}", "test-tx-hash", None

    def sign_cancel_order(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 2, "{}", "test-tx-hash", None

    def sign_modify_order(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 3, "{}", "test-tx-hash", None

    def sign_cancel_all_orders(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 4, "{}", "test-tx-hash", None

    def sign_update_leverage(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 5, "{}", "test-tx-hash", None

    def sign_update_margin(self, **kwargs: object) -> tuple[int, str, str, None]:
        return 6, "{}", "test-tx-hash", None


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


def _endpoint_parameter_signatures(
    mode: str,
    exchange: str,
) -> dict[tuple[str, str, str], tuple[object, ...]]:
    base = ROOT / "dcex"
    if mode == "async":
        base /= "async_support"
    exchange_dir = base / exchange

    def source(node: ast.expr | None) -> str | None:
        return ast.unparse(node) if node is not None else None

    signatures: dict[tuple[str, str, str], tuple[object, ...]] = {}
    for path in sorted(exchange_dir.glob("*.py")):
        if not path.name.endswith(ENDPOINT_FILE_SUFFIXES):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for cls in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
            for node in cls.body:
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("_") or node.name in {"async_init", "close"}:
                    continue

                positional = node.args.posonlyargs + node.args.args
                defaults = [None] * (len(positional) - len(node.args.defaults))
                defaults.extend(node.args.defaults)
                positional_signature = tuple(
                    (argument.arg, source(argument.annotation), source(default))
                    for argument, default in zip(positional, defaults, strict=True)
                )
                keyword_signature = tuple(
                    (argument.arg, source(argument.annotation), source(default))
                    for argument, default in zip(
                        node.args.kwonlyargs,
                        node.args.kw_defaults,
                        strict=True,
                    )
                )
                signatures[(path.name, cls.name, node.name)] = (
                    positional_signature,
                    keyword_signature,
                    None
                    if node.args.vararg is None
                    else (node.args.vararg.arg, source(node.args.vararg.annotation)),
                    None
                    if node.args.kwarg is None
                    else (node.args.kwarg.arg, source(node.args.kwarg.annotation)),
                )
    return signatures


def _cases(mode: str, exchanges: tuple[str, ...]) -> list[EndpointCase]:
    return [
        EndpointCase(mode=mode, exchange=exchange, method_name=name)
        for exchange in exchanges
        for name in _endpoint_method_names(mode, exchange)
    ]


SYNC_CASES = _cases("sync", SYNC_EXCHANGES)
ASYNC_CASES = _cases("async", ASYNC_EXCHANGES)


@pytest.mark.parametrize("exchange", sorted(set(SYNC_EXCHANGES) & set(ASYNC_EXCHANGES)))
def test_sync_async_endpoint_parameter_signatures_match(exchange: str) -> None:
    assert _endpoint_parameter_signatures(
        "sync",
        exchange,
    ) == _endpoint_parameter_signatures("async", exchange)


def _client_class(mode: str, exchange: str) -> type:
    module_name = f"dcex.{exchange}.client"
    if mode == "async":
        module_name = f"dcex.async_support.{exchange}.client"
    return import_module(module_name).Client


def _client_kwargs(exchange: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"preload_product_table": False}
    if exchange == "aster":
        kwargs.update(
            user_address="0x0000000000000000000000000000000000000002",
            signer_address="0x0000000000000000000000000000000000000001",
            private_key="0x" + "1" * 64,
        )
    elif exchange == "backpack":
        kwargs.update(
            api_key=base64.b64encode(b"2" * 32).decode(),
            api_secret=base64.b64encode(b"1" * 32).decode(),
        )
    elif exchange in {"binance", "bingx", "bitmex", "bybit", "gateio", "mexc"}:
        kwargs.update(api_key="api-key", api_secret="api-secret")
    elif exchange == "bitmart":
        kwargs.update(api_key="api-key", api_secret="api-secret", memo="memo")
    elif exchange in {"bitget", "okx", "kucoin"}:
        kwargs.update(api_key="api-key", api_secret="api-secret", passphrase="passphrase")
    elif exchange == "kraken":
        kwargs.update(
            spot_api_key="api-key",
            spot_api_secret="api-secret",
            futures_api_key="api-key",
            futures_api_secret="api-secret",
        )
    elif exchange == "hyperliquid":
        kwargs.update(
            wallet_address="0x0000000000000000000000000000000000000001",
            private_key="0x" + "1" * 64,
        )
    elif exchange == "lighter":
        kwargs.update(account_index=1, api_key_index=2, api_private_key="1" * 64)
    return kwargs


def _wire_sync(client: Any) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    client.ptm = FakePTM()
    client.session = FakeSyncSession()

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
        if getattr(path, "name", "") in {"LISTEN_KEY", "USER_DATA_STREAM"} or "listenKey" in str(
            path
        ):
            return {"listenKey": "test-listen-key"}
        if "nextNonce" in str(path):
            return {"nonce": 1}
        return {"ok": True}

    client._request = fake_request
    if hasattr(client, "_native_public"):
        client._native_client = FakeSyncNativePublicClient(calls)
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
        if getattr(path, "name", "") in {"LISTEN_KEY", "USER_DATA_STREAM"} or "listenKey" in str(
            path
        ):
            return {"listenKey": "test-listen-key"}
        if "nextNonce" in str(path):
            return {"nonce": 1}
        return {"ok": True}

    client._request = fake_request
    if hasattr(client, "_native_public"):
        client._native_client = FakeAsyncNativePublicClient(calls)
    return calls


def _product_symbol(exchange: str, method_name: str) -> str:
    if exchange == "bitmex":
        return "XBT-USDT-SWAP"
    if exchange == "hyperliquid":
        return "BTC-USD-SWAP"
    if exchange == "kraken":
        return "BTC-USDT-SPOT" if "spot" in method_name else "BTC-USD-SWAP"
    if exchange == "backpack":
        return "BTC-USDC-SPOT" if "spot" in method_name else "BTC-USDC-SWAP"
    if "spot" in method_name:
        return "BTC-USDT-SPOT"
    return "BTC-USDT-SWAP"


def _sample_order(exchange: str) -> dict[str, Any]:
    if exchange == "aster":
        return {
            "product_symbol": "BTC-USDT-SWAP",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "1",
            "price": "1",
        }
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
    if exchange == "bitget":
        return {
            "symbol": "BTCUSDT",
            "side": "buy",
            "orderType": "limit",
            "force": "gtc",
            "size": "1",
            "price": "1",
        }
    if exchange == "mexc":
        return {
            "product_symbol": "BTC-USDT-SPOT",
            "side": "BUY",
            "type": "LIMIT",
            "quantity": "1",
            "price": "1",
        }
    if exchange == "backpack":
        return {
            "product_symbol": "BTC-USDC-SPOT",
            "side": "Bid",
            "orderType": "Limit",
            "quantity": "1",
            "price": "1",
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
        if case.exchange == "aster":
            return "BUY"
        if case.exchange == "backpack":
            return "Bid"
        if case.exchange == "bitmart" and "contract" in method_name:
            return 1
        if case.exchange == "mexc" and "contract" in method_name:
            return 1
        if case.exchange in {"bybit", "bitmex"}:
            return "Buy"
        return "buy"
    if name in {"isBuy", "reduceOnly", "isCross", "randomize", "dual_mode"}:
        return True
    if name in {"is_ask", "reduce_only"}:
        return False
    if name in {"mxDeductEnable"}:
        return True
    if name in {"type", "type_"}:
        if case.exchange == "mexc" and "contract" in method_name:
            return 1
        return "limit"
    if name in {"orderType"}:
        if case.exchange == "bitget":
            return "limit"
        return "Limit"
    if name in {"tdMode", "mgnMode"}:
        return "cross"
    if name in {"ordType"}:
        return "limit"
    if name in {"ordertype"}:
        return "limit"
    if name in {"productType"}:
        return "USDT-FUTURES"
    if name in {"category"}:
        return "linear"
    if name in {"instType"}:
        return "SPOT"
    if name in {"ccy", "currency", "coin", "quoteCoin", "baseCoin", "asset", "unit"}:
        return "USDT"
    if name in {"settleCoin"}:
        return "USDT"
    if name in {"marginCoin"}:
        return "USDT"
    if name in {"marginMode"}:
        return "crossed"
    if name in {"holdSide"}:
        return "long"
    if name in {"force"}:
        return "gtc"
    if name in {"assetType"}:
        return "all"
    if name in {"symbol"}:
        if case.exchange == "backpack":
            return "USDC" if "borrow" in method_name or "withdrawal" in method_name else "BTC_USDC"
        return "XBT-USDT-SWAP" if case.exchange == "bitmex" else "BTCUSDT"
    if name in {"blockchain"}:
        return "Solana"
    if name in {"country"}:
        return "US"
    if name in {"marketType"}:
        return "SPOT"
    if name in {"sortDirection"}:
        return "Desc"
    if name in {"source"}:
        return "TradingFees"
    if name in {"borrow"}:
        return "eyJzeW1ib2wiOiJVU0RDIiwicXVhbnRpdHkiOiIxIiwic2lkZSI6IkJvcnJvdyJ9"
    if name in {"orders"} and case.exchange == "backpack":
        return [_sample_order(case.exchange)]
    if name in {"contract"}:
        return "BTC_USDT"
    if name in {"path"}:
        return "futures"
    if name in {"tif", "timeInForce"}:
        return "GTC"
    if name in {"posMode"}:
        return "net_mode"
    if name in {"positionMode"}:
        return 1
    if name in {"greeksType"}:
        return "PA"
    if name in {"spotMarginMode", "marginType"}:
        return "REGULAR_MARGIN"
    if name in {"cancelReplaceMode"}:
        return "STOP_ON_FAILURE"
    if name in {"positionSide"}:
        return "LONG"
    if name in {"positionType", "openType"}:
        return 1
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
    if name in {"subOrderList"}:
        if case.exchange == "aster":
            return [
                {
                    "strategySubId": "1",
                    "securityType": "USDT_FUTURES",
                    "symbol": "BTCUSDT",
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": "1",
                    "price": "1",
                    "timeInForce": "GTC",
                },
                {
                    "strategySubId": "2",
                    "securityType": "USDT_FUTURES",
                    "symbol": "BTCUSDT",
                    "side": "SELL",
                    "type": "LIMIT",
                    "quantity": "1",
                    "price": "2",
                    "timeInForce": "GTC",
                },
            ]
        return [_sample_order(case.exchange)]
    if name in {"modifies"}:
        return [{"oid": 1, "order": {"a": 0, "b": True, "p": "100", "s": "1", "r": False}}]
    if name in {
        "orderId",
        "order_id",
        "ordId",
        "orderID",
        "clientOrderId",
        "clientOid",
        "clOrdID",
        "cloid",
        "txid",
    }:
        return "test-order-id"
    if name in {
        "oid",
        "twap_id",
        "positionId",
        "id",
        "page",
        "limit",
        "size",
        "qty",
        "quantity",
        "vol",
        "market_index",
        "client_order_index",
        "countdownTime",
        "frozenTimeInMilliseconds",
        "windowTimeInMilliseconds",
        "base_amount",
        "price",
        "order_index",
        "order_type",
        "time_in_force",
        "timestamp_ms",
        "fraction",
        "margin_mode",
        "direction",
        "tx_type",
    }:
        return 1
    if name in {"orderQty", "leverage", "lever", "ntli", "minutes"}:
        return 1
    if name in {"amount", "notional", "price", "px", "sz", "funds", "volume"}:
        return "1"
    if name in {"tx_info", "tx_infos", "tx_types"}:
        return "{}"
    if name in {"fromAccount", "toAccount"}:
        return "cash"
    if name in {"fromType"}:
        return "spot"
    if name in {"toType"}:
        return "usdt_futures"
    if name in {"orderIds", "cliOrdIds"}:
        return ["test-order-id"]
    if name in {"order_ids"}:
        return ["test-order-id"]
    if name in {"orderList", "orderIdList"}:
        return [{"orderId": "test-order-id"}]
    if name in {"from_", "to", "transId", "wdId"}:
        return "test-id"
    if name in {"fromAccountType", "toAccountType"}:
        return "SPOT"
    if name in {"kindType"}:
        return "FUTURE_SPOT"
    if name in {"stpMode"}:
        return "EXPIRE_TAKER"
    if name in {"multiAssetsMargin"}:
        return True
    if name in {"quantityUnit"}:
        return "BASE"
    if name in {"chaseOffset", "maxChaseOffset"}:
        return "1"
    if name in {"chaseOffsetType", "maxChaseOffsetType"}:
        return "ABSOLUTE"
    if name in {"strategyType"}:
        return "OTO"
    if name in {"strategyId", "clientStrategyId"}:
        return "test-strategy-id"
    if name in {"listenKey"}:
        return "test-listen-key"
    if name in {"pair"}:
        return "BTCUSDT"
    if name in {"external_oid", "externalOid"}:
        return "test-external-id"
    if name in {"chain", "addr", "dest", "fee", "toAddr"}:
        return "test"
    if name in {"amt"}:
        return "1"
    if name in {"startTime", "endTime", "start_time", "end_time", "begin", "end", "timestamp"}:
        return 1
    if name in {"interval", "bar", "binSize"}:
        return "1m"
    if name in {"contractType"}:
        return "flexible_futures"
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
    if case.exchange == "aster" and case.method_name in {
        "cancel_futures_order",
        "cancel_spot_order",
        "get_futures_open_order",
        "get_futures_order",
        "get_spot_open_order",
        "get_spot_order",
        "modify_futures_order",
    }:
        kwargs["orderId"] = 1
    if case.exchange == "bitmex" and case.method_name == "amend_order":
        kwargs["orderID"] = "test-order-id"
    if case.exchange == "binance" and case.method_name in {
        "cancel_futures_algo_order",
        "get_futures_algo_order",
    }:
        kwargs["algoId"] = 1
    if case.exchange == "okx" and case.method_name == "get_deposit_withdraw_status":
        kwargs.update(
            txId="test-transaction-id",
            ccy="USDT",
            to="test-address",
            chain="USDT-ERC20",
        )
    if case.exchange == "kraken" and case.method_name == "cancel_spot_order":
        kwargs["txid"] = "test-order-id"
    if case.exchange == "kraken" and case.method_name == "cancel_futures_order":
        kwargs["order_id"] = "test-order-id"
    if case.exchange == "bitget" and case.method_name in {
        "cancel_spot_order",
        "get_spot_order",
        "cancel_futures_order",
        "get_futures_order",
        "cancel_uta_order",
        "get_uta_order",
    }:
        kwargs["orderId"] = "test-order-id"
    if case.exchange == "backpack" and case.method_name in {"cancel_order", "get_open_order"}:
        kwargs["orderId"] = "test-order-id"
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


def _patch_lighter_signer(client: Any) -> None:
    if client.__class__.__module__.endswith(".lighter.client"):
        client._signer = FakeLighterSigner()


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
    assert calls[0]["query"]["timeInForce"] == "PostOnly"
    assert calls[0]["query"]["positionIdx"] == "1"


def test_sync_bitmart_modify_limit_order_uses_documented_payload_types() -> None:
    client = _client_class("sync", "bitmart")(**_client_kwargs("bitmart"))
    calls = _wire_sync(client)

    result = client.modify_limit_order(
        product_symbol="BTC-USDT-SWAP",
        order_id="123456",
        price="100.1",
        size=1,
    )

    query = calls[0]["query"]
    assert result == {"ok": True}
    assert query["order_id"] == 123456
    assert query["price"] == "100.1"
    assert query["size"] == 1


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


@pytest.mark.parametrize("case", ASYNC_CASES, ids=[case.id for case in ASYNC_CASES])
@pytest.mark.asyncio
async def test_async_endpoint_wrapper_is_reachable(
    case: EndpointCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class(case.mode, case.exchange)(**_client_kwargs(case.exchange))
    _patch_lighter_signer(client)
    calls = _wire_async(client)
    _patch_async_case(client, case)

    method = getattr(client, case.method_name)
    result = await method(**_case_kwargs(case, method))

    if case.method_name != "check_client":
        assert result is not None
    if case.method_name not in NO_REQUEST_METHODS:
        assert calls


@pytest.mark.asyncio
async def test_async_gateio_batch_order_uses_list_body() -> None:
    client = _client_class("async", "gateio")(**_client_kwargs("gateio"))
    calls = _wire_async(client)

    result = await client.place_futures_batch_order(
        [{"product_symbol": "BTC-USDT-SWAP", "size": 1, "price": "100"}]
    )

    assert result == {"ok": True}
    assert isinstance(calls[0]["body"], list)
    assert calls[0]["body"][0]["contract"] == "BTC_USDT"
    assert "orders" not in calls[0]["body"]


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
async def test_async_hyperliquid_market_order_uses_ioc_limit_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_hyperliquid_market(monkeypatch)
    client = _client_class("async", "hyperliquid")(**_client_kwargs("hyperliquid"))
    calls = _wire_async(client)

    await client.place_future_market_buy_order(product_symbol="BTC-USD-SWAP", size="1")

    order = calls[0]["query"]["action"]["orders"][0]
    assert order["p"] == "103"
    assert order["t"] == {"limit": {"tif": "Ioc"}}


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

    query = calls[0]["query"]
    assert result == {"ok": True}
    assert query["order_id"] == 123456
    assert query["price"] == "100.1"
    assert query["size"] == 1


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
    assert calls[0]["query"]["side"] == 2


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
