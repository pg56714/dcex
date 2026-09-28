"""OKX SBE bytes and JSON API errors through both public Python clients."""

from __future__ import annotations

import pytest

from dcex.async_support.okx.client import Client as AsyncClient
from dcex.okx.client import Client
from tests.unit.native_http_helpers import _http_server


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("server_error", [False, True])
async def test_sbe_binary_snapshot_and_json_error(asynchronous: bool, server_error: bool) -> None:
    snapshot = b"\x08\x00\xee\x03\x01\x00\x01\x00\x00\xff\x80"
    with _http_server(
        {"code": "51000", "msg": "Parameter instIdCode error", "data": []},
        response_bytes=None if server_error else snapshot,
        content_type="application/json" if server_error else "application/sbe",
    ) as (base, received):
        client = (AsyncClient if asynchronous else Client)(
            base_api=base, preload_product_table=False
        )
        try:
            if asynchronous:
                await client.async_init()
            if server_error:
                with pytest.raises(Exception, match="51000.*instIdCode"):
                    if asynchronous:
                        await client.get_sbe_orderbook(12345)
                    else:
                        client.get_sbe_orderbook(12345)
            elif asynchronous:
                assert await client.get_sbe_orderbook(12345) == snapshot
            else:
                assert client.get_sbe_orderbook(12345) == snapshot
        finally:
            if asynchronous:
                await client.close()
            else:
                client.close()
        request = received.get_nowait()
        assert request["method"] == "GET"
        assert request["path"] == "/api/v5/market/books-sbe?instIdCode=12345&source=0"
        assert not request.get("OK-ACCESS-SIGN")
