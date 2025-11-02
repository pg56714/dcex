"""
Bybit Position HTTP client.

This module provides HTTP client functionality for position management
operations on the Bybit exchange, including position queries, leverage
settings, and PnL history.
"""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.position import Position


class PositionHTTP(HTTPManager):
    """
    HTTP client for Bybit position operations.

    This class handles all position-related API requests including:
    - Position list queries
    - Leverage settings
    - Position mode switching
    - Closed PnL history
    """

    def get_positions(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get positions list.

        Args:
            category: Product category (linear, inverse, option)
            product_symbol: Product symbol to filter by
            settleCoin: Settlement coin to filter by
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing positions
        """
        payload: dict[str, Any] = {
            "category": category,
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if settleCoin is not None:
            payload["settleCoin"] = settleCoin

        res = self._request(
            method="GET",
            path=Position.GET_POSITIONS,
            query=payload,
        )
        return res

    def set_leverage(
        self,
        product_symbol: str,
        leverage: str,
    ) -> dict[str, Any]:
        """
        Set leverage for a product.

        Args:
            product_symbol: Product symbol
            leverage: Leverage value to set

        Returns:
            dict[str, Any]: API response confirming the leverage setting
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "buyLeverage": leverage,
            "sellLeverage": leverage,
        }

        res = self._request(
            method="POST",
            path=Position.SET_LEVERAGE,
            query=payload,
        )
        return res

    def switch_position_mode(
        self,
        mode: int,
        product_symbol: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Switch position mode.

        Args:
            mode: Position mode (0: Merged Single, 3: Both Sides)
            product_symbol: Product symbol to apply mode to
            coin: Coin to apply mode to

        Returns:
            dict[str, Any]: API response confirming the mode switch
        """
        payload = {
            "category": "linear",
            "mode": mode,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
        if coin is not None:
            payload["coin"] = coin

        res = self._request(
            method="POST",
            path=Position.SWITCH_POSITION_MODE,
            query=payload,
        )
        return res

    def get_closed_pnl(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get closed PnL history.

        Args:
            category: Product category
            product_symbol: Product symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing closed PnL history
        """
        payload: dict[str, Any] = {
            "category": category,
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Position.GET_CLOSED_PNL,
            query=payload,
        )
        return res
