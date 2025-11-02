"""
Bybit position management HTTP client module.

This module provides the PositionHTTP class for interacting with Bybit's
position management API endpoints, including position queries, leverage
settings, position mode switching, and closed PnL information.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.position import Position


class PositionHTTP(HTTPManager):
    """
    Bybit position management HTTP client.

    This class provides methods for interacting with Bybit's position management
    API endpoints, including:
    - Position queries and information
    - Leverage settings
    - Position mode switching
    - Closed PnL history

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_positions(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get position information.

        Args:
            category: Position category (linear, inverse, option)
            product_symbol: Optional product symbol to filter results
            settleCoin: Optional settlement coin to filter results
            limit: Maximum number of positions to return (default: 20)

        Returns:
            Dict containing position information
        """
        payload = {
            "category": category,
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if settleCoin is not None:
            payload["settleCoin"] = settleCoin

        res = await self._request(
            method="GET",
            path=Position.GET_POSITIONS,
            query=payload,
        )
        return res

    async def set_leverage(
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
            Dict containing leverage setting result
        """
        payload = {
            "category": self.ptm.get_exchange_type(Common.BYBIT, product_symbol),
            "symbol": self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol),
            "buyLeverage": leverage,
            "sellLeverage": leverage,
        }

        res = await self._request(
            method="POST",
            path=Position.SET_LEVERAGE,
            query=payload,
        )
        return res

    async def switch_position_mode(
        self,
        mode: int,
        product_symbol: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Switch position mode.

        Args:
            mode: Position mode (0: Merged Single, 3: Both Sides)
            product_symbol: Optional product symbol
            coin: Optional coin symbol

        Returns:
            Dict containing position mode switch result
        """
        payload = {
            "category": "linear",
            "mode": mode,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
        if coin is not None:
            payload["coin"] = coin

        res = await self._request(
            method="POST",
            path=Position.SWITCH_POSITION_MODE,
            query=payload,
        )
        return res

    async def get_closed_pnl(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get closed PnL history.

        Args:
            category: Position category (linear, inverse, option)
            product_symbol: Optional product symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing closed PnL history
        """
        payload = {
            "category": category,
            "limit": limit,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Position.GET_CLOSED_PNL,
            query=payload,
        )
        return res
