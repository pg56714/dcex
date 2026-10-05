"""Generate Binance business wrappers from the committed official SDK inventory."""

import json
from pathlib import Path
from typing import Any

from scripts.generation import run
from scripts.wrapper_codegen import (
    generated_endpoints,
    write_python_wrappers,
    write_rust_wrappers,
    write_schemas,
)

ROOT = Path(__file__).resolve().parents[1]


def wire_name(name: str) -> str:
    """Use the SDK's snake-to-camel field mapping."""
    first, *parts = name.rstrip("_").split("_")
    return first + "".join(p[:1].upper() + p[1:] for p in parts)


def operation_name(op: dict[str, Any]) -> str:
    """Disambiguate separate Alpha and prediction API namespaces."""
    if op["path"] == "/sapi/v1/c2c/orderMatch/listUserOrderHistory":
        return "get_c2c_trade_history"
    prefix = (
        "alpha_"
        if op["path"].startswith("/bapi/")
        else "prediction_"
        if "/prediction/" in op["path"]
        else ""
    )
    return prefix + ("fiat_deposit" if op["sdk_method"] == "deposit" else op["sdk_method"])


def field_kind(field: dict[str, Any]) -> str:
    """Preserve decimals and distinguish structured SDK parameters."""
    t = field["type"]
    if "List[" in t:
        return "array"
    if "int" in t:
        return "int"
    if "float" in t:
        return "decimal"
    if "bool" in t:
        return "bool"
    if "object" in t or ("Request" in t and "Enum" not in t):
        return "object"
    return "str"


def main() -> None:
    """Generate Rust metadata and synchronous/asynchronous Python wrappers."""
    selected = generated_endpoints("binance")
    inventory = json.loads(
        (ROOT / "docs/official-endpoint-inventory/binance.json").read_text(encoding="utf-8")
    )["endpoints"]
    specs = []
    for op in inventory:
        if not op.get("sdk_method") or operation_name(op) not in selected or op["method"] == "WS":
            continue
        path = op["path"]
        public = (
            path.startswith("/bapi/")
            or path in {"/sapi/v1/mining/pub/algoList", "/sapi/v1/mining/pub/coinList"}
            or "/prediction/market/" in path
            or ("/prediction/category/" in path)
            or ("/prediction/order-book" in path)
        )
        fields = [
            {**f, "wire": wire_name(f["name"]), "kind": field_kind(f)} for f in op["parameters"]
        ]
        spec = {
            "name": operation_name(op),
            "method": op["method"],
            "path": path,
            "public": public,
        }
        # MARKET_DATA routes are unsigned but still require the X-MBX-APIKEY header.
        if public and not path.startswith("/bapi/"):
            spec["api_key"] = True
        specs.append(
            {
                **spec,
                "fields": fields,
                "json_body": path in {"/sapi/v1/fiat/deposit", "/sapi/v2/fiat/withdraw"},
                "source": op["official_source"],
                "summary": op["doc"].strip().splitlines()[0].strip(),
            }
        )
    write_schemas("binance", specs)
    groups = {True: [], False: []}
    for op in specs:
        args = ", ".join(
            f["name"] + " => " + json.dumps(f["wire"]) for f in op["fields"] if f["required"]
        )
        line = f"        {op['name']}({args}),"
        if "withdraw" in op["path"] and op["method"] == "POST":
            line = (
                "        /// API withdrawals have no second confirmation; they execute on submit.\n"
                + line
            )
        groups[op["public"]].append(line)
    write_rust_wrappers(
        "binance",
        "use super::BinanceClient;\n"
        "crate::exchanges::impl_exchange_method_wrappers! {\n"
        "    @extend; BinanceClient;\n"
        "    public [\n"
        + "\n".join(groups[True])
        + "\n    ];\n    private [\n"
        + "\n".join(groups[False])
        + "\n    ];\n}\n",
    )
    for asynchronous in (False, True):
        lines = [
            '"""Additional Binance endpoints from the official SDK request tables."""',
            "from typing import Any",
            "from json import dumps",
            "from dcex._schema_codec import normalize_params",
            "from ._market_http import MarketHTTP",
            "from ._trade_http import TradeHTTP",
            "",
            "class GeneratedMethods(MarketHTTP, TradeHTTP):",
            '    """Alpha, fiat, mining, gift card, VIP loan and prediction endpoints."""',
        ]
        for op in specs:
            args = []
            for f in op["fields"]:
                annotation = {
                    "int": "int",
                    "bool": "bool",
                    "array": "list[Any]",
                    "object": "dict[str, Any]",
                    "decimal": "str",
                    "str": "str",
                }[f["kind"]]
                args.append(
                    f["name"] + ": " + annotation + ("" if f["required"] else " | None = None")
                )
            lines += [
                "",
                "    "
                + ("async " if asynchronous else "")
                + "def "
                + op["name"]
                + "(self"
                + (", *, " + ", ".join(args) if args else "")
                + ") -> Any:  # noqa: ANN401",
                '        """',
                "        " + op["summary"] + ".",
                "",
                "        Native symbols and caller-provided field values are preserved.",
                "        Source: " + op["source"],
            ]
            if "withdraw" in op["path"] and op["method"] == "POST":
                lines += [
                    "",
                    "        API withdrawals have no second confirmation; they execute on submit.",
                ]
            lines += ['        """']
            values = ", ".join(json.dumps(f["wire"]) + ": " + f["name"] for f in op["fields"])
            lines.append(
                "        return "
                + ("await " if asynchronous else "")
                + f"self._native_{('public' if op['public'] else 'private')}({op['name']!r}, "
                + '[(key, dumps(value, separators=(",", ":")) '
                + "if isinstance(value, (dict, list, bool)) else str(value)) "
                + f"for key, value in normalize_params({{{values}}}).items() if value is not None])"
            )
        write_python_wrappers("binance", asynchronous, "\n".join(lines) + "\n")
    print(f"Generated {len(specs)} operations.")


if __name__ == "__main__":
    raise SystemExit(run(main))
