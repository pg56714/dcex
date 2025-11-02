"""
Bybit Client.

This module provides the main client class that combines all Bybit API
functionality including trading, account management, asset operations,
position management, and market data.
"""

from typing import Any

from ._account_http import AccountHTTP
from ._asset_http import AssetHTTP
from ._market_http import MarketHTTP
from ._position_http import PositionHTTP
from ._trade_http import TradeHTTP


class Client(
    TradeHTTP,
    AccountHTTP,
    AssetHTTP,
    PositionHTTP,
    MarketHTTP,
):
    """
    Main Bybit client combining all API functionality.

    This client inherits from all HTTP manager classes to provide
    a unified interface for all Bybit API operations including:
    - Trading operations (orders, executions)
    - Account management (balances, settings)
    - Asset operations (deposits, withdrawals, transfers)
    - Position management (leverage, PnL)
    - Market data (instruments, klines, orderbook)

    Args:
        **args: Arguments passed to the base HTTPManager class
    """

    def __init__(
        self,
        **args: Any,  # noqa: ANN401
    ) -> None:
        """
        Initialize the Bybit client.

        Args:
            **args: Arguments passed to the base HTTPManager class
        """
        super().__init__(**args)
