"""Backpack private trade async HTTP client."""

from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Backpack private trading operations."""

    async def get_rfqs(
        self,
        product_symbol: str | None = None,
        rfq_id: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve active RFQs."""
        return await self._native_private(
            "get_rfqs",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def submit_rfq(
        self,
        product_symbol: str,
        side: str,
        *,
        quantity: str | None = None,
        quote_quantity: str | None = None,
        execution_mode: str = "AwaitAccept",
        price: str | None = None,
        client_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Submit an RFQ. Stock RFQs require quantity, not quote_quantity."""
        return await self._native_private(
            "submit_rfq",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                quoteQuantity=quote_quantity,
                executionMode=execution_mode,
                price=price,
                clientId=client_id,
            ),
        )

    async def accept_rfq_quote(
        self,
        quote_id: str,
        *,
        rfq_id: str | None = None,
        client_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Accept a firm quote using exactly one RFQ or client ID."""
        if (rfq_id is None) == (client_id is None):
            raise ValueError("Specify exactly one of rfq_id or client_id.")
        return await self._native_private(
            "accept_rfq_quote",
            self._native_params(quoteId=quote_id, rfqId=rfq_id, clientId=client_id),
        )

    async def refresh_rfq(self, rfq_id: str) -> dict[str, Any] | list[Any] | str:
        """Refresh an RFQ."""
        return await self._native_private("refresh_rfq", self._native_params(rfqId=rfq_id))

    async def cancel_rfq(
        self, *, rfq_id: str | None = None, client_id: int | None = None
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel an RFQ using exactly one RFQ or client ID."""
        if (rfq_id is None) == (client_id is None):
            raise ValueError("Specify exactly one of rfq_id or client_id.")
        return await self._native_private(
            "cancel_rfq", self._native_params(rfqId=rfq_id, clientId=client_id)
        )

    async def get_rfq_history(
        self,
        product_symbol: str | None = None,
        *,
        rfq_id: str | None = None,
        status: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get historical RFQs."""
        return await self._native_private(
            "get_rfq_history",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                status=status,
                side=side,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_quote_history(
        self,
        product_symbol: str | None = None,
        *,
        quote_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get historical RFQ quotes."""
        return await self._native_private(
            "get_quote_history",
            self._native_params(
                product_symbol=product_symbol,
                quoteId=quote_id,
                status=status,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_rfq_fill_history(
        self,
        product_symbol: str | None = None,
        *,
        rfq_id: str | None = None,
        quote_id: str | None = None,
        side: str | None = None,
        fill_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get RFQ fills."""
        return await self._native_private(
            "get_rfq_fill_history",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                quoteId=quote_id,
                side=side,
                fillType=fill_type,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_quote_fill_history(
        self,
        product_symbol: str | None = None,
        *,
        quote_id: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get quote fills."""
        return await self._native_private(
            "get_quote_fill_history",
            self._native_params(
                product_symbol=product_symbol,
                quoteId=quote_id,
                side=side,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
            ),
        )

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
        if (orderId is None) == (clientId is None):
            raise ValueError("Specify exactly one of orderId or clientId.")
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
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
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
        timeInForce: str | None = None,
        reduceOnly: bool | None = None,
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
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
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
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
        if (orderId is None) == (clientId is None):
            raise ValueError("Specify exactly one of orderId or clientId.")
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
        brokerId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place Backpack batch orders."""
        return await self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders, brokerId=brokerId),
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
        product_symbol: str,
        orderType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel Backpack open orders."""
        return await self._native_private(
            "cancel_open_orders",
            self._native_params(product_symbol=product_symbol, orderType=orderType),
        )

    async def get_fill_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        strategyId: str | None = None,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        fillType: str | None = None,
        marketType: list[str] | None = None,
        assetClass: str | None = None,
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
        strategyId: str | None = None,
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
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open positions."""
        return await self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
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
