"""
Live WebSocket smoke: public market streams and private log-in plus subscribe only.

Nothing is ordered, cancelled or changed. Private streams reuse the stateful harness's
``stream_spec`` (the same connect and subscribe calls) without its order lifecycle.
Some private streams need a short-lived listen key or token first; the client closes
it again. Only frame kinds (event names or key names) are recorded, never values.
"""

import argparse
import asyncio
import importlib
import inspect
import json
import logging
import os
import re
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from scripts.live.redaction import redact
from scripts.live.smoke_public import EXCHANGES

WAIT_SECONDS = 20.0
CLOSE_SECONDS = 10.0

# One liquid market stream per exchange and market: (label, factory kwargs, subscribe).
Subscribe = Callable[[Any], Awaitable[object]]
PUBLIC: dict[str, list[tuple[str, dict[str, Any], Subscribe]]] = {
    "arcus": [("swap", {}, lambda c: c.subscribe_orderbook("BTC-USD"))],
    "aster": [
        ("spot", {"market": "spot"}, lambda c: c.subscribe_book_ticker("BTC-USDT-SPOT")),
        ("swap", {"market": "futures"}, lambda c: c.subscribe_book_ticker("BTC-USDT-SWAP")),
    ],
    "backpack": [("spot", {}, lambda c: c.subscribe_book_ticker("SOL-USDC-SPOT"))],
    "binance": [
        ("spot", {}, lambda c: c.subscribe_ticker("BTC-USDT-SPOT")),
        ("swap", {"profile": "futures_market"}, lambda c: c.subscribe_ticker("BTC-USDT-SWAP")),
    ],
    "bingx": [
        ("spot", {}, lambda c: c.subscribe_book_ticker("BTC-USDT-SPOT")),
        ("swap", {"market": "swap"}, lambda c: c.subscribe_book_ticker("BTC-USDT")),
    ],
    "bitget": [("spot", {}, lambda c: c.subscribe_ticker("BTC-USDT-SPOT"))],
    "bybit": [
        ("spot", {"category": "spot"}, lambda c: c.subscribe_ticker("BTC-USDT-SPOT")),
        ("swap", {}, lambda c: c.subscribe_ticker("BTC-USDT-SWAP")),
    ],
    "extended": [("swap", {}, lambda c: c.subscribe_trades("BTC-USD"))],
    "hyperliquid": [("swap", {}, lambda c: c.subscribe_orderbook("BTC"))],
    "kraken": [("spot", {}, lambda c: c.subscribe_ticker("BTC/USD"))],
    "kucoin": [
        ("spot", {}, lambda c: c.subscribe_ticker("BTC-USDT-SPOT")),
        ("swap", {"market": "futures"}, lambda c: c.subscribe_ticker("BTC-USDT-SWAP")),
    ],
    "lighter": [("mainnet", {}, lambda c: c.subscribe_orderbook(0))],
    "mexc": [("spot", {}, lambda c: c.subscribe_book_ticker("BTC-USDT-SPOT"))],
    "okx": [("spot", {}, lambda c: c.subscribe_ticker("BTC-USDT-SPOT"))],
    "ondo": [("swap", {}, lambda c: c.subscribe_depth("BTC-USD.P"))],
}


def frame_kind(payload: object) -> str:
    """The event-type field or the key names; account numbers in channel names are masked."""
    from tests.stateful_ws import frame_kind as kind

    return re.sub(r"\d{4,}", "#", kind(payload))


def rejection_text(payload: object) -> str:
    """The exchange's own error text (never account data), shortened."""
    if not isinstance(payload, dict):
        return ""
    for key in ("msg", "message", "error", "ret_msg", "data"):
        if payload.get(key):
            return str(payload[key])[:160]
    return ""


def looks_rejected(payload: object) -> bool:
    """Common rejection shapes; values are inspected here and then discarded."""
    if not isinstance(payload, dict):
        return False
    if payload.get("event") == "error" or payload.get("type") == "error":
        return True
    if payload.get("success") is False or payload.get("channel") == "error":
        return True
    return "error" in payload and payload["error"] not in (None, "", [], {})


async def _close(client: Any) -> None:  # noqa: ANN401
    closed = client.close()
    if inspect.isawaitable(closed):
        await asyncio.wait_for(closed, CLOSE_SECONDS)


async def observe(client: Any, frames_needed: int) -> tuple[str, list[str], str]:  # noqa: ANN401
    """Read until `frames_needed` frames arrive; a rejection or silence fails the check."""
    kinds: list[str] = []
    deadline = time.monotonic() + WAIT_SECONDS
    while len(kinds) < frames_needed:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return ("no_data" if kinds else "silent"), kinds, ""
        try:
            payload = await asyncio.wait_for(client.recv(), remaining)
        except TimeoutError:
            continue
        kinds.append(frame_kind(payload))
        if looks_rejected(payload):
            return "rejected", kinds, rejection_text(payload)
    return "ok", kinds, ""


async def public_case(
    exchange: str, label: str, kwargs: dict[str, Any], subscribe: Subscribe
) -> dict[str, Any]:
    """Subscribe to one market stream and require an acknowledgement plus data frames."""
    module = importlib.import_module(f"dcex.ws.{exchange}")
    row: dict[str, Any] = {"exchange": exchange, "scope": "public", "market": label}
    client = None
    try:
        client = module.public(timeout=WAIT_SECONDS, **kwargs)
        await client.connect()
        await subscribe(client)
        # Three frames: a subscription acknowledgement (when the exchange sends one) plus data.
        row["outcome"], row["kinds"], reason = await observe(client, 3)
        if reason:
            row["message"] = reason
    except Exception as error:  # noqa: BLE001
        row.update(outcome="error", message=redact(error)[:300])
    finally:
        if client is not None:
            try:
                await _close(client)
            except Exception as error:  # noqa: BLE001
                row["close_error"] = redact(error)[:200]
    return row


async def private_case(exchange: str, market: str) -> dict[str, Any]:
    """Log in and subscribe to the private order stream, then close; nothing is ordered."""
    from tests.stateful_runner import client_options
    from tests.stateful_ws import stream_spec

    row: dict[str, Any] = {"exchange": exchange, "scope": "private", "market": market}
    client = None
    try:
        if exchange == "lighter":
            from dcex.lighter.credentials import credential_env_names

            if any(not os.getenv(name) for name in credential_env_names(market)):
                return {**row, "outcome": "skipped", "message": "missing credentials"}
            options: dict[str, Any] = {}
        else:
            import pytest

            try:
                options = client_options(exchange)
            except pytest.skip.Exception as error:
                return {**row, "outcome": "skipped", "message": redact(error)[:200]}
        spec = stream_spec(exchange, market, options)
        row["method"] = spec.method
        client = await spec.open()
        if spec.ack is None:
            # Push-only stream: an open, authenticated socket that stays up is the check.
            await asyncio.sleep(3)
            row["outcome"] = "ok" if _connected(client) else "closed"
        else:
            row["outcome"], row["kinds"], reason = await _acknowledged(client, spec.ack)
            if reason:
                row["message"] = reason
    except Exception as error:  # noqa: BLE001
        row.update(outcome="error", message=redact(error)[:300])
    finally:
        if client is not None:
            try:
                await _close(client)
            except Exception as error:  # noqa: BLE001
                row["close_error"] = redact(error)[:200]
    return row


def _connected(client: Any) -> bool:  # noqa: ANN401
    probe = getattr(client, "is_connected", None)
    value = probe() if callable(probe) else True
    return bool(value)


async def _acknowledged(
    client: Any,  # noqa: ANN401
    ack: Callable[[object], str | None],
) -> tuple[str, list[str], str]:
    kinds: list[str] = []
    deadline = time.monotonic() + WAIT_SECONDS
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return "no_ack", kinds, ""
        try:
            payload = await asyncio.wait_for(client.recv(), remaining)
        except TimeoutError:
            continue
        kinds.append(frame_kind(payload))
        verdict = ack(payload)
        if verdict == "ok":
            return "ok", kinds, ""
        if verdict == "error":
            return "rejected", kinds, rejection_text(payload)


async def run(exchanges: list[str], scopes: set[str]) -> Path:
    """Run every case concurrently and write outcomes (no payload values) to live-results."""
    from tests.stateful_runner import MARKETS

    cases: list[Awaitable[dict[str, Any]]] = []
    for exchange in exchanges:
        if "public" in scopes:
            cases += [public_case(exchange, *case) for case in PUBLIC.get(exchange, [])]
        if "private" in scopes:
            markets = [
                m for m, _ in MARKETS.get(exchange, []) if not (exchange == "arcus" and m == "spot")
            ]
            if exchange == "lighter":
                markets = ["mainnet"]
            cases += [private_case(exchange, market) for market in markets]
    rows = await asyncio.gather(*cases)
    out = Path("live-results") / f"smoke-ws-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    for row in rows:
        detail = row.get("message") or ", ".join(row.get("kinds", [])[:4])
        label = f"{row['exchange']:<12} {row['scope']:<8} {row['market']:<9}"
        print(f"{label} {row['outcome']:<9} {detail}")
    return out


def main() -> int:
    """Run the public and/or private WebSocket smoke and write the outcome file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exchange", choices=EXCHANGES, action="append")
    parser.add_argument("--scope", choices=["public", "private"], action="append")
    args = parser.parse_args()
    load_dotenv(".env")
    logging.disable(logging.CRITICAL)  # Client loggers could otherwise echo payloads.
    Path("live-results").mkdir(exist_ok=True)
    out = asyncio.run(
        run(args.exchange or list(EXCHANGES), set(args.scope or ["public", "private"]))
    )
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
