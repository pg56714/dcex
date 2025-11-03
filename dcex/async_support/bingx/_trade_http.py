"""BingX trade HTTP client."""

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import SwapTrade


class TradeHTTP(HTTPManager):
    """HTTP client for BingX trade-related API endpoints."""

    async def place_swap_order(
        self,
        product_symbol: str,
        type_: str,
        side: str,
        positionSide: str | None = None,
        reduceOnly: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        stopPrice: float | None = None,
        priceRate: float | None = None,
        stopLoss: str | None = None,
        takeProfit: str | None = None,
        workingType: str | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
        timeInForce: str | None = None,
        closePosition: str | None = None,
        activationPrice: float | None = None,
        stopGuaranteed: str | None = None,
        positionId: int | None = None,
    ) -> dict:
        """
        Place a swap order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            type_: Order type (MARKET, LIMIT, STOP, STOP_MARKET, TAKE_PROFIT, TAKE_PROFIT_MARKET)
            side: Order side (BUY, SELL)
            positionSide: Position side (LONG, SHORT)
            reduceOnly: Reduce only flag (true, false)
            price: Order price
            quantity: Order quantity
            stopPrice: Stop price
            priceRate: Price rate
            stopLoss: Stop loss price
            takeProfit: Take profit price
            workingType: Working type
            clientOrderId: Client order ID
            recvWindow: Receive window
            timeInForce: Time in force (GTC, IOC, FOK)
            closePosition: Close position flag (true, false)
            activationPrice: Activation price
            stopGuaranteed: Stop guaranteed flag (true, false)
            positionId: Position ID

        Returns:
            dict: Order data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "type": type_,
            "side": side,
        }
        if positionSide is not None:
            payload["positionSide"] = positionSide
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if price is not None:
            payload["price"] = str(price)
        if quantity is not None:
            payload["quantity"] = str(quantity)
        if stopPrice is not None:
            payload["stopPrice"] = str(stopPrice)
        if priceRate is not None:
            payload["priceRate"] = str(priceRate)
        if stopLoss is not None:
            payload["stopLoss"] = stopLoss
        if takeProfit is not None:
            payload["takeProfit"] = takeProfit
        if workingType is not None:
            payload["workingType"] = workingType
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if closePosition is not None:
            payload["closePosition"] = closePosition
        if activationPrice is not None:
            payload["activationPrice"] = str(activationPrice)
        if stopGuaranteed is not None:
            payload["stopGuaranteed"] = stopGuaranteed
        if positionId is not None:
            payload["positionId"] = str(positionId)

        res = await self._request(
            method="POST",
            path=SwapTrade.PLACE_ORDER,
            query=payload,
        )
        return res

    async def place_swap_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
        positionSide: str | None = None,
    ) -> dict:
        """
        Place a market order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (BUY, SELL)
            quantity: Order quantity
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)
            positionSide: Position side (LONG, SHORT)

        Returns:
            dict: Order data
        """

        return await self.place_swap_order(
            product_symbol=product_symbol,
            type_="MARKET",
            side=side,
            quantity=quantity,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
            positionSide=positionSide,
        )

    async def place_swap_market_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        positionSide: str = "LONG",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a market buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            positionSide: Position side (LONG, SHORT)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """

        return await self.place_swap_market_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            positionSide=positionSide,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_market_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        positionSide: str = "SHORT",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a market sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            positionSide: Position side (LONG, SHORT)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """
        return await self.place_swap_market_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            positionSide=positionSide,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        clientOrderId: str | None = None,
        timeInForce: str = "GTC",
        reduceOnly: str | None = None,
        positionSide: str | None = None,
    ) -> dict:
        """
        Place a limit order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (BUY, SELL)
            quantity: Order quantity
            price: Order price
            clientOrderId: Client order ID
            timeInForce: Time in force (GTC, IOC, FOK)
            reduceOnly: Reduce only flag (true, false)
            positionSide: Position side (LONG, SHORT)

        Returns:
            dict: Order data
        """
        return await self.place_swap_order(
            product_symbol=product_symbol,
            type_="LIMIT",
            side=side,
            quantity=quantity,
            price=price,
            clientOrderId=clientOrderId,
            timeInForce=timeInForce,
            reduceOnly=reduceOnly,
            positionSide=positionSide,
        )

    async def place_swap_limit_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "LONG",
        timeInForce: str = "GTC",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a limit buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            price: Order price
            positionSide: Position side (LONG, SHORT)
            timeInForce: Time in force (GTC, IOC, FOK)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """
        return await self.place_swap_limit_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            timeInForce=timeInForce,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_limit_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "SHORT",
        timeInForce: str = "GTC",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a limit sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            price: Order price
            positionSide: Position side (LONG, SHORT)
            timeInForce: Time in force (GTC, IOC, FOK)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """
        return await self.place_swap_limit_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            timeInForce=timeInForce,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_post_only_order(
        self,
        product_symbol: str,
        side: str,
        quantity: float,
        price: float,
        clientOrderId: str | None = None,
        timeInForce: str = "PostOnly",
        reduceOnly: str | None = None,
        positionSide: str | None = None,
    ) -> dict:
        """
        Place a post-only order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Order side (BUY, SELL)
            quantity: Order quantity
            price: Order price
            clientOrderId: Client order ID
            timeInForce: Time in force (PostOnly)
            reduceOnly: Reduce only flag (true, false)
            positionSide: Position side (LONG, SHORT)

        Returns:
            dict: Order data
        """
        return await self.place_swap_order(
            product_symbol=product_symbol,
            type_="LIMIT",
            side=side,
            quantity=quantity,
            price=price,
            clientOrderId=clientOrderId,
            timeInForce=timeInForce,
            reduceOnly=reduceOnly,
            positionSide=positionSide,
        )

    async def place_swap_post_only_buy_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "LONG",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a post-only buy order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            price: Order price
            positionSide: Position side (LONG, SHORT)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """
        return await self.place_swap_post_only_order(
            product_symbol=product_symbol,
            side="BUY",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_post_only_sell_order(
        self,
        product_symbol: str,
        quantity: float,
        price: float,
        positionSide: str = "SHORT",
        clientOrderId: str | None = None,
        reduceOnly: str | None = None,
    ) -> dict:
        """
        Place a post-only sell order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            quantity: Order quantity
            price: Order price
            positionSide: Position side (LONG, SHORT)
            clientOrderId: Client order ID
            reduceOnly: Reduce only flag (true, false)

        Returns:
            dict: Order data
        """
        return await self.place_swap_post_only_order(
            product_symbol=product_symbol,
            side="SELL",
            quantity=quantity,
            price=price,
            positionSide=positionSide,
            clientOrderId=clientOrderId,
            reduceOnly=reduceOnly,
        )

    async def place_swap_batch_order(
        self,
        batchOrders: list,
    ) -> dict:
        """
        Place batch orders.

        Args:
            batchOrders: List of order dictionaries

        Returns:
            dict: Batch order response
        """
        payload = {"batchOrders": batchOrders}
        res = await self._request(
            method="POST",
            path=SwapTrade.PLACE_BATCH_ORDER,
            query=payload,
        )
        return res

    async def cancel_swap_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        clientOrderId: str | None = None,
        recvWindow: int | None = None,
    ) -> dict:
        """
        Cancel a swap order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            orderId: Order ID
            clientOrderId: Client order ID
            recvWindow: Receive window

        Returns:
            dict: Cancel order response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId
        if recvWindow is not None:
            payload["recvWindow"] = str(recvWindow)

        res = await self._request(
            method="DELETE",
            path=SwapTrade.CANCEL_ORDER,
            query=payload,
        )
        return res

    async def cancel_swap_batch_order(
        self,
        product_symbol: str,
        orderIdList: list | None = None,
        clientOrderIdList: list | None = None,
    ) -> dict:
        """
        Cancel batch orders.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            orderIdList: List of order IDs
            clientOrderIdList: List of client order IDs

        Returns:
            dict: Cancel batch order response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if orderIdList is not None:
            payload["orderIdList"] = str(orderIdList).replace("'", "").replace(" ", "")
        if clientOrderIdList is not None:
            payload["clientOrderIdList"] = str(clientOrderIdList).replace("'", "").replace(" ", "")

        res = await self._request(
            method="DELETE",
            path=SwapTrade.CANCEL_BATCH_ORDER,
            query=payload,
        )
        return res

    async def cancel_swap_all_orders(
        self,
        product_symbol: str,
        type_: str | None = None,
    ) -> dict:
        """
        Cancel all open orders.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            type_: Order type (LIMIT, MARKET)

        Returns:
            dict: Cancel all orders response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if type_ is not None:
            payload["type"] = type_

        res = await self._request(
            method="DELETE",
            path=SwapTrade.CANCEL_ALL_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def replace_swap_order(
        self,
        product_symbol: str,
        orderId: str,
        cancelReplaceMode: str,
        type_: str,
        side: str,
        positionSide: str,
        cancelClientOrderId: int | None = None,
        cancelOrderId: str | None = None,
        cancelRestrictions: str | None = None,
        reduceOnly: str | None = None,
        price: float | None = None,
        quantity: float | None = None,
        stopPrice: float | None = None,
        priceRate: float | None = None,
        workingType: str | None = None,
        stopLoss: str | None = None,
        takeProfit: str | None = None,
        clientOrderId: str | None = None,
        closePosition: str | None = None,
        activationPrice: float | None = None,
        stopGuaranteed: str | None = None,
        timeInForce: str | None = None,
        positionId: int | None = None,
    ) -> dict:
        """
        Replace a swap order.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            orderId: Order ID
            cancelReplaceMode: Cancel replace mode
            type_: Order type
            side: Order side (BUY, SELL)
            positionSide: Position side (LONG, SHORT)
            cancelClientOrderId: Cancel client order ID
            cancelOrderId: Cancel order ID
            cancelRestrictions: Cancel restrictions
            reduceOnly: Reduce only flag (true, false)
            price: Order price
            quantity: Order quantity
            stopPrice: Stop price
            priceRate: Price rate
            workingType: Working type
            stopLoss: Stop loss price
            takeProfit: Take profit price
            clientOrderId: Client order ID
            closePosition: Close position flag (true, false)
            activationPrice: Activation price
            stopGuaranteed: Stop guaranteed flag (true, false)
            timeInForce: Time in force
            positionId: Position ID

        Returns:
            dict: Replace order response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "orderId": orderId,
            "cancelReplaceMode": cancelReplaceMode,
            "type": type_,
            "side": side,
            "positionSide": positionSide,
        }
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if price is not None:
            payload["price"] = str(price)
        if quantity is not None:
            payload["quantity"] = str(quantity)
        if cancelClientOrderId is not None:
            payload["cancelClientOrderId"] = str(cancelClientOrderId)
        if cancelOrderId is not None:
            payload["cancelOrderId"] = cancelOrderId
        if cancelRestrictions is not None:
            payload["cancelRestrictions"] = cancelRestrictions
        if stopPrice is not None:
            payload["stopPrice"] = str(stopPrice)
        if priceRate is not None:
            payload["priceRate"] = str(priceRate)
        if workingType is not None:
            payload["workingType"] = workingType
        if stopLoss is not None:
            payload["stopLoss"] = stopLoss
        if takeProfit is not None:
            payload["takeProfit"] = takeProfit
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId
        if closePosition is not None:
            payload["closePosition"] = closePosition
        if activationPrice is not None:
            payload["activationPrice"] = str(activationPrice)
        if stopGuaranteed is not None:
            payload["stopGuaranteed"] = stopGuaranteed
        if timeInForce is not None:
            payload["timeInForce"] = timeInForce
        if positionId is not None:
            payload["positionId"] = str(positionId)

        res = await self._request(
            method="POST",
            path=SwapTrade.REPLACE_ORDER,
            query=payload,
        )
        return res

    async def close_swap_position(
        self,
        positionId: str,
    ) -> dict:
        """
        Close a swap position.

        Args:
            positionId: Position ID

        Returns:
            dict: Close position response
        """
        payload = {
            "positionId": positionId,
        }

        res = await self._request(
            method="POST",
            path=SwapTrade.CLOSE_POSITION,
            query=payload,
        )
        return res

    async def close_swap_all_positions(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Close all swap positions.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Close all positions response
        """
        payload = {}
        if product_symbol:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = await self._request(
            method="POST",
            path=SwapTrade.CLOSE_ALL_POSITIONS,
            query=payload,
        )
        return res

    async def get_order_detail(
        self,
        product_symbol: str,
        orderId: int | None = None,
        clientOrderId: str | None = None,
    ) -> dict:
        """
        Get order detail.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            orderId: Order ID
            clientOrderId: Client order ID

        Returns:
            dict: Order detail data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if clientOrderId is not None:
            payload["clientOrderId"] = clientOrderId

        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_ORDER_DETAIL,
            query=payload,
        )
        return res

    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        type_: str | None = None,
    ) -> dict:
        """
        Get open orders.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            type_: Order type (LIMIT, MARKET)

        Returns:
            dict: Open orders data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)
        if type_ is not None:
            payload["type"] = type_

        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_ALL_OPEN_ORDERS,
            query=payload,
        )
        return res

    async def get_order_history(
        self,
        product_symbol: str | None = None,
        currency: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """
        Get order history.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            currency: Currency
            orderId: Order ID
            startTime: Start time in milliseconds
            endTime: End time in milliseconds
            limit: Number of records per page

        Returns:
            dict: Order history data
        """
        payload = {}
        if product_symbol is not None:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)
        if currency is not None:
            payload["currency"] = currency
        if orderId is not None:
            payload["orderId"] = str(orderId)
        if startTime is not None:
            payload["startTime"] = startTime
        if endTime is not None:
            payload["endTime"] = endTime
        if limit is not None:
            payload["limit"] = str(limit)

        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_ORDER_HISTORY,
            query=payload,
        )
        return res

    async def change_margin_type(
        self,
        product_symbol: str,
        marginType: str,
    ) -> dict:
        """
        Change margin type.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            marginType: Margin type

        Returns:
            dict: Change margin type response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "marginType": marginType,
        }

        res = await self._request(
            method="POST",
            path=SwapTrade.CHANGE_MARGIN_TYPE,
            query=payload,
        )
        return res

    async def get_margin_type(
        self,
        product_symbol: str | None = None,
    ) -> dict:
        """
        Get margin type.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Margin type data
        """
        payload = {}
        if product_symbol:
            payload["symbol"] = self.ptm.get_exchange_symbol(Common.BINGX, product_symbol)

        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_MARGIN_TYPE,
            query=payload,
        )
        return res

    async def set_leverage(
        self,
        product_symbol: str,
        side: str,
        leverage: int,
    ) -> dict:
        """
        Set leverage.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')
            side: Position side (LONG, SHORT)
            leverage: Leverage value

        Returns:
            dict: Set leverage response
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
            "side": side,
            "leverage": leverage,
        }

        res = await self._request(
            method="POST",
            path=SwapTrade.SET_LEVERAGE,
            query=payload,
        )
        return res

    async def get_leverage(
        self,
        product_symbol: str,
    ) -> dict:
        """
        Get leverage.

        Args:
            product_symbol: Trading pair symbol (e.g., 'BTC-USDT')

        Returns:
            dict: Leverage data
        """
        payload = {
            "symbol": self.ptm.get_exchange_symbol(Common.BINGX, product_symbol),
        }

        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_LEVERAGE,
            query=payload,
        )
        return res

    async def set_position_mode(
        self,
        dualSidePosition: str,
    ) -> dict:
        """
        Set position mode.

        Args:
            dualSidePosition: Dual side position flag

        Returns:
            dict: Set position mode response
        """
        payload = {
            "dualSidePosition": dualSidePosition,
        }

        res = await self._request(
            method="POST",
            path=SwapTrade.SET_POSITION_MODE,
            query=payload,
        )
        return res

    async def get_position_mode(
        self,
    ) -> dict:
        """
        Get position mode.

        Returns:
            dict: Position mode data
        """
        payload = {}
        res = await self._request(
            method="GET",
            path=SwapTrade.QUERY_POSITION_MODE,
            query=payload,
        )
        return res
