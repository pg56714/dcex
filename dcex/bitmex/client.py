"""
BitMEX Client for comprehensive API access.

This module provides a unified client interface for all BitMEX API operations,
combining market data, account management, trading, position management,
and trading history functionality.
"""

from typing import Any

from ._account_http import AccountHTTP
from ._market_http import MarketHTTP
from ._position_http import PositionHTTP
from ._trade_http import TradeHTTP
from ._trading_http import TradingHTTP


class Client(
    MarketHTTP,
    AccountHTTP,
    TradeHTTP,
    PositionHTTP,
    TradingHTTP,
):
    """
    BitMEX Client for comprehensive API access.

    This class combines all BitMEX API functionality into a single client interface,
    providing access to market data, account management, trading operations,
    position management, and trading history.

    The client inherits from multiple HTTP client classes to provide a unified
    interface for all BitMEX API operations.

    Example:
        ```python
        client = Client(
            api_key="your_api_key",
            api_secret="your_api_secret"
        )

        # Market data
        ticker = client.get_ticker(symbol="XBTUSD")

        # Account information
        wallet = client.get_wallet_summary()

        # Trading
        order = client.place_limit_buy_order("XBTUSD", 100, 50000.0)
        ```
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the BitMEX client.

        Args:
            **args: Keyword arguments passed to the HTTP manager base class.
                   Common arguments include:
                   - api_key: BitMEX API key
                   - api_secret: BitMEX API secret
                   - base_url: Base URL for the API (default: https://www.bitmex.com)
                   - timeout: Request timeout in seconds (default: 30)
                   - logger: Logger instance for debugging
        """
        super().__init__(**args)
