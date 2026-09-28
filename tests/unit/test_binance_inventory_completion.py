"""Verify additional Binance methods against the official SDK request inventory."""

import hashlib
import hmac
import importlib
import inspect
import json
from collections import Counter
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import pytest

from scripts.build_binance_inventory_wrappers import operation_name, wire_name
from tests.unit.native_http_helpers import _http_server
from tests.unit.test_binance_batch_review import batch_client, invoke

ROOT = Path(__file__).resolve().parents[2]
NAMES = {
    name for name, value in vars(importlib.import_module("dcex.binance._inventory_http").InventoryHTTP).items()
    if not name.startswith("_") and callable(value)
}
OPERATIONS = [
    op for op in json.loads((ROOT / "docs/official-endpoint-inventory/binance.json").read_text(encoding="utf-8"))["endpoints"]
    if op.get("sdk_method") and operation_name(op) in NAMES
]
JSON_PATHS = {"/sapi/v1/fiat/deposit", "/sapi/v2/fiat/withdraw"}


def values_for(op):
    values = {}
    structured = {
        "cancel_info_list": [{"orderId": "11"}, {"clientOrderId": "other"}],
        "assets": [{"type": "USDT"}, {"type": "SHARE", "tokenId": "112233"}],
        "ext": {"note": "reference"},
        "account_info": {"accountNumber": "123456"},
    }
    for field in op["parameters"]:
        key = field["name"]
        kind = field["type"]
        if key in structured:
            value = structured[key]
        elif "List[" in kind:
            value = ["112233", "112234"]
        elif "bool" in kind:
            value = True
        elif "int" in kind:
            value = 1
        elif "float" in kind:
            value = "1.25"
        else:
            value = "1"
        values[key] = value
    return values


def wire_string(value):
    return value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("op", OPERATIONS, ids=operation_name)
async def test_inventory_wire(asynchronous, op):
    import dcex._native as native

    values = values_for(op)
    with _http_server({"code": "000000", "success": True, "data": {}}) as (base, received):
        async with batch_client(asynchronous, base) as client:
            client._native_client = native.BinanceHttpClient(
                api_key="key", api_secret="secret", timeout=2,
                spot_base_url=base, alpha_base_url=base,
            )
            await invoke(client, operation_name(op), **values)
        requests = [received.get_nowait() for _ in range(received.qsize())]
    request = next(r for r in requests if urlsplit(r["path"]).path != "/api/v3/time")
    assert request["method"] == op["method"]
    assert urlsplit(request["path"]).path == op["path"]
    public = (
        op["path"].startswith("/bapi/")
        or "web3-wallet-prediction-trading/api/rest-api/market-data#" in op["official_source"]
        or op["path"] in {"/sapi/v1/mining/pub/algoList", "/sapi/v1/mining/pub/coinList"}
    )
    json_body = op["path"] in JSON_PATHS
    raw = urlsplit(request["path"]).query if json_body or op["method"] != "POST" else request["body"]
    pairs = parse_qsl(raw, keep_blank_values=True)
    if public:
        assert request["api_key"] is None
        assert all(key not in {"signature", "timestamp"} for key, _ in pairs)
        assert len(requests) == 1
    else:
        assert len(requests) == 2
        assert requests[0]["method"] == "GET"
        assert requests[0]["path"] == "/api/v3/time"
        assert request["api_key"] == "key"
        signature = dict(pairs)["signature"]
        assert signature == hmac.new(b"secret", raw.rsplit("&signature=", 1)[0].encode(), hashlib.sha256).hexdigest()
        assert dict(pairs)["timestamp"].isdigit()
        pairs = [(k, v) for k, v in pairs if k not in {"signature", "timestamp"}]
        if "recv_window" not in values:
            pairs = [(k, v) for k, v in pairs if k != "recvWindow"]
    expected = []
    for key, value in values.items():
        wire = wire_name(key)
        if json_body and key != "recv_window":
            continue
        if key == "cancel_info_list":
            expected.extend((f"cancelInfoList[{i}].{k}", v) for i, item in enumerate(value) for k, v in item.items())
        elif isinstance(value, list):
            expected.extend((wire, wire_string(item)) for item in value)
        else:
            expected.append((wire, wire_string(value)))
    assert Counter(pairs) == Counter(expected)
    if json_body:
        assert json.loads(request["body"]) == {wire_name(k): v for k, v in values.items() if k != "recv_window"}
    elif op["method"] != "POST":
        assert request["body"] == ""


def test_inventory_surface():
    assert len(OPERATIONS) == len(NAMES)
    for prefix in ("dcex", "dcex.async_support"):
        cls = importlib.import_module(prefix + ".binance._inventory_http").InventoryHTTP
        assert {name for name, value in vars(cls).items() if not name.startswith("_") and callable(value)} == NAMES
        for name in NAMES:
            assert inspect.signature(getattr(cls, name))
