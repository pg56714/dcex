"""Bitmart unified client for trading, market data, and account management."""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    MarketHTTP,
    AccountHTTP,
):
    """
    Unified Bitmart client combining trading, market data, and account functionality.

    This client provides access to all Bitmart API endpoints including:
    - Spot and futures trading operations
    - Market data and ticker information
    - Account balance and transaction management

    Args:
        **args: Arguments passed to parent HTTP manager classes
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the Bitmart client.

        Args:
            **args: Configuration arguments including:
                api_key: API key for authentication
                api_secret: API secret for authentication
                memo: API memo for authentication
                timeout: Request timeout in seconds
                max_retries: Maximum number of retries
                retry_delay: Delay between retries
                logger: Logger instance
                preload_product_table: Whether to preload product table
        """
        super().__init__(**args)
