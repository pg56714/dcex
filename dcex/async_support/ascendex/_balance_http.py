from ._http_manager import HTTPManager
from .endpoints.balance import Balance


class BalanceHTTP(HTTPManager):
    """HTTP client for Ascendex balance-related API endpoints."""

    async def get_cash_account_balance(self) -> dict:
        """
        Get cash account balance.

        Returns:
            dict: Cash account balance information
        """
        payload = {}
        res = await self._request(
            method="GET",
            path=Balance.CASH_ACCOUNT_BALANCE,
            hash_path=Balance.CASH_ACCOUNT_BALANCE.hash,
            query=payload,
        )
        return res
