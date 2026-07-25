"""Aster V3 private trading HTTP client."""

from typing import Any

from ..enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Aster V3 private trading operations."""

    def place_spot_order(
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
        return self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                type_=type_,
                timeInForce=timeInForce,
                quantity=quantity,
                quoteOrderQty=quoteOrderQty,
                price=price,
                newClientOrderId=newClientOrderId,
                stopPrice=stopPrice,
            ),
        )

    def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def get_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "get_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def get_spot_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "get_spot_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster spot orders."""
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def cancel_all_spot_open_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all or selected open Aster spot orders for a symbol."""
        return self._native_private(
            "cancel_all_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    def get_spot_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot order history."""
        return self._native_private(
            "get_spot_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def get_spot_user_trades(
        self,
        product_symbol: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account trades."""
        return self._native_private(
            "get_spot_user_trades",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                fromId=fromId,
                limit=limit,
            ),
        )

    def place_futures_order(
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
        pegPriceType: str | None = None,
        pegOffset: str | None = None,
        stpMode: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures order."""
        return self._native_private(
            "place_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                positionSide=positionSide,
                type_=type_,
                timeInForce=timeInForce,
                quantity=quantity,
                reduceOnly=reduceOnly,
                price=price,
                newClientOrderId=newClientOrderId,
                stopPrice=stopPrice,
                closePosition=closePosition,
                activationPrice=activationPrice,
                callbackRate=callbackRate,
                workingType=workingType,
                priceProtect=priceProtect,
                newOrderRespType=newOrderRespType,
                pegPriceType=pegPriceType,
                pegOffset=pegOffset,
                stpMode=stpMode,
            ),
        )

    def modify_futures_order(
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
        return self._native_private(
            "modify_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                quantity=quantity,
                price=price,
            ),
        )

    def place_futures_chase_order(
        self,
        product_symbol: str,
        side: str | OrderSide,
        quantityUnit: str,
        quantity: str,
        positionSide: str | None = None,
        reduceOnly: bool | None = None,
        chaseOffset: str | None = None,
        chaseOffsetType: str | None = None,
        maxChaseOffset: str | None = None,
        maxChaseOffsetType: str | None = None,
        timeInForce: str | None = None,
        clientStrategyId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures chase order."""
        return self._native_private(
            "place_futures_chase_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                positionSide=positionSide,
                quantityUnit=quantityUnit,
                quantity=quantity,
                reduceOnly=reduceOnly,
                chaseOffset=chaseOffset,
                chaseOffsetType=chaseOffsetType,
                maxChaseOffset=maxChaseOffset,
                maxChaseOffsetType=maxChaseOffsetType,
                timeInForce=timeInForce,
                clientStrategyId=clientStrategyId,
            ),
        )

    def place_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Place multiple Aster futures orders."""
        return self._native_private(
            "place_futures_batch_orders",
            self._native_params(batchOrders=batchOrders),
        )

    def get_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "get_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "cancel_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def cancel_all_futures_open_orders(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all open Aster futures orders for a symbol."""
        return self._native_private(
            "cancel_all_futures_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel multiple Aster futures orders."""
        return self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    def set_futures_countdown_cancel_all(
        self,
        product_symbol: str,
        countdownTime: int,
    ) -> dict[str, Any] | list[Any]:
        """Set automatic cancellation of Aster futures open orders."""
        return self._native_private(
            "set_futures_countdown_cancel_all",
            self._native_params(product_symbol=product_symbol, countdownTime=countdownTime),
        )

    def get_futures_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return self._native_private(
            "get_futures_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster futures orders."""
        return self._native_private(
            "get_futures_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def get_futures_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures order history."""
        return self._native_private(
            "get_futures_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int,
    ) -> dict[str, Any] | list[Any]:
        """Change Aster futures initial leverage."""
        return self._native_private(
            "set_futures_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage),
        )

    def set_futures_margin_type(
        self,
        product_symbol: str,
        marginType: str,
    ) -> dict[str, Any] | list[Any]:
        """Change an Aster futures symbol margin type."""
        return self._native_private(
            "set_futures_margin_type",
            self._native_params(product_symbol=product_symbol, marginType=marginType),
        )

    def place_futures_strategy_order(
        self,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
        clientStrategyId: str | None = None,
        builder: str | None = None,
        feeRate: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures strategy order."""
        return self._native_private(
            "place_futures_strategy_order",
            self._native_params(
                clientStrategyId=clientStrategyId,
                strategyType=strategyType,
                subOrderList=subOrderList,
                builder=builder,
                feeRate=feeRate,
            ),
        )

    def update_futures_strategy_order(
        self,
        strategyId: int,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Update an Aster futures strategy order."""
        return self._native_private(
            "update_futures_strategy_order",
            self._native_params(
                strategyId=strategyId,
                strategyType=strategyType,
                subOrderList=subOrderList,
            ),
        )

    def get_futures_strategy_open_order(
        self,
        strategyType: str,
        strategyId: int | None = None,
        clientStrategyId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an open Aster futures strategy order."""
        return self._native_private(
            "get_futures_strategy_open_order",
            self._native_params(
                strategyId=strategyId,
                clientStrategyId=clientStrategyId,
                strategyType=strategyType,
            ),
        )

    def get_futures_strategy_history_order(
        self,
        strategyType: str,
        strategyId: int | None = None,
        clientStrategyId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query Aster futures strategy-order history."""
        return self._native_private(
            "get_futures_strategy_history_order",
            self._native_params(
                strategyId=strategyId,
                clientStrategyId=clientStrategyId,
                strategyType=strategyType,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )
