"""Backpack private trade async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import Order, Position


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
        return await self._request(
            "GET",
            Order.ORDER,
            {"symbol": self._symbol(product_symbol), "orderId": orderId, "clientId": clientId},
            signed=True,
            instruction="orderQuery",
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
        return await self._request(
            "POST",
            Order.ORDER,
            {
                "symbol": self._symbol(product_symbol),
                "side": side,
                "orderType": orderType,
                "quantity": quantity,
                "price": price,
                "quoteQuantity": quoteQuantity,
                "clientId": clientId,
                "timeInForce": timeInForce,
                "postOnly": postOnly,
                "reduceOnly": reduceOnly,
                "selfTradePrevention": selfTradePrevention,
                "autoBorrow": autoBorrow,
                "autoBorrowRepay": autoBorrowRepay,
                "autoLend": autoLend,
                "autoLendRedeem": autoLendRedeem,
            },
            signed=True,
            instruction="orderExecute",
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
        return await self.place_order(
            product_symbol,
            side,
            "Market",
            quantity=quantity,
            quoteQuantity=quoteQuantity,
            clientId=clientId,
            reduceOnly=reduceOnly,
            autoBorrow=autoBorrow,
            autoBorrowRepay=autoBorrowRepay,
            autoLend=autoLend,
            autoLendRedeem=autoLendRedeem,
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
        return await self.place_order(
            product_symbol,
            side,
            "Limit",
            quantity=quantity,
            price=price,
            timeInForce=timeInForce,
            clientId=clientId,
            postOnly=postOnly,
            reduceOnly=reduceOnly,
            autoBorrow=autoBorrow,
            autoBorrowRepay=autoBorrowRepay,
            autoLend=autoLend,
            autoLendRedeem=autoLendRedeem,
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
        return await self._request(
            "DELETE",
            Order.ORDER,
            {"symbol": self._symbol(product_symbol), "orderId": orderId, "clientId": clientId},
            signed=True,
            instruction="orderCancel",
        )

    async def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any] | str:
        """Place Backpack batch orders."""
        resolved_orders = [
            {
                **order,
                "symbol": self._symbol(order["product_symbol"])
                if "product_symbol" in order
                else order.get("symbol"),
            }
            for order in orders
        ]
        for order in resolved_orders:
            order.pop("product_symbol", None)
        return await self._request(
            "POST",
            Order.ORDERS,
            resolved_orders,
            signed=True,
            instruction="orderExecute",
        )

    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open orders."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Order.ORDERS,
            {"symbol": symbol, "marketType": marketType},
            signed=True,
            instruction="orderQueryAll",
        )

    async def cancel_open_orders(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel Backpack open orders."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "DELETE",
            Order.ORDERS,
            {"symbol": symbol, "marketType": marketType},
            signed=True,
            instruction="orderCancelAll",
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
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Order.FILLS,
            {
                "symbol": symbol,
                "orderId": orderId,
                "limit": limit,
                "offset": offset,
                "marketType": marketType,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="fillHistoryQueryAll",
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
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Order.ORDER_HISTORY,
            {
                "symbol": symbol,
                "orderId": orderId,
                "limit": limit,
                "offset": offset,
                "marketType": marketType,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="orderHistoryQueryAll",
        )

    async def get_open_positions(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open positions."""
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Position.POSITION,
            {"symbol": symbol},
            signed=True,
            instruction="positionQuery",
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
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Position.FUNDING,
            {
                "symbol": symbol,
                "subaccountId": subaccountId,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="fundingHistoryQueryAll",
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
        symbol = self._symbol(product_symbol) if product_symbol is not None else None
        return await self._request(
            "GET",
            Position.POSITION_HISTORY,
            {
                "symbol": symbol,
                "state": state,
                "marketType": marketType,
                "limit": limit,
                "offset": offset,
                "sortDirection": sortDirection,
            },
            signed=True,
            instruction="positionHistoryQueryAll",
        )
