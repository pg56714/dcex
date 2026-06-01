from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import FundingAccount, FuturesAccount


class AccountHTTP(HTTPManager):
    """HTTP client for BitMart account-related API endpoints."""

    async def get_account_balance(
        self,
        currency: str | None = None,
        needUsdValuation: bool = False,
    ) -> dict[str, Any]:
        """
        Get account balance.

        Args:
            currency: Currency symbol (e.g., 'USDT')
            needUsdValuation: Whether to include USD valuation

        Returns:
            dict: Account balance data
        """
        payload: dict[str, Any] = {
            "needUsdValuation": needUsdValuation,
        }
        if currency is not None:
            payload["currency"] = currency

        res = await self._request(
            method="GET",
            path=FundingAccount.GET_ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    async def get_account_currencies(
        self,
        currencies: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get account currencies.

        Args:
            currencies: Currency symbols

        Returns:
            dict: Account currencies data
        """
        payload = {}
        if currencies is not None:
            coinName = ",".join(currencies)
            payload = {
                "currencies": coinName,
            }

        res = await self._request(
            method="GET",
            path=FundingAccount.GET_ACCOUNT_CURRENCIES,
            query=payload,
        )
        return res

    async def get_spot_wallet(self) -> dict[str, Any]:
        """
        Get spot wallet balance.

        Returns:
            dict: Spot wallet balance data
        """
        res = await self._request(
            method="GET",
            path=FundingAccount.GET_SPOT_WALLET_BALANCE,
            query={},
        )
        return res

    async def get_deposit_address(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """
        Get deposit address.

        Args:
            currency: Currency symbol (e.g., 'USDT')

        Returns:
            dict: Deposit address data
        """
        payload = {
            "currency": currency,
        }

        res = await self._request(
            method="GET",
            path=FundingAccount.DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

    async def get_withdraw_charge(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """
        Get withdraw charge.

        Args:
            currency: Currency symbol (e.g., 'USDT')

        Returns:
            dict: Withdraw charge data
        """
        payload = {
            "currency": currency,
        }

        res = await self._request(
            method="GET",
            path=FundingAccount.WITHDRAW_QUOTA,
            query=payload,
        )
        return res

    async def get_contract_assets(self) -> dict[str, Any]:
        """
        Get contract assets.

        Returns:
            dict: Contract assets data
        """
        res = await self._request(
            method="GET",
            path=FuturesAccount.GET_CONTRACT_ASSETS,
            query={},
        )
        return res
