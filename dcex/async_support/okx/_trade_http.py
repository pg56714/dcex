from typing import Any

from ...utils.common import Common
from ._http_manager import HTTPManager
from .endpoints.trade import Trade


class TradeHTTP(HTTPManager):
    async def place_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        ordType: str,
        sz: str,
        ccy: str | None = None,
        clOrdId: str | None = None,
        posSide: str | None = None,
        px: str | None = None,
        pxUsd: str | None = None,
        pxVol: str | None = None,
        reduceOnly: str | None = None,
        tgtCcy: str | None = None,
        banAmend: str | None = None,
        quickMgnType: str | None = None,
        stpId: str | None = None,
        stpMode: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a new order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            side: Order side (buy, sell)
            ordType: Order type (market, limit, post_only, fok, ioc)
            sz: Order size
            ccy: Currency
            clOrdId: Client order ID
            posSide: Position side (long, short, net)
            px: Order price
            pxUsd: Price in USD
            pxVol: Price in volatility
            reduceOnly: Whether to reduce position only
            tgtCcy: Target currency
            banAmend: Whether to ban order amendment
            quickMgnType: Quick margin type
            stpId: Stop loss/take profit order ID
            stpMode: Stop loss/take profit mode
            tag: broker tag

        Returns:
            Dict containing order placement result
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "tdMode": tdMode,
            "side": side,
            "ordType": ordType,
            "sz": sz,
        }
        if ccy is not None:
            payload["ccy"] = ccy
        if clOrdId is not None:
            payload["clOrdId"] = clOrdId
        if posSide is not None:
            payload["posSide"] = posSide
        if px is not None:
            payload["px"] = px
        if pxUsd is not None:
            payload["pxUsd"] = pxUsd
        if pxVol is not None:
            payload["pxVol"] = pxVol
        if reduceOnly is not None:
            payload["reduceOnly"] = reduceOnly
        if tgtCcy is not None:
            payload["tgtCcy"] = tgtCcy
        if banAmend is not None:
            payload["banAmend"] = banAmend
        if quickMgnType is not None:
            payload["quickMgnType"] = quickMgnType
        if stpId is not None:
            payload["stpId"] = stpId
        if stpMode is not None:
            payload["stpMode"] = stpMode
        if tag is not None:
            payload["tag"] = tag

        return await self._request(
            method="POST",
            path=Trade.PLACE_ORDER,
            query=payload,
        )

    async def place_batch_orders(
        self,
        orders: list[dict],
    ) -> dict[str, Any]:
        """
        Place multiple orders in batch.

        Args:
            orders: List of order dictionaries

        Returns:
            Dict containing batch order placement results
        """

        return await self._request(
            method="POST",
            path=Trade.PLACE_BATCH_ORDERS,
            query=orders,
        )

    async def place_market_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        sz: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            side: Order side (buy, sell)
            sz: Order size
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side=side,
            ordType="market",
            sz=sz,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        tdMode: str,  # cash or cross
        sz: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market buy order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash or cross)
            sz: Order size
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="buy",
            sz=sz,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        tdMode: str,
        sz: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a market sell order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            sz: Order size
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_market_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="sell",
            sz=sz,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            side: Order side (buy, sell)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side=side,
            ordType="limit",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        tdMode: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit buy order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="buy",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        tdMode: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a limit sell order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_limit_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="sell",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only limit order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            side: Order side (buy, sell)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side=side,
            ordType="post_only",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        tdMode: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only limit buy order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="buy",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        tdMode: str,
        sz: str,
        px: str,
        posSide: str | None = None,
        reduceOnly: str | None = None,
        ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a post-only limit sell order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            sz: Order size
            px: Order price
            posSide: Position side (long, short, net)
            reduceOnly: Whether to reduce position only
            ccy: Currency

        Returns:
            Dict containing order placement result
        """
        return await self.place_post_only_limit_order(
            product_symbol=product_symbol,
            tdMode=tdMode,
            side="sell",
            sz=sz,
            px=px,
            posSide=posSide,
            reduceOnly=reduceOnly,
            ccy=ccy,
        )

    async def cancel_order(
        self,
        product_symbol: str,
        ordId: str | None = None,
        clOrdId: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an order.

        Args:
            product_symbol: Trading pair symbol
            ordId: Order ID
            clOrdId: Client order ID

        Returns:
            Dict containing cancellation result
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if ordId is not None:
            payload["ordId"] = ordId
        if clOrdId is not None:
            payload["clOrdId"] = clOrdId

        return await self._request(
            method="POST",
            path=Trade.CANCEL_ORDER,
            query=payload,
        )

    async def cancel_batch_orders(
        self,
        orders: list[dict],
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            orders: List of order dictionaries to cancel

        Returns:
            Dict containing batch cancellation results
        """
        return await self._request(
            method="POST",
            path=Trade.CANCEL_BATCH_ORDERS,
            query=orders,
        )

    async def cancel_all_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders for a trading pair or all trading pairs.

        Args:
            product_symbol: Trading pair symbol. If None, cancels all orders.

        Returns:
            Dict containing cancellation results
        """
        payload = []

        all_orders = await self.get_order_list()
        all_orders = all_orders["data"]
        if product_symbol is not None:
            exchange_symbol = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
            payload.extend(
                [
                    {
                        "instId": order["instId"],
                        "ordId": order["ordId"],
                        "clOrdId": order["clOrdId"],
                    }
                    for order in all_orders
                    if order["instId"] == exchange_symbol
                ]
            )
        else:
            payload.extend(
                [
                    {
                        "instId": order["instId"],
                        "ordId": order["ordId"],
                        "clOrdId": order["clOrdId"],
                    }
                    for order in all_orders
                ]
            )

        return await self._request(
            method="POST",
            path=Trade.CANCEL_BATCH_ORDERS,
            query=payload,
        )

    async def amend_order(
        self,
        product_symbol: str,
        ordId: str | None = None,
        clOrdId: str | None = None,
        newSz: str | None = None,
        newPx: str | None = None,
        newPxUsd: str | None = None,
        newPxVol: str | None = None,
        cxlOnFail: str | None = None,
        reqId: str | None = None,
    ) -> dict[str, Any]:
        """
        Amend an order.

        Args:
            product_symbol: Trading pair symbol
            ordId: Order ID
            clOrdId: Client order ID
            newSz: New order size
            newPx: New order price
            newPxUsd: New price in USD
            newPxVol: New price in volatility
            cxlOnFail: Cancel on fail flag
            reqId: Request ID

        Returns:
            Dict containing amendment result
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if ordId is not None:
            payload["ordId"] = ordId
        if clOrdId is not None:
            payload["clOrdId"] = clOrdId
        if newSz is not None:
            payload["newSz"] = newSz
        if newPx is not None:
            payload["newPx"] = newPx
        if newPxUsd is not None:
            payload["newPxUsd"] = newPxUsd
        if newPxVol is not None:
            payload["newPxVol"] = newPxVol
        if cxlOnFail is not None:
            payload["cxlOnFail"] = cxlOnFail
        if reqId is not None:
            payload["reqId"] = reqId

        return await self._request(
            method="POST",
            path=Trade.AMEND_ORDER,
            query=payload,
        )

    async def amend_multiple_orders(
        self,
        product_symbol: str,
        ordId: str | None = None,
        clOrdId: str | None = None,
        newSz: str | None = None,
        newPx: str | None = None,
        newPxUsd: str | None = None,
        newPxVol: str | None = None,
        cxlOnFail: str | None = None,
        reqId: str | None = None,
    ) -> dict[str, Any]:
        """
        Amend multiple orders.

        Args:
            product_symbol: Trading pair symbol
            ordId: Order ID
            clOrdId: Client order ID
            newSz: New order size
            newPx: New order price
            newPxUsd: New price in USD
            newPxVol: New price in volatility
            cxlOnFail: Cancel on fail flag
            reqId: Request ID

        Returns:
            Dict containing amendment results
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if ordId is not None:
            payload["ordId"] = ordId
        if clOrdId is not None:
            payload["clOrdId"] = clOrdId
        if newSz is not None:
            payload["newSz"] = newSz
        if newPx is not None:
            payload["newPx"] = newPx
        if newPxUsd is not None:
            payload["newPxUsd"] = newPxUsd
        if newPxVol is not None:
            payload["newPxVol"] = newPxVol
        if cxlOnFail is not None:
            payload["cxlOnFail"] = cxlOnFail
        if reqId is not None:
            payload["reqId"] = reqId

        return await self._request(
            method="POST",
            path=Trade.AMEND_BATCH_ORDER,
            query=payload,
        )

    async def close_positions(
        self,
        product_symbol: str,
        mgnMode: str,
        posSide: str | None = None,
        autoCxl: bool | None = None,
        ccy: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Close positions.

        Args:
            product_symbol: Trading pair symbol
            mgnMode: Margin mode (cross, isolated)
            posSide: Position side (long, short, net)
            autoCxl: Auto cancel flag
            ccy: Currency
            tag: broker tag

        Returns:
            Dict containing position closure result
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
            "mgnMode": mgnMode,
        }
        if posSide is not None:
            payload["posSide"] = posSide
        if autoCxl is not None:
            payload["autoCxl"] = str(autoCxl)
        if ccy is not None:
            payload["ccy"] = ccy
        if tag is not None:
            payload["tag"] = tag

        return await self._request(
            method="POST",
            path=Trade.CLOSE_POSITION,
            query=payload,
        )

    async def get_order(
        self,
        product_symbol: str,
        ordId: str | None = None,
        clOrdId: str | None = None,
    ) -> dict[str, Any]:
        """
        Get order information.

        Args:
            product_symbol: Trading pair symbol
            ordId: Order ID
            clOrdId: Client order ID

        Returns:
            Dict containing order information
        """
        payload = {
            "instId": self.ptm.get_exchange_symbol(Common.OKX, product_symbol),
        }
        if ordId is not None:
            payload["ordId"] = ordId
        if clOrdId is not None:
            payload["clOrdId"] = clOrdId

        res = await self._request(
            method="GET",
            path=Trade.ORDER_INFO,
            query=payload,
        )
        return res

    async def get_order_list(
        self,
        instType: str | None = None,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get pending orders list.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ordType: Order type
            state: Order state
            limit: Number of results per request (max 100)

        Returns:
            Dict containing pending orders list
        """
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ordType is not None:
            payload["ordType"] = ordType
        if state is not None:
            payload["state"] = state
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Trade.ORDERS_PENDING,
            query=payload,
        )
        return res

    async def get_orders_history(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        category: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get orders history.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ordType: Order type
            state: Order state
            category: Order category
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing orders history
        """
        payload = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ordType is not None:
            payload["ordType"] = ordType
        if state is not None:
            payload["state"] = state
        if category is not None:
            payload["category"] = category
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Trade.ORDERS_HISTORY,
            query=payload,
        )
        return res

    async def get_orders_history_archive(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        category: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get archived orders history.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ordType: Order type
            state: Order state
            category: Order category
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing archived orders history
        """
        payload = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ordType is not None:
            payload["ordType"] = ordType
        if state is not None:
            payload["state"] = state
        if category is not None:
            payload["category"] = category
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Trade.ORDERS_HISTORY_ARCHIVE,
            query=payload,
        )
        return res

    async def get_fills(
        self,
        instType: str | None = None,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordId: str | None = None,
        subType: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get recent fills.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ordId: Order ID
            subType: Fill subtype
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing recent fills
        """
        payload = {}
        if instType is not None:
            payload["instType"] = instType
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ordId is not None:
            payload["ordId"] = ordId
        if subType is not None:
            payload["subType"] = subType
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Trade.ORDER_FILLS,
            query=payload,
        )
        return res

    async def get_fills_history(
        self,
        instType: str,
        uly: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordId: str | None = None,
        subType: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get fills history.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            uly: Underlying asset
            instFamily: Instrument family
            product_symbol: Trading pair symbol
            ordId: Order ID
            subType: Fill subtype
            begin: Start time (Unix timestamp in milliseconds)
            end: End time (Unix timestamp in milliseconds)
            limit: Number of results per request (max 100)

        Returns:
            Dict containing fills history
        """
        payload = {
            "instType": instType,
        }
        if uly is not None:
            payload["uly"] = uly
        if instFamily is not None:
            payload["instFamily"] = instFamily
        if product_symbol is not None:
            payload["instId"] = self.ptm.get_exchange_symbol(Common.OKX, product_symbol)
        if ordId is not None:
            payload["ordId"] = ordId
        if subType is not None:
            payload["subType"] = subType
        if begin is not None:
            payload["begin"] = begin
        if end is not None:
            payload["end"] = end
        if limit is not None:
            payload["limit"] = limit

        res = await self._request(
            method="GET",
            path=Trade.ORDERS_FILLS_HISTORY,
            query=payload,
        )
        return res

    async def get_account_rate_limit(self) -> dict[str, Any]:
        """
        Get account rate limit information.

        Returns:
            Dict containing account rate limit information
        """
        res = await self._request(
            method="GET",
            path=Trade.ACCOUNT_RATE_LIMIT,
            query=None,
        )
        return res
