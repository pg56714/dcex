"""
Gate.io Client for comprehensive API access.

This module provides a unified client interface for all Gate.io API operations,
combining market data, account management, and trading functionality for
spot, futures, and delivery markets.
"""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    AccountHTTP,
    MarketHTTP,
):
    """
    Gate.io Client for comprehensive API access.

    This class combines all Gate.io API functionality into a single client interface,
    providing access to market data, account management, and trading operations
    for spot, futures, and delivery markets.

    The client inherits from multiple HTTP client classes to provide a unified
    interface for all Gate.io API operations.

    Example:
        ```python
        client = Client(
            api_key="your_api_key",
            api_secret="your_api_secret"
        )

        # Market data
        contracts = client.get_all_futures_contracts()
        ticker = client.get_contract_list_tickers("BTC_USDT")

        # Account information
        account = client.get_futures_account()

        # Trading
        order = client.place_contract_limit_buy_order("BTC_USDT", 100, "50000.0")
        ```
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the Gate.io client.

        Args:
            **args: Keyword arguments passed to the HTTP manager base class.
                   Common arguments include:
                   - api_key: Gate.io API key
                   - api_secret: Gate.io API secret
                   - base_url: Base URL for the API (default: https://api.gateio.ws)
                   - logger: Logger instance for debugging
                   - preload_product_table: Whether to preload product table (default: True)
        """
        super().__init__(**args)
