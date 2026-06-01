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
