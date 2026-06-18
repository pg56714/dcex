# ruff: noqa: D100, D103, F401

import base64
import hashlib
import hmac
import json
from urllib.parse import parse_qsl, urlsplit

import msgspec
import pytest
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa

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
        status, _headers, body = client.request_raw(
            "GET",
            "/test",
            [("symbol", "BTC USDT"), ("limit", "10")],
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
    assert json.loads(body) == {"ok": True}
    assert request["bingx_api_key"] == "api-key"
    assert signed_pairs[0] == ("limit", "10")
    assert signed_pairs[1] == ("symbol", "BTC USDT")
    assert signed_pairs[2][0] == "timestamp"
    assert pairs[-1][0] == "signature"
    assert signature == expected_signature


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

    assert manager.session is not None
    await manager.session.aclose()
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
        "/openApi/spot/v2/market/depth?depth=10&symbol=ETH-USDT&type=step1"
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
        status, _headers, body = client.private_request(
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
    assert json.loads(body) == {"code": 0, "data": {"orderId": "1"}}
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
        status, _headers, body = client.private_request(
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
    assert json.loads(body) == {"code": 0, "data": {"orders": []}}
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
        status, _headers, body = client.request_raw(
            "GET",
            "spot",
            "/test",
            [("symbol", "BTCUSDT")],
            None,
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(urlsplit(request["path"]).query)
    payload = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"ok": True}
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
        status, _headers, body = client.request_raw(
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
    assert json.loads(body) == {"ok": True}
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

    assert manager.session is not None
    await manager.session.aclose()
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
        status, _headers, body = client.public_request(
            "get_contract_depth",
            [("product_symbol", "BTC-USDT-SWAP"), ("limit", "5")],
        )

    request = received.get_nowait()
    assert status == 200
    assert json.loads(body) == {"ok": True}
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
        status, _headers, body = client.private_request(
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

    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    batch_orders = json.loads(query["batchOrders"])
    assert status == 200
    assert json.loads(body) == {"ok": True}
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
        status, _headers, body = client.private_request(
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
    assert json.loads(body) == {"ok": True}
    assert request["path"] == "/api/v1/private/order/create"
    assert payload["symbol"] == "BTC_USDT"
    assert payload["side"] == 1
    assert payload["type"] == 2
    assert payload["openType"] == 2
    assert payload["vol"] == 1
    assert payload["reduceOnly"] is False


def test_native_bitmex_signed_get() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BitmexHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "/test",
            [("symbol", "XBT USD")],
            None,
            True,
        )

    request = received.get_nowait()
    payload = f"GET{request['path']}{request['api-expires']}"
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["bitmex_api_key"] == "api-key"
    assert request["api-signature"] == expected_signature
    assert request["path"] == "/test?symbol=XBT+USD"


def test_sync_bitmex_manager_uses_native_transport() -> None:
    from dcex.bitmex._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            {"symbol": "XBTUSD"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=XBTUSD"


@pytest.mark.asyncio
async def test_async_bitmex_manager_uses_native_signed_body() -> None:
    from dcex.async_support.bitmex._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            api_key="api-key",
            api_secret="secret",
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "POST",
            "/test",
            {"symbol": "XBTUSD", "orderQty": 1},
            signed=True,
        )

    assert manager.session is not None
    await manager.session.aclose()
    request = received.get_nowait()
    payload = f"POST/test{request['api-expires']}{request['body']}"
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '{"symbol":"XBTUSD","orderQty":1}'
    assert request["api-signature"] == expected_signature


def test_sync_bitmex_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.bitmex.client import Client

    with _http_server() as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        result = client.get_orderbook("XBT-USD-SWAP", depth=25)

    client.close()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/orderBook/L2?symbol=XBTUSD&depth=25"


def test_native_bitmex_private_limit_order_builds_json_body() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BitmexHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.private_request(
            "place_limit_buy_order",
            [
                ("product_symbol", "XBT-USD-SWAP"),
                ("orderQty", "100"),
                ("price", "1.5"),
            ],
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["path"] == "/api/v2/order"
    assert payload == {
        "ordType": "Limit",
        "orderQty": 100,
        "price": 1.5,
        "side": "Buy",
        "symbol": "XBTUSD",
        "timeInForce": "GoodTillCancel",
    }


@pytest.mark.asyncio
async def test_async_bitmex_public_wrapper_uses_native_dispatcher() -> None:
    from dcex.async_support.bitmex.client import Client

    with _http_server() as (base_url, received):
        client = Client(base_url=base_url, preload_product_table=False)
        await client.async_init()
        result = await client.get_liquidations(
            product_symbol="ETH-USDT-SWAP",
            filter={"side": "Sell"},
            count=1,
        )

    await client.close()
    request = received.get_nowait()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert urlsplit(request["path"]).path == "/api/v1/liquidation"
    assert parse_qsl(urlsplit(request["path"]).query) == [
        ("symbol", "ETHUSDT"),
        ("filter", '{"side":"Sell"}'),
        ("count", "1"),
    ]


def test_native_bitmart_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'{"symbol":"BTC_USDT","side":"buy"}'

    with _http_server({"code": 1000}) as (base_url, received):
        client = native.BitmartHttpClient(
            api_key="api-key",
            api_secret="secret",
            memo="memo",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "spot",
            "/test",
            [],
            request_body,
            True,
        )

    request = received.get_nowait()
    payload = f"{request['X-BM-TIMESTAMP']}#memo#{request_body.decode()}"
    expected_signature = hmac.new(
        b"secret",
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"code": 1000}
    assert request["X-BM-KEY"] == "api-key"
    assert request["X-BM-MEMO"] == "memo"
    assert request["X-BM-SIGN"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_bitmart_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.bitmart._http_manager import HTTPManager
    from dcex.bitmart.endpoints.market import SpotMarket

    with _http_server({"code": 1000}) as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        manager._native_client = native.BitmartHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = manager._request(
            "GET",
            SpotMarket.GET_TICKER_OF_A_PAIR,
            {"symbol": "BTC_USDT"},
            signed=False,
        )

    manager.close()
    assert result == {"code": 1000}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (f"{SpotMarket.GET_TICKER_OF_A_PAIR}?symbol=BTC_USDT")


@pytest.mark.asyncio
async def test_async_bitmart_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.bitmart._http_manager import HTTPManager
    from dcex.async_support.bitmart.endpoints.trade import SpotTrade

    with _http_server({"code": 1000}) as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        await manager.async_init()
        manager._native_client = native.BitmartHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await manager._request(
            "POST",
            SpotTrade.SUBMIT_ORDER,
            {"symbol": "BTC_USDT", "side": "buy"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    request = received.get_nowait()
    assert result == {"code": 1000}
    assert manager.last_response_headers["x-response"] == "native"
    assert request["body"] == '{"symbol":"BTC_USDT","side":"buy"}'


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
        status, _headers, body = client.request_raw(
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
    assert json.loads(body) == {"code": "00000"}
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

    assert manager.session is not None
    await manager.session.aclose()
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
        status, _headers, body = client.request_raw(
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
    assert json.loads(body) == {"retCode": 0}
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

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"retCode": 0}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_native_gateio_signed_body() -> None:
    native = pytest.importorskip("dcex._native")
    request_body = b'{"size":1}'

    with _http_server() as (base_url, received):
        client = native.GateioHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "/api/v4/test",
            [("settle", "usdt")],
            request_body,
            True,
        )

    request = received.get_nowait()
    canonical = (
        "POST\n/api/v4/test\nsettle=usdt\n"
        f"{hashlib.sha512(request_body).hexdigest()}\n{request['gateio_timestamp']}"
    )
    expected_signature = hmac.new(
        b"secret",
        canonical.encode(),
        hashlib.sha512,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["gateio_key"] == "api-key"
    assert request["gateio_sign"] == expected_signature
    assert request["body"] == request_body.decode()


def test_sync_gateio_manager_uses_native_transport() -> None:
    from dcex.gateio._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/test",
            query={"settle": "usdt"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v4/test?settle=usdt"


@pytest.mark.asyncio
async def test_async_gateio_manager_uses_native_transport() -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    with _http_server() as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/test",
            query={"settle": "usdt"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v4/test?settle=usdt"
