from typing import Any

from ._http_manager import HTTPManager
from .endpoints.funds import Account


class AccountHTTP(HTTPManager):
    """
    BitMEX Account HTTP client for account-related operations.

    This class provides methods for retrieving account information,
    wallet summaries, and other account-related data from the BitMEX API.
    """

    def get_wallet_summary(
        self,
        currency: str = "all",
        start_time: str | None = None,
        end_time: str | None = None,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """
        Get wallet summary information for the account.

        Args:
            currency: Currency to filter by (default: "all")
            start_time: Start time for the query (ISO format)
            end_time: End time for the query (ISO format)
            target_account_id: Specific account ID to query
            target_account_ids: List of account IDs or "*" for all accounts

        Returns:
            Dict containing wallet summary data

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, str | int | list[str] | float | bool] = {
            "currency": currency,
        }

        if start_time is not None:
            payload["startTime"] = start_time

        if end_time is not None:
            payload["endTime"] = end_time

        if target_account_id is not None:
            payload["targetAccountId"] = target_account_id

        if target_account_ids is not None:
            if isinstance(target_account_ids, list):
                payload["targetAccountIds[]"] = target_account_ids
            elif isinstance(target_account_ids, str):
                payload["targetAccountIds"] = target_account_ids

        res = self._request(
            method="GET",
            path=Account.ACCOUNT_INFO,
            query=payload,
        )
        return res
