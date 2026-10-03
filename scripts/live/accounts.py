"""Read-only account snapshots for the locally executed test preparation tools."""

import importlib
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from scripts.live.redaction import redact
from tests.stateful_adapters import CexAdapter, balance
from tests.stateful_arcus import ARCUS_SPOT_NA
from tests.stateful_lifecycle import MarketUnavailable, decimal
from tests.stateful_runner import ADAPTERS, MARKETS, client_options


@dataclass
class Snapshot:
    """Only balances, minimum requirements and redacted market summaries."""

    balances: dict[str, Decimal] = field(default_factory=dict)
    required: dict[str, Decimal] = field(default_factory=dict)
    markets: list[dict[str, Any]] = field(default_factory=list)
    blocked: list[str] = field(default_factory=list)
    assets: dict[str, str] = field(default_factory=dict)
    # Markets that cannot run the order lifecycle; still read and reported, never funded.
    unavailable: list[str] = field(default_factory=list)
    # Destination accounts funded by another wallet's balance (no transfer needed), with a note.
    shared: dict[str, str] = field(default_factory=dict)


def account_name(exchange: str, market: str, symbol: str) -> str:
    """Map tested markets onto their actual shared or separate trading wallets."""
    if exchange in {"bybit", "okx", "bitget", "backpack", "extended"}:
        return {
            "bybit": "UNIFIED",
            "okx": "trading",
            "bitget": "UTA",
            "backpack": "trading",
            "extended": "trading",
        }[exchange]
    if exchange == "kucoin":
        return "trade" if market == "spot" else "futures"
    if exchange == "mexc":
        return "spot" if market == "spot" else "contract"
    if exchange == "aster":
        return "spot" if market == "spot" else "futures"
    if exchange in {"hyperliquid", "ondo", "arcus"}:
        return "spot" if market == "spot" else "perp"
    if exchange in {"binance", "kraken"}:
        return market + "_" + symbol.split("-")[1]
    return market


@asynccontextmanager
async def clients_for(exchange: str):  # noqa: ANN201
    """Construct clients only inside an explicitly invoked local CLI operation."""
    opened = []
    try:
        cls = importlib.import_module("dcex." + exchange + ".client").Client
        if exchange == "arcus":
            options = client_options(exchange)
            client = cls(**options)
            opened.append(client)
            spot_cls = importlib.import_module("dcex.arcus.spot").SpotClient
            spot = spot_cls(
                wallet_address=options["address"],
                logger=options["logger"],
                timeout=20,
            )
            opened.append(spot)
            clients = [(spot, "spot", ""), (client, "swap", "BTC-USD")]
        elif exchange == "lighter":
            logger = logging.Logger("account-tools-no-payload-logging")
            logger.disabled = True
            clients = []
            for market, symbol in MARKETS[exchange]:
                client = cls.from_env(network=market, preload_product_table=False, logger=logger)
                opened.append(client)
                clients.append((client, market, symbol))
        else:
            client = cls(**client_options(exchange))
            opened.append(client)
            clients = [(client, market, symbol) for market, symbol in MARKETS[exchange]]
        yield clients
    finally:
        for client in reversed(opened):
            client.close()


async def collect(exchange: str, clients: list[tuple[Any, str, str]]) -> Snapshot:
    """Read only; never create, cancel, transfer, or change account settings."""
    snapshot = Snapshot()
    for client, market, symbol in clients:
        if exchange == "arcus" and market == "spot":
            data = client.get_balances(include_wrapped=False)
            amounts = [
                decimal(row["balance"]) / Decimal(10) ** int(row["decimals"])
                for row in data["balances"]
                if row.get("symbol") == "USDG"
            ]
            available = sum(amounts, Decimal(0))
            snapshot.balances["spot"] = available
            snapshot.assets["spot"] = "USDG"
            snapshot.markets.append(
                {
                    "market": "spot",
                    "account": "spot",
                    "available": str(available),
                    "status": "N/A",
                    "skip_reason": ARCUS_SPOT_NA,
                    "open_orders": [],
                    "positions": [],
                }
            )
            continue
        adapter = ADAPTERS.get(exchange, CexAdapter)(client, exchange, market, symbol)
        account = account_name(exchange, market, symbol)
        try:
            positions = await adapter.positions()
            orders = await adapter.open_orders()
        except MarketUnavailable as error:
            snapshot.blocked.append(redact(error))
            continue
        try:
            plan, available = await adapter.prepare()
        except MarketUnavailable as error:
            # Unavailable for order testing only: its balance, orders and positions are still
            # read and reported, and it never blocks transfers needed by the other stage.
            plan, available, reason = None, await adapter.available(), redact(error)
            snapshot.unavailable.append(reason)
        snapshot.balances[account] = available
        snapshot.assets[account] = (
            "USDG"
            if exchange == "arcus" or (exchange == "lighter" and market == "robinhood")
            else "USDC"
            if exchange in {"hyperliquid", "lighter"}
            else symbol.split("-")[1]
        )
        if plan is not None:
            # Serial tests share the same collateral: reserve the larger requirement,
            # not the sum of two orders that will never be open together.
            snapshot.required[account] = max(
                snapshot.required.get(account, Decimal(0)), plan.notional
            )
        allowed = (
            "orderId",
            "ordId",
            "id",
            "oid",
            "order_index",
            "symbol",
            "instId",
            "market",
            "side",
            "size",
            "pos",
            "positionAmt",
            "currentQty",
            "netQuantity",
            "coin",
            "szi",
            "position",
            "market_index",
        )
        snapshot.markets.append(
            {
                "market": market,
                "symbol": symbol,
                "account": account,
                "available": str(available),
                "minimum_order": "N/A" if plan is None else str(plan.notional),
                "open_orders": [
                    {key: redact(row[key]) for key in allowed if key in row} for row in orders
                ],
                "positions": [
                    {
                        key: redact(item[key])
                        for key in allowed
                        if key in item and not isinstance(item[key], (dict, list))
                    }
                    for row in positions
                    for item in [
                        row.get("position", row) if isinstance(row.get("position"), dict) else row
                    ]
                ],
                "status": "dirty"
                if orders or positions
                else "unavailable"
                if plan is None
                else "insufficient"
                if available < plan.notional
                else "clean",
                **({"skip_reason": reason} if plan is None else {}),
            }
        )
    if not clients or exchange == "arcus":
        return snapshot
    client, market, symbol = clients[0]
    adapter = ADAPTERS.get(exchange, CexAdapter)(client, exchange, market, symbol)
    if exchange == "binance":
        data = await adapter.call("get_funding_wallet")
        for asset in ("USDC", "USDT"):
            account = "funding_" + asset
            snapshot.balances[account] = balance(data, asset, "asset", "free")
            snapshot.assets[account] = asset
    elif exchange == "bybit":
        data = await adapter.call("get_coin_balance", accountType="FUND", coin="USDT")
        snapshot.balances["FUND"] = decimal(data["balance"]["transferBalance"])
        snapshot.assets["FUND"] = "USDT"
    elif exchange == "kucoin":
        data = await adapter.call("get_account_balance", currency="USDT", type="main")
        snapshot.balances["main"] = balance(data, "USDT", "currency", "available")
        snapshot.assets["main"] = "USDT"
    elif exchange == "bingx":
        data = await adapter.call("get_fund_account_balance")
        snapshot.balances["fund"] = balance(data["assets"], "USDT", "asset", "free")
        snapshot.assets["fund"] = "USDT"
    elif exchange == "kraken":
        accounts = (await adapter.call("get_futures_accounts"))["accounts"]
        currencies = accounts["flex"]["currencies"]
        # The official per-currency available field is a token amount; availableMargin is not.
        snapshot.balances["flex_USDT"] = (
            decimal(currencies["USDT"]["available"]) if "USDT" in currencies else Decimal(0)
        )
        snapshot.balances["cash_USDT"] = decimal(
            accounts.get("cash", {}).get("balances", {}).get("usdt", "0")
        )
        snapshot.assets.update(flex_USDT="USDT", cash_USDT="USDT")
        if "swap_USD" in snapshot.required:
            snapshot.required["flex_USDT"] = snapshot.required["swap_USD"]
    elif exchange == "hyperliquid" and await adapter.unified():
        snapshot.shared["perp"] = "unified account: spot USDC is perp collateral"
    return snapshot
