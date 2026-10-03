"""Read-only summary of tested markets, open orders, positions and quote balances."""

import argparse
import asyncio
import json
from dataclasses import asdict

import pytest
from dotenv import load_dotenv

from scripts.live.accounts import clients_for, collect
from scripts.live.redaction import redact
from tests.stateful_runner import MARKETS


async def run_cli(exchange: str | None) -> int:
    """Read every selected market; nonzero exit means dirty, blocked or failed."""
    load_dotenv()
    failed = False
    for name in [exchange] if exchange else list(MARKETS):
        try:
            async with clients_for(name) as clients:
                snapshot = await collect(name, clients)
            data = asdict(snapshot)
            data["exchange"] = name
            data["balances"] = {key: str(value) for key, value in snapshot.balances.items()}
            data["required"] = {key: str(value) for key, value in snapshot.required.items()}
            failed |= bool(snapshot.blocked) or any(
                row["status"] == "dirty" for row in snapshot.markets
            )
            print(json.dumps(data, ensure_ascii=False))
        except (Exception, pytest.skip.Exception) as error:
            failed = True
            print(json.dumps({"exchange": name, "status": "blocked", "reason": redact(error)}))
    return int(failed)


def main() -> int:
    """Parse exchange selection; this tool intentionally has no execution option."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exchange", choices=sorted(MARKETS))
    args = parser.parse_args()
    return asyncio.run(run_cli(args.exchange))


if __name__ == "__main__":
    raise SystemExit(main())
