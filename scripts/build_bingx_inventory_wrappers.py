"""Generate the remaining BingX REST wrappers from committed official request tables."""

import json
from pathlib import Path
from typing import Any

from scripts.build_bitget_inventory_wrappers import snake

ROOT = Path(__file__).resolve().parents[1]


def operation_name(op: dict[str, Any]) -> str:
    """Keep the API version explicit when it is a distinct route."""
    return snake(
        op["method"] + "_" + op["path"].removeprefix("/openApi/").lstrip("/").replace("/", "_")
    )


def field_kind(field: dict[str, Any]) -> str:
    """Map documented wire types, preserving financial decimals as strings."""
    value = field["type"].lower()
    if value in {"long", "int", "int64", "integer", "int32"}:
        return "int"
    if value in {"float64", "float", "double", "decimal"}:
        return "decimal"
    if value in {"array", "list"}:
        return "array"
    if value in {"boolean", "bool"}:
        return "bool"
    return "str"


def main() -> None:
    """Regenerate both Python clients and the native wrapper metadata."""
    operations = json.loads(
        (ROOT / "docs/official-endpoint-inventory/sources/bingx-operations.json").read_text(
            encoding="utf-8"
        )
    )
    specs = []
    for op in operations:
        fields = [
            {**f, "kind": field_kind(f)} for f in op["parameters"] if f["name"] != "timestamp"
        ]
        if op["path"].startswith("/api/lindorm/"):
            fields += [
                {"name": name, "kind": "str", "required": True}
                for name in ("access_token", "proxy_user")
            ]
        specs.append(
            {
                "name": operation_name(op),
                "method": op["method"],
                "path": op["path"],
                "signed": op["signed"],
                "fields": fields,
                "source": op["official_source"],
                "summary": op["title"],
                "scoped": op["path"].endswith("/allOpenOrders"),
            }
        )
    folder = ROOT / "crates/dcex/src/exchanges/bingx"
    (folder / "inventory_completion.json").write_text(
        json.dumps(specs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    groups = {True: [], False: []}
    for spec in specs:
        params = ", ".join(
            snake(f["name"]) + " => " + json.dumps(f["name"])
            for f in spec["fields"]
            if f["required"]
        )
        groups[spec["signed"]].append(f"        {spec['name']}({params}),")
    (folder / "inventory_wrappers.rs").write_text(
        "use "
        "super::BingxClient;\ncrate::exchanges::impl_exchange_method_wrappers! "
        "{\n    @extend; BingxClient;\n    public [\n"
        + "\n".join(groups[False])
        + "\n    ];\n    private [\n"
        + "\n".join(groups[True])
        + "\n    ];\n}\n",
        encoding="utf-8",
    )
    for asynchronous in [False, True]:
        lines = [
            '"""Additional BingX endpoints from the official request tables."""',
            "from typing import Any",
            "from dcex._operation_guards import require_scope",
            "from ._market_http import MarketHTTP",
            "",
            "class InventoryHTTP(MarketHTTP):",
            '    """Versioned market, copy-trading, agent and dual-currency methods."""',
        ]
        for spec in specs:
            fields = sorted(spec["fields"], key=lambda f: not f["required"])
            args = []
            for f in fields:
                annotation = {
                    "int": "int",
                    "bool": "bool",
                    "array": "list[Any]",
                    "str": "str",
                    "decimal": "str",
                }[f["kind"]]
                args.append(
                    snake(f["name"])
                    + ": "
                    + annotation
                    + ("" if f["required"] else " | None = None")
                )
            if spec["scoped"]:
                args.append("all_symbols: bool = False")
            lines += [
                "",
                "    "
                + ("async " if asynchronous else "")
                + "def "
                + spec["name"]
                + "(self"
                + (", *, " + ", ".join(args) if args else "")
                + ") -> Any:  # noqa: ANN401",
                '        """' + spec["summary"] + ".",
                "",
                "        Use native BingX symbols. "
                "Decimal fields are strings to preserve precision.",
                "        Source: " + spec["source"],
                '        """',
            ]
            if spec["scoped"]:
                lines.append("        require_scope(symbol, all_symbols)")
            values = ", ".join(json.dumps(f["name"]) + ": " + snake(f["name"]) for f in fields)
            if spec["scoped"]:
                values += ', "all_symbols": all_symbols'
            lines.append(
                "        return "
                + ("await " if asynchronous else "")
                + f"self._native_{'private' if spec['signed'] else 'public'}"
                + f"({spec['name']!r}, self._native_params(**{{{values}}}))"
            )
        folder = ROOT / ("dcex/async_support" if asynchronous else "dcex") / "bingx"
        (folder / "_inventory_http.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(specs)} endpoints.")


if __name__ == "__main__":
    main()
