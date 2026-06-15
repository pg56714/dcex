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

from . import _native
from .registry import EXCHANGES

# Exchanges that take a boolean side flag or signed order payload instead of a side string.
_BOOL_SIDE_EXCHANGES = frozenset({"hyperliquid", "lighter"})

# Compatibility view of the Rust mapping for callers that imported this private constant.
_ORDER_SIDE_MAP: dict[str, dict[str, str]] = {
    side: {
        exchange: _native.order_side_to_exchange(side, exchange)
        for exchange in EXCHANGES
        if exchange not in _BOOL_SIDE_EXCHANGES
    }
    for side in ("BUY", "SELL")
}


class OrderSide(str, Enum):
    """Unified order side."""

    BUY = "BUY"
    SELL = "SELL"

    @classmethod
    def from_any(cls, value: str) -> "OrderSide":
        """Parse a loose buy/sell string (case-insensitive) into an OrderSide."""
        return cls(_native.order_side_parse(value))

    def is_buy(self) -> bool:
        """Return True for BUY. Useful for exchanges that take a boolean flag."""
        return _native.order_side_is_buy(self.value)

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
        return _native.order_side_to_exchange(self.value, exchange)


def _exchanges_needing_string_side() -> set[str]:
    """Registry exchanges that are expected to have a string side mapping."""
    return {name for name in EXCHANGES if name not in _BOOL_SIDE_EXCHANGES}
