"""Aster V3 private trading async HTTP client."""

from typing import Any

from ...enums import OrderSide
from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import FuturesTrade, SpotTrade


class TradeHTTP(HTTPManager):
    """HTTP client for Aster V3 private trading operations."""

    def _trade_symbol(self, product_symbol: str) -> str:
        if "-" not in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.ASTER, product_symbol)

    @staticmethod
    def _side(side: str | OrderSide) -> str:
        if isinstance(side, OrderSide):
            return side.to_exchange(Common.ASTER)
        return side.upper()

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str | OrderSide,
        type_: str,
        quantity: str | None = None,
        quoteOrderQty: str | None = None,
        price: str | None = None,
        timeInForce: str | None = None,
        newClientOrderId: str | None = None,
        stopPrice: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster spot order."""
        return await self._request(
            "POST",
            SpotTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "side": self._side(side),
                "type": type_,
                "timeInForce": timeInForce,
                "quantity": quantity,
                "quoteOrderQty": quoteOrderQty,
                "price": price,
                "newClientOrderId": newClientOrderId,
                "stopPrice": stopPrice,
            },
        )

    async def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "DELETE",
            SpotTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def get_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "GET",
            SpotTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def get_spot_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "GET",
            SpotTrade.OPEN_ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster spot orders."""
        symbol = self._trade_symbol(product_symbol) if product_symbol else None
        return await self._request("GET", SpotTrade.OPEN_ORDERS, {"symbol": symbol})

    async def cancel_all_spot_open_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all or selected open Aster spot orders for a symbol."""
        return await self._request(
            "DELETE",
            SpotTrade.ALL_OPEN_ORDERS,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderIdList": orderIdList,
                "origClientOrderIdList": origClientOrderIdList,
            },
        )

    async def get_spot_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot order history."""
        return await self._request(
            "GET",
            SpotTrade.ALL_ORDERS,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def get_spot_user_trades(
        self,
        product_symbol: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account trades."""
        symbol = self._trade_symbol(product_symbol) if product_symbol else None
        return await self._request(
            "GET",
            SpotTrade.USER_TRADES,
            {
                "symbol": symbol,
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "fromId": fromId,
                "limit": limit,
            },
        )

    async def place_futures_order(
        self,
        product_symbol: str,
        side: str | OrderSide,
        type_: str,
        quantity: str | None = None,
        positionSide: str | None = None,
        timeInForce: str | None = None,
        reduceOnly: bool | None = None,
        price: str | None = None,
        newClientOrderId: str | None = None,
        stopPrice: str | None = None,
        closePosition: bool | None = None,
        activationPrice: str | None = None,
        callbackRate: str | None = None,
        workingType: str | None = None,
        priceProtect: bool | None = None,
        newOrderRespType: str | None = None,
        stpMode: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures order."""
        return await self._request(
            "POST",
            FuturesTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "side": self._side(side),
                "positionSide": positionSide,
                "type": type_,
                "timeInForce": timeInForce,
                "quantity": quantity,
                "reduceOnly": reduceOnly,
                "price": price,
                "newClientOrderId": newClientOrderId,
                "stopPrice": stopPrice,
                "closePosition": closePosition,
                "activationPrice": activationPrice,
                "callbackRate": callbackRate,
                "workingType": workingType,
                "priceProtect": priceProtect,
                "newOrderRespType": newOrderRespType,
                "stpMode": stpMode,
            },
        )

    async def modify_futures_order(
        self,
        product_symbol: str,
        quantity: str,
        price: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Modify an open Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "PUT",
            FuturesTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
                "quantity": quantity,
                "price": price,
            },
        )

    async def place_futures_chase_order(
        self,
        product_symbol: str,
        side: str | OrderSide,
        quantityUnit: str,
        quantity: str,
        chaseOffset: str,
        chaseOffsetType: str,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
        maxChaseOffset: str | None = None,
        maxChaseOffsetType: str | None = None,
        priceLimit: str | None = None,
        timeInForce: str | None = None,
        clientStrategyId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures chase order."""
        return await self._request(
            "POST",
            FuturesTrade.CHASE,
            {
                "symbol": self._trade_symbol(product_symbol),
                "side": self._side(side),
                "positionSide": positionSide,
                "quantityUnit": quantityUnit,
                "quantity": quantity,
                "reduceOnly": reduceOnly,
                "chaseOffset": chaseOffset,
                "chaseOffsetType": chaseOffsetType,
                "maxChaseOffset": maxChaseOffset,
                "maxChaseOffsetType": maxChaseOffsetType,
                "priceLimit": priceLimit,
                "timeInForce": timeInForce,
                "clientStrategyId": clientStrategyId,
            },
        )

    async def place_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Place multiple Aster futures orders."""
        resolved = []
        for order in batchOrders:
            normalized = dict(order)
            product_symbol = normalized.pop("product_symbol", None)
            if product_symbol is not None:
                normalized["symbol"] = self._trade_symbol(str(product_symbol))
            if "side" in normalized:
                normalized["side"] = self._side(normalized["side"])
            resolved.append(normalized)
        return await self._request(
            "POST",
            FuturesTrade.BATCH_ORDERS,
            {"batchOrders": resolved},
        )

    async def get_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "GET",
            FuturesTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "DELETE",
            FuturesTrade.ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def cancel_all_futures_open_orders(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all open Aster futures orders for a symbol."""
        return await self._request(
            "DELETE",
            FuturesTrade.ALL_OPEN_ORDERS,
            {"symbol": self._trade_symbol(product_symbol)},
        )

    async def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel multiple Aster futures orders."""
        return await self._request(
            "DELETE",
            FuturesTrade.BATCH_ORDERS,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderIdList": orderIdList,
                "origClientOrderIdList": origClientOrderIdList,
            },
        )

    async def set_futures_countdown_cancel_all(
        self,
        product_symbol: str,
        countdownTime: int,
    ) -> dict[str, Any] | list[Any]:
        """Set automatic cancellation of Aster futures open orders."""
        return await self._request(
            "POST",
            FuturesTrade.COUNTDOWN_CANCEL_ALL,
            {
                "symbol": self._trade_symbol(product_symbol),
                "countdownTime": countdownTime,
            },
        )

    async def get_futures_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._request(
            "GET",
            FuturesTrade.OPEN_ORDER,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "origClientOrderId": origClientOrderId,
            },
        )

    async def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster futures orders."""
        symbol = self._trade_symbol(product_symbol) if product_symbol else None
        return await self._request("GET", FuturesTrade.OPEN_ORDERS, {"symbol": symbol})

    async def get_futures_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures order history."""
        return await self._request(
            "GET",
            FuturesTrade.ALL_ORDERS,
            {
                "symbol": self._trade_symbol(product_symbol),
                "orderId": orderId,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )

    async def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int,
    ) -> dict[str, Any] | list[Any]:
        """Change Aster futures initial leverage."""
        return await self._request(
            "POST",
            FuturesTrade.LEVERAGE,
            {"symbol": self._trade_symbol(product_symbol), "leverage": leverage},
        )

    async def set_futures_margin_type(
        self,
        product_symbol: str,
        marginType: str,
    ) -> dict[str, Any] | list[Any]:
        """Change an Aster futures symbol margin type."""
        return await self._request(
            "POST",
            FuturesTrade.MARGIN_TYPE,
            {"symbol": self._trade_symbol(product_symbol), "marginType": marginType},
        )

    async def place_futures_strategy_order(
        self,
        clientStrategyId: str,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures strategy order."""
        return await self._request(
            "POST",
            FuturesTrade.PLACE_STRATEGY_ORDER,
            {
                "clientStrategyId": clientStrategyId,
                "strategyType": strategyType,
                "subOrderList": subOrderList,
            },
        )

    async def update_futures_strategy_order(
        self,
        strategyId: str,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Update an Aster futures strategy order."""
        return await self._request(
            "POST",
            FuturesTrade.UPDATE_STRATEGY_ORDER,
            {
                "strategyId": strategyId,
                "strategyType": strategyType,
                "subOrderList": subOrderList,
            },
        )

    async def get_futures_strategy_open_order(
        self,
        strategyType: str,
        strategyId: str | None = None,
        clientStrategyId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an open Aster futures strategy order."""
        return await self._request(
            "GET",
            FuturesTrade.STRATEGY_OPEN_ORDER,
            {
                "strategyId": strategyId,
                "clientStrategyId": clientStrategyId,
                "strategyType": strategyType,
            },
        )

    async def get_futures_strategy_history_order(
        self,
        strategyType: str,
        strategyId: str | None = None,
        clientStrategyId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query Aster futures strategy-order history."""
        return await self._request(
            "GET",
            FuturesTrade.STRATEGY_HISTORY_ORDER,
            {
                "strategyId": strategyId,
                "clientStrategyId": clientStrategyId,
                "strategyType": strategyType,
                "startTime": startTime,
                "endTime": endTime,
                "limit": limit,
            },
        )
