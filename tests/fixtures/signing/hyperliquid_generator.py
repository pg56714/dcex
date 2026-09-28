import json
import subprocess

import msgpack
from eth_account import Account
from hyperliquid.utils.signing import action_hash, sign_l1_action

key = "0x" + "11" * 32
wallet = Account.from_key(key)
nonce = 1700000000123
cases = []
for action in [
    dict(type="vaultTransfer", vaultAddress="0x" + "22" * 20, isDeposit=True, usd=1234567),
    dict(type="subAccountTransfer", subAccountUser="0x" + "33" * 20, isDeposit=False, usd=1000000),
    dict(
        type="order",
        orders=[dict(a=0, b=True, p="100", s="1", r=False, t=dict(limit=dict(tif="Gtc")))],
        grouping="na",
    ),
    dict(type="cancel", cancels=[dict(a=0, o=42)]),
]:
    for mainnet, vault, expires in [(True, None, None), (False, "0x" + "44" * 20, 1700000060123)]:
        cases.append(
            dict(
                action=action,
                nonce=nonce,
                vault_address=vault,
                expires_after=expires,
                is_mainnet=mainnet,
                msgpack_hex=msgpack.packb(action).hex(),
                action_hash=action_hash(action, vault, nonce, expires).hex(),
                signature=sign_l1_action(wallet, action, vault, nonce, expires, mainnet),
            )
        )
print(
    json.dumps(
        dict(
            source="https://github.com/hyperliquid-dex/hyperliquid-python-sdk",
            commit=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            private_key=key,
            cases=cases,
        ),
        indent=2,
    )
)
