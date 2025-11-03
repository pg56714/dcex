from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import DeliveryAccount, FutureAccount, SpotAccount


class AccountHTTP(HTTPManager):
    """
    Gate.io Account HTTP client for account management operations.

    This class provides methods for managing account-related operations
    including spot, futures, and delivery account queries and transactions.
    """

    def get_futures_account(
        self,
        ccy: str = "usdt",  # or "btc"
    ) -> dict[str, Any]:
        """
        Get futures account information.

        Args:
            ccy: Settlement currency, either "usdt" or "btc"

        Returns:
            dict[str, Any]: Futures account information including balance and margin
        """
        path_params = {
            "settle": ccy,
        }

        res = self._request(
            method="GET",
            path=FutureAccount.QUERY_FUTURES_ACCOUNT,
            path_params=path_params,
        )
        return res

    def get_futures_account_book(
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
        Get futures account transaction history.

        Args:
            ccy: Settlement currency, either "usdt" or "btc"
            contract: Contract symbol to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip
            from_time: Start timestamp in milliseconds
            to_time: End timestamp in milliseconds
            change_type: Type of account change to filter by

        Returns:
            dict[str, Any]: Account transaction history
        """
        path_params: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=FutureAccount.QUERY_ACCOUNT_BOOK,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_delivery_account(
        self,
        ccy: str = "usdt",
    ) -> dict[str, Any]:
        """
        Get delivery account information.

        Args:
            ccy: Settlement currency, typically "usdt"

        Returns:
            dict[str, Any]: Delivery account information including balance and margin
        """
        path_params = {
            "settle": ccy,
        }

        res = self._request(
            method="GET",
            path=DeliveryAccount.QUERY_DELIVERY_ACCOUNT,
            path_params=path_params,
        )
        return res

    def get_delivery_account_book(
        self,
        ccy: str = "usdt",
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        change_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get delivery account transaction history.

        Args:
            ccy: Settlement currency, typically "usdt"
            limit: Maximum number of records to return
            offset: Number of records to skip
            from_time: Start timestamp in milliseconds
            to_time: End timestamp in milliseconds
            change_type: Type of account change to filter by

        Returns:
            dict[str, Any]: Delivery account transaction history
        """
        path_params: dict[str, Any] = {
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

        res = self._request(
            method="GET",
            path=DeliveryAccount.QUERY_ACCOUNT_BOOK,
            path_params=path_params,
            query=payload,
        )
        return res

    def get_spot_account(
        self,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Get spot account information.

        Args:
            ccy: Currency to filter by, if None returns all currencies

        Returns:
            dict[str, Any]: Spot account information including balances
        """
        payload: dict[str, Any] = {}
        if ccy:
            payload["currency"] = ccy

        res = self._request(
            method="GET",
            path=SpotAccount.QUERY_SPOT_ACCOUNT,
            query=payload,
        )
        return res

    def get_spot_account_book(
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
        Get spot account transaction history.

        Args:
            ccy: Currency to filter by
            from_timestamp: Start timestamp in milliseconds
            to_timestamp: End timestamp in milliseconds
            page: Page number for pagination
            limit: Maximum number of records per page
            type_: Transaction type to filter by
            code: Transaction code to filter by

        Returns:
            dict[str, Any]: Spot account transaction history
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

        res = self._request(
            method="GET",
            path=SpotAccount.QUERY_ACCOUNT_BOOK,
            query=payload,
        )
        return res
