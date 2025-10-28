"""OKX Public HTTP client for public data operations."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.public import Public


class PublicHTTP(HTTPManager):
    """HTTP client for OKX public data operations."""

    async def get_public_instruments(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get public instruments information.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol

        Returns:
            Dict containing instruments information
        """
        payload = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)

        res = await self._request(
            method="GET",
            path=Public.GET_INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    async def get_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get funding rate information.

        Args:
            product_symbol: Trading pair symbol

        Returns:
            Dict containing funding rate information
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE,
            query=payload,
            signed=False,
        )
        return res

    async def get_funding_rate_history(
        self,
        product_symbol: str,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get funding rate history.

        Args:
            product_symbol: Trading pair symbol
            before: Pagination parameter - records before this ID
            after: Pagination parameter - records after this ID
            limit: Number of results per request (max 100)

        Returns:
            Dict containing funding rate history
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if before is not None:
            payload["before"] = before
        if after is not None:
            payload["after"] = after
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res

    async def get_position_tiers(
        self,
        instType: str = "SWAP",
        tdMode: str = "isolated",
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ccy: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """
        Get position tiers information.

        Args:
            instType: Instrument type (default: SWAP)
            tdMode: Trading mode (default: isolated)
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ccy: Currency
            tier: Tier level

        Returns:
            Dict containing position tiers information
        """
        payload = {"instType": instType, "tdMode": tdMode}
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ccy is not None:
            payload["ccy"] = ccy
        if tier is not None:
            payload["tier"] = tier

        res = await self._request(
            method="GET",
            path=Public.GET_POSITION_TIERS,
            query=payload,
            signed=False,
        )
        return res
