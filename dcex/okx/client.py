"""
OKX API Client Module.

This module provides a comprehensive client for interacting with the OKX cryptocurrency
exchange API. It combines all HTTP modules for trading operations, account management,
asset operations, and market data retrieval.

The client supports both live and demo trading modes and provides access to:
- Trading operations (place orders, cancel orders, etc.)
- Account management (balance, positions, etc.)
- Asset operations (deposits, withdrawals, transfers)
- Public market data (instruments, funding rates)
- Market data (candles, orderbook, tickers)
"""

from typing import Any

from ._account_http import AccountHTTP
from ._asset_http import AssetHTTP
from ._market_http import MarketHTTP
from ._public_http import PublicHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    AccountHTTP,
    AssetHTTP,
    PublicHTTP,
    MarketHTTP,
):
    """
    OKX API Client that combines all HTTP modules for trading operations.

    This client provides access to all OKX API endpoints including:
    - Trading operations (place orders, cancel orders, etc.)
    - Account management (balance, positions, etc.)
    - Asset operations (deposits, withdrawals, transfers)
    - Public market data (instruments, funding rates)
    - Market data (candles, orderbook, tickers)

    Args:
        **args: Arbitrary keyword arguments passed to the HTTP manager.
               Common parameters include:
               - api_key: OKX API key
               - api_secret: OKX API secret
               - passphrase: OKX API passphrase
               - flag: Trading flag ("0" for live, "1" for demo)
               - base_api: Base API URL (default: "https://www.okx.com")
               - max_retries: Maximum number of retries for failed requests
               - retry_delay: Delay between retries in seconds
               - logger: Custom logger instance
               - preload_product_table: Whether to preload product table
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the OKX client with the provided configuration.

        Args:
            **args: Configuration parameters for the HTTP manager.
        """
        super().__init__(**args)
