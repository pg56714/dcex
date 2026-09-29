"""
Generate independent signatures with the official hyperliquid-python-sdk package.

Run in an isolated environment with ``uv run --no-sync --with hyperliquid-python-sdk
python -m scripts.build_hyperliquid_action_vectors --write``. The fixture records the
installed SDK version; normal tests do not import or install the SDK.
"""

import copy
import json
from importlib.metadata import version
from pathlib import Path

# These optional SDK dependencies belong only to the isolated generation environment above.
import msgpack  # pyright: ignore[reportMissingImports]
from eth_account import Account  # pyright: ignore[reportMissingImports]
from hyperliquid.utils.signing import (  # pyright: ignore[reportMissingImports]
    sign_convert_to_multi_sig_user_action,
    sign_l1_action,
    sign_multi_sig_action,
)

from scripts.generation import emit, run

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY = "0x" + "11" * 32
NONCE = 1700000000123
VAULT = "0x" + "22" * 20
EXPIRY = 1900000000000


def main() -> None:
    """Regenerate the committed artifacts from the documented source data."""
    specs = json.loads(
        (ROOT / "docs/official-endpoint-inventory/sources/hyperliquid-actions.json").read_text(
            encoding="utf-8"
        )
    )
    wallet = Account.from_key(PRIVATE_KEY)
    cases = []
    for op in specs:
        if op["public"]:
            continue
        for mainnet in (False, True):
            if mainnet and op["testnet_only"]:
                continue
            action = copy.deepcopy(op["sample"])
            if op["type"] == "convertToMultiSigUser":
                signature = sign_convert_to_multi_sig_user_action(wallet, action, mainnet)
            elif op["type"] == "multiSig":
                signature = sign_multi_sig_action(wallet, action, mainnet, VAULT, NONCE, EXPIRY)
            else:
                signature = sign_l1_action(wallet, action, VAULT, NONCE, EXPIRY, mainnet)
            signature = {
                key: ("0x" + value[2:].zfill(64) if key in {"r", "s"} else value)
                for key, value in signature.items()
            }
            cases.append(
                {
                    "name": op["name"],
                    "action": action,
                    "nonce": NONCE,
                    "signature": signature,
                    "vault_address": VAULT,
                    "expires_after": EXPIRY,
                    "mainnet": mainnet,
                    "caller_signed": op["signed"],
                    "msgpack_hex": msgpack.packb(action).hex(),
                }
            )
    output = {
        "source": "https://github.com/hyperliquid-dex/hyperliquid-python-sdk",
        "sdk_version": version("hyperliquid-python-sdk"),
        "private_key": PRIVATE_KEY,
        "wallet_address": wallet.address,
        "cases": cases,
    }
    emit(
        ROOT / "tests/fixtures/signing/hyperliquid_actions.json",
        json.dumps(output, indent=2) + "\n",
    )


if __name__ == "__main__":
    raise SystemExit(run(main))
