"""Binary income export and server-error handling through the native client."""

# ruff: noqa: ANN401, D103
from __future__ import annotations

import asyncio
import hashlib
import hmac
from typing import Any

import pytest
from aiohttp import web


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("server_error", [False, True])
async def test_income_export_preserves_bytes_and_checks_errors(
    asynchronous: bool, server_error: bool
) -> None:
    from dcex.async_support.bingx.client import Client as AsyncClient
    from dcex.bingx.client import Client

    report = b"PK\x03\x04\x00\xff\x80binary-report"
    requests: list[dict[str, Any]] = []

    async def handle(request: web.Request) -> web.Response:
        requests.append(dict(request.query))
        assert request.headers["X-BX-APIKEY"] == "api-key"
        if server_error:
            return web.json_response({"code": 100004, "msg": "permission denied"})
        return web.Response(
            body=report,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    app = web.Application()
    app.router.add_get("/openApi/swap/v2/user/income/export", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    assert site._server is not None
    base = f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}"
    cls = AsyncClient if asynchronous else Client
    client = cls(
        api_key="api-key", api_secret="api-secret", preload_product_table=False, base_url=base
    )
    if asynchronous:
        await client.async_init()
    kwargs = {
        "product_symbol": "BTC-USDT",
        "income_type": "FUNDING_FEE",
        "start_time": 1700000000000,
        "end_time": 1700000010000,
        "limit": 100,
    }
    try:

        async def call() -> bytes:
            if asynchronous:
                return await client.export_swap_income(**kwargs)
            return await asyncio.to_thread(client.export_swap_income, **kwargs)

        if server_error:
            with pytest.raises(Exception, match="100004.*permission denied"):
                await call()
        else:
            assert await call() == report
    finally:
        if asynchronous:
            await client.close()
        else:
            client.close()
        await runner.cleanup()
    assert len(requests) == 1
    query = requests[0]
    signature = query.pop("signature")
    canonical = "&".join(f"{key}={value}" for key, value in sorted(query.items()))
    assert signature == hmac.new(b"api-secret", canonical.encode(), hashlib.sha256).hexdigest()
    assert query.pop("timestamp").isdigit()
    assert query == {
        "symbol": "BTC-USDT",
        "incomeType": "FUNDING_FEE",
        "startTime": "1700000000000",
        "endTime": "1700000010000",
        "limit": "100",
    }
