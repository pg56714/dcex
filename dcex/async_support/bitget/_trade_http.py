"""Bitget private trade async HTTP client backed by Rust."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Bitget private trading operations."""

    async def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: str,
        price: str | None = None,
        force: str | None = None,
        clientOid: str | None = None,
        triggerPrice: str | None = None,
        tpslType: str | None = None,
        requestTime: int | str | None = None,
        receiveWindow: int | str | None = None,
        stpMode: str | None = None,
        presetTakeProfitPrice: str | None = None,
        executeTakeProfitPrice: str | None = None,
        presetStopLossPrice: str | None = None,
        executeStopLossPrice: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot order."""
        return await self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                size=size,
                price=price,
                force=force,
                clientOid=clientOid,
                triggerPrice=triggerPrice,
                tpslType=tpslType,
                requestTime=requestTime,
                receiveWindow=receiveWindow,
                stpMode=stpMode,
                presetTakeProfitPrice=presetTakeProfitPrice,
                executeTakeProfitPrice=executeTakeProfitPrice,
                presetStopLossPrice=presetStopLossPrice,
                executeStopLossPrice=executeStopLossPrice,
            ),
        )

    async def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market order."""
        return await self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                clientOid=clientOid,
            ),
        )

    async def place_spot_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market buy order."""
        return await self._native_private(
            "place_spot_market_buy_order",
            self._native_params(product_symbol=product_symbol, size=size, clientOid=clientOid),
        )

    async def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market sell order."""
        return await self._native_private(
            "place_spot_market_sell_order",
            self._native_params(product_symbol=product_symbol, size=size, clientOid=clientOid),
        )

    async def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit order."""
        return await self._native_private(
            "place_spot_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                force=force,
                clientOid=clientOid,
            ),
        )

    async def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit buy order."""
        return await self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit sell order."""
        return await self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit order."""
        return await self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit buy order."""
        return await self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit sell order."""
        return await self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Place Bitget spot orders in batch."""
        return await self._native_private(
            "place_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batchMode,
                orderList=orderList,
            ),
        )

    async def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        tpslType: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget spot order."""
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOid=clientOid,
                tpslType=tpslType,
            ),
        )

    async def cancel_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Cancel Bitget spot orders in batch."""
        return await self._native_private(
            "cancel_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batchMode,
                orderList=orderList,
            ),
        )

    async def get_spot_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
        requestTime: int | str | None = None,
        receiveWindow: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget spot order."""
        return await self._native_private(
            "get_spot_order",
            self._native_params(
                orderId=orderId,
                clientOid=clientOid,
                requestTime=requestTime,
                receiveWindow=receiveWindow,
            ),
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        orderId: str | None = None,
        tpslType: str | None = None,
        requestTime: int | str | None = None,
        receiveWindow: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot open orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
                orderId=orderId,
                tpslType=tpslType,
                requestTime=requestTime,
                receiveWindow=receiveWindow,
            ),
        )

    async def get_spot_history_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        orderId: str | None = None,
        tpslType: str | None = None,
        requestTime: int | str | None = None,
        receiveWindow: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot historical orders."""
        return await self._native_private(
            "get_spot_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
                orderId=orderId,
                tpslType=tpslType,
                requestTime=requestTime,
                receiveWindow=receiveWindow,
            ),
        )

    async def get_spot_fills(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot fills."""
        return await self._native_private(
            "get_spot_fills",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def place_uta_order(
        self,
        category: str,
        product_symbol: str,
        side: str,
        orderType: str,
        qty: str,
        price: str | None = None,
        timeInForce: str | None = None,
        posSide: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
        stpMode: str | None = None,
        marginMode: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget UTA order."""
        return await self._native_private(
            "place_uta_order",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
                timeInForce=timeInForce,
                posSide=posSide,
                clientOid=clientOid,
                reduceOnly=reduceOnly,
                stpMode=stpMode,
                marginMode=marginMode,
                tpTriggerBy=tpTriggerBy,
                slTriggerBy=slTriggerBy,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpOrderType=tpOrderType,
                slOrderType=slOrderType,
                tpLimitPrice=tpLimitPrice,
                slLimitPrice=slLimitPrice,
            ),
        )

    async def place_reality_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        qty: str,
        price: str | None = None,
        category: str = "SPOT",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget Reality stock order through the dedicated endpoint."""
        return await self._native_private(
            "place_reality_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
                category=category,
                clientOid=clientOid,
            ),
        )

    async def place_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Place Bitget UTA orders in batch."""
        return await self._native_private(
            "place_uta_batch_orders",
            self._native_params(orderList=orderList),
        )

    async def cancel_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA order."""
        return await self._native_private(
            "cancel_uta_order",
            self._native_params(orderId=orderId, clientOid=clientOid, category=category),
        )

    async def cancel_reality_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        category: str = "SPOT",
    ) -> dict[str, Any]:
        """Cancel a Bitget Reality stock order through the dedicated endpoint."""
        return await self._native_private(
            "cancel_reality_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOid=clientOid,
                category=category,
            ),
        )

    async def cancel_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel Bitget UTA orders in batch."""
        return await self._native_private(
            "cancel_uta_batch_orders",
            self._native_params(orderList=orderList),
        )

    async def get_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget UTA order."""
        return await self._native_private(
            "get_uta_order",
            self._native_params(orderId=orderId, clientOid=clientOid),
        )

    async def get_uta_open_orders(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        symbol: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA open orders."""
        return await self._native_private(
            "get_uta_open_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_history_orders(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA historical orders."""
        return await self._native_private(
            "get_uta_history_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_fills(
        self,
        category: str | None = None,
        orderId: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA fills."""
        return await self._native_private(
            "get_uta_fills",
            self._native_params(
                category=category,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_positions(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        posSide: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA positions."""
        return await self._native_private(
            "get_uta_positions",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                posSide=posSide,
            ),
        )

    async def place_futures_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: str,
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        price: str | None = None,
        tradeSide: str | None = None,
        force: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
        presetStopSurplusPrice: str | None = None,
        presetStopLossPrice: str | None = None,
        presetStopSurplusExecutePrice: str | None = None,
        presetStopLossExecutePrice: str | None = None,
        stpMode: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures order."""
        return await self._native_private(
            "place_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginMode=marginMode,
                marginCoin=marginCoin,
                size=size,
                price=price,
                side=side,
                tradeSide=tradeSide,
                orderType=orderType,
                force=force,
                clientOid=clientOid,
                reduceOnly=reduceOnly,
                presetStopSurplusPrice=presetStopSurplusPrice,
                presetStopLossPrice=presetStopLossPrice,
                presetStopSurplusExecutePrice=presetStopSurplusExecutePrice,
                presetStopLossExecutePrice=presetStopLossExecutePrice,
                stpMode=stpMode,
            ),
        )

    async def place_futures_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
        productType: str = "USDT-FUTURES",
        tradeSide: str | None = None,
        clientOid: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures market order."""
        return await self._native_private(
            "place_futures_market_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginMode=marginMode,
                marginCoin=marginCoin,
                side=side,
                size=size,
                tradeSide=tradeSide,
                clientOid=clientOid,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_market_buy_order(
        self,
        product_symbol: str,
        size: str,
    ) -> dict[str, Any]:
        """Place a Bitget futures market buy order."""
        return await self._native_private(
            "place_futures_market_buy_order",
            self._native_params(product_symbol=product_symbol, size=size),
        )

    async def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures market sell order."""
        return await self._native_private(
            "place_futures_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                reduceOnly=reduceOnly,
            ),
        )

    async def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit order."""
        return await self._native_private(
            "place_futures_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                force=force,
                clientOid=clientOid,
            ),
        )

    async def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit buy order."""
        return await self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit sell order."""
        return await self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit order."""
        return await self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit buy order."""
        return await self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit sell order."""
        return await self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    async def place_futures_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str,
        productType: str = "USDT-FUTURES",
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Place Bitget futures orders in batch."""
        return await self._native_private(
            "place_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginMode=marginMode,
                marginCoin=marginCoin,
                orderList=orderList,
            ),
        )

    async def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel a Bitget futures order."""
        return await self._native_private(
            "cancel_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                orderId=orderId,
                clientOid=clientOid,
            ),
        )

    async def cancel_futures_batch_orders(
        self,
        product_symbol: str | None = None,
        orderIdList: list[dict[str, Any]] | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel Bitget futures orders in batch."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                orderIdList=orderIdList,
            ),
        )

    async def get_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures order."""
        return await self._native_private(
            "get_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                orderId=orderId,
                clientOid=clientOid,
            ),
        )

    async def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        orderId: str | None = None,
        clientOid: str | None = None,
        idLessThan: str | None = None,
        status: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open orders."""
        return await self._native_private(
            "get_futures_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                orderId=orderId,
                clientOid=clientOid,
                idLessThan=idLessThan,
                status=status,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_futures_history_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        orderId: str | None = None,
        clientOid: str | None = None,
        orderSource: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures historical orders."""
        return await self._native_private(
            "get_futures_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                startTime=startTime,
                endTime=endTime,
                idLessThan=idLessThan,
                orderId=orderId,
                clientOid=clientOid,
                orderSource=orderSource,
                limit=limit,
            ),
        )

    async def get_futures_fills(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        productType: str = "USDT-FUTURES",
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures fills."""
        return await self._native_private(
            "get_futures_fills",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                productType=productType,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def place_uta_strategy_order(
        self, category: str, product_symbol: str, **params: object
    ) -> dict[str, Any]:
        """Place a Bitget UTA TP/SL or trigger strategy order."""
        return await self._native_private(
            "place_uta_strategy_order",
            self._native_params(category=category, product_symbol=product_symbol, **params),
        )

    async def modify_uta_strategy_order(
        self,
        orderId: str,
        qty: str,
        clientOid: str | None = None,
        **params: object,
    ) -> dict[str, Any]:
        """Modify a Bitget UTA strategy order."""
        return await self._native_private(
            "modify_uta_strategy_order",
            self._native_params(qty=qty, orderId=orderId, clientOid=clientOid, **params),
        )

    async def cancel_uta_strategy_order(
        self,
        orderId: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA strategy order."""
        return await self._native_private(
            "cancel_uta_strategy_order",
            self._native_params(orderId=orderId, clientOid=clientOid),
        )

    async def get_uta_unfilled_strategy_orders(
        self,
        category: str,
        type: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve pending Bitget UTA strategy orders."""
        return await self._native_private(
            "get_uta_unfilled_strategy_orders",
            self._native_params(
                category=category,
                type=type,
            ),
        )

    async def get_uta_history_strategy_orders(
        self,
        category: str,
        type: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve historical Bitget UTA strategy orders."""
        return await self._native_private(
            "get_uta_history_strategy_orders",
            self._native_params(
                category=category,
                type=type,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def modify_futures_tpsl_order(
        self,
        margin_coin: str,
        product_type: str,
        product_symbol: str,
        trigger_price: str,
        size: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        trigger_type: str | None = None,
        execute_price: str | None = None,
        range_rate: str | None = None,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v2/mix/order/modify-tpsl-order``. Pass an empty size for position-wide
        TP/SL orders.
        """
        return await self._native_private(
            "modify_futures_tpsl_order",
            self._native_params(
                marginCoin=margin_coin,
                productType=product_type,
                product_symbol=product_symbol,
                triggerPrice=trigger_price,
                size=size,
                orderId=order_id,
                clientOid=client_oid,
                triggerType=trigger_type,
                executePrice=execute_price,
                rangeRate=range_rate,
            ),
        )

    async def place_futures_plan_order(
        self,
        plan_type: str,
        product_symbol: str,
        product_type: str,
        margin_mode: str,
        margin_coin: str,
        size: str,
        trigger_price: str,
        trigger_type: str,
        side: str,
        order_type: str,
        *,
        price: str | None = None,
        callback_ratio: str | None = None,
        trade_side: str | None = None,
        client_oid: str | None = None,
        reduce_only: str | None = None,
        stop_surplus_trigger_price: str | None = None,
        stop_surplus_execute_price: str | None = None,
        stop_surplus_trigger_type: str | None = None,
        stop_loss_trigger_price: str | None = None,
        stop_loss_execute_price: str | None = None,
        stop_loss_trigger_type: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/place-plan-order``."""
        return await self._native_private(
            "place_futures_plan_order",
            self._native_params(
                planType=plan_type,
                product_symbol=product_symbol,
                productType=product_type,
                marginMode=margin_mode,
                marginCoin=margin_coin,
                size=size,
                triggerPrice=trigger_price,
                triggerType=trigger_type,
                side=side,
                orderType=order_type,
                price=price,
                callbackRatio=callback_ratio,
                tradeSide=trade_side,
                clientOid=client_oid,
                reduceOnly=reduce_only,
                stopSurplusTriggerPrice=stop_surplus_trigger_price,
                stopSurplusExecutePrice=stop_surplus_execute_price,
                stopSurplusTriggerType=stop_surplus_trigger_type,
                stopLossTriggerPrice=stop_loss_trigger_price,
                stopLossExecutePrice=stop_loss_execute_price,
                stopLossTriggerType=stop_loss_trigger_type,
                stpMode=stp_mode,
            ),
        )

    async def place_futures_position_tpsl(
        self,
        margin_coin: str,
        product_type: str,
        product_symbol: str,
        hold_side: str,
        *,
        stop_surplus_trigger_price: str | None = None,
        stop_surplus_size: str | None = None,
        stop_surplus_trigger_type: str | None = None,
        stop_surplus_execute_price: str | None = None,
        stop_loss_trigger_price: str | None = None,
        stop_loss_size: str | None = None,
        stop_loss_trigger_type: str | None = None,
        stop_loss_execute_price: str | None = None,
        stp_mode: str | None = None,
        stop_surplus_client_oid: str | None = None,
        stop_loss_client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/place-pos-tpsl``."""
        return await self._native_private(
            "place_futures_position_tpsl",
            self._native_params(
                marginCoin=margin_coin,
                productType=product_type,
                product_symbol=product_symbol,
                holdSide=hold_side,
                stopSurplusTriggerPrice=stop_surplus_trigger_price,
                stopSurplusSize=stop_surplus_size,
                stopSurplusTriggerType=stop_surplus_trigger_type,
                stopSurplusExecutePrice=stop_surplus_execute_price,
                stopLossTriggerPrice=stop_loss_trigger_price,
                stopLossSize=stop_loss_size,
                stopLossTriggerType=stop_loss_trigger_type,
                stopLossExecutePrice=stop_loss_execute_price,
                stpMode=stp_mode,
                stopSurplusClientOid=stop_surplus_client_oid,
                stopLossClientOid=stop_loss_client_oid,
            ),
        )

    async def place_futures_tpsl_order(
        self,
        margin_coin: str,
        product_type: str,
        product_symbol: str,
        plan_type: str,
        trigger_price: str,
        hold_side: str,
        *,
        size: str | None = None,
        trigger_type: str | None = None,
        execute_price: str | None = None,
        range_rate: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/place-tpsl-order``."""
        return await self._native_private(
            "place_futures_tpsl_order",
            self._native_params(
                marginCoin=margin_coin,
                productType=product_type,
                product_symbol=product_symbol,
                planType=plan_type,
                triggerPrice=trigger_price,
                holdSide=hold_side,
                size=size,
                triggerType=trigger_type,
                executePrice=execute_price,
                rangeRate=range_rate,
                clientOid=client_oid,
                stpMode=stp_mode,
            ),
        )

    async def get_futures_plan_sub_order(
        self, plan_type: str, plan_order_id: str, product_type: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/order/plan-sub-order``."""
        return await self._native_private(
            "get_futures_plan_sub_order",
            self._native_params(
                planType=plan_type, planOrderId=plan_order_id, productType=product_type
            ),
        )

    async def modify_futures_plan_order(
        self,
        product_type: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_size: str | None = None,
        new_price: str | None = None,
        new_callback_ratio: str | None = None,
        new_trigger_price: str | None = None,
        new_trigger_type: str | None = None,
        new_stop_surplus_trigger_price: str | None = None,
        new_stop_surplus_execute_price: str | None = None,
        new_stop_surplus_trigger_type: str | None = None,
        new_stop_loss_trigger_price: str | None = None,
        new_stop_loss_execute_price: str | None = None,
        new_stop_loss_trigger_type: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/modify-plan-order``."""
        return await self._native_private(
            "modify_futures_plan_order",
            self._native_params(
                productType=product_type,
                orderId=order_id,
                clientOid=client_oid,
                newSize=new_size,
                newPrice=new_price,
                newCallbackRatio=new_callback_ratio,
                newTriggerPrice=new_trigger_price,
                newTriggerType=new_trigger_type,
                newStopSurplusTriggerPrice=new_stop_surplus_trigger_price,
                newStopSurplusExecutePrice=new_stop_surplus_execute_price,
                newStopSurplusTriggerType=new_stop_surplus_trigger_type,
                newStopLossTriggerPrice=new_stop_loss_trigger_price,
                newStopLossExecutePrice=new_stop_loss_execute_price,
                newStopLossTriggerType=new_stop_loss_trigger_type,
            ),
        )

    async def cancel_futures_plan_orders(
        self,
        product_type: str,
        *,
        order_id_list: list[dict[str, Any]] | None = None,
        product_symbol: str | None = None,
        margin_coin: str | None = None,
        plan_type: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/cancel-plan-order``."""
        return await self._native_private(
            "cancel_futures_plan_orders",
            self._native_params(
                productType=product_type,
                orderIdList=dumps(order_id_list) if order_id_list is not None else None,
                product_symbol=product_symbol,
                marginCoin=margin_coin,
                planType=plan_type,
            ),
        )

    async def get_pending_futures_plan_orders(
        self,
        plan_type: str,
        product_type: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        product_symbol: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/order/orders-plan-pending``."""
        return await self._native_private(
            "get_pending_futures_plan_orders",
            self._native_params(
                planType=plan_type,
                productType=product_type,
                orderId=order_id,
                clientOid=client_oid,
                product_symbol=product_symbol,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_plan_order_history(
        self,
        plan_type: str,
        product_type: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        plan_status: str | None = None,
        product_symbol: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/order/orders-plan-history``."""
        return await self._native_private(
            "get_futures_plan_order_history",
            self._native_params(
                planType=plan_type,
                productType=product_type,
                orderId=order_id,
                clientOid=client_oid,
                planStatus=plan_status,
                product_symbol=product_symbol,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def place_spot_plan_order(
        self,
        product_symbol: str,
        side: str,
        trigger_price: str,
        order_type: str,
        size: str,
        trigger_type: str,
        *,
        execute_price: str | None = None,
        plan_type: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/place-plan-order``."""
        return await self._native_private(
            "place_spot_plan_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                triggerPrice=trigger_price,
                orderType=order_type,
                size=size,
                triggerType=trigger_type,
                executePrice=execute_price,
                planType=plan_type,
                clientOid=client_oid,
                stpMode=stp_mode,
            ),
        )

    async def modify_spot_plan_order(
        self,
        trigger_price: str,
        order_type: str,
        size: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        execute_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/modify-plan-order``."""
        return await self._native_private(
            "modify_spot_plan_order",
            self._native_params(
                triggerPrice=trigger_price,
                orderType=order_type,
                size=size,
                orderId=order_id,
                clientOid=client_oid,
                executePrice=execute_price,
            ),
        )

    async def cancel_spot_plan_order(
        self, *, order_id: str | None = None, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/cancel-plan-order``."""
        return await self._native_private(
            "cancel_spot_plan_order", self._native_params(orderId=order_id, clientOid=client_oid)
        )

    async def cancel_spot_plan_orders(
        self, *, symbol_list: list[str] | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/batch-cancel-plan-order``."""
        return await self._native_private(
            "cancel_spot_plan_orders",
            self._native_params(symbolList=dumps(symbol_list) if symbol_list is not None else None),
        )

    async def get_pending_spot_plan_orders(
        self,
        *,
        product_symbol: str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/trade/current-plan-order``."""
        return await self._native_private(
            "get_pending_spot_plan_orders",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
            ),
        )

    async def get_spot_plan_order_history(
        self,
        *,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/trade/history-plan-order``."""
        return await self._native_private(
            "get_spot_plan_order_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    async def get_spot_plan_sub_order(self, plan_order_id: str) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/trade/plan-sub-order``."""
        return await self._native_private(
            "get_spot_plan_sub_order", self._native_params(planOrderId=plan_order_id)
        )

    async def modify_futures_order(
        self,
        product_symbol: str,
        product_type: str,
        new_client_oid: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_size: str | None = None,
        new_price: str | None = None,
        new_preset_stop_surplus_price: str | None = None,
        new_preset_stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/modify-order``."""
        return await self._native_private(
            "modify_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                newClientOid=new_client_oid,
                orderId=order_id,
                clientOid=client_oid,
                newSize=new_size,
                newPrice=new_price,
                newPresetStopSurplusPrice=new_preset_stop_surplus_price,
                newPresetStopLossPrice=new_preset_stop_loss_price,
            ),
        )

    async def close_futures_positions(
        self, product_type: str, *, product_symbol: str | None = None, hold_side: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/close-positions``."""
        return await self._native_private(
            "close_futures_positions",
            self._native_params(
                productType=product_type, product_symbol=product_symbol, holdSide=hold_side
            ),
        )

    async def cancel_all_futures_orders(
        self,
        product_type: str,
        *,
        margin_coin: str | None = None,
        request_time: str | None = None,
        receive_window: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/cancel-all-orders``."""
        return await self._native_private(
            "cancel_all_futures_orders",
            self._native_params(
                productType=product_type,
                marginCoin=margin_coin,
                requestTime=request_time,
                receiveWindow=receive_window,
            ),
        )

    async def cancel_spot_orders_by_symbol(self, product_symbol: str) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/cancel-symbol-order``."""
        return await self._native_private(
            "cancel_spot_orders_by_symbol", self._native_params(product_symbol=product_symbol)
        )

    async def cancel_replace_spot_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        *,
        client_oid: str | None = None,
        order_id: str | None = None,
        new_client_oid: str | None = None,
        preset_take_profit_price: str | None = None,
        execute_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        execute_stop_loss_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/cancel-replace-order``."""
        return await self._native_private(
            "cancel_replace_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                price=price,
                size=size,
                clientOid=client_oid,
                orderId=order_id,
                newClientOid=new_client_oid,
                presetTakeProfitPrice=preset_take_profit_price,
                executeTakeProfitPrice=execute_take_profit_price,
                presetStopLossPrice=preset_stop_loss_price,
                executeStopLossPrice=execute_stop_loss_price,
            ),
        )

    async def adjust_futures_position_margin(
        self, product_symbol: str, product_type: str, margin_coin: str, hold_side: str, amount: str
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v2/mix/account/set-margin``. Positive amount adds margin; negative
        amount reduces it.
        """
        return await self._native_private(
            "adjust_futures_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                holdSide=hold_side,
                amount=amount,
            ),
        )

    async def modify_uta_order(
        self,
        product_symbol: str,
        category: str,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        request_id: int | None = None,
        auto_cancel: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        px_amend_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/modify-order``. Symbol and category satisfy the September 30,
        2026 requirements.
        """
        return await self._native_private(
            "modify_uta_order",
            self._native_params(
                product_symbol=product_symbol,
                category=category,
                orderId=order_id,
                clientOid=client_oid,
                qty=qty,
                price=price,
                requestId=request_id,
                autoCancel=auto_cancel,
                tpTriggerBy=tp_trigger_by,
                slTriggerBy=sl_trigger_by,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                tpOrderType=tp_order_type,
                slOrderType=sl_order_type,
                tpLimitPrice=tp_limit_price,
                slLimitPrice=sl_limit_price,
                pxAmendType=px_amend_type,
            ),
        )

    async def cancel_uta_orders_by_symbol(
        self, category: str, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/trade/cancel-symbol-order``."""
        return await self._native_private(
            "cancel_uta_orders_by_symbol",
            self._native_params(category=category, product_symbol=product_symbol),
        )

    async def set_uta_cancel_countdown(self, countdown: str) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/countdown-cancel-all``. Exchange approval is required;
        countdown is 0 or 5..60 seconds.
        """
        return await self._native_private(
            "set_uta_cancel_countdown", self._native_params(countdown=countdown)
        )

    async def close_uta_positions(
        self, category: str, *, product_symbol: str | None = None, pos_side: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/trade/close-positions``."""
        return await self._native_private(
            "close_uta_positions",
            self._native_params(category=category, product_symbol=product_symbol, posSide=pos_side),
        )

    async def get_uta_position_history(
        self,
        category: str,
        *,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/position/history-position``."""
        return await self._native_private(
            "get_uta_position_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def adjust_uta_position_margin(
        self, category: str, product_symbol: str, pos_side: str, operation: str, amount: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-margin``."""
        return await self._native_private(
            "adjust_uta_position_margin",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                posSide=pos_side,
                operation=operation,
                amount=amount,
            ),
        )

    async def get_uta_financial_records(
        self,
        category: str,
        *,
        coin: str | None = None,
        type_: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/financial-records``."""
        return await self._native_private(
            "get_uta_financial_records",
            self._native_params(
                category=category,
                coin=coin,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_futures_sub_account_assets(self, product_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/sub-account-assets``."""
        return await self._native_private(
            "get_futures_sub_account_assets", self._native_params(productType=product_type)
        )

    async def get_futures_estimated_open_count(
        self,
        product_symbol: str,
        product_type: str,
        margin_coin: str,
        open_amount: str,
        open_price: str,
        *,
        leverage: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/open-count``."""
        return await self._native_private(
            "get_futures_estimated_open_count",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                openAmount=open_amount,
                openPrice=open_price,
                leverage=leverage,
            ),
        )

    async def get_futures_liquidation_price(
        self,
        product_symbol: str,
        product_type: str,
        margin_coin: str,
        pos_side: str,
        order_type: str,
        open_amount: str,
        *,
        open_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/liq-price``."""
        return await self._native_private(
            "get_futures_liquidation_price",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                posSide=pos_side,
                orderType=order_type,
                openAmount=open_amount,
                openPrice=open_price,
            ),
        )

    async def get_futures_max_open_quantity(
        self,
        product_symbol: str,
        product_type: str,
        margin_coin: str,
        pos_side: str,
        order_type: str,
        *,
        open_price: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/max-open``."""
        return await self._native_private(
            "get_futures_max_open_quantity",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                marginCoin=margin_coin,
                posSide=pos_side,
                orderType=order_type,
                openPrice=open_price,
            ),
        )

    async def get_futures_interest_history(
        self,
        product_type: str,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/interest-history``."""
        return await self._native_private(
            "get_futures_interest_history",
            self._native_params(
                productType=product_type,
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    async def set_futures_all_leverage(self, product_type: str, leverage: str) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/set-all-leverage``."""
        return await self._native_private(
            "set_futures_all_leverage",
            self._native_params(productType=product_type, leverage=leverage),
        )

    async def set_futures_auto_margin(
        self, product_symbol: str, auto_margin: str, margin_coin: str, hold_side: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/set-auto-margin``."""
        return await self._native_private(
            "set_futures_auto_margin",
            self._native_params(
                product_symbol=product_symbol,
                autoMargin=auto_margin,
                marginCoin=margin_coin,
                holdSide=hold_side,
            ),
        )

    async def set_futures_asset_mode(self, product_type: str, asset_mode: str) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/set-asset-mode``."""
        return await self._native_private(
            "set_futures_asset_mode",
            self._native_params(productType=product_type, assetMode=asset_mode),
        )

    async def convert_futures_union_asset(self, coin: str, amount: str) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/account/union-convert``."""
        return await self._native_private(
            "convert_futures_union_asset", self._native_params(coin=coin, amount=amount)
        )

    async def get_futures_union_transfer_limits(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/transfer-limits``."""
        return await self._native_private(
            "get_futures_union_transfer_limits", self._native_params(coin=coin)
        )

    async def get_futures_union_config(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/union-config``."""
        return await self._native_private("get_futures_union_config", self._native_params())

    async def get_futures_isolated_symbols(self, product_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/isolated-symbols``."""
        return await self._native_private(
            "get_futures_isolated_symbols", self._native_params(productType=product_type)
        )

    async def get_futures_position_history(
        self,
        *,
        product_symbol: str | None = None,
        product_type: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/position/history-position``."""
        return await self._native_private(
            "get_futures_position_history",
            self._native_params(
                product_symbol=product_symbol,
                productType=product_type,
                idLessThan=id_less_than,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_futures_adl_rank(self, product_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/position/adlRank``."""
        return await self._native_private(
            "get_futures_adl_rank", self._native_params(productType=product_type)
        )

    async def reverse_futures_position(
        self,
        product_symbol: str,
        margin_coin: str,
        product_type: str,
        side: str,
        *,
        size: str | None = None,
        trade_side: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/mix/order/click-backhand``."""
        return await self._native_private(
            "reverse_futures_position",
            self._native_params(
                product_symbol=product_symbol,
                marginCoin=margin_coin,
                productType=product_type,
                side=side,
                size=size,
                tradeSide=trade_side,
                clientOid=client_oid,
            ),
        )

    async def get_futures_fill_history(
        self,
        product_type: str,
        *,
        order_id: str | None = None,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/order/fill-history``."""
        return await self._native_private(
            "get_futures_fill_history",
            self._native_params(
                productType=product_type,
                orderId=order_id,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    async def get_spot_sub_account_transfer_records(
        self,
        *,
        coin: str | None = None,
        role: str | None = None,
        sub_uid: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        client_oid: str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/account/sub-main-trans-record``."""
        return await self._native_private(
            "get_spot_sub_account_transfer_records",
            self._native_params(
                coin=coin,
                role=role,
                subUid=sub_uid,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_spot_sub_account_assets(
        self, *, id_less_than: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/account/subaccount-assets``."""
        return await self._native_private(
            "get_spot_sub_account_assets", self._native_params(idLessThan=id_less_than, limit=limit)
        )

    async def transfer_spot_sub_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        from_user_id: str,
        to_user_id: str,
        *,
        product_symbol: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/wallet/subaccount-transfer``."""
        return await self._native_private(
            "transfer_spot_sub_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                fromUserId=from_user_id,
                toUserId=to_user_id,
                product_symbol=product_symbol,
                clientOid=client_oid,
            ),
        )

    async def get_cross_margin_assets(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/assets``."""
        return await self._native_private("get_cross_margin_assets", self._native_params(coin=coin))

    async def borrow_cross_margin_asset(
        self, coin: str, borrow_amount: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/borrow``."""
        return await self._native_private(
            "borrow_cross_margin_asset",
            self._native_params(coin=coin, borrowAmount=borrow_amount, clientOid=client_oid),
        )

    async def repay_cross_margin_asset(self, coin: str, repay_amount: str) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/repay``."""
        return await self._native_private(
            "repay_cross_margin_asset", self._native_params(coin=coin, repayAmount=repay_amount)
        )

    async def get_cross_margin_risk_rate(self) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/risk-rate``."""
        return await self._native_private("get_cross_margin_risk_rate", self._native_params())

    async def get_cross_margin_max_borrowable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/max-borrowable-amount``."""
        return await self._native_private(
            "get_cross_margin_max_borrowable", self._native_params(coin=coin)
        )

    async def get_cross_margin_max_transferable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/account/max-transfer-out-amount``."""
        return await self._native_private(
            "get_cross_margin_max_transferable", self._native_params(coin=coin)
        )

    async def flash_repay_cross_margin_assets(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/flash-repay``."""
        return await self._native_private(
            "flash_repay_cross_margin_assets", self._native_params(coin=coin)
        )

    async def get_cross_margin_flash_repay_result(self, id_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/account/query-flash-repay-status``."""
        return await self._native_private(
            "get_cross_margin_flash_repay_result", self._native_params(idList=id_list)
        )

    async def get_cross_margin_interest_rate_limits(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/interest-rate-and-limit``."""
        return await self._native_private(
            "get_cross_margin_interest_rate_limits", self._native_params(coin=coin)
        )

    async def get_cross_margin_tiers(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/tier-data``."""
        return await self._native_private("get_cross_margin_tiers", self._native_params(coin=coin))

    async def get_cross_margin_borrow_history(
        self,
        start_time: int,
        *,
        loan_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/borrow-history``."""
        return await self._native_private(
            "get_cross_margin_borrow_history",
            self._native_params(
                startTime=start_time,
                loanId=loan_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_cross_margin_repay_history(
        self,
        start_time: int,
        *,
        repay_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/repay-history``."""
        return await self._native_private(
            "get_cross_margin_repay_history",
            self._native_params(
                startTime=start_time,
                repayId=repay_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_cross_margin_interest_history(
        self,
        start_time: int,
        *,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/interest-history``."""
        return await self._native_private(
            "get_cross_margin_interest_history",
            self._native_params(
                startTime=start_time,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_cross_margin_liquidation_history(
        self,
        start_time: int,
        *,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/liquidation-history``."""
        return await self._native_private(
            "get_cross_margin_liquidation_history",
            self._native_params(
                startTime=start_time, endTime=end_time, limit=limit, idLessThan=id_less_than
            ),
        )

    async def get_cross_margin_financial_records(
        self,
        start_time: int,
        *,
        margin_type: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/financial-records``."""
        return await self._native_private(
            "get_cross_margin_financial_records",
            self._native_params(
                startTime=start_time,
                marginType=margin_type,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def place_cross_margin_order(
        self,
        product_symbol: str,
        order_type: str,
        loan_type: str,
        force: str,
        side: str,
        *,
        price: str | None = None,
        base_size: str | None = None,
        quote_size: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/place-order``."""
        return await self._native_private(
            "place_cross_margin_order",
            self._native_params(
                product_symbol=product_symbol,
                orderType=order_type,
                loanType=loan_type,
                force=force,
                side=side,
                price=price,
                baseSize=base_size,
                quoteSize=quote_size,
                clientOid=client_oid,
                stpMode=stp_mode,
            ),
        )

    async def cancel_cross_margin_order(
        self, product_symbol: str, *, order_id: str | None = None, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/cancel-order``."""
        return await self._native_private(
            "cancel_cross_margin_order",
            self._native_params(
                product_symbol=product_symbol, orderId=order_id, clientOid=client_oid
            ),
        )

    async def get_cross_margin_open_orders(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/open-orders``."""
        return await self._native_private(
            "get_cross_margin_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                clientOid=client_oid,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_cross_margin_order_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        enter_point_source: str | None = None,
        client_oid: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/history-orders``."""
        return await self._native_private(
            "get_cross_margin_order_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                enterPointSource=enter_point_source,
                clientOid=client_oid,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_cross_margin_fills(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        id_less_than: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/fills``."""
        return await self._native_private(
            "get_cross_margin_fills",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                idLessThan=id_less_than,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_isolated_margin_assets(
        self, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/assets``."""
        return await self._native_private(
            "get_isolated_margin_assets", self._native_params(product_symbol=product_symbol)
        )

    async def borrow_isolated_margin_asset(
        self, product_symbol: str, coin: str, borrow_amount: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/borrow``."""
        return await self._native_private(
            "borrow_isolated_margin_asset",
            self._native_params(
                product_symbol=product_symbol,
                coin=coin,
                borrowAmount=borrow_amount,
                clientOid=client_oid,
            ),
        )

    async def repay_isolated_margin_asset(
        self, repay_amount: str, coin: str, product_symbol: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/repay``."""
        return await self._native_private(
            "repay_isolated_margin_asset",
            self._native_params(
                repayAmount=repay_amount,
                coin=coin,
                product_symbol=product_symbol,
                clientOid=client_oid,
            ),
        )

    async def get_isolated_margin_risk_rate(
        self,
        *,
        product_symbol: str | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/risk-rate``."""
        return await self._native_private(
            "get_isolated_margin_risk_rate",
            self._native_params(
                product_symbol=product_symbol, pageNum=page_num, pageSize=page_size
            ),
        )

    async def get_isolated_margin_max_borrowable(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/max-borrowable-amount``."""
        return await self._native_private(
            "get_isolated_margin_max_borrowable", self._native_params(product_symbol=product_symbol)
        )

    async def get_isolated_margin_max_transferable(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/account/max-transfer-out-amount``."""
        return await self._native_private(
            "get_isolated_margin_max_transferable",
            self._native_params(product_symbol=product_symbol),
        )

    async def flash_repay_isolated_margin_assets(
        self, *, symbol_list: list[str] | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/flash-repay``."""
        return await self._native_private(
            "flash_repay_isolated_margin_assets", self._native_params(symbolList=symbol_list)
        )

    async def get_isolated_margin_flash_repay_result(self, id_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/account/query-flash-repay-status``."""
        return await self._native_private(
            "get_isolated_margin_flash_repay_result", self._native_params(idList=id_list)
        )

    async def get_isolated_margin_interest_rate_limits(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/interest-rate-and-limit``."""
        return await self._native_private(
            "get_isolated_margin_interest_rate_limits",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_isolated_margin_tiers(self, product_symbol: str) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/tier-data``."""
        return await self._native_private(
            "get_isolated_margin_tiers", self._native_params(product_symbol=product_symbol)
        )

    async def get_isolated_margin_borrow_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        loan_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/borrow-history``."""
        return await self._native_private(
            "get_isolated_margin_borrow_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                loanId=loan_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_repay_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        repay_id: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/repay-history``."""
        return await self._native_private(
            "get_isolated_margin_repay_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                repayId=repay_id,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_interest_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/interest-history``."""
        return await self._native_private(
            "get_isolated_margin_interest_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_liquidation_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/liquidation-history``."""
        return await self._native_private(
            "get_isolated_margin_liquidation_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_financial_records(
        self,
        product_symbol: str,
        start_time: int,
        *,
        margin_type: str | None = None,
        coin: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/financial-records``."""
        return await self._native_private(
            "get_isolated_margin_financial_records",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                marginType=margin_type,
                coin=coin,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def place_isolated_margin_order(
        self,
        product_symbol: str,
        order_type: str,
        loan_type: str,
        force: str,
        side: str,
        *,
        price: str | None = None,
        base_size: str | None = None,
        quote_size: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/place-order``."""
        return await self._native_private(
            "place_isolated_margin_order",
            self._native_params(
                product_symbol=product_symbol,
                orderType=order_type,
                loanType=loan_type,
                force=force,
                side=side,
                price=price,
                baseSize=base_size,
                quoteSize=quote_size,
                clientOid=client_oid,
                stpMode=stp_mode,
            ),
        )

    async def cancel_isolated_margin_order(
        self, product_symbol: str, *, order_id: str | None = None, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/cancel-order``."""
        return await self._native_private(
            "cancel_isolated_margin_order",
            self._native_params(
                product_symbol=product_symbol, orderId=order_id, clientOid=client_oid
            ),
        )

    async def get_isolated_margin_open_orders(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        client_oid: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/open-orders``."""
        return await self._native_private(
            "get_isolated_margin_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                clientOid=client_oid,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_isolated_margin_order_history(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        enter_point_source: str | None = None,
        client_oid: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/history-orders``."""
        return await self._native_private(
            "get_isolated_margin_order_history",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                enterPointSource=enter_point_source,
                clientOid=client_oid,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_fills(
        self,
        product_symbol: str,
        start_time: int,
        *,
        order_id: str | None = None,
        id_less_than: str | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/fills``."""
        return await self._native_private(
            "get_isolated_margin_fills",
            self._native_params(
                product_symbol=product_symbol,
                startTime=start_time,
                orderId=order_id,
                idLessThan=id_less_than,
                endTime=end_time,
                limit=limit,
            ),
        )

    async def get_uta_funding_assets(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/funding-assets``."""
        return await self._native_private("get_uta_funding_assets", self._native_params(coin=coin))

    async def get_uta_funding_records(
        self,
        *,
        coin: str | None = None,
        type_: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/funding-financial-records``."""
        return await self._native_private(
            "get_uta_funding_records",
            self._native_params(
                coin=coin,
                type=type_,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_fee_rate(self, product_symbol: str, category: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/fee-rate``."""
        return await self._native_private(
            "get_uta_fee_rate",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    async def get_uta_max_transferable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/max-transferable``."""
        return await self._native_private(
            "get_uta_max_transferable", self._native_params(coin=coin)
        )

    async def set_uta_collateral_type(
        self,
        collateral_type: str,
        *,
        collateral_coins: str | None = None,
        allow_cashplus: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-collateral-type``."""
        return await self._native_private(
            "set_uta_collateral_type",
            self._native_params(
                collateralType=collateral_type,
                collateralCoins=collateral_coins,
                allowCashplus=allow_cashplus,
            ),
        )

    async def get_uta_settings(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/settings``."""
        return await self._native_private("get_uta_settings", self._native_params())

    async def get_uta_delta_info(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/delta-info``."""
        return await self._native_private("get_uta_delta_info", self._native_params())

    async def get_uta_repayable_coins(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/repayable-coins``."""
        return await self._native_private("get_uta_repayable_coins", self._native_params())

    async def get_uta_payment_coins(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/payment-coins``."""
        return await self._native_private("get_uta_payment_coins", self._native_params())

    async def borrow_uta_asset(
        self, coin: str, amount: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/borrow``."""
        return await self._native_private(
            "borrow_uta_asset", self._native_params(coin=coin, amount=amount, clientOid=client_oid)
        )

    async def get_uta_max_borrowable(self, coin: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/max-borrowable``."""
        return await self._native_private("get_uta_max_borrowable", self._native_params(coin=coin))

    async def get_uta_account_open_interest_limit(
        self, product_symbol: str, category: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/open-interest-limit``."""
        return await self._native_private(
            "get_uta_account_open_interest_limit",
            self._native_params(product_symbol=product_symbol, category=category),
        )

    async def get_uta_transferable_coins(self, from_type: str, to_type: str) -> dict[str, Any]:
        """Call ``GET /api/v3/account/transferable-coins``."""
        return await self._native_private(
            "get_uta_transferable_coins", self._native_params(fromType=from_type, toType=to_type)
        )

    async def get_uta_max_open_available(
        self,
        category: str,
        product_symbol: str,
        order_type: str,
        side: str,
        *,
        price: str | None = None,
        size: str | None = None,
        auto_borrow: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/max-open-available``."""
        return await self._native_private(
            "get_uta_max_open_available",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                orderType=order_type,
                side=side,
                price=price,
                size=size,
                autoBorrow=auto_borrow,
            ),
        )

    async def get_uta_position_transfer_history(
        self,
        category: str,
        *,
        product_symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/move-position-history``."""
        return await self._native_private(
            "get_uta_position_transfer_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                startTime=start_time,
                endTime=end_time,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def set_uta_repay_mode(self, repay_mode: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/set-repay-mode``."""
        return await self._native_private(
            "set_uta_repay_mode", self._native_params(repayMode=repay_mode)
        )

    async def get_uta_eligible_discount_rates(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-discount-rate``."""
        return await self._native_private(
            "get_uta_eligible_discount_rates", self._native_params(coin=coin)
        )

    async def get_uta_eligible_loan_info(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-loan-info``."""
        return await self._native_private(
            "get_uta_eligible_loan_info", self._native_params(coin=coin)
        )

    async def get_uta_eligible_margin_tiers(self, *, coin: str | None = None) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-margin-tier``."""
        return await self._native_private(
            "get_uta_eligible_margin_tiers", self._native_params(coin=coin)
        )

    async def get_uta_eligible_symbols(
        self, *, product_symbol: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/eligible-symbols``."""
        return await self._native_private(
            "get_uta_eligible_symbols", self._native_params(product_symbol=product_symbol)
        )

    async def get_uta_convert_records(
        self,
        *,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/convert-records``."""
        return await self._native_private(
            "get_uta_convert_records",
            self._native_params(
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def set_uta_account_mode(
        self, mode: str, *, delta_switch: str | None = None, target_uid: str | None = None
    ) -> dict[str, Any]:
        """
        Call ``POST /api/v3/account/adjust-account-mode``. Uses advanced mode with delta_switch;
        the deprecated delta mode is not accepted.
        """
        return await self._native_private(
            "set_uta_account_mode",
            self._native_params(mode=mode, deltaSwitch=delta_switch, targetUid=target_uid),
        )

    async def get_uta_adl_rank(self) -> dict[str, Any]:
        """Call ``GET /api/v3/position/adlRank``."""
        return await self._native_private("get_uta_adl_rank", self._native_params())

    async def place_cross_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/batch-place-order``."""
        return await self._native_private(
            "place_cross_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderList=orders),
        )

    async def place_isolated_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/batch-place-order``."""
        return await self._native_private(
            "place_isolated_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderList=orders),
        )

    async def cancel_cross_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/crossed/batch-cancel-order``."""
        return await self._native_private(
            "cancel_cross_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderIdList=orders),
        )

    async def cancel_isolated_margin_batch_orders(
        self, product_symbol: str, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/margin/isolated/batch-cancel-order``."""
        return await self._native_private(
            "cancel_isolated_margin_batch_orders",
            self._native_params(product_symbol=product_symbol, orderIdList=orders),
        )

    async def batch_cancel_replace_spot_orders(
        self, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/trade/batch-cancel-replace-order``."""
        return await self._native_private(
            "batch_cancel_replace_spot_orders", self._native_params(orderList=orders)
        )

    async def modify_uta_batch_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Call ``POST /api/v3/trade/batch-modify-order``. At most 20 orders in one category; ACK
        does not confirm matching-engine completion.
        """
        return await self._native_private(
            "modify_uta_batch_orders", self._native_params(orders=orders)
        )

    async def transfer_uta_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        *,
        product_symbol: str | None = None,
        allow_borrow: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/transfer``."""
        return await self._native_private(
            "transfer_uta_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                product_symbol=product_symbol,
                allowBorrow=allow_borrow,
                clientOid=client_oid,
            ),
        )

    async def transfer_uta_sub_to_master(
        self, from_type: str, to_type: str, amount: str, coin: str, *, client_oid: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/sub-master-transfer``."""
        return await self._native_private(
            "transfer_uta_sub_to_master",
            self._native_params(
                fromType=from_type, toType=to_type, amount=amount, coin=coin, clientOid=client_oid
            ),
        )

    async def transfer_uta_sub_account(
        self,
        from_type: str,
        to_type: str,
        amount: str,
        coin: str,
        from_user_id: str,
        to_user_id: str,
        client_oid: str,
        *,
        allow_borrow: str | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/account/sub-transfer``."""
        return await self._native_private(
            "transfer_uta_sub_account",
            self._native_params(
                fromType=from_type,
                toType=to_type,
                amount=amount,
                coin=coin,
                fromUserId=from_user_id,
                toUserId=to_user_id,
                clientOid=client_oid,
                allowBorrow=allow_borrow,
            ),
        )

    async def get_uta_sub_account_transfer_records(
        self,
        *,
        sub_uid: str | None = None,
        role: str | None = None,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        client_oid: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-transfer-record``."""
        return await self._native_private(
            "get_uta_sub_account_transfer_records",
            self._native_params(
                subUid=sub_uid,
                role=role,
                coin=coin,
                startTime=start_time,
                endTime=end_time,
                clientOid=client_oid,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_sub_accounts(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/sub-list``."""
        return await self._native_private(
            "get_uta_sub_accounts", self._native_params(limit=limit, cursor=cursor)
        )

    async def get_uta_sub_account_assets(
        self, *, sub_uid: str | None = None, cursor: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-unified-assets``."""
        return await self._native_private(
            "get_uta_sub_account_assets",
            self._native_params(subUid=sub_uid, cursor=cursor, limit=limit),
        )

    async def get_uta_strategy_sub_orders(
        self, order_id: str, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/trade/strategy-sub-orders``."""
        return await self._native_private(
            "get_uta_strategy_sub_orders",
            self._native_params(orderId=order_id, limit=limit, cursor=cursor),
        )

    async def get_uta_deposit_records(
        self,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        order_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deposit-records``."""
        return await self._native_private(
            "get_uta_deposit_records",
            self._native_params(
                coin=coin,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_all_trade_rates(self, business_type: str) -> dict[str, Any]:
        """Call ``GET /api/v2/common/all-trade-rate``."""
        return await self._native_private(
            "get_all_trade_rates", self._native_params(businessType=business_type)
        )

    async def set_uta_fee_deduction(self, deduct: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/switch-deduct``."""
        return await self._native_private(
            "set_uta_fee_deduction", self._native_params(deduct=deduct)
        )

    async def get_uta_fee_deduction(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deduct-info``."""
        return await self._native_private("get_uta_fee_deduction", self._native_params())

    async def upgrade_to_uta(self) -> dict[str, Any]:
        """Call ``POST /api/v3/account/switch``."""
        return await self._native_private("upgrade_to_uta", self._native_params())

    async def get_uta_upgrade_status(self) -> dict[str, Any]:
        """Call ``GET /api/v3/account/switch-status``."""
        return await self._native_private("get_uta_upgrade_status", self._native_params())

    async def get_futures_margin_mode_switch_quota(self) -> dict[str, Any]:
        """Call ``GET /api/v2/mix/account/switch-union-usdt``."""
        return await self._native_private(
            "get_futures_margin_mode_switch_quota", self._native_params()
        )

    async def get_cross_margin_liquidation_orders(
        self,
        *,
        type_: str | None = None,
        product_symbol: str | None = None,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/crossed/liquidation-order``."""
        return await self._native_private(
            "get_cross_margin_liquidation_orders",
            self._native_params(
                type=type_,
                product_symbol=product_symbol,
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_isolated_margin_liquidation_orders(
        self,
        *,
        type_: str | None = None,
        product_symbol: str | None = None,
        from_coin: str | None = None,
        to_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/margin/isolated/liquidation-order``."""
        return await self._native_private(
            "get_isolated_margin_liquidation_orders",
            self._native_params(
                type=type_,
                product_symbol=product_symbol,
                fromCoin=from_coin,
                toCoin=to_coin,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_classic_account_upgrade_status(
        self, *, sub_uid: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/account/upgrade-status``."""
        return await self._native_private(
            "get_classic_account_upgrade_status", self._native_params(subUid=sub_uid)
        )

    async def upgrade_classic_account(self, *, sub_uid: str | None = None) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/account/upgrade``."""
        return await self._native_private(
            "upgrade_classic_account", self._native_params(subUid=sub_uid)
        )

    async def get_spot_fee_deduction(self) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/account/deduct-info``."""
        return await self._native_private("get_spot_fee_deduction", self._native_params())

    async def set_spot_fee_deduction(self, deduct: str) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/account/switch-deduct``."""
        return await self._native_private(
            "set_spot_fee_deduction", self._native_params(deduct=deduct)
        )

    async def set_spot_deposit_account(self, account_type: str, coin: str) -> dict[str, Any]:
        """Call ``POST /api/v2/spot/wallet/modify-deposit-account``."""
        return await self._native_private(
            "set_spot_deposit_account", self._native_params(accountType=account_type, coin=coin)
        )

    async def get_deposit_address(
        self, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/deposit-address``."""
        return await self._native_private(
            "get_deposit_address", self._native_params(coin=coin, chain=chain, size=size)
        )

    async def get_sub_account_deposit_address(
        self, sub_uid: str, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/subaccount-deposit-address``."""
        return await self._native_private(
            "get_sub_account_deposit_address",
            self._native_params(subUid=sub_uid, coin=coin, chain=chain, size=size),
        )

    async def get_sub_account_deposit_records(
        self,
        sub_uid: str,
        *,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/spot/wallet/subaccount-deposit-records``."""
        return await self._native_private(
            "get_sub_account_deposit_records",
            self._native_params(
                subUid=sub_uid,
                coin=coin,
                startTime=start_time,
                endTime=end_time,
                idLessThan=id_less_than,
                limit=limit,
            ),
        )

    async def set_uta_deposit_account(self, coin: str, account_type: str) -> dict[str, Any]:
        """Call ``POST /api/v3/account/deposit-account``."""
        return await self._native_private(
            "set_uta_deposit_account", self._native_params(coin=coin, accountType=account_type)
        )

    async def create_uta_sub_account(
        self, username: str, *, account_mode: str | None = None, note: str | None = None
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/create-sub``."""
        return await self._native_private(
            "create_uta_sub_account",
            self._native_params(username=username, accountMode=account_mode, note=note),
        )

    async def get_uta_deposit_address(
        self, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/deposit-address``."""
        return await self._native_private(
            "get_uta_deposit_address", self._native_params(coin=coin, chain=chain, size=size)
        )

    async def get_uta_sub_deposit_address(
        self, sub_uid: str, coin: str, *, chain: str | None = None, size: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-deposit-address``."""
        return await self._native_private(
            "get_uta_sub_deposit_address",
            self._native_params(subUid=sub_uid, coin=coin, chain=chain, size=size),
        )

    async def get_uta_sub_deposit_records(
        self,
        sub_uid: str,
        start_time: int,
        end_time: int,
        *,
        coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/account/sub-deposit-records``."""
        return await self._native_private(
            "get_uta_sub_deposit_records",
            self._native_params(
                subUid=sub_uid,
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_rate_limit_quota(
        self,
        category: str,
        *,
        uid: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/rate-limit-quota``."""
        return await self._native_private(
            "get_uta_rate_limit_quota",
            self._native_params(category=category, uid=uid, cursor=cursor, limit=limit),
        )

    async def uta_set_rate_limit_quota(
        self, category: str, uids: list[str], quota: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/set-rate-limit-quota``."""
        return await self._native_private(
            "uta_set_rate_limit_quota",
            self._native_params(category=category, uids=uids, quota=quota),
        )

    async def get_uta_small_assets_history(
        self,
        *,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/convert/small-assets-history``."""
        return await self._native_private(
            "get_uta_small_assets_history",
            self._native_params(
                orderId=order_id, startTime=start_time, endTime=end_time, limit=limit, cursor=cursor
            ),
        )

    async def get_uta_small_assets(self) -> dict[str, Any]:
        """Call ``GET /api/v3/convert/small-assets``."""
        return await self._native_private("get_uta_small_assets", self._native_params())

    async def uta_small_assets_trade(self, from_coin_list: list[str]) -> dict[str, Any]:
        """Call ``POST /api/v3/convert/small-assets-trade``."""
        return await self._native_private(
            "uta_small_assets_trade", self._native_params(fromCoinList=from_coin_list)
        )

    async def uta_delete_sub(self, sub_uid: str) -> dict[str, Any]:
        """Call ``POST /api/v3/user/delete-sub``."""
        return await self._native_private("uta_delete_sub", self._native_params(subUid=sub_uid))

    async def uta_freeze_sub(self, sub_uid: str, operation: str) -> dict[str, Any]:
        """Call ``POST /api/v3/user/freeze-sub``."""
        return await self._native_private(
            "uta_freeze_sub", self._native_params(subUid=sub_uid, operation=operation)
        )

    async def uta_create_sub_api(
        self,
        sub_uid: str,
        note: str,
        type_: str,
        passphrase: str,
        permissions: list[str],
        ips: list[str],
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/create-sub-api``."""
        return await self._native_private(
            "uta_create_sub_api",
            self._native_params(
                subUid=sub_uid,
                note=note,
                type=type_,
                passphrase=passphrase,
                permissions=permissions,
                ips=ips,
            ),
        )

    async def uta_update_sub_api(
        self,
        api_key: str,
        passphrase: str,
        *,
        type_: str | None = None,
        permissions: list[str] | None = None,
        ips: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v3/user/update-sub-api``."""
        return await self._native_private(
            "uta_update_sub_api",
            self._native_params(
                apiKey=api_key, passphrase=passphrase, type=type_, permissions=permissions, ips=ips
            ),
        )

    async def uta_delete_sub_api(self, api_key: str) -> dict[str, Any]:
        """Call ``POST /api/v3/user/delete-sub-api``."""
        return await self._native_private("uta_delete_sub_api", self._native_params(apiKey=api_key))

    async def get_uta_sub_api_list(
        self, sub_uid: str, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """Call ``GET /api/v3/user/sub-api-list``."""
        return await self._native_private(
            "get_uta_sub_api_list", self._native_params(subUid=sub_uid, limit=limit, cursor=cursor)
        )

    async def classic_create_virtual_subaccount(
        self, sub_account_list: list[str]
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/create-virtual-subaccount``."""
        return await self._native_private(
            "classic_create_virtual_subaccount",
            self._native_params(subAccountList=sub_account_list),
        )

    async def classic_create_virtual_subaccount_apikey(
        self,
        sub_account_uid: str,
        passphrase: str,
        label: str,
        perm_list: list[str],
        *,
        ip_list: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/create-virtual-subaccount-apikey``."""
        return await self._native_private(
            "classic_create_virtual_subaccount_apikey",
            self._native_params(
                subAccountUid=sub_account_uid,
                passphrase=passphrase,
                label=label,
                permList=perm_list,
                ipList=ip_list,
            ),
        )

    async def classic_modify_virtual_subaccount(
        self, sub_account_uid: str, perm_list: list[str], status: str
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/modify-virtual-subaccount``."""
        return await self._native_private(
            "classic_modify_virtual_subaccount",
            self._native_params(subAccountUid=sub_account_uid, permList=perm_list, status=status),
        )

    async def classic_modify_virtual_subaccount_apikey(
        self,
        sub_account_uid: str,
        passphrase: str,
        label: str,
        sub_account_api_key: str,
        *,
        ip_list: list[str] | None = None,
        perm_list: list[str] | None = None,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/user/modify-virtual-subaccount-apikey``."""
        return await self._native_private(
            "classic_modify_virtual_subaccount_apikey",
            self._native_params(
                subAccountUid=sub_account_uid,
                passphrase=passphrase,
                label=label,
                subAccountApiKey=sub_account_api_key,
                ipList=ip_list,
                permList=perm_list,
            ),
        )

    async def get_classic_virtual_subaccount_list(
        self,
        *,
        limit: int | None = None,
        id_less_than: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/user/virtual-subaccount-list``."""
        return await self._native_private(
            "get_classic_virtual_subaccount_list",
            self._native_params(limit=limit, idLessThan=id_less_than, status=status),
        )

    async def get_classic_virtual_subaccount_apikey_list(
        self, sub_account_uid: str
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/user/virtual-subaccount-apikey-list``."""
        return await self._native_private(
            "get_classic_virtual_subaccount_apikey_list",
            self._native_params(subAccountUid=sub_account_uid),
        )

    async def get_classic_quoted_price(
        self,
        from_coin: str,
        to_coin: str,
        *,
        from_coin_size: str | None = None,
        to_coin_size: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/convert/quoted-price``."""
        return await self._native_private(
            "get_classic_quoted_price",
            self._native_params(
                fromCoin=from_coin,
                toCoin=to_coin,
                fromCoinSize=from_coin_size,
                toCoinSize=to_coin_size,
            ),
        )

    async def classic_trade(
        self,
        from_coin: str,
        from_coin_size: str,
        cnvt_price: str,
        to_coin: str,
        to_coin_size: str,
        trace_id: str,
    ) -> dict[str, Any]:
        """Call ``POST /api/v2/convert/trade``."""
        return await self._native_private(
            "classic_trade",
            self._native_params(
                fromCoin=from_coin,
                fromCoinSize=from_coin_size,
                cnvtPrice=cnvt_price,
                toCoin=to_coin,
                toCoinSize=to_coin_size,
                traceId=trace_id,
            ),
        )

    async def get_classic_convert_record(
        self,
        start_time: int,
        end_time: int,
        *,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict[str, Any]:
        """Call ``GET /api/v2/convert/convert-record``."""
        return await self._native_private(
            "get_classic_convert_record",
            self._native_params(
                startTime=start_time, endTime=end_time, limit=limit, idLessThan=id_less_than
            ),
        )

    async def batch_create_classic_sub_accounts(
        self, accounts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create 1..5 virtual sub-accounts and API keys using an array body."""
        return await self._native_private(
            "batch_create_classic_sub_accounts", self._native_params(accounts=accounts)
        )

    async def move_uta_positions(
        self, from_uid: str, to_uid: str, category: str, position_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Move up to 10 cross-margin positions within the same account family.

        Requires a whitelisted master account. Bitget cancels pending orders for
        the moved symbols in both accounts. Only USDT/USDC futures are supported.
        Nested symbols use native exchange IDs. Execution uses the mark price.
        """
        return await self._native_private(
            "move_uta_positions",
            self._native_params(
                fromUid=from_uid, toUid=to_uid, category=category, positionList=position_list
            ),
        )

    async def get_uta_account_max_withdrawal(self, *, coin: str) -> dict[str, Any]:
        """
        GET /api/v3/account/max-withdrawal. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/assets-balance#get-max-withdrawal
        """
        return await self._native_private(
            "get_uta_account_max_withdrawal", self._native_params(coin=coin)
        )

    async def get_classic_account_bot_assets(
        self, *, account_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v2/account/bot-assets. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/classic-common-account/classic-common-account#bot-account
        """
        return await self._native_private(
            "get_classic_account_bot_assets", self._native_params(accountType=account_type)
        )

    async def get_classic_spot_wallet_withdrawal_records(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        client_oid: str | None = None,
        id_less_than: str | None = None,
        order_id: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/spot/wallet/withdrawal-records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-withdrawal-records
        """
        return await self._native_private(
            "get_classic_spot_wallet_withdrawal_records",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                clientOid=client_oid,
                idLessThan=id_less_than,
                orderId=order_id,
                limit=limit,
            ),
        )

    async def get_uta_account_withdrawal_records(
        self,
        *,
        start_time: str,
        end_time: str,
        coin: str | None = None,
        order_id: str | None = None,
        client_oid: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v3/account/withdrawal-records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdrawal-records
        """
        return await self._native_private(
            "get_uta_account_withdrawal_records",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                coin=coin,
                orderId=order_id,
                clientOid=client_oid,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_uta_account_withdraw_address(
        self,
        *,
        coin: str | None = None,
        type_: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v3/account/withdraw-address. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdraw-address-book
        """
        return await self._native_private(
            "get_uta_account_withdraw_address",
            self._native_params(coin=coin, type=type_, limit=limit, cursor=cursor),
        )

    async def get_classic_earn_elite_product(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/product. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-product
        """
        return await self._native_private("get_classic_earn_elite_product", self._native_params())

    async def classic_earn_elite_subscribe(
        self,
        *,
        product_sub_id: str,
        amount: str,
        coin: str | None = None,
        payment_account: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/elite/subscribe. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#elite-subscribe
        """
        return await self._native_private(
            "classic_earn_elite_subscribe",
            self._native_params(
                productSubId=product_sub_id,
                amount=amount,
                coin=coin,
                paymentAccount=payment_account,
            ),
        )

    async def get_classic_earn_elite_subscribe_result(self, *, order_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/subscribe-result. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-subscribe-result
        """
        return await self._native_private(
            "get_classic_earn_elite_subscribe_result", self._native_params(orderId=order_id)
        )

    async def get_classic_earn_elite_subscribe_info(self, *, product_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/subscribe-info. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-subscribe-info
        """
        return await self._native_private(
            "get_classic_earn_elite_subscribe_info", self._native_params(productId=product_id)
        )

    async def classic_earn_elite_redeem(
        self,
        *,
        product_id: str,
        product_sub_id: str,
        redeem_type: str,
        amount: str,
        receive_account: str,
        advanced_settle: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/elite/redeem. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#elite-redeem
        """
        return await self._native_private(
            "classic_earn_elite_redeem",
            self._native_params(
                productId=product_id,
                productSubId=product_sub_id,
                redeemType=redeem_type,
                amount=amount,
                receiveAccount=receive_account,
                advancedSettle=advanced_settle,
                coin=coin,
            ),
        )

    async def get_classic_earn_elite_redeem_info(self, *, product_id: str) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/redeem-info. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-redeem-info
        """
        return await self._native_private(
            "get_classic_earn_elite_redeem_info", self._native_params(productId=product_id)
        )

    async def get_classic_earn_elite_assets(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/assets. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-assets
        """
        return await self._native_private("get_classic_earn_elite_assets", self._native_params())

    async def get_classic_earn_elite_records(
        self,
        *,
        type_: str,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/elite/records. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-records
        """
        return await self._native_private(
            "get_classic_earn_elite_records",
            self._native_params(
                type=type_, startTime=start_time, endTime=end_time, limit=limit, cursor=cursor
            ),
        )

    async def classic_earn_loan_borrow(
        self,
        *,
        loan_coin: str,
        pledge_coin: str,
        daily: str,
        pledge_amount: str | None = None,
        loan_amount: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/borrow. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#borrow
        """
        return await self._native_private(
            "classic_earn_loan_borrow",
            self._native_params(
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                daily=daily,
                pledgeAmount=pledge_amount,
                loanAmount=loan_amount,
            ),
        )

    async def get_classic_earn_loan_ongoing_orders(
        self,
        *,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/ongoing-orders. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-loan-orders
        """
        return await self._native_private(
            "get_classic_earn_loan_ongoing_orders",
            self._native_params(orderId=order_id, loanCoin=loan_coin, pledgeCoin=pledge_coin),
        )

    async def classic_earn_loan_repay(
        self,
        *,
        order_id: str,
        repay_all: str,
        amount: str | None = None,
        repay_unlock: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/repay. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#repay
        """
        return await self._native_private(
            "classic_earn_loan_repay",
            self._native_params(
                orderId=order_id, repayAll=repay_all, amount=amount, repayUnlock=repay_unlock
            ),
        )

    async def get_classic_earn_loan_repay_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/repay-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-repay-history
        """
        return await self._native_private(
            "get_classic_earn_loan_repay_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    async def classic_earn_loan_revise_pledge(
        self, *, order_id: str, amount: str, pledge_coin: str, revise_type: str
    ) -> dict[str, Any]:
        """
        POST /api/v2/earn/loan/revise-pledge. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#modify-pledge-rate
        """
        return await self._native_private(
            "classic_earn_loan_revise_pledge",
            self._native_params(
                orderId=order_id, amount=amount, pledgeCoin=pledge_coin, reviseType=revise_type
            ),
        )

    async def get_classic_earn_loan_revise_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        revise_side: str | None = None,
        pledge_coin: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/revise-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-pledge-rate-history
        """
        return await self._native_private(
            "get_classic_earn_loan_revise_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                reviseSide=revise_side,
                pledgeCoin=pledge_coin,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    async def get_classic_earn_loan_borrow_history(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/borrow-history. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-loan-history
        """
        return await self._native_private(
            "get_classic_earn_loan_borrow_history",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    async def get_classic_earn_loan_debts(self) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/debts. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-debts
        """
        return await self._native_private("get_classic_earn_loan_debts", self._native_params())

    async def get_classic_earn_loan_reduces(
        self,
        *,
        start_time: str,
        end_time: str,
        order_id: str | None = None,
        loan_coin: str | None = None,
        pledge_coin: str | None = None,
        status: str | None = None,
        page_no: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v2/earn/loan/reduces. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/earn-classic-loan/classic-earn-loan#get-liquidation-records
        """
        return await self._native_private(
            "get_classic_earn_loan_reduces",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                orderId=order_id,
                loanCoin=loan_coin,
                pledgeCoin=pledge_coin,
                status=status,
                pageNo=page_no,
                pageSize=page_size,
            ),
        )

    async def uta_trade_grid_add_investment(
        self,
        *,
        category: str,
        bot_id: str,
        coin: str,
        size: str,
        funds_source: list[str],
        adjust_type: str | None = None,
        reinvest_profit: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/add-investment. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#add-investment-amount
        """
        return await self._native_private(
            "uta_trade_grid_add_investment",
            self._native_params(
                category=category,
                botId=bot_id,
                coin=coin,
                size=size,
                fundsSource=funds_source,
                adjustType=adjust_type,
                reinvestProfit=reinvest_profit,
            ),
        )

    async def get_uta_trade_grid_bot_detail(self, *, bot_id: str) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/bot-detail. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-grid-bot-detail
        """
        return await self._native_private(
            "get_uta_trade_grid_bot_detail", self._native_params(botId=bot_id)
        )

    async def uta_trade_grid_close_bot(self, *, bot_id: str) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/close-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#close-grid-bot
        """
        return await self._native_private(
            "uta_trade_grid_close_bot", self._native_params(botId=bot_id)
        )

    async def uta_trade_grid_create_bot(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        investment_amount: list[dict[str, str]],
        funds_source: list[str],
        slippage: str,
        auto_transfer_profits: str,
        grid_type: str | None = None,
        leverage: str | None = None,
        auto_reserve_margin: str | None = None,
        reserved_margin: str | None = None,
        trigger_condition: str | None = None,
        trigger_params: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        termination_sell: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        trailing_grid: str | None = None,
        moving_average_gains: str | None = None,
        stop_upward_price: str | None = None,
        hodl_mode: str | None = None,
        market_open: str | None = None,
        loss_reserve: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/create-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#create-grid-bot
        """
        return await self._native_private(
            "uta_trade_grid_create_bot",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                investmentAmount=investment_amount,
                fundsSource=funds_source,
                slippage=slippage,
                autoTransferProfits=auto_transfer_profits,
                gridType=grid_type,
                leverage=leverage,
                autoReserveMargin=auto_reserve_margin,
                reservedMargin=reserved_margin,
                triggerCondition=trigger_condition,
                triggerParams=trigger_params,
                triggerPrice=trigger_price,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                terminationSell=termination_sell,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                trailingGrid=trailing_grid,
                movingAverageGains=moving_average_gains,
                stopUpwardPrice=stop_upward_price,
                hodlMode=hodl_mode,
                marketOpen=market_open,
                lossReserve=loss_reserve,
            ),
        )

    async def uta_trade_grid_create_neutral_bot(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        funds_source: list[str],
        leverage: str | None = None,
        investment_amount: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/create-neutral-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#create-neutral-grid-bot
        """
        return await self._native_private(
            "uta_trade_grid_create_neutral_bot",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                fundsSource=funds_source,
                leverage=leverage,
                investmentAmount=investment_amount,
                triggerPrice=trigger_price,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    async def get_uta_trade_grid_list_details(
        self, *, category: str, bot_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/list-details. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-grid-bot-order-details
        """
        return await self._native_private(
            "get_uta_trade_grid_list_details", self._native_params(category=category, botId=bot_id)
        )

    async def uta_trade_grid_modify_bot(
        self,
        *,
        bot_id: str,
        category: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        hodl_mode: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-grid-bot-parameters
        """
        return await self._native_private(
            "uta_trade_grid_modify_bot",
            self._native_params(
                botId=bot_id,
                category=category,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                hodlMode=hodl_mode,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    async def uta_trade_grid_modify_grid_interval(
        self, *, category: str, bot_id: str, max_price: str, min_price: str, grid_num: str
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-grid-interval. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-grid-interval-and-grid-number
        """
        return await self._native_private(
            "uta_trade_grid_modify_grid_interval",
            self._native_params(
                category=category,
                botId=bot_id,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
            ),
        )

    async def uta_trade_grid_modify_neutral_bot(
        self,
        *,
        bot_id: str,
        category: str,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-neutral-bot. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-neutral-grid-bot-parameters
        """
        return await self._native_private(
            "uta_trade_grid_modify_neutral_bot",
            self._native_params(
                botId=bot_id,
                category=category,
                takeProfit=take_profit,
                stopLoss=stop_loss,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    async def uta_trade_grid_modify_neutral_grid_interval(
        self, *, category: str, bot_id: str, max_price: str, min_price: str, grid_num: str
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/modify-neutral-grid-interval. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#modify-neutral-grid-interval-and-grid-number
        """
        return await self._native_private(
            "uta_trade_grid_modify_neutral_grid_interval",
            self._native_params(
                category=category,
                botId=bot_id,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
            ),
        )

    async def get_uta_trade_grid_neutral_bot_detail(self, *, bot_id: str) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/neutral-bot-detail. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-neutral-grid-bot-detail
        """
        return await self._native_private(
            "get_uta_trade_grid_neutral_bot_detail", self._native_params(botId=bot_id)
        )

    async def get_uta_trade_grid_neutral_list_details(
        self, *, category: str, bot_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v3/trade/grid/neutral-list-details. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#get-neutral-grid-bot-order-details
        """
        return await self._native_private(
            "get_uta_trade_grid_neutral_list_details",
            self._native_params(category=category, botId=bot_id),
        )

    async def uta_trade_grid_validate_neutral(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        leverage: str | None = None,
        investment_amount: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        auto_transfer_profits: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/validate-neutral. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#validate-neutral-grid-parameters
        """
        return await self._native_private(
            "uta_trade_grid_validate_neutral",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                leverage=leverage,
                investmentAmount=investment_amount,
                triggerPrice=trigger_price,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                autoTransferProfits=auto_transfer_profits,
            ),
        )

    async def uta_trade_grid_validate(
        self,
        *,
        category: str,
        symbol: str,
        max_price: str,
        min_price: str,
        grid_num: str,
        grid_order_mode: str,
        investment_amount: list[dict[str, str]],
        auto_transfer_profits: str,
        grid_type: str | None = None,
        leverage: str | None = None,
        reserved_margin: str | None = None,
        trigger_condition: str | None = None,
        trigger_params: list[dict[str, str]] | None = None,
        trigger_price: str | None = None,
        termination_condition: str | None = None,
        termination_params: list[dict[str, str]] | None = None,
        stop_loss: str | None = None,
        take_profit: str | None = None,
        trailing_grid: str | None = None,
        moving_average_gains: str | None = None,
        stop_upward_price: str | None = None,
        hodl_mode: str | None = None,
        market_open: str | None = None,
        loss_reserve: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v3/trade/grid/validate. Native symbols and decimal strings.

        Source: https://www.bitget.com/docs/catalog/trading/grid-trading#validate-grid-parameters
        """
        return await self._native_private(
            "uta_trade_grid_validate",
            self._native_params(
                category=category,
                symbol=symbol,
                maxPrice=max_price,
                minPrice=min_price,
                gridNum=grid_num,
                gridOrderMode=grid_order_mode,
                investmentAmount=investment_amount,
                autoTransferProfits=auto_transfer_profits,
                gridType=grid_type,
                leverage=leverage,
                reservedMargin=reserved_margin,
                triggerCondition=trigger_condition,
                triggerParams=trigger_params,
                triggerPrice=trigger_price,
                terminationCondition=termination_condition,
                terminationParams=termination_params,
                stopLoss=stop_loss,
                takeProfit=take_profit,
                trailingGrid=trailing_grid,
                movingAverageGains=moving_average_gains,
                stopUpwardPrice=stop_upward_price,
                hodlMode=hodl_mode,
                marketOpen=market_open,
                lossReserve=loss_reserve,
            ),
        )
