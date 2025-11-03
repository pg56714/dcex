"""
Gate.io account management HTTP client module.

This module provides the AccountHTTP class for interacting with Gate.io's
account management API endpoints, including futures, delivery, and spot
account queries and account book operations.
"""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import DeliveryAccount, FutureAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """
    Gate.io account management HTTP client.

    This class provides methods for interacting with Gate.io's account management
    API endpoints, including:
    - Futures account queries and account book
    - Delivery account queries and account book
    - Spot account queries and account book

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_futures_account(
        self,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Get futures account information.

        Args:
            ccy: Settlement currency (usdt or btc)

        Returns:
            Dict containing futures account information
        """
        path_params = {
            "settle": ccy,
        }

        res = await self._request(
            method="GET",
            path=FutureAccount.QUERY_FUTURES_ACCOUNT,
            path_params=path_params,
        )
        return res

    async def get_futures_account_book(
        self,
        ccy: str = "usdt",  # or "btc"
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        change_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get futures account book.

        Args:
            ccy: Settlement currency (usdt or btc)
            contract: Optional contract symbol to filter results
            limit: Optional maximum number of records
            offset: Optional offset for pagination
            from_time: Optional start time timestamp
            to_time: Optional end time timestamp
            change_type: Optional change type to filter results

        Returns:
            Dict containing futures account book
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {}
        if contract:
            payload["contract"] = contract
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset
        if from_time:
            payload["from"] = from_time
        if to_time:
            payload["to"] = to_time
        if change_type:
            payload["type"] = change_type

        res = await self._request(
            method="GET",
            path=FutureAccount.QUERY_ACCOUNT_BOOK,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_delivery_account(
        self,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        Get delivery account information.

        Args:
            ccy: Settlement currency (default: usdt)

        Returns:
            Dict containing delivery account information
        """
        path_params = {
            "settle": ccy,
        }

        res = await self._request(
            method="GET",
            path=DeliveryAccount.QUERY_DELIVERY_ACCOUNT,
            path_params=path_params,
        )
        return res

    async def get_delivery_account_book(
        self,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        change_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get delivery account book.

        Args:
            ccy: Settlement currency (default: usdt)
            limit: Optional maximum number of records
            offset: Optional offset for pagination
            from_time: Optional start time timestamp
            to_time: Optional end time timestamp
            change_type: Optional change type to filter results

        Returns:
            Dict containing delivery account book
        """
        path_params = {
            "settle": ccy,
        }

        payload: dict[str, Any] = {}
        if limit:
            payload["limit"] = limit
        if offset:
            payload["offset"] = offset
        if from_time:
            payload["from"] = from_time
        if to_time:
            payload["to"] = to_time
        if change_type:
            payload["type"] = change_type

        res = await self._request(
            method="GET",
            path=DeliveryAccount.QUERY_ACCOUNT_BOOK,
            path_params=path_params,
            query=payload,
        )
        return res

    async def get_spot_account(
        self,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot account information.

        Args:
            ccy: Optional currency symbol to filter results

        Returns:
            Dict containing spot account information
        """
        payload: dict[str, Any] = {}
        if ccy:
            payload["currency"] = ccy

        res = await self._request(
            method="GET",
            path=SpotAccount.QUERY_SPOT_ACCOUNT,
            query=payload,
        )
        return res

    async def get_spot_account_book(
        self,
        ccy: str | None = None,
        from_timestamp: int | None = None,
        to_timestamp: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        type_: str | None = None,
        code: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot account book.

        Args:
            ccy: Optional currency symbol to filter results
            from_timestamp: Optional start time timestamp
            to_timestamp: Optional end time timestamp
            page: Optional page number for pagination
            limit: Optional maximum number of records
            type_: Optional transaction type to filter results
            code: Optional transaction code to filter results

        Returns:
            Dict containing spot account book
        """
        payload: dict[str, Any] = {}
        if ccy:
            payload["currency"] = ccy
        if from_timestamp:
            payload["from"] = from_timestamp
        if to_timestamp:
            payload["to"] = to_timestamp
        if page:
            payload["page"] = page
        if limit:
            payload["limit"] = limit
        if code:
            payload["code"] = code
        elif type_:
            payload["type"] = type_

        res = await self._request(
            method="GET",
            path=SpotAccount.QUERY_ACCOUNT_BOOK,
            query=payload,
        )
        return res
