"""Live WebSocket smoke tests for public and private streams."""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

import pytest
from dotenv import load_dotenv

from dcex.ws import (
    aster,
    backpack,
    binance,
    bingx,
    bitget,
    bitmart,
    bitmex,
    bybit,
    gateio,
    hyperliquid,
    kraken,
    kucoin,
    lighter,
    mexc,
    okx,
)

load_dotenv()

LIVE_WS_TIMEOUT = float(os.getenv("DCEX_LIVE_WS_TIMEOUT", "20"))
PRIVATE_WS_IDLE_TIMEOUT = float(os.getenv("DCEX_PRIVATE_WS_IDLE_TIMEOUT", "3"))

Payload = dict[str, Any] | list[Any] | str | bytes


class WebSocketLike(Protocol):
    """Minimal protocol shared by all live WebSocket wrappers."""

    async def recv(self) -> Payload:
        """Receive one WebSocket payload."""


WsFactory = Callable[[], WebSocketLike]
WsAction = Callable[[WebSocketLike], Awaitable[object]]


@dataclass(frozen=True)
class WebSocketSpec:
    """Live WebSocket client factory and subscription action."""

    name: str
    factory: WsFactory
    subscribe: WsAction
    env: tuple[str, ...] = ()


def _selected_exchanges() -> set[str] | None:
    value = os.getenv("DCEX_LIVE_WS_EXCHANGES")
    if not value:
        return None
    return {part.strip().lower() for part in value.split(",") if part.strip()}


def _skip_if_unselected(exchange: str) -> None:
    selected = _selected_exchanges()
    if selected is not None and exchange not in selected:
        pytest.skip(f"{exchange} not selected by DCEX_LIVE_WS_EXCHANGES.")


def _require_env(names: tuple[str, ...]) -> None:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        pytest.skip(f"Set {', '.join(missing)} before running this private live WS test.")


def _env_int(name: str) -> int:
    return int(os.environ[name].strip().lstrip("#"))


def _assert_payload(payload: Payload) -> None:
    if isinstance(payload, dict):
        assert payload
        return
    if isinstance(payload, list | str | bytes):
        assert len(payload) > 0
        return
    pytest.fail(f"Unexpected WebSocket payload type: {type(payload)!r}")


def _is_permission_error(exc: BaseException) -> bool:
    return "permission denied" in str(exc).lower()


async def _recv_one(ws: WebSocketLike, seconds: float) -> Payload:
    async with asyncio.timeout(seconds):
        return await ws.recv()


async def _recv_optional(ws: WebSocketLike) -> Payload | None:
    try:
        return await _recv_one(ws, PRIVATE_WS_IDLE_TIMEOUT)
    except TimeoutError:
        return None


PUBLIC_WS_SPECS = (
    WebSocketSpec(
        name="aster",
        factory=lambda: aster.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_agg_trades("BTC-USDT-SWAP"),
    ),
    WebSocketSpec(
        name="backpack",
        factory=lambda: backpack.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_ticker("SOL_USDC"),
    ),
    WebSocketSpec(
        name="binance",
        factory=lambda: binance.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_agg_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="bingx",
        factory=lambda: bingx.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="bitget",
        factory=lambda: bitget.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="bitmart",
        factory=lambda: bitmart.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="bitmex",
        factory=lambda: bitmex.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("XBTUSD"),
    ),
    WebSocketSpec(
        name="bybit",
        factory=lambda: bybit.public(category="spot", timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="gateio",
        factory=lambda: gateio.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="hyperliquid",
        factory=lambda: hyperliquid.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC"),
    ),
    WebSocketSpec(
        name="kraken",
        factory=lambda: kraken.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USD-SPOT"),
    ),
    WebSocketSpec(
        name="kucoin",
        factory=lambda: kucoin.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="lighter",
        factory=lambda: lighter.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades(0),
    ),
    WebSocketSpec(
        name="mexc",
        factory=lambda: mexc.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
    WebSocketSpec(
        name="okx",
        factory=lambda: okx.public(timeout=LIVE_WS_TIMEOUT),
        subscribe=lambda ws: ws.subscribe_trades("BTC-USDT-SPOT"),
    ),
)

PRIVATE_WS_SPECS = (
    WebSocketSpec(
        name="aster",
        env=("ASTER_USER_ADDRESS", "ASTER_SIGNER_ADDRESS", "ASTER_PRIVATE_KEY"),
        factory=lambda: aster.private(
            user_address=os.environ["ASTER_USER_ADDRESS"],
            signer_address=os.environ["ASTER_SIGNER_ADDRESS"],
            private_key=os.environ["ASTER_PRIVATE_KEY"],
            market="futures",
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.keep_alive(),
    ),
    WebSocketSpec(
        name="backpack",
        env=("BACKPACK_API_KEY", "BACKPACK_API_SECRET"),
        factory=lambda: backpack.private(
            api_key=os.environ["BACKPACK_API_KEY"],
            api_secret=os.environ["BACKPACK_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_orders(),
    ),
    WebSocketSpec(
        name="binance",
        env=("BINANCE_API_KEY", "BINANCE_API_SECRET"),
        factory=lambda: binance.private(
            api_key=os.environ["BINANCE_API_KEY"],
            api_secret=os.environ["BINANCE_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.keep_alive(),
    ),
    WebSocketSpec(
        name="bingx",
        env=("BINGX_API_KEY", "BINGX_API_SECRET"),
        factory=lambda: bingx.private(
            api_key=os.environ["BINGX_API_KEY"],
            api_secret=os.environ["BINGX_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_orders(),
    ),
    WebSocketSpec(
        name="bitget",
        env=("BITGET_API_KEY", "BITGET_API_SECRET", "BITGET_PASSPHRASE"),
        factory=lambda: bitget.private(
            api_key=os.environ["BITGET_API_KEY"],
            api_secret=os.environ["BITGET_API_SECRET"],
            passphrase=os.environ["BITGET_PASSPHRASE"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_account(),
    ),
    WebSocketSpec(
        name="bitmart",
        env=("BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"),
        factory=lambda: bitmart.private(
            api_key=os.environ["BITMART_API_KEY"],
            api_secret=os.environ["BITMART_API_SECRET"],
            memo=os.environ["BITMART_MEMO"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_balance(),
    ),
    WebSocketSpec(
        name="bitmex",
        env=("BITMEX_API_KEY", "BITMEX_API_SECRET"),
        factory=lambda: bitmex.private(
            api_key=os.environ["BITMEX_API_KEY"],
            api_secret=os.environ["BITMEX_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_margin(),
    ),
    WebSocketSpec(
        name="bybit",
        env=("BYBIT_API_KEY", "BYBIT_API_SECRET"),
        factory=lambda: bybit.private(
            api_key=os.environ["BYBIT_API_KEY"],
            api_secret=os.environ["BYBIT_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_wallet(),
    ),
    WebSocketSpec(
        name="gateio",
        env=("GATEIO_API_KEY", "GATEIO_API_SECRET"),
        factory=lambda: gateio.private(
            api_key=os.environ["GATEIO_API_KEY"],
            api_secret=os.environ["GATEIO_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_balances(),
    ),
    WebSocketSpec(
        name="hyperliquid",
        env=("HYPERLIQUID_WALLET_ADDRESS",),
        factory=lambda: hyperliquid.private(
            user=os.environ["HYPERLIQUID_WALLET_ADDRESS"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_user_events(),
    ),
    WebSocketSpec(
        name="kraken",
        env=("KRAKEN_SPOT_API_KEY", "KRAKEN_SPOT_API_SECRET"),
        factory=lambda: kraken.private(
            api_key=os.environ["KRAKEN_SPOT_API_KEY"],
            api_secret=os.environ["KRAKEN_SPOT_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_balances(),
    ),
    WebSocketSpec(
        name="kucoin",
        env=("KUCOIN_API_KEY", "KUCOIN_API_SECRET", "KUCOIN_API_PASSPHRASE"),
        factory=lambda: kucoin.private(
            api_key=os.environ["KUCOIN_API_KEY"],
            api_secret=os.environ["KUCOIN_API_SECRET"],
            passphrase=os.environ["KUCOIN_API_PASSPHRASE"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_orders(),
    ),
    WebSocketSpec(
        name="lighter",
        env=("LIGHTER_ACCOUNT_INDEX", "LIGHTER_API_KEY_INDEX", "LIGHTER_API_PRIVATE_KEY"),
        factory=lambda: lighter.private(
            account_index=_env_int("LIGHTER_ACCOUNT_INDEX"),
            api_key_index=_env_int("LIGHTER_API_KEY_INDEX"),
            api_private_key=os.environ["LIGHTER_API_PRIVATE_KEY"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_account_all_orders(),
    ),
    WebSocketSpec(
        name="mexc",
        env=("MEXC_API_KEY", "MEXC_API_SECRET"),
        factory=lambda: mexc.private(
            api_key=os.environ["MEXC_API_KEY"],
            api_secret=os.environ["MEXC_API_SECRET"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_account(),
    ),
    WebSocketSpec(
        name="okx",
        env=("OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"),
        factory=lambda: okx.private(
            api_key=os.environ["OKX_API_KEY"],
            api_secret=os.environ["OKX_API_SECRET"],
            passphrase=os.environ["OKX_PASSPHRASE"],
            timeout=LIVE_WS_TIMEOUT,
        ),
        subscribe=lambda ws: ws.subscribe_account(),
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize("spec", PUBLIC_WS_SPECS, ids=lambda spec: spec.name)
async def test_public_ws_live_receives_event(spec: WebSocketSpec) -> None:
    """Subscribe to a public stream and require one live payload."""

    _skip_if_unselected(spec.name)

    async with spec.factory() as ws:
        await spec.subscribe(ws)
        payload = await _recv_one(ws, LIVE_WS_TIMEOUT)

    _assert_payload(payload)


@pytest.mark.asyncio
@pytest.mark.private
@pytest.mark.parametrize("spec", PRIVATE_WS_SPECS, ids=lambda spec: spec.name)
async def test_private_ws_live_connects_and_subscribes(spec: WebSocketSpec) -> None:
    """Authenticate or connect a private stream and issue one user-data subscription."""

    _skip_if_unselected(spec.name)
    _require_env(spec.env)

    try:
        async with spec.factory() as ws:
            await spec.subscribe(ws)
            payload = await _recv_optional(ws)
    except RuntimeError as exc:
        if _is_permission_error(exc):
            pytest.skip(f"{spec.name} private WebSocket credentials lack required permission.")
        raise

    if payload is not None:
        _assert_payload(payload)
