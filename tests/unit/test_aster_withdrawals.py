"""Offline coverage for aster withdrawals."""

import inspect
from dataclasses import replace
from urllib.parse import parse_qsl, urlsplit

import pytest

from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_orders import invoke


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_aster_futures_withdraw_signature_chain_id(asynchronous):
    from tests.unit.test_aster_endpoint_coverage import AsyncClient, Client, _client_kwargs

    fields = dict(
        chain_id=56,
        asset="USDT",
        amount="1",
        fee="0.1",
        receiver="0x" + "22" * 20,
        user_nonce="123",
        user_signature="0x" + "11" * 65,
        signature_chain_id="0x38",
    )
    with _http_server() as (base, received):
        client = (AsyncClient if asynchronous else Client)(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            await invoke(client, "withdraw_futures_signed", **fields)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        requests = [received.get_nowait() for _ in range(received.qsize())]
    request = next(r for r in requests if "user-withdraw" in r["path"])
    assert request["method"] == "POST"
    params = dict(parse_qsl(request["body"] or urlsplit(request["path"]).query))
    assert params["signatureChainId"] == "0x38"
    assert params["userNonce"] == "123"


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("whitelist", [None, "192.0.2.1"])
async def test_aster_withdraw_permission_preserved(asynchronous, whitelist):
    from tests.unit.test_aster_endpoint_coverage import (
        CASES,
        AsyncClient,
        Client,
        _assert_request,
        _client_kwargs,
        _drain,
    )

    case = next(c for c in CASES if c.method == "register_agent_signed")
    kwargs = dict(case.kwargs, can_withdraw=True)
    params = dict(case.params, canWithdraw="true")
    if whitelist is not None:
        kwargs["ip_whitelist"] = whitelist
        params["ipWhitelist"] = whitelist
    case = replace(case, kwargs=kwargs, params=params, verb="POST")
    with _http_server() as (base, received):
        client = (AsyncClient if asynchronous else Client)(**_client_kwargs(base))
        if asynchronous:
            await client.async_init()
        try:
            if whitelist is None:
                with pytest.raises(ValueError, match="ipWhitelist"):
                    await invoke(client, case.method, **case.kwargs)
                assert received.empty()
                return
            await invoke(client, case.method, **case.kwargs)
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        _assert_request(case, _drain(received))
