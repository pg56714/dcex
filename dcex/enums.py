"""
Cross-exchange unified enums.

These provide a single vocabulary (e.g. ``OrderSide.BUY``) that maps to each
exchange's native representation, so cross-exchange strategy code does not have
to remember that Binance wants ``"BUY"`` while OKX wants ``"buy"``.

Design notes:

- The per-exchange mapping tables are **module-level constants**, not rebuilt
  on every call (this library targets low latency).
- The mapping keys are the exchange names from :mod:`dcex.registry`, and a test
  asserts every registered exchange is covered, so the tables cannot silently
  drift from the supported-exchange list.
- Only lossless, unambiguous conversions live here. Things that an exchange
  encodes structurally (e.g. time-in-force folded into the order type, or
  Hyperliquid's boolean ``isBuy``) are handled explicitly rather than forced
  into a single string.
"""

from enum import Enum

from .registry import EXCHANGES

# Exchanges that take a boolean buy flag instead of a side string.
_BOOL_SIDE_EXCHANGES = frozenset({"hyperliquid"})

# value -> {exchange: native side string}. Module-level constant.
_ORDER_SIDE_MAP: dict[str, dict[str, str]] = {
    "BUY": {
        "binance": "BUY",
        "bybit": "Buy",
        "okx": "buy",
        "bitget": "buy",
        "bitmart": "buy",
        "bitmex": "Buy",
        "gateio": "buy",
        "bingx": "BUY",
        "kucoin": "buy",
        "kraken": "buy",
        "mexc": "BUY",
    },
    "SELL": {
        "binance": "SELL",
        "bybit": "Sell",
        "okx": "sell",
        "bitget": "sell",
        "bitmart": "sell",
        "bitmex": "Sell",
        "gateio": "sell",
        "bingx": "SELL",
        "kucoin": "sell",
        "kraken": "sell",
        "mexc": "SELL",
    },
}


class OrderSide(str, Enum):
    """Unified order side."""

    BUY = "BUY"
    SELL = "SELL"

    @classmethod
    def from_any(cls, value: str) -> "OrderSide":
        """Parse a loose buy/sell string (case-insensitive) into an OrderSide."""
        normalized = value.strip().lower()
        if normalized == "buy":
            return cls.BUY
        if normalized == "sell":
            return cls.SELL
        raise ValueError(f"Unknown order side: {value!r}")

    def is_buy(self) -> bool:
        """Return True for BUY. Useful for exchanges that take a boolean flag."""
        return self is OrderSide.BUY

    def to_exchange(self, exchange: str) -> str:
        """
        Return the native side string for ``exchange``.

        Args:
            exchange: Exchange name (see :mod:`dcex.registry`).

        Returns:
            The exchange's native side string.

        Raises:
            ValueError: If the exchange uses a boolean flag (use :meth:`is_buy`)
                or has no mapping.
        """
        key = exchange.lower()
        if key in _BOOL_SIDE_EXCHANGES:
            raise ValueError(
                f"{exchange} expresses side as a boolean; use OrderSide.is_buy() instead"
            )
        try:
            return _ORDER_SIDE_MAP[self.name][key]
        except KeyError as exc:
            raise ValueError(f"No OrderSide mapping for exchange: {exchange!r}") from exc


def _exchanges_needing_string_side() -> set[str]:
    """Registry exchanges that are expected to have a string side mapping."""
    return {name for name in EXCHANGES if name not in _BOOL_SIDE_EXCHANGES}
