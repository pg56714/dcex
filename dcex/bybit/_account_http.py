"""
Bybit Account HTTP client.

This module provides HTTP client functionality for account-related operations
on the Bybit exchange, including wallet balance queries, transfers,
collateral management, and account settings.
"""

from typing import Any

from ..utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import Account


class AccountHTTP(HTTPManager):
    """
    HTTP client for Bybit account operations.

    This class handles all account-related API requests including:
    - Wallet balance management
    - Account transfers and withdrawals
    - Collateral and margin settings
    - Account information and transaction logs
    """

    def get_wallet_balance(self) -> dict[str, Any]:
        """
        Get wallet balance for UNIFIED account.

        Retrieves the wallet balance for the unified trading account.
        Ensure the account is upgraded to unified account before trading.

        Returns:
            dict[str, Any]: API response containing wallet balance information
        """
        payload = {
            "accountType": "UNIFIED",
        }

        res = self._request(
            method="GET",
            path=Account.GET_WALLET_BALANCE,
            query=payload,
        )
        return res

    def get_transferable_amount(
        self,
        coins: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get transferable amount for specified coins.

        Args:
            coins: List of coin symbols to query transferable amounts for

        Returns:
            dict[str, Any]: API response containing transferable amounts
        """
        payload = {}
        if coins is not None:
            coinName = ",".join(coins)
            payload = {
                "coinName": coinName,
            }

        res = self._request(
            method="GET",
            path=Account.GET_TRANSFERABLE_AMOUNT,
            query=payload,
        )
        return res

    def upgrade_to_unified_trading_account(self) -> dict[str, Any]:
        """
        Upgrade account to unified trading account.

        Upgrades the current account to a unified trading account (UTA).
        This is required for trading on Bybit.

        Returns:
            dict[str, Any]: API response confirming the upgrade
        """
        res = self._request(
            method="POST",
            path=Account.UPGRADE_TO_UNIFIED_ACCOUNT,
            query={},
        )
        return res

    def get_borrow_history(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get borrow history.

        Args:
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing borrow history
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["currency"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Account.GET_BORROW_HISTORY,
            query=payload,
        )
        return res

    def repay_liability(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Repay liability for specified coin.

        Args:
            coin: Currency symbol to repay liability for

        Returns:
            dict[str, Any]: API response confirming repayment
        """
        payload = {}
        if coin is not None:
            payload = {
                "coin": coin,
            }

        res = self._request(
            method="POST",
            path=Account.REPAY_LIABILITY,
            query=payload,
        )
        return res

    def get_collateral_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get collateral information.

        Args:
            coin: Currency symbol to get collateral info for

        Returns:
            dict[str, Any]: API response containing collateral information
        """
        payload = {}
        if coin is not None:
            payload = {
                "coin": coin,
            }

        res = self._request(
            method="GET",
            path=Account.GET_COLLATERAL_INFO,
            query=payload,
        )
        return res

    def set_collateral_coin(
        self,
        coin: str,
        switch: str,
    ) -> dict[str, Any]:
        """
        Set collateral coin switch.

        Args:
            coin: Currency symbol
            switch: "ON" to enable or "OFF" to disable as collateral

        Returns:
            dict[str, Any]: API response confirming the setting
        """
        payload = {
            "coin": coin,
            "collateralSwitch": switch,
        }

        res = self._request(
            method="POST",
            path=Account.SET_COLLATERAL_COIN,
            query=payload,
        )
        return res

    def get_fee_rates(
        self,
        product_symbol: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """
        Get trading fee rates.

        Retrieves the trading fee rate for specified product or category.
        If product_symbol is not specified, category must be provided.

        Args:
            product_symbol: Product symbol to get fee rate for
            category: Product type (spot, linear, inverse, option)

        Returns:
            dict[str, Any]: API response containing fee rate information
        """
        payload = {}
        if product_symbol is not None:
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)

        if category is not None:
            payload["category"] = category

        res = self._request(
            method="GET",
            path=Account.GET_FEE_RATE,
            query=payload,
        )
        return res

    def get_account_info(self) -> dict[str, Any]:
        """
        Get account information.

        Retrieves general account information and settings.

        Returns:
            dict[str, Any]: API response containing account information
        """
        res = self._request(
            method="GET",
            path=Account.GET_ACCOUNT_INFO,
            query={},
        )
        return res

    def get_transaction_log(
        self,
        category: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get transaction log.

        Args:
            category: Transaction category to filter by
            coin: Currency symbol to filter by
            startTime: Start timestamp in milliseconds
            limit: Maximum number of records to return (default: 20)

        Returns:
            dict[str, Any]: API response containing transaction log
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if category is not None:
            payload["category"] = category
        if coin is not None:
            payload["currency"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = self._request(
            method="GET",
            path=Account.GET_TRANSACTION_LOG,
            query=payload,
        )
        return res

    def set_margin_mode(
        self,
        margin_mode: str,
    ) -> dict[str, Any]:
        """
        Set margin mode.

        Args:
            margin_mode: Margin mode to set. Options:
                - ISOLATED_MARGIN: Isolated margin
                - REGULAR_MARGIN: Cross margin
                - PORTFOLIO_MARGIN: Portfolio margin

        Returns:
            dict[str, Any]: API response confirming the margin mode setting
        """
        payload = {
            "setMarginMode": margin_mode,
        }

        res = self._request(
            method="POST",
            path=Account.SET_MARGIN_MODE,
            query=payload,
        )
        return res
