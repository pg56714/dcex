from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.public import Public


class PublicHTTP(HTTPManager):
    def get_public_instruments(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Get public instrument information.

        Args:
            instType: Instrument type
            uly: Underlying asset symbol
            instFamily: Instrument family
            product_symbol: Product symbol

        Returns:
            Dictionary containing instrument information.
        """
        payload: dict[str, Any] = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)

        res = self._request(
            method="GET",
            path=Public.GET_INSTRUMENT_INFO,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate(
        self,
        product_symbol: str,
    ) -> dict[str, Any]:
        """
        Get current funding rate for a trading pair.

        Args:
            product_symbol: Trading pair symbol

        Returns:
            Dictionary containing funding rate information.
        """
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }

        res = self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE,
            query=payload,
            signed=False,
        )
        return res

    def get_funding_rate_history(
        self,
        product_symbol: str,
        before: str | None = None,
        after: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get historical funding rates for a trading pair.

        Args:
            product_symbol: Trading pair symbol
            before: Pagination parameter - timestamp before this value
            after: Pagination parameter - timestamp after this value
            limit: Number of results to return

        Returns:
            Dictionary containing historical funding rate data.
        """
        payload: dict[str, Any] = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if before is not None:
            payload["before"] = before
        if after is not None:
            payload["after"] = after
        if limit is not None:
            payload["limit"] = limit

        res = self._request(
            method="GET",
            path=Public.GET_FUNDING_RATE_HISTORY,
            query=payload,
            signed=False,
        )
        return res
