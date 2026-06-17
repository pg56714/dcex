"""BitMart private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for BitMart private account APIs."""

    def get_account_balance(
        self,
        currency: str | None = None,
        needUsdValuation: bool = False,
    ) -> dict[str, Any]:
        """Get BitMart account balance information."""
        return self._native_private(
            "get_account_balance",
            self._native_params(currency=currency, needUsdValuation=needUsdValuation),
        )

    def get_account_currencies(
        self,
        currencies: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get BitMart account currency metadata."""
        return self._native_private(
            "get_account_currencies",
            self._native_params(
                currencies=",".join(currencies) if currencies is not None else None
            ),
        )

    def get_spot_wallet(self) -> dict[str, Any]:
        """Get BitMart Spot wallet balance."""
        return self._native_private("get_spot_wallet", [])

    def get_deposit_address(
        self,
        currency: str,
    ) -> dict[str, Any]:
        """Get BitMart deposit address for a currency."""
        return self._native_private(
            "get_deposit_address",
            self._native_params(currency=currency),
        )

    def get_contract_assets(self) -> dict[str, Any]:
        """Get BitMart contract account assets."""
        return self._native_private("get_contract_assets", [])
