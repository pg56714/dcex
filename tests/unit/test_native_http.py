# ruff: noqa: D100, D103

import base64
import hashlib
import hmac
import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qsl, urlsplit

import msgspec
import pytest
from Crypto.PublicKey import ECC
from Crypto.Signature import eddsa


@contextmanager
def _http_server(
    response_payload: dict[str, Any] | None = None,
) -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    response_payload = response_payload or {"ok": True}

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            request = {
                "path": self.path,
                "header": self.headers.get("X-Test"),
                "api_key": self.headers.get("X-MBX-APIKEY"),
            }
            if bingx_api_key := self.headers.get("X-BX-APIKEY"):
                request["bingx_api_key"] = bingx_api_key
            for header in (
                "X-MEXC-APIKEY",
                "ApiKey",
                "Request-Time",
                "Signature",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            if value := self.headers.get("api-key"):
                request["bitmex_api_key"] = value
            for header in ("api-signature", "api-expires"):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("X-BM-KEY", "X-BM-SIGN", "X-BM-TIMESTAMP", "X-BM-MEMO"):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "ACCESS-KEY",
                "ACCESS-SIGN",
                "ACCESS-TIMESTAMP",
                "ACCESS-PASSPHRASE",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "X-BAPI-API-KEY",
                "X-BAPI-SIGN",
                "X-BAPI-TIMESTAMP",
                "X-BAPI-RECV-WINDOW",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("KEY", "Timestamp", "SIGN"):
                if value := self.headers.get(header):
                    request[f"gateio_{header.lower()}"] = value
            for header in (
                "OK-ACCESS-KEY",
                "OK-ACCESS-SIGN",
                "OK-ACCESS-TIMESTAMP",
                "OK-ACCESS-PASSPHRASE",
                "x-simulated-trading",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "KC-API-KEY",
                "KC-API-SIGN",
                "KC-API-TIMESTAMP",
                "KC-API-PASSPHRASE",
                "KC-API-KEY-VERSION",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("API-Key", "API-Sign", "APIKey", "Authent", "Nonce"):
                if value := self.headers.get(header):
                    request[f"kraken_{header.lower()}"] = value
            for header in ("X-API-Key", "X-Signature", "X-Timestamp", "X-Window"):
                if value := self.headers.get(header):
                    request[f"backpack_{header.lower()}"] = value
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length:
                request["body"] = self.rfile.read(content_length).decode()
            received.put(request)
            body = json.dumps(response_payload, separators=(",", ":")).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Response", "native")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_DELETE(self) -> None:  # noqa: N802
            self._handle()

        def do_GET(self) -> None:  # noqa: N802
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def do_PUT(self) -> None:  # noqa: N802
            self._handle()

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_native_sync_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = client.request(
            "GET",
            base_url,
            "/test",
            [("symbol", "BTCUSDT")],
            {"X-Test": "sync"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "path": "/test?symbol=BTCUSDT",
        "header": "sync",
        "api_key": None,
    }


@pytest.mark.asyncio
async def test_native_async_http_client() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.HttpClient(timeout=2)
        status, headers, body = await client.request_async(
            "GET",
            base_url,
            "/test",
            [("symbol", "ETHUSDT")],
            {"X-Test": "async"},
        )

    assert status == 200
    assert headers["x-response"] == "native"
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait() == {
        "path": "/test?symbol=ETHUSDT",
        "header": "async",
        "api_key": None,
    }


def test_native_binance_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request(
            "GET",
            "spot",
            "/test",
            [("symbol", "BTCUSDT")],
            True,
        )

    request = received.get_nowait()
    signed_query, signature = request["path"].split("?", 1)[1].rsplit("&signature=", 1)
    expected_signature = hmac.new(
        b"secret",
        signed_query.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["api_key"] == "api-key"
    assert "timestamp=" in signed_query
    assert "recvWindow=5000" in signed_query
    assert signature == expected_signature


@pytest.mark.asyncio
async def test_native_binance_async_public_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server() as (base_url, received):
        client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = await client.request_async(
            "GET",
            "futures",
            "/test",
            [("symbol", "ETHUSDT")],
            False,
        )

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert received.get_nowait()["path"] == "/test?symbol=ETHUSDT"


def test_sync_binance_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance._http_manager import HTTPManager
    from dcex.binance.endpoints.market import SpotMarket

    with _http_server() as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        manager._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = manager._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": "BTCUSDT"},
            signed=False,
        )

    manager.close()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (f"{SpotMarket.EXCHANGE_INFO}?symbol=BTCUSDT")


@pytest.mark.asyncio
async def test_async_binance_manager_uses_native_transport() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance._http_manager import HTTPManager
    from dcex.async_support.binance.endpoints.market import SpotMarket

    with _http_server() as (base_url, received):
        manager = HTTPManager(preload_product_table=False)
        await manager.async_init()
        manager._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await manager._request(
            "GET",
            SpotMarket.EXCHANGE_INFO,
            {"symbol": "ETHUSDT"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"ok": True}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == (f"{SpotMarket.EXCHANGE_INFO}?symbol=ETHUSDT")


def test_sync_binance_public_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(preload_product_table=False)
        client._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = client.get_spot_orderbook("BTC-USDT-SPOT", limit=5)

    client.close()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v3/depth?symbol=BTCUSDT&limit=5"


@pytest.mark.asyncio
async def test_async_binance_public_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(preload_product_table=False)
        await client.async_init()
        client._native_client = native.BinanceHttpClient(
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await client.get_klines("BTC-USDT-SWAP", interval="1m", limit=2)

    await client.close()
    assert result == {"ok": True}
    assert client.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/fapi/v1/klines?symbol=BTCUSDT&interval=1m&limit=2"


def test_sync_binance_private_trade_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = client.place_limit_buy_order(
            product_symbol="BTC-USDT-SPOT",
            quantity="1",
            price="100",
        )

    client.close()
    request = received.get_nowait()
    body = dict(parse_qsl(request["body"]))
    assert result == {"ok": True}
    assert request["path"] == "/api/v3/order"
    assert request["api_key"] == "api-key"
    assert body["symbol"] == "BTCUSDT"
    assert body["side"] == "BUY"
    assert body["type"] == "LIMIT"
    assert body["timeInForce"] == "GTC"
    assert "signature" in body


def test_binance_native_dispatcher_uses_product_table_symbols() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        client._native_client.set_product_table(
            native.ProductTable(
                [
                    {
                        "exchange": "binance",
                        "exchange_symbol": "BTCUSDT_250627",
                        "product_symbol": "BTC-USDT-250627",
                        "product_type": "futures",
                        "exchange_type": "delivery",
                        "price_precision": "0.1",
                        "size_precision": "0.001",
                        "min_size": "0.001",
                        "base_currency": "BTC",
                        "quote_currency": "USDT",
                        "min_notional": "0",
                        "size_per_contract": "1",
                    }
                ]
            )
        )
        result = client.place_limit_buy_order(
            product_symbol="BTC-USDT-250627",
            quantity="1",
            price="100",
        )

    client.close()
    request = received.get_nowait()
    body = dict(parse_qsl(request["body"]))
    assert result == {"ok": True}
    assert request["path"] == "/fapi/v1/order"
    assert body["symbol"] == "BTCUSDT_250627"
    assert body["side"] == "BUY"


@pytest.mark.asyncio
async def test_async_binance_private_account_wrapper_uses_native_dispatcher() -> None:
    native = pytest.importorskip("dcex._native")
    from dcex.async_support.binance.client import Client

    with _http_server() as (base_url, received):
        client = Client(
            api_key="api-key",
            api_secret="secret",
            preload_product_table=False,
        )
        await client.async_init()
        client._native_client = native.BinanceHttpClient(
            api_key="api-key",
            api_secret="secret",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        result = await client.get_account_balance(market_type="swap")

    await client.close()
    request = received.get_nowait()
    query = dict(parse_qsl(urlsplit(request["path"]).query))
    assert result == {"ok": True}
    assert urlsplit(request["path"]).path == "/fapi/v3/balance"
    assert request["api_key"] == "api-key"
    assert "signature" in query


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


def test_native_okx_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        client = native.OkxHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            flag="1",
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "/api/v5/account/balance",
            [("ccy", "BTC")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["OK-ACCESS-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v5/account/balance?ccy=BTC"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"code": "0", "data": []}
    assert request["OK-ACCESS-KEY"] == "api-key"
    assert request["OK-ACCESS-PASSPHRASE"] == "passphrase"
    assert request["OK-ACCESS-SIGN"] == expected_signature
    assert request["x-simulated-trading"] == "1"


def test_sync_okx_manager_uses_native_transport() -> None:
    from dcex.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"


@pytest.mark.asyncio
async def test_async_okx_manager_uses_native_transport() -> None:
    from dcex.async_support.okx._http_manager import HTTPManager

    with _http_server({"code": "0", "data": []}) as (base_url, received):
        manager = HTTPManager(
            base_api=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v5/public/time",
            {"source": "native"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"code": "0", "data": []}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v5/public/time?source=native"


def test_native_kucoin_signed_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": "200000", "data": {}}) as (base_url, received):
        client = native.KucoinHttpClient(
            api_key="api-key",
            api_secret="secret",
            passphrase="passphrase",
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "spot",
            "/api/v1/accounts",
            [("currency", "BTC USDT"), ("type", "trade")],
            None,
            True,
        )

    request = received.get_nowait()
    timestamp = request["KC-API-TIMESTAMP"]
    canonical = f"{timestamp}GET/api/v1/accounts?currency=BTC+USDT&type=trade"
    expected_signature = base64.b64encode(
        hmac.new(b"secret", canonical.encode(), hashlib.sha256).digest()
    ).decode()
    expected_passphrase = base64.b64encode(
        hmac.new(b"secret", b"passphrase", hashlib.sha256).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"code": "200000", "data": {}}
    assert request["KC-API-KEY"] == "api-key"
    assert request["KC-API-SIGN"] == expected_signature
    assert request["KC-API-PASSPHRASE"] == expected_passphrase
    assert request["KC-API-KEY-VERSION"] == "2"


def test_sync_kucoin_manager_uses_native_transport() -> None:
    from dcex.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    manager.close()
    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"


@pytest.mark.asyncio
async def test_async_kucoin_manager_uses_native_transport() -> None:
    from dcex.async_support.kucoin._http_manager import HTTPManager

    with _http_server({"code": "200000", "data": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/timestamp",
            {"source": "native"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"code": "200000", "data": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/timestamp?source=native"


def test_native_kraken_spot_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"error": [], "result": {}}) as (base_url, received):
        client = native.KrakenHttpClient(
            spot_api_key="api-key",
            spot_api_secret=api_secret,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "spot",
            "/0/private/Balance",
            [("asset", "BTC USD")],
            None,
            True,
        )

    request = received.get_nowait()
    encoded_body = request["body"]
    nonce = dict(parse_qsl(encoded_body))["nonce"]
    digest = hashlib.sha256((nonce + encoded_body).encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", b"/0/private/Balance" + digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"error": [], "result": {}}
    assert request["kraken_api-key"] == "api-key"
    assert request["kraken_api-sign"] == expected_signature
    assert request["path"] == "/0/private/Balance"


def test_native_kraken_futures_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_secret = base64.b64encode(b"secret").decode()

    with _http_server({"result": "success"}) as (base_url, received):
        client = native.KrakenHttpClient(
            futures_api_key="api-key",
            futures_api_secret=api_secret,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "futures",
            "/derivatives/api/v3/sendorder",
            [("symbol", "PI_XBTUSD"), ("side", "buy")],
            None,
            True,
        )

    request = received.get_nowait()
    post_data = request["body"]
    nonce = request["kraken_nonce"]
    digest = hashlib.sha256((post_data + nonce + "/api/v3/sendorder").encode()).digest()
    expected_signature = base64.b64encode(
        hmac.new(b"secret", digest, hashlib.sha512).digest()
    ).decode()

    assert status == 200
    assert json.loads(body) == {"result": "success"}
    assert request["kraken_apikey"] == "api-key"
    assert request["kraken_authent"] == expected_signature


def test_sync_kraken_manager_uses_native_transport() -> None:
    from dcex.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    manager.close()
    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"


@pytest.mark.asyncio
async def test_async_kraken_manager_uses_native_transport() -> None:
    from dcex.async_support.kraken._http_manager import HTTPManager

    with _http_server({"error": [], "result": {"unixtime": 1}}) as (
        base_url,
        received,
    ):
        manager = HTTPManager(
            base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/0/public/Time",
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"error": [], "result": {"unixtime": 1}}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/0/public/Time"


def test_native_backpack_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    api_key = base64.b64encode(b"2" * 32).decode()
    api_secret = base64.b64encode(b"1" * 32).decode()

    with _http_server({}) as (base_url, received):
        client = native.BackpackHttpClient(
            api_key=api_key,
            api_secret=api_secret,
            window=5000,
            timeout=2,
            base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "GET",
            "/api/v1/order",
            [("symbol", "BTC_USDC"), ("orderId", "test-order-id")],
            None,
            True,
            "orderQuery",
            [[("symbol", "BTC_USDC"), ("orderId", "test-order-id")]],
            None,
        )

    request = received.get_nowait()
    timestamp = request["backpack_x-timestamp"]
    message = (
        "instruction=orderQuery&orderId=test-order-id&symbol=BTC_USDC"
        f"&timestamp={timestamp}&window=5000"
    )
    key = ECC.construct(curve="Ed25519", seed=b"1" * 32)
    expected_signature = base64.b64encode(eddsa.new(key, "rfc8032").sign(message.encode())).decode()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert request["backpack_x-api-key"] == api_key
    assert request["backpack_x-signature"] == expected_signature
    assert request["path"] == ("/api/v1/order?symbol=BTC_USDC&orderId=test-order-id")


def test_sync_backpack_manager_uses_native_transport() -> None:
    pytest.importorskip("dcex._native")
    from dcex.backpack._http_manager import HTTPManager

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/time",
            signed=False,
        )

    manager.close()
    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/time"


@pytest.mark.asyncio
async def test_async_backpack_manager_uses_native_transport() -> None:
    pytest.importorskip("dcex._native")
    from dcex.async_support.backpack._http_manager import HTTPManager

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/time",
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/time"


def test_native_lighter_form_request() -> None:
    native = pytest.importorskip("dcex._native")

    with _http_server({"code": 0}) as (base_url, received):
        client = native.LighterHttpClient(timeout=2, base_url=base_url)
        status, _headers, body = client.request_raw(
            "POST",
            "/api/v1/sendTx",
            [("account_index", "1")],
            [("tx_type", "14"), ("tx_info", '{"Price":100}')],
            False,
            {"Authorization": "token"},
            "form",
        )

    request = received.get_nowait()
    assert status == 200
    assert json.loads(body) == {"code": 0}
    assert request["path"] == "/api/v1/sendTx?account_index=1"
    assert request["body"] == "tx_type=14&tx_info=%7B%22Price%22%3A100%7D"


def test_sync_lighter_manager_uses_native_transport() -> None:
    from dcex.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    manager.close()
    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"


@pytest.mark.asyncio
async def test_async_lighter_manager_uses_native_transport() -> None:
    from dcex.async_support.lighter._http_manager import HTTPManager

    with _http_server({"code": 0, "status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            "/api/v1/status",
            {"source": "native"},
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"code": 0, "status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/api/v1/status?source=native"


def test_native_aster_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"

    with _http_server({}) as (base_url, received):
        client = native.AsterHttpClient(
            signer_address=signer,
            private_key="0x" + "11" * 32,
            timeout=2,
            spot_base_url=base_url,
            futures_base_url=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "spot",
            "/api/v3/order",
            [("symbol", "BTCUSDT"), ("side", "BUY")],
            True,
        )

    request = received.get_nowait()
    pairs = parse_qsl(request["body"])
    signature = dict(pairs)["signature"]
    message = "&".join(f"{key}={value}" for key, value in pairs[:-1])
    from dcex.aster._http_manager import sign_message

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert signature == sign_message(message, "0x" + "11" * 32)


def test_sync_aster_manager_uses_native_transport() -> None:
    from dcex.aster._http_manager import HTTPManager
    from dcex.aster.endpoints.market import SpotMarket

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        result = manager._request(
            "GET",
            SpotMarket.SERVER_TIME,
            signed=False,
        )

    manager.close()
    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == str(SpotMarket.SERVER_TIME)


@pytest.mark.asyncio
async def test_async_aster_manager_uses_native_transport() -> None:
    from dcex.aster.endpoints.market import SpotMarket
    from dcex.async_support.aster._http_manager import HTTPManager

    with _http_server({"serverTime": 1}) as (base_url, received):
        manager = HTTPManager(
            spot_base_url=base_url,
            futures_base_url=base_url,
            preload_product_table=False,
        )
        await manager.async_init()
        result = await manager._request(
            "GET",
            SpotMarket.SERVER_TIME,
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"serverTime": 1}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == str(SpotMarket.SERVER_TIME)


def test_native_hyperliquid_signed_request() -> None:
    native = pytest.importorskip("dcex._native")
    action = {"type": "order", "a": 1}

    with _http_server({}) as (base_url, received):
        client = native.HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key="0x" + "11" * 32,
            timeout=2,
            endpoint=base_url,
        )
        status, _headers, body = client.request_raw(
            "POST",
            "/exchange",
            json.dumps({"action": action}, separators=(",", ":")).encode(),
            msgspec.msgpack.encode(action),
            True,
        )

    request = received.get_nowait()
    payload = json.loads(request["body"])
    from dcex.hyperliquid._http_manager import HTTPManager

    manager = HTTPManager(
        wallet_address="0x" + "22" * 20,
        private_key="0x" + "11" * 32,
        preload_product_table=False,
    )
    expected = manager._auth({"action": action}, payload["nonce"])
    manager.close()

    assert status == 200
    assert json.loads(body) == {"ok": True}
    assert payload["signature"] == expected


def test_sync_hyperliquid_manager_uses_native_transport() -> None:
    from dcex.hyperliquid._http_manager import HTTPManager

    with _http_server({"status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
        )
        manager.endpoint = base_url
        manager._native_client = pytest.importorskip("dcex._native").HyperliquidHttpClient(
            timeout=2, endpoint=base_url
        )
        result = manager._request(
            "POST",
            "/info",
            {"type": "meta"},
            signed=False,
        )

    manager.close()
    assert result == {"status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/info"


@pytest.mark.asyncio
async def test_async_hyperliquid_manager_uses_native_transport() -> None:
    from dcex.async_support.hyperliquid._http_manager import HTTPManager

    with _http_server({"status": "ok"}) as (base_url, received):
        manager = HTTPManager(
            preload_product_table=False,
        )
        await manager.async_init()
        manager.endpoint = base_url
        manager._native_client = pytest.importorskip("dcex._native").HyperliquidHttpClient(
            timeout=2, endpoint=base_url
        )
        result = await manager._request(
            "POST",
            "/info",
            {"type": "meta"},
            signed=False,
        )

    assert manager.session is not None
    await manager.session.aclose()
    assert result == {"status": "ok"}
    assert manager.last_response_headers["x-response"] == "native"
    assert received.get_nowait()["path"] == "/info"
