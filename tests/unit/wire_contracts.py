"""Compare existing endpoint-coverage captures with declared wire field names."""

import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from dcex._input_codec import CATALOG
from tests.unit.input_contract_coverage import missing_wire_declarations

CONTROLS = json.loads((Path(__file__).parents[1] / "fixtures/wire_controls.json").read_text(encoding="utf-8"))


def remove_control(value, path, allowed):
    """Remove one reviewed control only at its exact path and known value."""
    if path[0] == "[]":
        for item in value:
            remove_control(item, path[1:], allowed)
    elif isinstance(value, dict) and path[0] in value:
        if len(path) == 1:
            assert value[path[0]] in allowed, (path, value[path[0]], allowed)
            del value[path[0]]
        else:
            remove_control(value[path[0]], path[1:], allowed)


def decoded(value):
    if isinstance(value, str) and value.startswith(("{", "[")):
        try:
            return decoded(json.loads(value))
        except ValueError:
            return value
    if isinstance(value, dict):
        return {key: decoded(child) for key, child in value.items()}
    if isinstance(value, list):
        return [decoded(child) for child in value]
    return value


def assert_wire_contract(exchange, method, request):
    schema = deepcopy(CATALOG["exchanges"][exchange].get(method, {"properties": {}}))
    query = request.get("query") or dict(parse_qsl(urlsplit(request.get("path", "")).query))
    body = request.get("body") or ""
    if isinstance(body, bytes):
        body = body.decode()
    if isinstance(body, str):
        body = decoded(body) if body.startswith(("{", "[")) else dict(parse_qsl(body))
    if isinstance(body, list):
        candidates = [key for key, field in schema.get("properties", {}).items() if field.get("type") == "array"]
        if candidates:
            body = {candidates[0]: body}
        else:
            schema = {"properties": {"$root": {"type": "array", "items": schema}}}
            body = {"$root": body}
    payload = {**decoded(query), **decoded(body)}
    for path, control in CONTROLS.get(f"{exchange}/{method}", {}).items():
        remove_control(payload, path.split("/"), control["values"])
    missing = missing_wire_declarations(payload, schema)
    assert not missing, (exchange, method, missing, payload)
