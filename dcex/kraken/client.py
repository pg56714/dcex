"""Kraken sync client module."""
# pylint: disable=unused-argument

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    MarketHTTP,
    AccountHTTP,
    TradeHTTP,
):
    """Kraken sync client for public market-data operations."""

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """Initialize the Kraken client."""
        super().__init__(**args)
