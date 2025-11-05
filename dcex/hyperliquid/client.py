"""Hyperliquid client module."""
# pylint: disable=unused-argument

from typing import Any

from ._account_http import AccountHTTP
from ._asset_http import AssetHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    AccountHTTP,
    AssetHTTP,
    MarketHTTP,
):
    """Hyperliquid client for trading operations."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the Hyperliquid client.

        Args:
            **args: Additional arguments passed to parent classes.
        """
        super().__init__(**args)
