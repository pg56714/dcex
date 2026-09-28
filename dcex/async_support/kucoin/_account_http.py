"""KuCoin async account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import AccountHTTPTransfersHTTP


class AccountHTTP(AccountHTTPTransfersHTTP, HTTPManager):
    """Async HTTP client for KuCoin account API operations."""

    async def get_spot_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current KuCoin Spot maker and taker fee rates."""
        return await self._native_private(
            "get_spot_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_fee_rates(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve current KuCoin Futures maker and taker fee rates."""
        return await self._native_private(
            "get_futures_fee_rates",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_uta_fee_rates(
        self,
        tradeType: str,
        symbol: str,
    ) -> dict[str, Any]:
        """Retrieve KuCoin UTA actual fee rates for up to ten symbols."""
        return await self._native_private(
            "get_uta_fee_rates",
            self._native_params(tradeType=tradeType, symbol=symbol),
        )

    async def get_account_balance(
        self,
        currency: str | None = None,
        type: str | None = None,  # noqa: A002
    ) -> dict[str, Any]:
        """Retrieve account balance information."""
        return await self._native_private(
            "get_account_balance",
            self._native_params(currency=currency, type=type),
        )

    async def get_subaccounts(
        self,
        currentPage: int = 1,
        pageSize: int = 10,
    ) -> dict[str, Any]:
        """Retrieve the Classic account's paginated sub-account summary."""
        return await self._native_private(
            "get_subaccounts",
            self._native_params(currentPage=currentPage, pageSize=pageSize),
        )

    async def get_subaccount_balance(
        self,
        subUserId: str,
        includeBaseAmount: bool | None = None,
        baseCurrency: str | None = None,
        baseAmount: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve balances for one Classic sub-account."""
        return await self._native_private(
            "get_subaccount_balance",
            self._native_params(
                subUserId=subUserId,
                includeBaseAmount=includeBaseAmount,
                baseCurrency=baseCurrency,
                baseAmount=baseAmount,
            ),
        )

    async def get_spot_subaccount_balances(
        self,
        currentPage: int = 1,
        pageSize: int = 10,
    ) -> dict[str, Any]:
        """Retrieve paginated Classic Spot balances for all sub-accounts."""
        return await self._native_private(
            "get_spot_subaccount_balances",
            self._native_params(currentPage=currentPage, pageSize=pageSize),
        )

    async def get_futures_subaccount_balances(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Classic Futures balances for all sub-accounts."""
        return await self._native_private(
            "get_futures_subaccount_balances",
            self._native_params(currency=currency),
        )

    async def get_uta_subaccounts(
        self,
        currentPage: int = 1,
        pageSize: int = 10,
    ) -> dict[str, Any]:
        """Retrieve the UTA account's paginated sub-account list."""
        return await self._native_private(
            "get_uta_subaccounts",
            self._native_params(currentPage=currentPage, pageSize=pageSize),
        )

    async def get_uta_subaccount_currency_assets(
        self,
        uid: int | str | None = None,
        pageSize: int = 50,
        lastId: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve currency-level assets held by UTA sub-accounts."""
        return await self._native_private(
            "get_uta_subaccount_currency_assets",
            self._native_params(uid=uid, pageSize=pageSize, lastId=lastId),
        )

    async def get_futures_account(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures account overview."""
        return await self._native_private(
            "get_futures_account",
            self._native_params(currency=currency),
        )

    async def get_futures_positions(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve KuCoin futures positions."""
        return await self._native_private(
            "get_futures_positions",
            self._native_params(currency=currency),
        )

    async def get_futures_position(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve one KuCoin futures position."""
        return await self._native_private(
            "get_futures_position",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_position_mode(self) -> dict[str, Any]:
        """Retrieve KuCoin futures position mode."""
        return await self._native_private("get_futures_position_mode", [])

    async def get_futures_cross_margin_leverage(self, product_symbol: str) -> dict[str, Any]:
        """Retrieve cross-margin leverage for one KuCoin futures contract."""
        return await self._native_private(
            "get_futures_cross_margin_leverage",
            self._native_params(product_symbol=product_symbol),
        )

    async def modify_futures_cross_margin_leverage(
        self,
        product_symbol: str,
        leverage: int | str,
    ) -> dict[str, Any]:
        """Modify cross-margin leverage for one KuCoin futures contract."""
        return await self._native_private(
            "modify_futures_cross_margin_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage),
        )

    async def get_uta_positions(
        self,
        *,
        product_symbol: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Get KuCoin UTA V2 futures positions and liquidation risk."""
        return await self._native_private(
            "get_uta_positions",
            self._native_params(
                product_symbol=product_symbol, pageNumber=page_number, pageSize=page_size
            ),
        )

    async def get_uta_account_balance(self) -> dict[str, Any]:
        """Get KuCoin UTA V2 asset balances."""
        return await self._native_private("get_uta_account_balance", [])

    async def get_uta_account_overview(self) -> dict[str, Any]:
        """Get KuCoin UTA account-level margin and risk summary (V1 route)."""
        return await self._native_private("get_uta_account_overview", [])
