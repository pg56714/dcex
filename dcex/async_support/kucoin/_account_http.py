"""KuCoin async account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
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
        symbol: str | None = None,
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

    async def get_transfer_quotas(
        self,
        currency: str,
        account_type: str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve transferable balance for one KuCoin account type."""
        return await self._native_private(
            "get_transfer_quotas",
            self._native_params(currency=currency, account_type=account_type, tag=tag),
        )

    async def flex_transfer(
        self,
        currency: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
        clientOid: str | None = None,
        transfer_type: str = "INTERNAL",
        fromUserId: str | None = None,
        toUserId: str | None = None,
    ) -> dict[str, Any]:
        """Transfer funds between KuCoin account types."""
        return await self._native_private(
            "flex_transfer",
            self._native_params(
                currency=currency,
                amount=amount,
                fromAccountType=fromAccountType,
                toAccountType=toAccountType,
                clientOid=clientOid,
                transfer_type=transfer_type,
                fromUserId=fromUserId,
                toUserId=toUserId,
            ),
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
