"""Independent official SDK signatures and complete Hyperliquid action envelopes."""

# ruff: noqa: ANN001, ANN201, D103
import inspect
import json
from pathlib import Path

import pytest

from tests.unit.native_http_helpers import _http_server

VECTORS = json.loads(
    (Path(__file__).parents[1] / "fixtures/signing/hyperliquid_official.json").read_text(
        encoding="utf-8"
    )
)


def _signature(case):
    return {
        key: ("0x" + value[2:].zfill(64) if key in {"r", "s"} else value)
        for key, value in case["signature"].items()
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "case",
    [
        c
        for c in VECTORS["cases"]
        if c["is_mainnet"] and c["action"]["type"] in {"vaultTransfer", "subAccountTransfer"}
    ],
)
async def test_transfer_body_and_signature_match_official_sdk(asynchronous, case):
    from dcex.async_support.hyperliquid.client import Client as AsyncClient
    from dcex.hyperliquid.client import Client

    with _http_server({"status": "ok"}) as (base, received):
        client = (AsyncClient if asynchronous else Client)(
            wallet_address="0x" + "22" * 20,
            private_key=VECTORS["private_key"],
            preload_product_table=False,
        )
        if asynchronous:
            await client.async_init()
        from dcex._native_http import load_native

        client._native_client = load_native().HyperliquidHttpClient(
            wallet_address="0x" + "22" * 20,
            private_key=VECTORS["private_key"],
            endpoint=base,
            timeout=10,
        )
        action = case["action"]
        try:
            if action["type"] == "vaultTransfer":
                result = client.transfer_vault_usd(
                    target_vault=action["vaultAddress"],
                    is_deposit=action["isDeposit"],
                    usd=action["usd"],
                    nonce=case["nonce"],
                )
            else:
                result = client.transfer_sub_account_usd(
                    sub_account_user=action["subAccountUser"],
                    is_deposit=action["isDeposit"],
                    usd=action["usd"],
                    nonce=case["nonce"],
                )
            if inspect.isawaitable(result):
                await result
        finally:
            result = client.close()
            if inspect.isawaitable(result):
                await result
        request = received.get(timeout=10)
    assert request["method"] == "POST"
    assert request["path"] == "/exchange"
    body = json.loads(request["body"])
    assert body == {"action": action, "nonce": case["nonce"], "signature": _signature(case)}
    assert list(body["action"]) == list(action)


@pytest.mark.parametrize(
    "case", [c for c in VECTORS["cases"] if c["action"]["type"] in {"order", "cancel"}]
)
def test_ws_helpers_match_official_sdk_without_connecting(case):
    from dcex.ws.hyperliquid import PrivateClient

    client = PrivateClient(
        "0x" + "22" * 20, testnet=not case["is_mainnet"], base_url="ws://127.0.0.1:1"
    )
    common = dict(
        nonce=case["nonce"],
        private_key=VECTORS["private_key"],
        vault_address=case["vault_address"],
        expires_after=case["expires_after"],
    )
    if case["action"]["type"] == "order":
        actual = client.sign_order(case["action"]["orders"], grouping="na", **common)
    else:
        actual = client.sign_cancel(case["action"]["cancels"], **common)
    expected = {"action": case["action"], "nonce": case["nonce"], "signature": _signature(case)}
    if case["vault_address"] is not None:
        expected["vaultAddress"] = case["vault_address"]
    if case["expires_after"] is not None:
        expected["expiresAfter"] = case["expires_after"]
    assert actual == expected
    assert list(actual["action"]) == list(case["action"])


@pytest.mark.parametrize(
    "method,items",
    [
        ("sign_order", []),
        ("sign_cancel", []),
        ("sign_cancel", [{"a": 0, "o": 1.5}]),
        (
            "sign_order",
            [{"a": 0, "b": True, "p": 1.5, "s": "1", "r": False, "t": {"limit": {"tif": "Gtc"}}}],
        ),
    ],
)
def test_ws_signing_helpers_validate_locally(method, items):
    from dcex.ws.hyperliquid import PrivateClient

    client = PrivateClient("0x" + "22" * 20, base_url="ws://127.0.0.1:1")
    with pytest.raises(ValueError):
        getattr(client, method)(items, nonce=1, private_key=VECTORS["private_key"])
