"""Full wire envelopes and independent SDK signatures for HIP/admin methods."""

import importlib
import inspect
import json
from pathlib import Path

import pytest

from tests.unit.native_http_helpers import _http_server

ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = json.loads(
    (ROOT / "docs/official-endpoint-inventory/sources/hyperliquid-actions.json").read_text(
        encoding="utf-8"
    )
)
VECTORS = json.loads(
    (ROOT / "tests/fixtures/signing/hyperliquid_inventory.json").read_text(encoding="utf-8")
)
NAMES = {op["name"] for op in OPERATIONS}
CONFIRMED = {"perp_deploy_disable_dex", "convert_to_multi_sig_user_signed"}


async def invoke(asynchronous, base, name, testnet=True, **kwargs):
    import dcex._native as native

    cls = importlib.import_module(
        ("dcex.async_support" if asynchronous else "dcex") + ".hyperliquid.client"
    ).Client
    client = cls(
        private_key=VECTORS["private_key"],
        wallet_address=VECTORS["wallet_address"],
        preload_product_table=False,
    )
    if asynchronous:
        await client.async_init()
    client._native_client = native.HyperliquidHttpClient(
        private_key=VECTORS["private_key"],
        wallet_address=VECTORS["wallet_address"],
        testnet=testnet,
        endpoint=base,
        timeout=2,
    )
    try:
        result = getattr(client, name)(**kwargs)
        return await result if inspect.isawaitable(result) else result
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "case", VECTORS["cases"], ids=lambda c: c["name"] + ("-mainnet" if c["mainnet"] else "-testnet")
)
async def test_action_wire(asynchronous, case):
    kwargs = {key: case[key] for key in ("action", "nonce", "vault_address", "expires_after")}
    if case["name"] in CONFIRMED:
        kwargs["confirm"] = True
    if case["caller_signed"]:
        kwargs["signature"] = case["signature"]
    with _http_server({"status": "ok"}) as (base, received):
        await invoke(asynchronous, base, case["name"], testnet=not case["mainnet"], **kwargs)
        assert received.qsize() == 1
        request = received.get_nowait()
    assert request["method"] == "POST"
    assert request["path"] == "/exchange"
    body = json.loads(request["body"])
    assert body == {
        "action": case["action"],
        "nonce": case["nonce"],
        "signature": case["signature"],
        "vaultAddress": case["vault_address"],
        "expiresAfter": case["expires_after"],
    }
    assert list(body["action"]) == list(case["action"])


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("op", [op for op in OPERATIONS if op["public"]], ids=lambda op: op["name"])
async def test_info_wire(asynchronous, op):
    with _http_server() as (base, received):
        await invoke(
            asynchronous, base, op["name"], **({"user": op["sample"]["user"]} if op["user"] else {})
        )
        assert received.qsize() == 1
        request = received.get_nowait()
    assert request["method"] == "POST"
    assert request["path"] == "/info"
    assert json.loads(request["body"]) == op["sample"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "op", [op for op in OPERATIONS if not op["public"]], ids=lambda op: op["name"]
)
async def test_wrong_action_rejected_before_transport(asynchronous, op):
    kwargs = {"action": {"type": "order"}, "nonce": 1}
    if op["name"] in CONFIRMED:
        kwargs["confirm"] = True
    if op["signed"]:
        kwargs["signature"] = VECTORS["cases"][0]["signature"]
    with _http_server() as (base, received):
        with pytest.raises(ValueError, match="action.type"):
            await invoke(asynchronous, base, op["name"], **kwargs)
        assert received.empty()


def test_inventory_surface():
    assert NAMES == {c["name"] for c in VECTORS["cases"]} | {
        op["name"] for op in OPERATIONS if op["public"]
    }
    for prefix in ("dcex", "dcex.async_support"):
        cls = importlib.import_module(prefix + ".hyperliquid._inventory_http").InventoryHTTP
        assert {
            name
            for name, method in vars(cls).items()
            if not name.startswith("_") and callable(method)
        } == NAMES


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("name", sorted(CONFIRMED))
@pytest.mark.parametrize("confirm", [None, False, 1, "true"])
async def test_irreversible_action_requires_confirmation(asynchronous, name, confirm):
    case = next(c for c in VECTORS["cases"] if c["name"] == name)
    kwargs = {"action": case["action"], "nonce": case["nonce"]}
    if case["caller_signed"]:
        kwargs["signature"] = case["signature"]
    if confirm is not None:
        kwargs["confirm"] = confirm
    with _http_server() as (base, received):
        with pytest.raises(ValueError, match="confirm"):
            await invoke(asynchronous, base, name, **kwargs)
        assert received.empty()


@pytest.mark.parametrize("name", sorted(CONFIRMED))
@pytest.mark.parametrize("confirm", [None, "false", "1", "True"])
def test_native_irreversible_action_requires_confirmation(name, confirm):
    import dcex._native as native

    case = next(c for c in VECTORS["cases"] if c["name"] == name)
    params = [("action", json.dumps(case["action"])), ("nonce", str(case["nonce"]))]
    if case["caller_signed"]:
        params.append(("signature", json.dumps(case["signature"])))
    if confirm is not None:
        params.append(("confirm", confirm))
    with _http_server() as (base, received):
        client = native.HyperliquidHttpClient(
            private_key=VECTORS["private_key"], testnet=True, endpoint=base, timeout=2
        )
        with pytest.raises(ValueError, match="confirm"):
            client.private_request_json(name, params)
        assert received.empty()
