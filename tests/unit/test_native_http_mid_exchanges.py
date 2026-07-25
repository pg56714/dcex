# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server


def test_native_bingx_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "/test",
            [("symbol", "BTC USDT"), ("limit", "10"), ("type", "LIMIT")],
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(urlsplit(request["path"]).query)
    signed_pairs = pairs[:-1]
    signature = pairs[-1][1]
    payload = "&".join(f"{key}={value}" for key, value in signed_pairs)
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert request["bingx_api_key"] == "api-key"
    assert signed_pairs[0] == ("limit", "10")
    assert signed_pairs[1] == ("symbol", "BTC USDT")
    assert signed_pairs[2][0] == "timestamp"
    assert signed_pairs[3] == ("type", "LIMIT")
    assert pairs[-1][0] == "signature"
    assert signature == expected_signature


def test_native_bingx_listen_key_requires_api_key() -> None:
    native = pytest.importorskip("dcex._native")

    client = native.BingxHttpClient(timeout=2)
    with pytest.raises(ValueError, match="BingX API key is required for this request"):
        client.private_request_json("get_listen_key")


def test_sync_bingx_listen_key_uses_api_key_without_secret() -> None:
    from dcex.bingx.client import Client

    with _http_server({"code": 0, "listenKey": "listen-key"}) as (base_url, received):
        client = Client(
            api_key="api-key",
            base_url=base_url,
            preload_product_table=False,
        )
        result = client.get_listen_key()

    client.close()
    request = received.get_nowait()
    assert result == "listen-key"
    assert request["bingx_api_key"] == "api-key"


@pytest.mark.asyncio
async def test_async_bingx_listen_key_uses_api_key_without_secret() -> None:
    from dcex.async_support.bingx.client import Client

    with _http_server({"code": 0, "listenKey": "listen-key"}) as (base_url, received):
        client = Client(
            api_key="api-key",
            base_url=base_url,
            preload_product_table=False,
        )
        await client.async_init()
        result = await client.get_listen_key()

    await client.close()
    request = received.get_nowait()
    assert result == "listen-key"
    assert request["bingx_api_key"] == "api-key"


def test_sync_bingx_manager_uses_native_transport() -> None:
    from dcex.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


def test_sync_bingx_manager_sends_unsigned_json_body() -> None:
    from dcex.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "POST",
            "/test",
            {"symbol": "BTCUSDT", "limit": 1},
            signed=False,
        )

    manager.close()
    request = received.get_nowait()
    assert result == {"ok": True}
    assert request["path"] == "/test"
    assert request["body"] == '{"symbol":"BTCUSDT","limit":1}'


@pytest.mark.asyncio
async def test_async_bingx_manager_uses_native_transport() -> None:
    from dcex.async_support.bingx._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/test",
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_sync_bingx_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.bingx.client import Client

    with _http_server({"code": 0, "data": []}) as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        result = client.get_orderbook("BTC-USDT-SWAP", limit=5)

    client.close()
    assert result == {"code": 0, "data": []}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == ("/openApi/swap/v2/quote/depth?limit=5&symbol=BTC-USDT")


@pytest.mark.asyncio
async def test_async_bingx_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.async_support.bingx.client import Client

    with _http_server({"code": 0, "data": []}) as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        await client.async_init()
        result = await client.get_spot_orderbook_v2(
            "ETH-USDT-SPOT",
            limit=10,
            type_="step1",
        )

    await client.close()
    assert result == {"code": 0, "data": []}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (
        "/openApi/spot/v2/market/depth?depth=10&symbol=ETH_USDT&type=step1"
    )


def test_native_bingx_private_spot_order_uses_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0, "data": {"orderId": "1"}}) as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_spot_limit_buy_order",
            [
                ("product_symbol", "BTC-USDT-SPOT"),
                ("quantity", "0.001"),
                ("price", "100"),
            ],
        )

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    assert status == 200
    assert body == {"code": 0, "data": {"orderId": "1"}}
    assert urlsplit(request["path"]).path == "/openApi/spot/v1/trade/order"
    assert request["bingx_api_key"] == "api-key"
    assert query["symbol"] == "BTC-USDT"
    assert query["side"] == "BUY"
    assert query["type"] == "LIMIT"
    assert query["quantity"] == "0.001"
    assert query["price"] == "100"
    assert "timestamp" in query
    assert "signature" in query


def test_native_bingx_private_batch_order_normalizes_numbers() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0, "data": {"orders": []}}) as (base_url, received):
        client = native.BingxHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_swap_batch_order",
            [
                (
                    "batchOrders",
                    json.dumps(
                        [
                            {
                                "symbol": "BTC-USDT",
                                "side": "BUY",
                                "type": "LIMIT",
                                "quantity": "0.001",
                                "price": "100",
                            }
                        ],
                        separators=(",", ":"),
                    ),
                )
            ],
        )

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    orders = json.loads(query["batchOrders"])
    assert status == 200
    assert body == {"code": 0, "data": {"orders": []}}
    assert urlsplit(request["path"]).path == "/openApi/swap/v2/trade/batchOrders"
    assert orders[0]["quantity"] == 0.001
    assert orders[0]["price"] == 100
    assert "signature" in query


def test_native_mexc_spot_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "GET",
            "spot",
            "/test",
            [("symbol", "BTCUSDT")],
            None,
            True,
        )

    time_request = received.get_nowait()
    request = received.get_nowait()
    pairs = parse_qsl(urlsplit(request["path"]).query)
    payload = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert time_request["path"] == "/api/v3/time"
    assert request["X-MEXC-APIKEY"] == "api-key"
    assert pairs[-1] == ("signature", expected_signature)


def test_native_mexc_contract_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'[{"orderId":"1"},{"orderId":"2"}]'

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "contract",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    expected_signature = hmac.new(
        b"secret",
        f"api-key{request['Request-Time']}{request_body.decode()}".encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"ok": True}
    assert request["ApiKey"] == "api-key"
    assert request["Signature"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_mexc_manager_uses_native_transport() -> None:
    from dcex.mexc._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            contract_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


@pytest.mark.asyncio
async def test_async_mexc_manager_uses_native_contract_transport() -> None:
    from dcex.async_support.mexc._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            api_key="api-key",
            api_secret="secret",
            base_url=base_url,
            contract_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "POST",
            "/test",
            [{"orderId": "1"}, {"orderId": "2"}],
            signed=True,
            api="contract",
        )

    request = received.get_nowait()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '[{"orderId":"1"},{"orderId":"2"}]'


def test_native_mexc_public_dispatcher_normalizes_product_symbol() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.public_request_json(
            "get_contract_depth",
            [("product_symbol", "BTC-USDT-SWAP"), ("limit", "5")],
        )

    request = received.get_nowait()
    assert status == 200
    assert body == {"ok": True}
    assert request["path"] == "/api/v1/contract/depth/BTC_USDT?limit=5"


def test_native_mexc_private_spot_batch_order_converts_product_symbols() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_spot_batch_orders",
            [
                (
                    "batchOrders",
                    json.dumps(
                        [
                            {
                                "product_symbol": "BTC-USDT-SPOT",
                                "side": "BUY",
                                "type": "LIMIT_MAKER",
                                "quantity": "1",
                                "price": "1",
                            }
                        ],
                        separators=(",", ":"),
                    ),
                )
            ],
        )

    time_request = received.get_nowait()
    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    batch_orders = json.loads(query["batchOrders"])
    assert status == 200
    assert body == {"ok": True}
    assert time_request["path"] == "/api/v3/time"
    assert urlsplit(request["path"]).path == "/api/v3/batchOrders"
    assert batch_orders[0]["symbol"] == "BTCUSDT"
    assert "product_symbol" not in batch_orders[0]
    assert "signature" in query


def test_native_mexc_private_contract_order_builds_json_body() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.MexcHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
            contract_base_url=base_url,
        )
        status, _headers, body = client.private_request_json(
            "place_contract_order",
            [
                ("product_symbol", "BTC-USDT-SWAP"),
                ("side", "1"),
                ("type", "2"),
                ("openType", "2"),
                ("vol", "1"),
                ("price", "100"),
                ("leverage", "50"),
                ("reduceOnly", "false"),
            ],
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    assert status == 200
    assert body == {"ok": True}
    assert request["path"] == "/api/v1/private/order/create"
    assert payload["symbol"] == "BTC_USDT"
    assert payload["side"] == 1
    assert payload["type"] == 2
    assert payload["openType"] == 2
    assert payload["vol"] == 1
    assert payload["reduceOnly"] is False


def test_native_bitget_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]'

    with _http_server({"code": "00000"}) as (base_url, received):
        client = native.BitgetHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    payload = f"{request['ACCESS-TIMESTAMP']}POST/test{request_body.decode()}"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", payload.encode(), hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert body == {"code": "00000"}
    assert request["ACCESS-KEY"] == "api-key"
    assert request["ACCESS-PASSPHRASE"] == "passphrase"
    assert request["ACCESS-SIGN"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_bitget_manager_uses_native_transport() -> None:
    from dcex.bitget._http_manager import HTTPManager

    with _http_server({"code": "00000"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "00000"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


@pytest.mark.asyncio
async def test_async_bitget_manager_uses_native_transport() -> None:
    from dcex.async_support.bitget._http_manager import HTTPManager

    with _http_server({"code": "00000"}) as (base_url, received):
        manager = HTTPManager(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "POST",
            "/test",
            [{"symbol": "BTCUSDT", "qty": "1"}],
            signed=True,
        )

    request = received.get_nowait()
    assert result == {"code": "00000"}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '[{"symbol":"BTCUSDT","qty":"1"}]'


def test_native_bybit_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'{"symbol":"BTCUSDT","qty":"1"}'

    with _http_server({"retCode": 0}) as (base_url, received):
        client = native.BybitHttpClient(
            api_key="api-key",
            api_secret="secret",
            recv_window=5000,
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw_json(
            "POST",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    payload = (
        f"{request['X-BAPI-TIMESTAMP']}api-key"
        f"{request['X-BAPI-RECV-WINDOW']}{request_body.decode()}"
    )
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert body == {"retCode": 0}
    assert request["X-BAPI-API-KEY"] == "api-key"
    assert request["X-BAPI-SIGN"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_bybit_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.bybit._http_manager import HTTPManager

    with _http_server({"retCode": 0}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
            sync_server_time=False,
        )
        manager._native_client = native.BybitHttpClient(
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"retCode": 0}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=BTCUSDT"


@pytest.mark.asyncio
async def test_async_bybit_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.bybit._http_manager import HTTPManager

    with _http_server({"retCode": 0}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
            sync_server_time=False,
        )
        await manager.async_init()
        manager._native_client = native.BybitHttpClient(
            sync_server_time=False,
            timeout=2,
            base_url=base_url,
        )
        result = await manager._request(
            "GET",
            "/test",
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert result == {"retCode": 0}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"
