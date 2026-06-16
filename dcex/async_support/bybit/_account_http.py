"""Async Bybit account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for Bybit account operations."""

    async def get_wallet_balance(self) -> dict[str, Any]:
        """Get wallet balance for UNIFIED account."""
        return await self._native_private("get_wallet_balance", [])

    async def get_transferable_amount(
        self,
        coins: list[str],
    ) -> dict[str, Any]:
        """Get transferable amount for specified coins."""
        if not coins:
            raise ValueError("coins must contain at least one coin.")
        if len(coins) > 20:
            raise ValueError("coins must contain no more than 20 coins.")
        return await self._native_private(
            "get_transferable_amount",
            self._native_params(coins=",".join(coins)),
        )

    async def upgrade_to_unified_trading_account(self) -> dict[str, Any]:
        """Upgrade account to unified trading account."""
        return await self._native_private("upgrade_to_unified_trading_account", [])

    async def get_borrow_history(
        self,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get borrow history."""
        return await self._native_private(
            "get_borrow_history",
            self._native_params(coin=coin, startTime=startTime, limit=limit),
        )

    async def get_collateral_info(
        self,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return await self._native_private(
            "get_collateral_info",
            self._native_params(coin=coin),
        )

    async def get_fee_rates(
        self,
        product_symbol: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Get trading fee rates."""
        return await self._native_private(
            "get_fee_rates",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    async def get_account_info(self) -> dict[str, Any]:
        """Get account information."""
        return await self._native_private("get_account_info", [])

    async def get_transaction_log(
        self,
        category: str | None = None,
        coin: str | None = None,
        startTime: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Get transaction log."""
        return await self._native_private(
            "get_transaction_log",
            self._native_params(category=category, coin=coin, startTime=startTime, limit=limit),
        )

    async def set_margin_mode(
        self,
        margin_mode: str,
    ) -> dict[str, Any]:
        """Set margin mode."""
        return await self._native_private(
            "set_margin_mode",
            self._native_params(margin_mode=margin_mode),
        )
