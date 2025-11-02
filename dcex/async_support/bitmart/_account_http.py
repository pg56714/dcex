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
        currencies: str | None = None,
    ) -> dict[str, Any]:
        """
        Get account currencies.

        Args:
            currencies: Comma-separated currency symbols

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

    async def post_withdraw_apply(
        self,
        currency: str,
        amount: str,
        address: str,
        address_memo: str | None = None,
        destination: str | None = None,
    ) -> dict[str, Any]:
        """
        Apply for withdrawal.

        Args:
            currency: Currency symbol (e.g., 'USDT')
            amount: Withdrawal amount
            address: Withdrawal address
            address_memo: Address memo
            destination: Destination

        Returns:
            dict: Withdrawal application response
        """
        payload = {
            "currency": currency,
            "amount": amount,
            "address": address,
        }
        if address_memo is not None:
            payload["address_memo"] = address_memo
        if destination is not None:
            payload["destination"] = destination

        res = await self._request(
            method="POST",
            path=FundingAccount.WITHDRAW,
            query=payload,
        )
        return res

    async def get_deposit_withdraw_history(
        self,
        operation_type: str = "withdraw",
        limit: int = 1000,
        currency: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get deposit/withdraw history.

        Args:
            operation_type: Operation type (deposit, withdraw)
            limit: Number of records per page
            currency: Currency symbol (e.g., 'USDT')
            startTime: Start time in milliseconds
            endTime: End time in milliseconds

        Returns:
            dict: Deposit/withdraw history data
        """
        payload = {
            "N": limit,
            "operation_type": operation_type,
        }
        if currency is not None:
            payload["currency"] = currency
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime

        res = await self._request(
            method="GET",
            path=FundingAccount.GET_DEPOSIT_WITHDRAW_HISTORY,
            query=payload,
        )
        return res

    async def get_deposit_withdraw_history_detail(
        self,
        id: str,
    ) -> dict[str, Any]:
        """
        Get deposit/withdraw history detail.

        Args:
            id: Withdraw ID or deposit ID

        Returns:
            dict: Deposit/withdraw history detail data
        """
        payload = {
            "id": id,
        }

        res = await self._request(
            method="GET",
            path=FundingAccount.GET_DEPOSIT_WITHDRAW_HISTORY_DETAIL,
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
