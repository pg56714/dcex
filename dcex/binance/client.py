"""Binance API client for spot and futures trading."""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(TradeHTTP, AccountHTTP, MarketHTTP):
    """
    Unified Binance API client combining trading, account, and market data functionality.

    This client provides access to all Binance API endpoints for both spot and futures trading,
    including order management, account information, and market data retrieval.
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the Binance API client.

        Args:
            **args: Keyword arguments passed to the HTTP manager, including:
                api_key: Binance API key for authenticated requests.
                api_secret: Binance API secret for request signing.
                timeout: Request timeout in seconds (default: 10).
                logger: Custom logger instance.
                preload_product_table: Whether to preload product table (default: True).
        """
        super().__init__(**args)
