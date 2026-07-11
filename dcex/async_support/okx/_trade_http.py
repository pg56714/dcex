from typing import Any

from ...enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    async def place_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: OrderSide | str,
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
        return await self._native_private(
            "place_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                side=side,
                ordType=ordType,
                sz=sz,
                ccy=ccy,
                clOrdId=clOrdId,
                posSide=posSide,
                px=px,
                pxUsd=pxUsd,
                pxVol=pxVol,
                reduceOnly=reduceOnly,
                tgtCcy=tgtCcy,
                banAmend=banAmend,
                quickMgnType=quickMgnType,
                stpId=stpId,
                stpMode=stpMode,
                tag=tag,
            ),
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

        return await self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: OrderSide | str,
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
        return await self._native_private(
            "place_market_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                side=side,
                sz=sz,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: OrderSide | str,
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
        return await self._native_private(
            "place_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                side=side,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: OrderSide | str,
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
        return await self._native_private(
            "place_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                side=side,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "place_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                sz=sz,
                px=px,
                posSide=posSide,
                reduceOnly=reduceOnly,
                ccy=ccy,
            ),
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
        return await self._native_private(
            "cancel_order",
            self._native_params(product_symbol=product_symbol, ordId=ordId, clOrdId=clOrdId),
        )

    async def cancel_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            orders: List of order dictionaries to cancel

        Returns:
            Dict containing batch cancellation results
        """
        return await self._native_private(
            "cancel_batch_orders",
            self._native_params(orders=orders),
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
        return await self._native_private(
            "cancel_all_orders",
            self._native_params(product_symbol=product_symbol),
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
        return await self._native_private(
            "amend_order",
            self._native_params(
                product_symbol=product_symbol,
                ordId=ordId,
                clOrdId=clOrdId,
                newSz=newSz,
                newPx=newPx,
                newPxUsd=newPxUsd,
                newPxVol=newPxVol,
                cxlOnFail=cxlOnFail,
                reqId=reqId,
            ),
        )

    async def amend_multiple_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Amend multiple orders.

        Args:
            orders: List of order amendment dictionaries.

        Returns:
            Dict containing amendment results
        """
        return await self._native_private(
            "amend_multiple_orders",
            self._native_params(orders=orders),
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
        return await self._native_private(
            "close_positions",
            self._native_params(
                product_symbol=product_symbol,
                mgnMode=mgnMode,
                posSide=posSide,
                autoCxl=autoCxl,
                ccy=ccy,
                tag=tag,
            ),
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
        return await self._native_private(
            "get_order",
            self._native_params(product_symbol=product_symbol, ordId=ordId, clOrdId=clOrdId),
        )

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
        return await self._native_private(
            "get_order_list",
            self._native_params(
                instType=instType,
                uly=uly,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                limit=limit,
            ),
        )

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
        return await self._native_private(
            "get_orders_history",
            self._native_params(
                instType=instType,
                uly=uly,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                category=category,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

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
        return await self._native_private(
            "get_orders_history_archive",
            self._native_params(
                instType=instType,
                uly=uly,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                category=category,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

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
        return await self._native_private(
            "get_fills",
            self._native_params(
                instType=instType,
                uly=uly,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordId=ordId,
                subType=subType,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

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
        return await self._native_private(
            "get_fills_history",
            self._native_params(
                instType=instType,
                uly=uly,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordId=ordId,
                subType=subType,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    async def get_account_rate_limit(self) -> dict[str, Any]:
        """
        Get account rate limit information.

        Returns:
            Dict containing account rate limit information
        """
        return await self._native_private("get_account_rate_limit", [])

    async def pre_check_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        ordType: str,
        sz: str,
        **params: object,
    ) -> dict[str, Any]:
        """Validate an OKX order before it reaches the matching engine."""
        return await self._native_private(
            "pre_check_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=tdMode,
                side=side,
                ordType=ordType,
                sz=sz,
                **params,
            ),
        )

    async def set_cancel_all_after(
        self,
        timeOut: int | str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Configure OKX countdown cancellation for outstanding orders."""
        return await self._native_private(
            "set_cancel_all_after",
            self._native_params(timeOut=timeOut, tag=tag),
        )
