"""
Zoomex market data HTTP client module.

This module provides the MarketHTTP class for interacting with Zoomex's
market data API endpoints, including instrument information queries.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.market import Market


class MarketHTTP(HTTPManager):
    """
    Zoomex market data HTTP client.

    This class provides methods for interacting with Zoomex's market data
    API endpoints, including:
    - Instrument information queries

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_instruments_info(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        status: str | None = None,
        baseCoin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get instruments information.

        Args:
            category: Product category (spot, linear, inverse, option)
            product_symbol: Optional product symbol to filter results
            status: Optional instrument status to filter results
            baseCoin: Optional base coin to filter results
            limit: Optional maximum number of records to return
            cursor: Optional cursor for pagination

        Returns:
            Dict containing instruments information
        """
        payload: dict[str, Any] = {
            "category": category,
        }
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.ZOOMEX, product_symbol)
            payload["category"] = self.ptm.get_exchange_type(Common.ZOOMEX, product_symbol)
        if status is not None:
            payload["status"] = status
        if baseCoin is not None:
            payload["baseCoin"] = baseCoin
        if limit is not None:
            payload["limit"] = limit
        if cursor is not None:
            payload["cursor"] = cursor

        res = await self._request(
            method="GET",
            path=Market.GET_INSTRUMENTS_INFO,
            query=payload,
            signed=False,
        )
        return res
