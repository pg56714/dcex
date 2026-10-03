"""Preview verified transfers between the user's own wallets; execute only by explicit flag."""

import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal
from typing import Any
from uuid import uuid4

import pytest
from dotenv import load_dotenv

from scripts.live.accounts import Snapshot, clients_for, collect
from scripts.live.redaction import redact
from tests.stateful_adapters import response_data
from tests.stateful_runner import MARKETS


@dataclass(frozen=True)
class Route:
    """An exact same-user route; there is no recipient or subaccount parameter."""

    exchange: str
    source: str
    destination: str
    asset: str
    target: Decimal
    stage: str = "spot"


CAP = Decimal(20)
# Transfer quantity steps; amounts are only ever rounded down. USDT/USDC use 1e-6
# unless the exchange documents finer precision (Kraken accepts 1e-8).
STEPS = {"kraken": Decimal("0.00000001")}
DEFAULT_STEP = Decimal("0.000001")
# Skip once the destination meets the test minimum (not max(minimum, 20)); move at most 20.
NEED_ONLY = {"bybit"}
# Kraken internal transfers settle asynchronously: poll ~30s before giving up.
KRAKEN_CONFIRM_POLLS = 10
KRAKEN_CONFIRM_DELAY = 3.0
ROUTES = tuple(
    Route(exchange, source, destination, asset, CAP, stage)
    for exchange, source, destination, asset, stage in (
        ("binance", "funding_USDC", "spot_USDC", "USDC", "spot"),
        ("binance", "funding_USDT", "swap_USDT", "USDT", "perp"),
        ("bybit", "FUND", "UNIFIED", "USDT", "spot"),
        ("bybit", "FUND", "UNIFIED", "USDT", "perp"),
        ("mexc", "contract", "spot", "USDT", "spot"),
        ("mexc", "spot", "contract", "USDT", "perp"),
        ("kucoin", "main", "trade", "USDT", "spot"),
        ("kucoin", "futures", "trade", "USDT", "spot"),
        ("kucoin", "main", "futures", "USDT", "perp"),
        ("kucoin", "trade", "futures", "USDT", "perp"),
        ("bingx", "fund", "spot", "USDT", "spot"),
        ("bingx", "swap", "spot", "USDT", "spot"),
        ("bingx", "spot", "swap", "USDT", "perp"),
        ("hyperliquid", "spot", "perp", "USDC", "perp"),
        ("aster", "futures", "spot", "USDT", "spot"),
        ("aster", "spot", "futures", "USDT", "perp"),
        ("kraken", "flex_USDT", "spot_USDT", "USDT", "spot"),
        ("kraken", "spot_USDT", "flex_USDT", "USDT", "perp"),
    )
)


def round_down(exchange: str, amount: Decimal) -> Decimal:
    """Truncate to the exchange transfer step; never round up."""
    step = STEPS.get(exchange, DEFAULT_STEP)
    return amount if amount % step == 0 else amount.quantize(step, rounding=ROUND_DOWN)


def plan_transfers(
    exchange: str, snapshot: Snapshot, stage: str, *, remaining: Decimal = CAP
) -> tuple[list[tuple[Route, Decimal]], dict[str, Decimal]]:
    """Move at most 20 across all same-owner sources for one trading stage."""
    if stage not in {"spot", "perp"} or not remaining.is_finite() or not 0 <= remaining <= CAP:
        raise ValueError("Invalid funding stage or remaining cap")
    after = dict(snapshot.balances)
    if snapshot.blocked:
        return [], after
    if any(row["open_orders"] or row["positions"] for row in snapshot.markets):
        raise ValueError("Existing orders or positions: no funds will be moved")
    if any(
        not value.is_finite() or value < 0
        for value in (*after.values(), *snapshot.required.values())
    ):
        raise ValueError("Invalid balance or minimum requirement")
    transfers = []
    for route in ROUTES:
        if route.exchange != exchange or route.stage != stage:
            continue
        if route.destination not in snapshot.required:
            continue  # The destination's market is unavailable for order testing.
        if route.destination in snapshot.shared:
            continue  # Already funded by the shared wallet; a transfer would not credit it.
        required = snapshot.required[route.destination]
        current = after[route.destination]
        if exchange == "kraken" and stage == "perp":
            current = max(current, snapshot.balances.get("swap_USD", Decimal(0)))
        if current >= (required if exchange in NEED_ONLY else max(required, route.target)):
            continue
        amount = round_down(exchange, min(after[route.source], remaining))
        if amount > 0:
            after[route.source] -= amount
            after[route.destination] += amount
            transfers.append((route, amount))
            remaining -= amount
    return transfers, after


def submit_transfer(client: Any, route: Route, amount: Decimal) -> None:  # noqa: ANN401
    """Send exactly one allowlisted same-owner transfer; never retry ambiguous results."""
    if route not in ROUTES or not amount.is_finite() or amount <= 0 or amount > route.target:
        raise ValueError("Rejected non-allowlisted internal transfer")
    amount = round_down(route.exchange, amount)
    if amount <= 0:
        raise ValueError("Transfer amount rounds to zero")
    quantity = format(amount, "f")
    if route.exchange == "binance":
        data = response_data(
            "binance",
            client.create_universal_transfer(
                type_="FUNDING_MAIN" if route.stage == "spot" else "FUNDING_UMFUTURE",
                asset=route.asset,
                amount=quantity,
            ),
        )
        if not data["tranId"]:
            raise ValueError("Binance transfer has no acknowledgement ID; do not retry")
    elif route.exchange == "bybit":
        data = response_data(
            "bybit",
            client.create_internal_transfer(
                coin="USDT",
                amount=quantity,
                fromAccountType="FUND",
                toAccountType="UNIFIED",
                transferId=str(uuid4()),
            ),
        )
        if data["status"] != "SUCCESS":
            raise ValueError("Bybit transfer not confirmed; do not retry")
    elif route.exchange == "kraken":
        if route.stage == "spot":
            data = response_data(
                "kraken",
                client.withdraw_futures_to_spot_wallet(
                    amount=quantity,
                    currency="usdt",
                    sourceWallet="flex",
                ),
            )
            if data["result"] != "success" or not data["uid"]:
                raise ValueError("Kraken internal withdrawal not acknowledged; do not retry")
        else:
            data = response_data(
                "kraken",
                client.wallet_transfer_to_futures(
                    asset="USDT",
                    amount=quantity,
                    from_="Spot Wallet",
                    to="Futures Wallet",
                ),
            )
            if not data["refid"]:
                raise ValueError("Kraken wallet transfer not acknowledged; do not retry")
    elif route.exchange == "mexc":
        data = response_data(
            "mexc",
            client.user_universal_transfer(
                fromAccountType="FUTURES" if route.source == "contract" else "SPOT",
                toAccountType="SPOT" if route.destination == "spot" else "FUTURES",
                asset="USDT",
                amount=quantity,
            ),
        )
        if not data["tranId"]:
            raise ValueError("MEXC transfer has no acknowledgement ID")
    elif route.exchange == "kucoin":
        data = response_data(
            "kucoin",
            client.flex_transfer(
                currency="USDT",
                amount=quantity,
                fromAccountType={"main": "MAIN", "trade": "TRADE", "futures": "CONTRACT"}[
                    route.source
                ],
                toAccountType="TRADE" if route.destination == "trade" else "CONTRACT",
                transfer_type="INTERNAL",
                clientOid=str(uuid4()),
            ),
        )
        if not data["orderId"]:
            raise ValueError("KuCoin transfer has no acknowledgement ID")
    elif route.exchange == "bingx":
        data = response_data(
            "bingx",
            client.asset_transfer(
                from_account={"fund": "fund", "spot": "spot", "swap": "USDTMPerp"}[route.source],
                to_account="spot" if route.destination == "spot" else "USDTMPerp",
                asset="USDT",
                amount=quantity,
            ),
        )
        if not data["tranId"]:
            raise ValueError("BingX transfer has no acknowledgement ID; do not retry")
    elif route.exchange == "aster":
        data = response_data(
            "aster",
            client.transfer_spot_futures(
                amount=quantity,
                asset="USDT",
                clientTranId=uuid4().hex,
                kindType="FUTURE_SPOT" if route.stage == "spot" else "SPOT_FUTURE",
                market="futures",
            ),
        )
        if not data["tranId"]:
            raise ValueError("Aster transfer has no acknowledgement ID")
    elif route.exchange == "hyperliquid":
        destination = client.wallet_address
        role = client.user_role(user=destination)
        if not isinstance(role, dict) or role.get("role") != "user":
            raise ValueError("Hyperliquid funding requires the owner wallet, not an API agent")
        owner = role.get("data", {}).get("user", destination)
        if not isinstance(destination, str) or not destination or owner != destination:
            raise ValueError("Hyperliquid transfer destination does not match the resolved owner")
        # agentSendAsset requires tokenName:tokenId, never a guessed symbol alone.
        tokens = [row for row in client.get_spot_meta()["tokens"] if row["name"] == "USDC"]
        if len(tokens) != 1 or not re.fullmatch(r"0x[0-9a-fA-F]{32}", tokens[0]["tokenId"]):
            raise ValueError("Hyperliquid USDC token metadata is missing or ambiguous")
        data = client.transfer_between_dexes(
            source_dex="spot",
            destination_dex="",
            token="USDC:" + tokens[0]["tokenId"],
            amount=quantity,
        )
        if data["status"] != "ok":
            raise ValueError("Hyperliquid transfer rejected")
    else:
        raise ValueError("Unsupported internal route")


async def prepare(
    exchange: str, clients: list[tuple[Any, str, str]], *, stage: str, execute: bool = False
) -> dict[str, Any]:
    """Preview first; re-read all prerequisites before each permitted transfer."""
    snapshot = await collect(exchange, clients)
    transfers, after = plan_transfers(exchange, snapshot, stage)
    manual = exchange == "kraken" and not callable(
        getattr(
            clients[0][0] if clients else None,
            "withdraw_futures_to_spot_wallet" if stage == "spot" else "wallet_transfer_to_futures",
            None,
        )
    )
    if manual:
        transfers, after = [], dict(snapshot.balances)
    report: dict[str, Any] = {
        "exchange": exchange,
        "stage": stage,
        "mode": "execute" if execute else "preview",
        "balances": {k: str(v) for k, v in snapshot.balances.items()},
        "markets": snapshot.markets,
        "proposed": [
            {"source": r.source, "destination": r.destination, "asset": r.asset, "amount": str(q)}
            for r, q in transfers
        ],
        "expected_balances": {k: str(v) for k, v in after.items()},
        "blocked": snapshot.blocked,
        "unavailable": snapshot.unavailable,
        "executed": [],
        "notes": [],
    }
    report["notes"].extend(snapshot.shared.values())
    if manual:
        report["notes"].append(
            "需手動 / Manual funding required: "
            "official Kraken internal wallet endpoint is unavailable"
        )
    elif not transfers:
        report["notes"].append(
            "Shared wallet, sufficient destination, or no available stage source"
        )
    if execute and snapshot.blocked:
        raise ValueError("; ".join(snapshot.blocked))
    if execute:
        remaining = CAP
        for route, amount in transfers:
            fresh = await collect(exchange, clients)
            eligible, _ = plan_transfers(exchange, fresh, stage, remaining=remaining)
            # Small upward drift (e.g. lend interest) is fine; never send more than previewed.
            if not any(r == route and q >= amount for r, q in eligible):
                raise ValueError("Balances/minima changed: stop and preview again")
            submit_transfer(clients[0][0], route, amount)
            remaining -= amount
            report["executed"].append(
                {
                    "source": route.source,
                    "destination": route.destination,
                    "asset": route.asset,
                    "amount": str(amount),
                }
            )
            await confirm_transfer(exchange, clients, route, amount, fresh, report)
        snapshot = await collect(exchange, clients)
    report["fund_locations"] = fund_locations(exchange, snapshot)
    return report


async def confirm_transfer(
    exchange: str,
    clients: list[tuple[Any, str, str]],
    route: Route,
    amount: Decimal,
    fresh: Snapshot,
    report: dict[str, Any],
) -> None:
    """Re-read balances (Kraken: short poll) and never send another transfer."""
    polls = KRAKEN_CONFIRM_POLLS if exchange == "kraken" else 1
    zero = Decimal(0)
    for attempt in range(polls):
        if attempt:
            await asyncio.sleep(KRAKEN_CONFIRM_DELAY)
        confirmed = await collect(exchange, clients)
        arrived = (
            confirmed.balances[route.destination] >= fresh.balances[route.destination] + amount
        )
        debited = confirmed.balances[route.source] <= fresh.balances[route.source] - amount
        if arrived and debited:
            return
        if (
            exchange == "kraken"
            and route.destination == "flex_USDT"
            and confirmed.balances.get("cash_USDT", zero)
            >= fresh.balances.get("cash_USDT", zero) + amount
        ):
            message = (
                f"Kraken credited {amount} USDT to futures cash_USDT, not flex_USDT. "
                "Manual action: move USDT cash -> flex in the Kraken UI; do not retry"
            )
            report["notes"].append(message)
            raise ValueError(message)
    if not arrived:
        raise ValueError(
            "Transfer acknowledged but destination balance not confirmed; do not retry"
        )
    raise ValueError("Transfer source balance not confirmed; do not retry")


def fund_locations(exchange: str, snapshot: Snapshot) -> list[dict[str, str]]:
    """Report observed available balances, never the projected transfer result."""
    assets = {r.source: r.asset for r in ROUTES if r.exchange == exchange}
    assets.update({r.destination: r.asset for r in ROUTES if r.exchange == exchange})
    assets.update(snapshot.assets)
    return [
        {
            "exchange": exchange,
            "account": account,
            "asset": assets.get(account, "unknown"),
            "amount": str(amount),
            "basis": "available margin (USD)"
            if exchange == "kraken" and account.startswith("swap_")
            else "available balance",
        }
        for account, amount in sorted(snapshot.balances.items())
    ]


async def run_cli(exchange: str | None, execute: bool, stage: str) -> int:
    """Print sanitized summaries without raw account payloads or tracebacks."""
    load_dotenv()
    failed = False
    locations = []
    for name in [exchange] if exchange else list(MARKETS):
        try:
            async with clients_for(name) as clients:
                try:
                    report = await prepare(name, clients, stage=stage, execute=execute)
                except (Exception, pytest.skip.Exception):
                    # One final read reports partially moved funds; never retry a transfer.
                    try:
                        observed = await collect(name, clients)
                        locations.extend(fund_locations(name, observed))
                    except (Exception, pytest.skip.Exception):
                        locations.append(
                            {
                                "exchange": name,
                                "account": "unknown",
                                "asset": "unknown",
                                "amount": "unknown",
                                "basis": "final read failed; manual check required",
                            }
                        )
                    raise
            locations.extend(report["fund_locations"])
            print(json.dumps(report, ensure_ascii=False))
            failed |= bool(report["blocked"])
        except (Exception, pytest.skip.Exception) as error:
            failed = True
            print(json.dumps({"exchange": name, "status": "blocked", "reason": redact(error)}))
    print("Current fund locations / 目前資金位置 (no restore)")
    print("Exchange | Account | Asset | Available amount | Basis")
    for row in locations:
        print(" | ".join(row[key] for key in ("exchange", "account", "asset", "amount", "basis")))
    return int(failed)


def main() -> int:
    """Parse an explicit exchange selection and optional execution flag."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exchange", choices=sorted(MARKETS))
    parser.add_argument("--stage", choices=("spot", "perp"), required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    return asyncio.run(run_cli(args.exchange, args.execute, args.stage))


if __name__ == "__main__":
    raise SystemExit(main())
