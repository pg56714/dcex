from ._http_manager import HTTPManager
from .endpoints.account import CashAccount


class AccountHTTP(HTTPManager):
    """HTTP client for Ascendex account-related API endpoints."""

    async def get_account_info(self) -> dict:
        """
        Get account information.

        Returns:
            dict: Account information including account group and other details
        """
        payload = {}
        res = await self._request(
            method="GET",
            path=CashAccount.ACCOUNT_INFO,
            hash_path=CashAccount.ACCOUNT_INFO.hash,
            query=payload,
        )
        return res
