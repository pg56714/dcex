"""Backpack private trade async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Backpack private trading operations."""

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)

    async def get_open_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack open order."""
        if orderId is None and clientId is None:
            raise ValueError("Specify orderId or clientId.")
        return await self._native_private(
            "get_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientId=clientId,
            ),
        )

    async def place_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        quantity: str | None = None,
        price: str | None = None,
        quoteQuantity: str | None = None,
        clientId: int | None = None,
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack order."""
        return await self._native_private(
            "place_order",
            self._native_params(**locals()),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str | None = None,
        quoteQuantity: str | None = None,
        clientId: int | None = None,
        reduceOnly: bool | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack market order."""
        return await self._native_private(
            "place_market_order",
            self._native_params(**locals()),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        clientId: int | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack limit order."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(**locals()),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel one Backpack open order."""
        if orderId is None and clientId is None:
            raise ValueError("Specify orderId or clientId.")
        return await self._native_private(
            "cancel_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientId=clientId,
            ),
        )

    async def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any] | str:
        """Place Backpack batch orders."""
        return await self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders),
        )

    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open orders."""
        return await self._native_private(
            "get_open_orders",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    async def cancel_open_orders(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel Backpack open orders."""
        return await self._native_private(
            "cancel_open_orders",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    async def get_fill_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        marketType: list[str] | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack fill history."""
        return await self._native_private(
            "get_fill_history",
            self._native_params(**locals()),
        )

    async def get_order_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        marketType: list[str] | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order history."""
        return await self._native_private(
            "get_order_history",
            self._native_params(**locals()),
        )

    async def get_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open positions."""
        return await self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_funding_payments(
        self,
        product_symbol: str | None = None,
        subaccountId: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack funding payments."""
        return await self._native_private(
            "get_funding_payments",
            self._native_params(**locals()),
        )

    async def get_position_history(
        self,
        product_symbol: str | None = None,
        state: str | None = None,
        marketType: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack position history."""
        return await self._native_private(
            "get_position_history",
            self._native_params(**locals()),
        )
