"""
Bybit account management HTTP client module.

This module provides the AccountHTTP class for interacting with Bybit's
account management API endpoints, including wallet balance, account info,
fee rates, transaction logs, and margin settings.
"""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.account import Account


class AccountHTTP(HTTPManager):
    """
    Bybit account management HTTP client.

    This class provides methods for interacting with Bybit's account management
    API endpoints, including:
    - Wallet balance queries
    - Account information
    - Transferable amounts
    - Fee rate information
    - Transaction logs
    - Margin mode settings
    - Collateral management

    Inherits from HTTPManager for HTTP request handling and authentication.
    """

    async def get_wallet_balance(self) -> dict[str, Any]:
        """
        Get wallet balance for UNIFIED account.

        Note: Defaults to UNIFIED account and ensures the account is upgraded
        to unified account before trading.

        Returns:
            Dict containing wallet balance information
        """
        payload = {
            "accountType": "UNIFIED",
        }

        res = await self._request(
            method="GET",
            path=Account.GET_WALLET_BALANCE,
            query=payload,
        )
        return res

    async def get_transferable_amount(
        self,
        coins: list[str],
    ) -> dict[str, Any]:
        """
        Get transferable amount for specified coins.

        Args:
            coins: List of coin symbols

        Returns:
            Dict containing transferable amount information
        """
        payload = {}
        if coins is not None:
            coinName = ",".join(coins)
            payload = {
                "coinName": coinName,
            }

        res = await self._request(
            method="GET",
            path=Account.GET_TRANSFERABLE_AMOUNT,
            query=payload,
        )
        return res

    async def upgrade_to_unified_trading_account(self) -> dict[str, Any]:
        """
        Upgrade account to unified trading account.

        Returns:
            Dict containing upgrade result
        """
        res = await self._request(
            method="POST",
            path=Account.UPGRADE_TO_UNIFIED_ACCOUNT,
            query=None,
        )
        return res

    async def get_borrow_history(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get borrow history.

        Args:
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing borrow history
        """
        payload: dict[str, Any] = {
            "limit": limit,
        }
        if coin is not None:
            payload["currency"] = coin
        if startTime is not None:
            payload["startTime"] = startTime

        res = await self._request(
            method="GET",
            path=Account.GET_BORROW_HISTORY,
            query=payload,
        )
        return res

    async def repay_liability(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Repay liability for a specific coin.

        Args:
            coin: Optional coin symbol to repay liability for

        Returns:
            Dict containing repayment result
        """
        payload = {}
        if coin is not None:
            payload = {
                "coin": coin,
            }

        res = await self._request(
            method="POST",
            path=Account.REPAY_LIABILITY,
            query=payload,
        )
        return res

    async def get_collateral_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        Get collateral information.

        Args:
            coin: Optional coin symbol to filter results

        Returns:
            Dict containing collateral information
        """
        payload = {}
        if coin is not None:
            payload = {
                "coin": coin,
            }

        res = await self._request(
            method="GET",
            path=Account.GET_COLLATERAL_INFO,
            query=payload,
        )
        return res

    async def set_collateral_coin(
        self,
        coin: str,
        switch: str,
    ) -> dict[str, Any]:
        """
        Set collateral coin switch.

        Args:
            coin: Coin symbol
            switch: Switch status ("ON" or "OFF")

        Returns:
            Dict containing collateral setting result
        """
        payload = {
            "coin": coin,
            "collateralSwitch": switch,
        }

        res = await self._request(
            method="POST",
            path=Account.SET_COLLATERAL_COIN,
            query=payload,
        )
        return res

    async def get_fee_rates(
        self,
        product_symbol: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """
        Get trading fee rates.

        Args:
            product_symbol: Optional product symbol to get fee rates for
            category: Optional product category (spot, linear, inverse, option)

        Note:
            If product_symbol is not specified, please specify the category.

        Returns:
            Dict containing fee rate information
        """
        payload = {}
        if product_symbol is not None:
            payload["category"] = self.ptm.get_exchange_type(Common.BYBIT, product_symbol)
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BYBIT, product_symbol)

        if category is not None:
            payload["category"] = category

        res = await self._request(
            method="GET",
            path=Account.GET_FEE_RATE,
            query=payload,
        )
        return res

    async def get_account_info(self) -> dict[str, Any]:
        """
        Get account information.

        Returns:
            Dict containing account information
        """
        res = await self._request(
            method="GET",
            path=Account.GET_ACCOUNT_INFO,
            query=None,
        )
        return res

    async def get_transaction_log(
        self,
        category: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get transaction log.

        Args:
            category: Optional transaction category
            coin: Optional coin symbol to filter results
            startTime: Optional start time timestamp
            limit: Maximum number of records to return (default: 20)

        Returns:
            Dict containing transaction log
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

        res = await self._request(
            method="GET",
            path=Account.GET_TRANSACTION_LOG,
            query=payload,
        )
        return res

    async def set_margin_mode(
        self,
        margin_mode: str,
    ) -> dict[str, Any]:
        """
        Set margin mode.

        Args:
            margin_mode: Margin mode (ISOLATED_MARGIN, REGULAR_MARGIN, PORTFOLIO_MARGIN)

        Returns:
            Dict containing margin mode setting result
        """
        payload = {
            "setMarginMode": margin_mode,
        }

        res = await self._request(
            method="POST",
            path=Account.SET_MARGIN_MODE,
            query=payload,
        )
        return res
