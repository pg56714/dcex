"""Generate additional Binance wrappers from the committed official SDK inventory."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def wire_name(name: str) -> str:
    """Use the SDK's snake-to-camel field mapping."""
    first, *parts = name.rstrip("_").split("_")
    return first + "".join(p[:1].upper() + p[1:] for p in parts)


def operation_name(op: dict[str, Any]) -> str:
    """Disambiguate separate Alpha and prediction API namespaces."""
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
    ledger = json.loads((ROOT / "docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
    paths = {
        r["path"]
        for r in ledger["rows"]
        if r["exchange"] == "binance"
        and r["kind"] == "REST"
        and (r["status"] == "pending" or "binance/inventory_completion.rs" in r.get("evidence", []))
    }
    inventory = json.loads(
        (ROOT / "docs/official-endpoint-inventory/binance.json").read_text(encoding="utf-8")
    )["endpoints"]
    specs = []
    for op in inventory:
        if op["path"] not in paths or op["method"] == "WS":
            continue
        path = op["path"]
        # Public SDK methods omit is_signed for some USER_DATA endpoints. The
        # documented security type is authoritative; only these market routes are public.
        public = (
            path.startswith("/bapi/")
            or path in {"/sapi/v1/mining/pub/algoList", "/sapi/v1/mining/pub/coinList"}
            or "/prediction/market/" in path
            or "/prediction/category/" in path
            or "/prediction/order-book" in path
        )
        fields = [
            {**f, "wire": wire_name(f["name"]), "kind": field_kind(f)} for f in op["parameters"]
        ]
        specs.append(
            {
                "name": operation_name(op),
                "method": op["method"],
                "path": path,
                "public": public,
                "fields": fields,
                "json_body": path in {"/sapi/v1/fiat/deposit", "/sapi/v2/fiat/withdraw"},
                "source": op["official_source"],
                "summary": op["doc"].strip().splitlines()[0].strip(),
            }
        )
    target = ROOT / "crates/dcex/src/exchanges/binance"
    (target / "inventory_completion.json").write_text(
        json.dumps(specs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
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
    (target / "inventory_wrappers.rs").write_text(
        "use "
        "super::BinanceClient;\ncrate::exchanges::impl_exchange_method_wrappers! "
        "{\n    @extend; BinanceClient;\n    public [\n"
        + "\n".join(groups[True])
        + "\n    ];\n    private [\n"
        + "\n".join(groups[False])
        + "\n    ];\n}\n",
        encoding="utf-8",
    )
    for asynchronous in (False, True):
        lines = [
            '"""Additional Binance endpoints from the official SDK request tables."""',
            "from typing import Any",
            "from json import dumps",
            "from ._market_http import MarketHTTP",
            "from ._trade_http import TradeHTTP",
            "",
            "class InventoryHTTP(MarketHTTP, TradeHTTP):",
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
                + f"self._native_{'public' if op['public'] else 'private'}({op['name']!r}, "
                + '[(key, dumps(value, separators=(",", ":")) '
                + "if isinstance(value, (dict, list, bool)) else str(value)) "
                + f"for key, value in {{{values}}}.items() if value is not None])"
            )
        (
            ROOT / ("dcex/async_support" if asynchronous else "dcex") / "binance/_inventory_http.py"
        ).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(specs)} operations.")


if __name__ == "__main__":
    main()
