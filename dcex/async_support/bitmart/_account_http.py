"""BitMart async private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """Async HTTP client for BitMart private account APIs."""

    async def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current BitMart Spot maker and taker fee rates."""
        return await self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current BitMart Futures maker and taker fee rates."""
        return await self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_account_balance(
        self,
        currency: str | None = None,
        needUsdValuation: bool = False,
    ) -> dict[str, Any]:
        """Get BitMart account balance information."""
        return await self._native_private(
            "get_account_balance",
            self._native_params(currency=currency, needUsdValuation=needUsdValuation),
        )

    async def get_account_currencies(
        self,
        currencies: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get BitMart account currency metadata."""
        return await self._native_private(
            "get_account_currencies",
            self._native_params(
                currencies=",".join(currencies) if currencies is not None else None
            ),
        )

    async def get_spot_wallet(self) -> dict[str, Any]:
        """Get BitMart Spot wallet balance."""
        return await self._native_private("get_spot_wallet", [])

    async def get_deposit_address(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """Get BitMart deposit address for a currency."""
        return await self._native_private(
            "get_deposit_address",
            self._native_params(currency=currency),
        )

    async def get_contract_assets(self) -> dict[str, Any]:
        """Get BitMart contract account assets."""
        return await self._native_private("get_contract_assets", [])
