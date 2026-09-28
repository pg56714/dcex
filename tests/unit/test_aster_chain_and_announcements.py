"""Verify the independent Chain and public announcement hosts and wire formats."""

import importlib
import inspect
import json
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server

CASES = [
    ("get_chain_locked_aster", {}, "GET", "/aster-chain/v3/staking/getLockedAster", {}),
    (
        "get_chain_withdraw_fee",
        {"chain_id": 56, "asset": "USDT"},
        "GET",
        "/aster-chain/v3/withdraw/estimateFee",
        {"chainId": "56", "asset": "USDT"},
    ),
    (
        "get_announcement",
        {"id": 12345},
        "GET",
        "/bapi/composite/v1/public/composite/ae/announcement/get",
        {"id": "12345"},
    ),
    (
        "search_announcements",
        {"page": 1, "size": 10, "category": "NEW_LISTING"},
        "POST",
        "/bapi/composite/v1/public/composite/ae/announcement/search",
        {"page": 1, "size": 10, "category": "NEW_LISTING"},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("case", CASES, ids=lambda c: c[0])
async def test_auxiliary_wire(asynchronous, case):
    name, kwargs, verb, path, expected = case
    cls = importlib.import_module(
        ("dcex.async_support" if asynchronous else "dcex") + ".aster.client"
    ).Client
    with _http_server({"code": "000000", "success": True, "data": {}}) as (base, received):
        client = cls(preload_product_table=False)
        if asynchronous:
            await client.async_init()
        client._native_client.set_auxiliary_base_urls(base, base)
        try:
            result = getattr(client, name)(**kwargs)
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        assert received.qsize() == 1
        request = received.get_nowait()
    assert request["method"] == verb
    assert urlsplit(request["path"]).path == path
    if verb == "GET":
        assert dict(parse_qsl(urlsplit(request["path"]).query)) == expected
        assert request["body"] == ""
    else:
        assert urlsplit(request["path"]).query == ""
        assert json.loads(request["body"]) == expected
