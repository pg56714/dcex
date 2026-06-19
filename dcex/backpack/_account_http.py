"""Backpack private account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for Backpack private account operations."""

    def get_account(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack account settings and limits."""
        return self._native_private("get_account", [])

    def get_max_borrow_quantity(self, symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max borrow quantity."""
        return self._native_private(
            "get_max_borrow_quantity",
            self._native_params(symbol=symbol),
        )

    def get_max_order_quantity(
        self,
        symbol: str,
        side: str,
        price: str | None = None,
        reduceOnly: bool | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max order quantity."""
        return self._native_private(
            "get_max_order_quantity",
            self._native_params(**locals()),
        )

    def get_max_withdrawal_quantity(
        self,
        symbol: str,
        autoBorrow: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max withdrawal quantity."""
        return self._native_private(
            "get_max_withdrawal_quantity",
            self._native_params(**locals()),
        )

    def get_borrow_lend_positions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend positions."""
        return self._native_private("get_borrow_lend_positions", [])

    def get_borrow_history(
        self,
        symbol: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend operation history."""
        return self._native_private(
            "get_borrow_history",
            self._native_params(**locals()),
        )

    def get_interest_history(
        self,
        symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend interest history."""
        return self._native_private(
            "get_interest_history",
            self._native_params(**locals()),
        )

    def get_borrow_position_history(
        self,
        symbol: str | None = None,
        side: str | None = None,
        state: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend position history."""
        return self._native_private(
            "get_borrow_position_history",
            self._native_params(**locals()),
        )

    def get_balances(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack balances."""
        return self._native_private("get_balances", [])

    def convert_dust(self, symbol: str) -> dict[str, Any] | list[Any] | str:
        """Convert a Backpack dust balance to USDC."""
        return self._native_private("convert_dust", self._native_params(symbol=symbol))

    def get_private_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack private collateral data."""
        return self._native_private("get_private_collateral", [])

    def get_deposits(
        self,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        excludePlatform: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack deposit history."""
        return self._native_private(
            "get_deposits",
            self._native_params(**locals()),
        )

    def get_deposit_address(self, blockchain: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack deposit address for a blockchain."""
        return self._native_private(
            "get_deposit_address",
            self._native_params(blockchain=blockchain),
        )

    def get_withdrawals(
        self,
        id: int | None = None,
        clientId: str | None = None,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack withdrawal history."""
        return self._native_private(
            "get_withdrawals",
            self._native_params(**locals()),
        )

    def get_dust_conversion_history(
        self,
        id: int | None = None,
        symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack dust conversion history."""
        return self._native_private(
            "get_dust_conversion_history",
            self._native_params(**locals()),
        )

    def get_settlement_history(
        self,
        limit: int | None = None,
        offset: int | None = None,
        source: str | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack settlement history."""
        return self._native_private(
            "get_settlement_history",
            self._native_params(**locals()),
        )
