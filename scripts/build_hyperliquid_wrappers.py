"""Generate named HIP and administrative action methods from reviewed action schemas."""

import json
from pathlib import Path

from scripts.wrapper_codegen import write_python_wrappers, write_rust_wrappers, write_schemas

CONFIRMED = {"perp_deploy_disable_dex", "convert_to_multi_sig_user_signed"}
ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    specs = json.loads(
        (ROOT / "docs/official-endpoint-inventory/sources/hyperliquid-actions.json").read_text(
            encoding="utf-8"
        )
    )
    metadata = [{k: v for k, v in op.items() if k != "sample"} for op in specs]
    write_schemas("hyperliquid", metadata)
    groups = {True: [], False: []}
    for op in specs:
        if op["public"]:
            args = 'user => "user"' if op["user"] else ""
        else:
            args = 'action => "action"'
            if op["signed"]:
                args += ', nonce => "nonce", signature => "signature"'
        if op["name"] in CONFIRMED:
            args += ', confirm => "confirm"'
        groups[op["public"]].append(f"        {op['name']}({args}),")
    write_rust_wrappers(
        "hyperliquid",
        "use super::HyperliquidClient;\n"
        "crate::exchanges::impl_exchange_method_wrappers! {\n"
        "    @extend; HyperliquidClient;\n"
        "    public [\n"
        + "\n".join(groups[True])
        + "\n    ];\n    private [\n"
        + "\n".join(groups[False])
        + "\n    ];\n}\n",
    )
    for asynchronous in (False, True):
        lines = [
            '"""Named HIP deployer and administrative action methods."""',
            "from typing import Any",
            "from dcex._operation_guards import require_confirmation",
            "from ._trade_http import TradeHTTP",
            "",
            "class GeneratedMethods(TradeHTTP):",
            '    """Methods preserve action field order and caller-signed envelopes."""',
        ]
        for op in specs:
            if op["public"]:
                args = ", *, user: str" if op["user"] else ""
                params = "user=user" if op["user"] else ""
                summary = "Query " + op["type"]
            else:
                args = ", *, action: dict[str, Any]"
                params = (
                    "action=action, nonce=nonce, vaultAddress=vault_address, "
                    "expiresAfter=expires_after"
                )
                if op["signed"]:
                    args += ", nonce: int, signature: dict[str, str | int]"
                    params += ", signature=signature"
                else:
                    args += ", nonce: int | None = None"
                args += ", vault_address: str | None = None, expires_after: int | None = None"
                summary = "Submit " + op["type"] + ("/" + op["variant"] if op["variant"] else "")
            if op["name"] in CONFIRMED:
                args += ", confirm: bool = False"
                params += ", confirm=confirm"
            lines += [
                "",
                "    "
                + ("async " if asynchronous else "")
                + "def "
                + op["name"]
                + "(self"
                + args
                + ") -> Any:  # noqa: ANN401",
                '        """',
                "        " + summary + ".",
                "",
                "        Source: " + op["source"],
            ]
            if not op["public"]:
                lines += [
                    "        Supply the complete documented action; field order is preserved.",
                    "        "
                    + (
                        "The signature must already cover the supplied action and envelope."
                        if op["signed"]
                        else "The native client signs the action with its configured private key."
                    ),
                    "        Tuple lists must be sorted before submission, as required by the API.",
                ]
            if op.get("testnet_only"):
                lines += ["        This action is documented for testnet only."]
            if op["name"] in CONFIRMED:
                lines += [
                    "        This irreversible account operation requires confirm=True.",
                    '        """',
                    "        require_confirmation(confirm)",
                ]
            else:
                lines += ['        """']
            lines += [
                "        return "
                + ("await " if asynchronous else "")
                + f"self._native_{('public' if op['public'] else 'private')}"
                + f"({op['name']!r}, self._native_params({params}))"
            ]
        write_python_wrappers("hyperliquid", asynchronous, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
