# ruff: noqa: D100, D103, F403, F405

from tests.unit.test_http_manager_requests import *


def test_sync_aster_signed_body_matches_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    from dcex.aster._http_manager import HTTPManager, sign_message
    from dcex.aster.endpoints.account import SpotAccount

    nonce = 1700000000000000
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    private_key = "0x" + "11" * 32
    session = _CaptureSession({})
    manager = HTTPManager(
        signer_address=signer,
        private_key=private_key,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    monkeypatch.setattr(manager, "_next_nonce", lambda: nonce)

    manager._request(
        "POST",
        SpotAccount.TRANSFER,
        {"amount": "1", "asset": "USDT", "kindType": "FUTURE_SPOT"},
    )

    method, url, kwargs = session.calls[0]
    message = f"amount=1&asset=USDT&kindType=FUTURE_SPOT&nonce={nonce}&signer={signer}"
    assert method == "POST"
    assert url == "https://sapi.asterdex.com/api/v3/asset/wallet/transfer"
    assert kwargs["data"]["signature"] == sign_message(message, private_key)


@pytest.mark.asyncio
async def test_async_aster_signed_body_matches_docs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.aster._http_manager import sign_message
    from dcex.async_support.aster._http_manager import HTTPManager
    from dcex.async_support.aster.endpoints.account import SpotAccount

    nonce = 1700000000000000
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    private_key = "0x" + "11" * 32
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        signer_address=signer,
        private_key=private_key,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    monkeypatch.setattr(manager, "_next_nonce", lambda: nonce)

    await manager._request(
        "POST",
        SpotAccount.TRANSFER,
        {"amount": "1", "asset": "USDT", "kindType": "FUTURE_SPOT"},
    )

    method, url, kwargs = session.calls[0]
    message = f"amount=1&asset=USDT&kindType=FUTURE_SPOT&nonce={nonce}&signer={signer}"
    assert method == "POST"
    assert url == "https://sapi.asterdex.com/api/v3/asset/wallet/transfer"
    assert kwargs["data"]["signature"] == sign_message(message, private_key)


def test_sync_aster_futures_signature_includes_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.aster._http_manager import HTTPManager, sign_message
    from dcex.aster.endpoints.account import FuturesAccount

    nonce = 1700000000000000
    user = "0x" + "22" * 20
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    private_key = "0x" + "11" * 32
    session = _CaptureSession([])
    manager = HTTPManager(
        user_address=user,
        signer_address=signer,
        private_key=private_key,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    monkeypatch.setattr(manager, "_next_nonce", lambda: nonce)

    manager._request("GET", FuturesAccount.BALANCE, {"asset": "USDC"})

    method, url, kwargs = session.calls[0]
    message = f"asset=USDC&nonce={nonce}&user={user}&signer={signer}"
    assert method == "GET"
    assert url == "https://fapi.asterdex.com/fapi/v3/balance"
    assert kwargs["params"]["user"] == user
    assert kwargs["params"]["signer"] == signer
    assert kwargs["params"]["signature"] == sign_message(message, private_key)


@pytest.mark.asyncio
async def test_async_aster_futures_signature_includes_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.aster._http_manager import sign_message
    from dcex.async_support.aster._http_manager import HTTPManager
    from dcex.async_support.aster.endpoints.account import FuturesAccount

    nonce = 1700000000000000
    user = "0x" + "22" * 20
    signer = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    private_key = "0x" + "11" * 32
    session = _AsyncCaptureSession([])
    manager = HTTPManager(
        user_address=user,
        signer_address=signer,
        private_key=private_key,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    monkeypatch.setattr(manager, "_next_nonce", lambda: nonce)

    await manager._request("GET", FuturesAccount.BALANCE, {"asset": "USDC"})

    method, url, kwargs = session.calls[0]
    message = f"asset=USDC&nonce={nonce}&user={user}&signer={signer}"
    assert method == "GET"
    assert url == "https://fapi.asterdex.com/fapi/v3/balance"
    assert kwargs["params"]["user"] == user
    assert kwargs["params"]["signer"] == signer
    assert kwargs["params"]["signature"] == sign_message(message, private_key)


def test_sync_backpack_signed_query_matches_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    from dcex.backpack._http_manager import HTTPManager

    backpack_http = import_module("dcex.backpack._http_manager")
    monkeypatch.setattr(backpack_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({})
    manager = HTTPManager(
        api_key=_backpack_key(),
        api_secret=_backpack_secret(),
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "GET",
        "/api/v1/order",
        {"symbol": "BTC_USDC", "orderId": "test-order-id"},
        signed=True,
        instruction="orderQuery",
    )

    method, url, kwargs = session.calls[0]
    message = (
        "instruction=orderQuery&orderId=test-order-id&symbol=BTC_USDC"
        f"&timestamp={int(TS_S) * 1000}&window=5000"
    )
    assert method == "GET"
    assert url == "https://api.backpack.exchange/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
    assert kwargs["headers"]["X-API-Key"] == _backpack_key()
    assert kwargs["headers"]["X-Timestamp"] == str(int(TS_S) * 1000)
    assert kwargs["headers"]["X-Window"] == "5000"
    assert kwargs["headers"]["X-Signature"] == _backpack_expected_signature(message)


@pytest.mark.asyncio
async def test_async_backpack_signed_query_matches_docs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.backpack._http_manager import HTTPManager

    backpack_http = import_module("dcex.async_support.backpack._http_manager")
    monkeypatch.setattr(backpack_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=_backpack_key(),
        api_secret=_backpack_secret(),
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    await manager._request(
        "GET",
        "/api/v1/order",
        {"symbol": "BTC_USDC", "orderId": "test-order-id"},
        signed=True,
        instruction="orderQuery",
    )

    method, url, kwargs = session.calls[0]
    message = (
        "instruction=orderQuery&orderId=test-order-id&symbol=BTC_USDC"
        f"&timestamp={int(TS_S) * 1000}&window=5000"
    )
    assert method == "GET"
    assert url == "https://api.backpack.exchange/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
    assert kwargs["headers"]["X-API-Key"] == _backpack_key()
    assert kwargs["headers"]["X-Timestamp"] == str(int(TS_S) * 1000)
    assert kwargs["headers"]["X-Window"] == "5000"
    assert kwargs["headers"]["X-Signature"] == _backpack_expected_signature(message)


def test_gateio_signed_query_order_matches_sent_params(monkeypatch: pytest.MonkeyPatch) -> None:
    from dcex.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        timeout=7,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"contract": "BTC_USD", "status": "finished", "limit": 50}

    manager._request("GET", "/futures/orders", query=query, signed=True)

    method, _url, kwargs = session.calls[0]
    query_string = "contract=BTC_USD&status=finished&limit=50"
    assert method == "GET"
    assert kwargs["params"] == query_string
    assert kwargs["timeout"] == 7
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature(query_string)


def test_sync_gateio_json_decode_failure_is_failed_request() -> None:
    from dcex.gateio._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    manager.session = _BadJsonSession()  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Failed to decode JSON response") as exc_info:
        manager._request("GET", "/spot/currencies", signed=False)

    assert exc_info.value.status_code == 200
    assert exc_info.value.resp_headers == {}


def test_sync_mexc_contract_list_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.mexc._http_manager import HTTPManager

    mexc_http = import_module("dcex.mexc._http_manager")
    monkeypatch.setattr(mexc_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({"success": True, "code": 0})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "POST",
        "/api/v1/private/order/cancel",
        [{"orderId": "test-order-id"}],
        api="contract",
    )

    method, url, kwargs = session.calls[0]
    request_time = str(int(int(TS_S) * 1000))
    body = '[{"orderId":"test-order-id"}]'
    assert method == "POST"
    assert url == "https://api.mexc.com/api/v1/private/order/cancel"
    assert kwargs["data"] == body
    assert kwargs["headers"]["Request-Time"] == request_time
    assert kwargs["headers"]["Signature"] == _mexc_contract_expected_signature(
        request_time,
        body,
    )


def test_sync_bitget_uta_batch_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.bitget._http_manager import HTTPManager

    bitget_http = import_module("dcex.bitget._http_manager")
    monkeypatch.setattr(bitget_http.time, "time", lambda: int(TS_S))
    session = _CaptureSession({"code": "00000", "data": {}})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        passphrase="test-passphrase",
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    orders = [
        {
            "category": "SPOT",
            "symbol": "BTCUSDT",
            "qty": "0.001",
            "price": None,
        }
    ]

    manager._request("POST", "/api/v3/trade/place-batch", orders)

    method, url, kwargs = session.calls[0]
    timestamp = str(int(int(TS_S) * 1000))
    body = '[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]'
    payload = f"{timestamp}POST/api/v3/trade/place-batch{body}"
    expected_signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    ).decode()
    assert orders[0]["price"] is None
    assert method == "POST"
    assert url == "https://api.bitget.com/api/v3/trade/place-batch"
    assert kwargs["data"] == body
    assert kwargs["headers"]["ACCESS-SIGN"] == expected_signature


@pytest.mark.asyncio
async def test_async_gateio_signed_query_order_matches_sent_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.async_support.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"contract": "BTC_USD", "status": "finished", "limit": 50}

    await manager._request("GET", "/futures/orders", query=query, signed=True)

    method, _url, kwargs = session.calls[0]
    query_string = "contract=BTC_USD&status=finished&limit=50"
    assert method == "GET"
    assert kwargs["params"] == query_string
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature(query_string)


@pytest.mark.asyncio
async def test_async_gateio_empty_post_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    gateio_http = import_module("dcex.async_support.gateio._http_manager")
    monkeypatch.setattr(gateio_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    query = {"leverage": "10"}

    await manager._request(
        "POST",
        "/futures/{settle}/positions/{contract}/leverage",
        path_params={"settle": "usdt", "contract": "BTC_USDT"},
        query=query,
        signed=True,
    )

    method, _url, kwargs = session.calls[0]
    query_string = "leverage=10"
    assert method == "POST"
    assert kwargs["params"] == query_string
    assert kwargs["content"] is None
    assert kwargs["headers"]["SIGN"] == _gateio_expected_signature_for(
        "POST",
        "/api/v4/futures/usdt/positions/BTC_USDT/leverage",
        query_string,
    )


@pytest.mark.asyncio
async def test_async_gateio_json_decode_failure_is_failed_request() -> None:
    from dcex.async_support.gateio._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    manager.session = _AsyncBadJsonSession()  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Failed to decode JSON response") as exc_info:
        await manager._request("GET", "/spot/currencies", signed=False)

    assert exc_info.value.status_code == 200
    assert exc_info.value.resp_headers == {}


@pytest.mark.asyncio
async def test_async_mexc_contract_list_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.mexc._http_manager import HTTPManager

    mexc_http = import_module("dcex.async_support.mexc._http_manager")
    monkeypatch.setattr(mexc_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({"success": True, "code": 0})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    await manager._request(
        "POST",
        "/api/v1/private/order/cancel",
        [{"orderId": "test-order-id"}],
        api="contract",
    )

    method, url, kwargs = session.calls[0]
    request_time = str(int(int(TS_S) * 1000))
    body = '[{"orderId":"test-order-id"}]'
    assert method == "POST"
    assert url == "https://api.mexc.com/api/v1/private/order/cancel"
    assert kwargs["content"] == body
    assert kwargs["headers"]["Request-Time"] == request_time
    assert kwargs["headers"]["Signature"] == _mexc_contract_expected_signature(
        request_time,
        body,
    )


@pytest.mark.asyncio
async def test_async_bitget_uta_batch_body_matches_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.async_support.bitget._http_manager import HTTPManager

    bitget_http = import_module("dcex.async_support.bitget._http_manager")
    monkeypatch.setattr(bitget_http.time, "time", lambda: int(TS_S))
    session = _AsyncCaptureSession({"code": "00000", "data": {}})
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        passphrase="test-passphrase",
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]
    orders = [
        {
            "category": "SPOT",
            "symbol": "BTCUSDT",
            "qty": "0.001",
            "price": None,
        }
    ]

    await manager._request("POST", "/api/v3/trade/place-batch", orders)

    method, url, kwargs = session.calls[0]
    timestamp = str(int(int(TS_S) * 1000))
    body = '[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]'
    payload = f"{timestamp}POST/api/v3/trade/place-batch{body}"
    expected_signature = base64.b64encode(
        hmac.new(API_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    ).decode()
    assert orders[0]["price"] is None
    assert method == "POST"
    assert url == "https://api.bitget.com/api/v3/trade/place-batch"
    assert kwargs["content"] == body
    assert kwargs["headers"]["ACCESS-SIGN"] == expected_signature


def test_sync_bitmex_passes_configured_timeout() -> None:
    from dcex.bitmex._http_manager import HTTPManager

    session = _CaptureSession({})
    manager = HTTPManager(timeout=7, preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    manager._request("GET", "/api/v1/instrument", signed=False)

    assert session.calls[0][2]["timeout"] == 7


def test_sync_okx_defaults_to_openapi_domain_and_passes_timeout() -> None:
    from dcex.okx._http_manager import HTTPManager

    session = _CaptureSession({"code": "0", "data": []})
    manager = HTTPManager(timeout=7, preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    manager._request("GET", "/api/v5/public/time", signed=False)

    method, url, kwargs = session.calls[0]
    assert method == "GET"
    assert url == "https://openapi.okx.com/api/v5/public/time"
    assert kwargs["timeout"] == 7


def test_sync_okx_error_with_empty_data_uses_top_level_message() -> None:
    from dcex.okx._http_manager import HTTPManager

    session = _CaptureSession(
        {"code": "51000", "msg": "Parameter error", "data": []},
        status_code=400,
    )
    manager = HTTPManager(preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Parameter error") as exc_info:
        manager._request("GET", "/api/v5/account/balance", {"ccy": "BTC"}, signed=False)

    assert "51000" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_okx_error_with_empty_data_uses_top_level_message() -> None:
    from dcex.async_support.okx._http_manager import HTTPManager

    session = _AsyncCaptureSession(
        {"code": "51000", "msg": "Parameter error", "data": []},
        status_code=400,
    )
    manager = HTTPManager(preload_product_table=False)
    manager.session = session  # type: ignore[assignment]

    with pytest.raises(FailedRequestError, match="Parameter error") as exc_info:
        await manager._request("GET", "/api/v5/account/balance", {"ccy": "BTC"}, signed=False)

    assert manager.base_api == "https://openapi.okx.com"
    assert "51000" in str(exc_info.value)
