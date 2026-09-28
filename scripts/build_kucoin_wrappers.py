"""Generate KuCoin affiliate, broker and copy-trading methods from official schemas."""

import json
from pathlib import Path
from typing import Any

from scripts.build_bitget_wrappers import snake
from scripts.wrapper_codegen import write_python_wrappers, write_rust_wrappers, write_schemas

ROOT = Path(__file__).resolve().parents[1]


def operation_name(op: dict[str, Any]) -> str:
    """Derive a stable method name from the documented route."""
    return snake(
        op["method"]
        + "_"
        + op["path"]
        .removeprefix("/api/")
        .replace("/", "_")
        .replace("{", "")
        .replace("}", "")
        .replace("-", "_")
    )


def fields(op: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect typed path, query and request-body fields."""
    result = []
    for location in ("path", "query"):
        result.extend(
            {
                "name": f["name"],
                "required": f["required"],
                "location": location,
                "schema": f.get("schema") or {"type": f["type"]},
            }
            for f in op["parameters"][location]
        )
    body = op["requestBody"].get("jsonSchema", {})
    if "$ref" in body:
        result.append(
            {"name": "body", "required": True, "location": "raw_body", "schema": {"type": "object"}}
        )
    else:
        for name, schema in body.get("properties", {}).items():
            required = name in body.get("required", [])
            if name in {"frontPhoto", "backendPhoto"}:
                required = False
            result.append(
                {"name": name, "required": required, "location": "body", "schema": schema}
            )
    return result


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    ops = json.loads(
        (ROOT / "docs/official-endpoint-inventory/sources/kucoin-operations.json").read_text(
            encoding="utf-8"
        )
    )
    specs = [
        {
            "name": operation_name(op),
            "method": op["method"].upper(),
            "path": op["path"],
            "market": op["customApiFields"]["10"].lower(),
            "fields": fields(op),
            "json_body": op["requestBody"]["type"] == "application/json",
            "source": op["official_source"],
            "summary": op["name"],
            "withdrawal": "withdrawal" in op["path"],
            "confirm": op["method"] == "delete" and "apikey" in op["path"],
        }
        for op in ops
    ]
    write_schemas("kucoin", specs)
    lines = []
    for op in specs:
        if op["withdrawal"]:
            lines.append(
                "        /// API withdrawals have no second confirmation; they execute on submit."
            )
        args = ", ".join(
            snake(f["name"]) + " => " + json.dumps(f["name"]) for f in op["fields"] if f["required"]
        )
        lines.append(f"        {op['name']}({args}),")
    write_rust_wrappers(
        "kucoin",
        "use super::KucoinClient;\n"
        "crate::exchanges::impl_exchange_method_wrappers! {\n"
        "    @extend; KucoinClient;\n"
        "    public [];\n"
        "    private [\n" + "\n".join(lines) + "\n    ];\n}\n",
    )
    for asynchronous in (False, True):
        lines = [
            '"""Official KuCoin affiliate, broker and copy-trading methods."""',
            "from typing import Any",
            "from ._trade_http import TradeHTTP",
            "",
            "class GeneratedMethods(TradeHTTP):",
            '    """Preserve native symbols and documented wire field types."""',
        ]
        for op in specs:
            args = []
            for f in op["fields"]:
                annotation = {
                    "integer": "int",
                    "number": "str",
                    "boolean": "bool",
                    "array": "list[Any]",
                    "object": "dict[str, Any]",
                }.get(f["schema"].get("type"), "str")
                args.append(
                    snake(f["name"])
                    + ": "
                    + annotation
                    + ("" if f["required"] else " | None = None")
                )
            if op["confirm"]:
                args.append("confirm: bool = False")
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
                "        Source: " + op["source"],
            ]
            if op["market"] == "broker":
                lines += ["        Uses the Broker host and the configured ND management API key."]
            if op["withdrawal"]:
                lines += [
                    "        API withdrawals have no second confirmation; they execute on submit.",
                    "        This Fast API may return validation factors; "
                    "submit them only if required",
                    "        by the exchange. The incomplete official schema is forwarded as "
                    "a body object.",
                ]
            params = ", ".join(f["name"] + "=" + snake(f["name"]) for f in op["fields"])
            if op["confirm"]:
                params += ", confirm=confirm"
            lines += [
                '        """',
                "        return "
                + ("await " if asynchronous else "")
                + f"self._native_private({op['name']!r}, self._native_params({params}))",
            ]
        write_python_wrappers("kucoin", asynchronous, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
