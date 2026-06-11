"""Backpack private account HTTP client."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.account import Account, BorrowLend, Capital


class AccountHTTP(HTTPManager):
    """HTTP client for Backpack private account operations."""

    def get_account(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack account settings and limits."""
        return self._request("GET", Account.ACCOUNT, signed=True, instruction="accountQuery")

    def get_max_borrow_quantity(self, symbol: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max borrow quantity."""
        return self._request(
            "GET",
            Account.MAX_BORROW_QUANTITY,
            {"symbol": symbol},
            signed=True,
            instruction="maxBorrowQuantity",
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
        return self._request(
            "GET",
            Account.MAX_ORDER_QUANTITY,
            {
                "symbol": symbol,
                "side": side,
                "price": price,
                "reduceOnly": reduceOnly,
                "autoBorrow": autoBorrow,
                "autoBorrowRepay": autoBorrowRepay,
                "autoLendRedeem": autoLendRedeem,
            },
            signed=True,
            instruction="maxOrderQuantity",
        )

    def get_max_withdrawal_quantity(
        self,
        symbol: str,
        autoBorrow: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack max withdrawal quantity."""
        return self._request(
            "GET",
            Account.MAX_WITHDRAWAL_QUANTITY,
            {
                "symbol": symbol,
                "autoBorrow": autoBorrow,
                "autoLendRedeem": autoLendRedeem,
            },
            signed=True,
            instruction="maxWithdrawalQuantity",
        )

    def get_borrow_lend_positions(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend positions."""
        return self._request(
            "GET",
            BorrowLend.POSITIONS,
            signed=True,
            instruction="borrowLendPositionQuery",
        )

    def get_borrow_history(
        self,
        symbol: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend operation history."""
        return self._request(
            "GET",
            BorrowLend.BORROW_HISTORY,
            {
                "symbol": symbol,
                "side": side,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="borrowHistoryQueryAll",
        )

    def get_interest_history(
        self,
        symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack borrow/lend interest history."""
        return self._request(
            "GET",
            BorrowLend.INTEREST_HISTORY,
            {
                "symbol": symbol,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="interestHistoryQueryAll",
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
        return self._request(
            "GET",
            BorrowLend.POSITION_HISTORY,
            {
                "symbol": symbol,
                "side": side,
                "state": state,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="borrowPositionHistoryQueryAll",
        )

    def get_balances(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack balances."""
        return self._request("GET", Capital.BALANCES, signed=True, instruction="balanceQuery")

    def convert_dust(self, symbol: str) -> dict[str, Any] | list[Any] | str:
        """Convert a Backpack dust balance to USDC."""
        return self._request(
            "POST",
            Capital.CONVERT_DUST,
            {"symbol": symbol},
            signed=True,
            instruction="convertDust",
        )

    def get_private_collateral(self) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack private collateral data."""
        return self._request(
            "GET",
            Capital.COLLATERAL,
            signed=True,
            instruction="collateralQuery",
        )

    def get_deposits(
        self,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        excludePlatform: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack deposit history."""
        return self._request(
            "GET",
            Capital.DEPOSITS,
            {
                "from": from_,
                "to": to,
                "limit": limit,
                "offset": offset,
                "excludePlatform": excludePlatform,
            },
            signed=True,
            instruction="depositQueryAll",
        )

    def get_deposit_address(self, blockchain: str) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack deposit address for a blockchain."""
        return self._request(
            "GET",
            Capital.DEPOSIT_ADDRESS,
            {"blockchain": blockchain},
            signed=True,
            instruction="depositAddressQuery",
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
        return self._request(
            "GET",
            Capital.WITHDRAWALS,
            {
                "id": id,
                "clientId": clientId,
                "from": from_,
                "to": to,
                "limit": limit,
                "offset": offset,
            },
            signed=True,
            instruction="withdrawalQueryAll",
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
        return self._request(
            "GET",
            Capital.DUST_CONVERSION_HISTORY,
            {
                "id": id,
                "symbol": symbol,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="dustHistoryQueryAll",
        )

    def get_settlement_history(
        self,
        limit: int | None = None,
        offset: int | None = None,
        source: str | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack settlement history."""
        return self._request(
            "GET",
            Capital.SETTLEMENT_HISTORY,
            {
                "limit": limit,
                "offset": offset,
                "source": source,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="settlementHistoryQueryAll",
        )
