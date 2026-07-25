"""Async Bybit account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for Bybit account operations."""

    async def get_wallet_balance(self, coin: str | None = None) -> dict[str, Any]:
        """Get wallet balance for UNIFIED account."""
        return await self._native_private("get_wallet_balance", self._native_params(coin=coin))

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
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get borrow history."""
        return await self._native_private(
            "get_borrow_history",
            self._native_params(
                coin=coin,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_collateral_info(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return await self._native_private(
            "get_collateral_info",
            self._native_params(currency=currency),
        )

    async def _request_fee_rates(
        self,
        method_name: str,
        product_symbol: str | None = None,
        baseCoin: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            method_name,
            self._native_params(product_symbol=product_symbol, baseCoin=baseCoin),
        )

    async def get_spot_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit Spot trading fee rates."""
        return await self._request_fee_rates("get_spot_fee_rates", product_symbol, baseCoin)

    async def get_linear_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit linear-contract trading fee rates."""
        return await self._request_fee_rates("get_linear_fee_rates", product_symbol, baseCoin)

    async def get_inverse_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit inverse-contract trading fee rates."""
        return await self._request_fee_rates("get_inverse_fee_rates", product_symbol, baseCoin)

    async def get_option_fee_rates(
        self, product_symbol: str | None = None, baseCoin: str | None = None
    ) -> dict[str, Any]:
        """Get Bybit option trading fee rates."""
        return await self._request_fee_rates("get_option_fee_rates", product_symbol, baseCoin)

    async def get_account_info(self) -> dict[str, Any]:
        """Get account information."""
        return await self._native_private("get_account_info", [])

    async def get_transaction_log(
        self,
        accountType: str | None = None,
        category: str | None = None,
        coin: str | None = None,
        baseCoin: str | None = None,
        type_: str | None = None,
        transSubType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get transaction log."""
        return await self._native_private(
            "get_transaction_log",
            self._native_params(
                accountType=accountType,
                category=category,
                coin=coin,
                baseCoin=baseCoin,
                type=type_,
                transSubType=transSubType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
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
