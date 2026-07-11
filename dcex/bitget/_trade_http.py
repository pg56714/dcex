"""Bitget private trade HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Bitget private trading operations."""

    def place_spot_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        size: str,
        price: str | None = None,
        force: str | None = None,
        clientOid: str | None = None,
        tpslType: str | None = None,
        stpMode: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot order."""
        return self._native_private(
            "place_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                size=size,
                price=price,
                force=force,
                clientOid=clientOid,
                tpslType=tpslType,
                stpMode=stpMode,
            ),
        )

    def place_spot_market_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market order."""
        return self._native_private(
            "place_spot_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                clientOid=clientOid,
            ),
        )

    def place_spot_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market buy order."""
        return self._native_private(
            "place_spot_market_buy_order",
            self._native_params(product_symbol=product_symbol, size=size, clientOid=clientOid),
        )

    def place_spot_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot market sell order."""
        return self._native_private(
            "place_spot_market_sell_order",
            self._native_params(product_symbol=product_symbol, size=size, clientOid=clientOid),
        )

    def place_spot_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit order."""
        return self._native_private(
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

    def place_spot_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit buy order."""
        return self._native_private(
            "place_spot_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_spot_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot limit sell order."""
        return self._native_private(
            "place_spot_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_spot_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit order."""
        return self._native_private(
            "place_spot_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_spot_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit buy order."""
        return self._native_private(
            "place_spot_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_spot_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget spot post-only limit sell order."""
        return self._native_private(
            "place_spot_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Place Bitget spot orders in batch."""
        return self._native_private(
            "place_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batchMode,
                orderList=orderList,
            ),
        )

    def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        tpslType: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget spot order."""
        return self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientOid=clientOid,
                tpslType=tpslType,
            ),
        )

    def cancel_spot_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        batchMode: str | None = None,
    ) -> dict[str, Any]:
        """Cancel Bitget spot orders in batch."""
        return self._native_private(
            "cancel_spot_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                batchMode=batchMode,
                orderList=orderList,
            ),
        )

    def get_spot_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget spot order."""
        return self._native_private(
            "get_spot_order",
            self._native_params(orderId=orderId, clientOid=clientOid),
        )

    def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot open orders."""
        return self._native_private(
            "get_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_spot_history_orders(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot historical orders."""
        return self._native_private(
            "get_spot_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                limit=limit,
                idLessThan=idLessThan,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    def get_spot_fills(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget spot fills."""
        return self._native_private(
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

    def place_uta_order(
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
    ) -> dict[str, Any]:
        """Place a Bitget UTA order."""
        return self._native_private(
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
            ),
        )

    def place_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Place Bitget UTA orders in batch."""
        return self._native_private(
            "place_uta_batch_orders",
            self._native_params(orderList=orderList),
        )

    def cancel_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA order."""
        return self._native_private(
            "cancel_uta_order",
            self._native_params(orderId=orderId, clientOid=clientOid, category=category),
        )

    def cancel_uta_batch_orders(self, orderList: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel Bitget UTA orders in batch."""
        return self._native_private(
            "cancel_uta_batch_orders",
            self._native_params(orderList=orderList),
        )

    def get_uta_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve one Bitget UTA order."""
        return self._native_private(
            "get_uta_order",
            self._native_params(orderId=orderId, clientOid=clientOid),
        )

    def get_uta_open_orders(
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
        return self._native_private(
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

    def get_uta_history_orders(
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
        return self._native_private(
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

    def get_uta_fills(
        self,
        category: str | None = None,
        orderId: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA fills."""
        return self._native_private(
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

    def get_uta_positions(
        self,
        category: str,
        product_symbol: str | None = None,
        symbol: str | None = None,
        posSide: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget UTA positions."""
        return self._native_private(
            "get_uta_positions",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                symbol=symbol,
                posSide=posSide,
            ),
        )

    def place_futures_order(
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
    ) -> dict[str, Any]:
        """Place a Bitget futures order."""
        return self._native_private(
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
            ),
        )

    def place_futures_market_order(
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
        return self._native_private(
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

    def place_futures_market_buy_order(self, product_symbol: str, size: str) -> dict[str, Any]:
        """Place a Bitget futures market buy order."""
        return self._native_private(
            "place_futures_market_buy_order",
            self._native_params(product_symbol=product_symbol, size=size),
        )

    def place_futures_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        reduceOnly: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures market sell order."""
        return self._native_private(
            "place_futures_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                reduceOnly=reduceOnly,
            ),
        )

    def place_futures_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        force: str = "gtc",
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit order."""
        return self._native_private(
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

    def place_futures_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit buy order."""
        return self._native_private(
            "place_futures_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_futures_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures limit sell order."""
        return self._native_private(
            "place_futures_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_futures_post_only_limit_order(
        self,
        product_symbol: str,
        side: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit order."""
        return self._native_private(
            "place_futures_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_futures_post_only_limit_buy_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit buy order."""
        return self._native_private(
            "place_futures_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_futures_post_only_limit_sell_order(
        self,
        product_symbol: str,
        size: str,
        price: str,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bitget futures post-only limit sell order."""
        return self._native_private(
            "place_futures_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                size=size,
                price=price,
                clientOid=clientOid,
            ),
        )

    def place_futures_batch_orders(
        self,
        orderList: list[dict[str, Any]],
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        marginMode: str = "crossed",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Place Bitget futures orders in batch."""
        return self._native_private(
            "place_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginMode=marginMode,
                marginCoin=marginCoin,
                orderList=orderList,
            ),
        )

    def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel a Bitget futures order."""
        return self._native_private(
            "cancel_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                orderId=orderId,
                clientOid=clientOid,
            ),
        )

    def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[dict[str, Any]] | None = None,
        productType: str = "USDT-FUTURES",
        marginCoin: str = "USDT",
    ) -> dict[str, Any]:
        """Cancel Bitget futures orders in batch."""
        return self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                marginCoin=marginCoin,
                orderIdList=orderIdList,
            ),
        )

    def get_futures_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientOid: str | None = None,
        productType: str = "USDT-FUTURES",
    ) -> dict[str, Any]:
        """Retrieve one Bitget futures order."""
        return self._native_private(
            "get_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                orderId=orderId,
                clientOid=clientOid,
            ),
        )

    def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        orderId: str | None = None,
        clientOid: str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures open orders."""
        return self._native_private(
            "get_futures_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                orderId=orderId,
                clientOid=clientOid,
                idLessThan=idLessThan,
                limit=limit,
            ),
        )

    def get_futures_history_orders(
        self,
        product_symbol: str | None = None,
        productType: str = "USDT-FUTURES",
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve Bitget futures historical orders."""
        return self._native_private(
            "get_futures_history_orders",
            self._native_params(
                product_symbol=product_symbol,
                productType=productType,
                startTime=startTime,
                endTime=endTime,
                idLessThan=idLessThan,
                limit=limit,
            ),
        )

    def get_futures_fills(
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
        return self._native_private(
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

    def place_uta_strategy_order(self, category: str, **params: object) -> dict[str, Any]:
        """Place a Bitget UTA TP/SL or trigger strategy order."""
        return self._native_private(
            "place_uta_strategy_order",
            self._native_params(category=category, **params),
        )

    def modify_uta_strategy_order(self, **params: object) -> dict[str, Any]:
        """Modify a Bitget UTA strategy order."""
        return self._native_private("modify_uta_strategy_order", self._native_params(**params))

    def cancel_uta_strategy_order(
        self,
        orderId: str | None = None,
        clientOid: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a Bitget UTA strategy order."""
        return self._native_private(
            "cancel_uta_strategy_order",
            self._native_params(orderId=orderId, clientOid=clientOid),
        )

    def get_uta_unfilled_strategy_orders(
        self,
        category: str,
        type: str | None = None,
        product_symbol: str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve pending Bitget UTA strategy orders."""
        return self._native_private(
            "get_uta_unfilled_strategy_orders",
            self._native_params(
                category=category,
                type=type,
                product_symbol=product_symbol,
                idLessThan=idLessThan,
                limit=limit,
            ),
        )

    def get_uta_history_strategy_orders(
        self,
        category: str,
        type: str | None = None,
        product_symbol: str | None = None,
        startTime: int | str | None = None,
        endTime: int | str | None = None,
        idLessThan: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve historical Bitget UTA strategy orders."""
        return self._native_private(
            "get_uta_history_strategy_orders",
            self._native_params(
                category=category,
                type=type,
                product_symbol=product_symbol,
                startTime=startTime,
                endTime=endTime,
                idLessThan=idLessThan,
                limit=limit,
            ),
        )
