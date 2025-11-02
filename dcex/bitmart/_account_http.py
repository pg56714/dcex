from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import FundingAccount, FuturesAccount


class AccountHTTP(HTTPManager):
    def get_account_balance(
        self,
        currency: str | None = None,
        needUsdValuation: bool = False,
    ) -> dict[str, Any]:
        """
        Get account balance information.

        Args:
            currency: Currency symbol to filter balance (optional)
            needUsdValuation: Whether to include USD valuation

        Returns:
            Dict containing account balance information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "needUsdValuation": needUsdValuation,
        }
        if currency is not None:
            payload["currency"] = str(currency)

        res = self._request(
            method="GET",
            path=FundingAccount.GET_ACCOUNT_BALANCE,
            query=payload,
        )
        return res

    def get_account_currencies(
        self,
        currencies: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get account currencies information.

        Args:
            currencies: List of currency symbols to filter (optional)

        Returns:
            Dict containing currencies information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {}
        if currencies is not None:
            coinName = ",".join(currencies)
            payload = {
                "currencies": coinName,
            }

        res = self._request(
            method="GET",
            path=FundingAccount.GET_ACCOUNT_CURRENCIES,
            query=payload,
        )
        return res

    def get_spot_wallet(self) -> dict[str, Any]:
        """
        Get spot wallet balance information.

        Returns:
            Dict containing spot wallet balance information

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=FundingAccount.GET_SPOT_WALLET_BALANCE,
            query=None,
        )
        return res

    def get_deposit_address(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """
        Get deposit address for a specific currency.

        Args:
            currency: Currency symbol for which to get deposit address

        Returns:
            Dict containing deposit address information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "currency": currency,
        }

        res = self._request(
            method="GET",
            path=FundingAccount.DEPOSIT_ADDRESS,
            query=payload,
        )
        return res

    def get_withdraw_charge(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """
        Get withdrawal fee information for a specific currency.

        Args:
            currency: Currency symbol for which to get withdrawal fee

        Returns:
            Dict containing withdrawal fee information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "currency": currency,
        }

        res = self._request(
            method="GET",
            path=FundingAccount.WITHDRAW_QUOTA,
            query=payload,
        )
        return res

    def post_withdraw_apply(
        self,
        currency: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        Apply for withdrawal of a specific currency and amount.

        Args:
            currency: Currency symbol to withdraw
            amount: Amount to withdraw (as string)

        Returns:
            Dict containing withdrawal application result

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "currency": currency,
            "amount": amount,
        }

        res = self._request(
            method="POST",
            path=FundingAccount.WITHDRAW,
            query=payload,
        )
        return res

    def get_deposit_withdraw_history(
        self,
        operation_type: str = "withdraw",
        limit: int = 1000,
        currency: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """
        Get deposit and withdrawal history.

        Args:
            operation_type: Type of operation ("deposit" or "withdraw")
            limit: Maximum number of records to return (default: 1000)
            currency: Currency symbol to filter (optional)
            startTime: Start timestamp in milliseconds (optional)
            endTime: End timestamp in milliseconds (optional)

        Returns:
            Dict containing deposit/withdrawal history

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "N": limit,
            "operation_type": operation_type,
        }
        if currency is not None:
            payload["currency"] = currency
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime

        res = self._request(
            method="GET",
            path=FundingAccount.GET_DEPOSIT_WITHDRAW_HISTORY,
            query=payload,
        )
        return res

    def get_deposit_withdraw_history_detail(
        self,
        id: str,
    ) -> dict[str, Any]:
        """
        Get detailed information for a specific deposit or withdrawal transaction.

        Args:
            id: Transaction ID (withdraw_id or deposit_id)

        Returns:
            Dict containing detailed transaction information

        Raises:
            FailedRequestError: If the API request fails
        """
        payload: dict[str, Any] = {
            "id": id,
        }

        res = self._request(
            method="GET",
            path=FundingAccount.GET_DEPOSIT_WITHDRAW_HISTORY_DETAIL,
            query=payload,
        )
        return res

    def get_contract_assets(self) -> dict[str, Any]:
        """
        Get contract assets information for futures trading.

        Returns:
            Dict containing contract assets information

        Raises:
            FailedRequestError: If the API request fails
        """
        res = self._request(
            method="GET",
            path=FuturesAccount.GET_CONTRACT_ASSETS,
            query=None,
        )
        return res
