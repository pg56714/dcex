from json import dumps
from typing import Any

from ..enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    def place_spread_order(
        self,
        sprd_id: str,
        side: str,
        order_type: str,
        size: str,
        *,
        price: str | None = None,
        client_order_id: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Place an OKX Nitro Spread order."""
        return self._native_private(
            "place_spread_order",
            self._native_params(
                sprdId=sprd_id,
                side=side,
                ordType=order_type,
                sz=size,
                px=price,
                clOrdId=client_order_id,
                tag=tag,
            ),
        )

    def cancel_spread_order(
        self, *, order_id: str | None = None, client_order_id: str | None = None
    ) -> dict[str, Any]:
        """Cancel one Nitro Spread order by exchange or client ID."""
        return self._native_private(
            "cancel_spread_order", self._native_params(ordId=order_id, clOrdId=client_order_id)
        )

    def cancel_all_spread_orders(self, sprd_id: str | None = None) -> dict[str, Any]:
        """Cancel Nitro Spread orders, optionally for one spread."""
        return self._native_private("cancel_all_spread_orders", self._native_params(sprdId=sprd_id))

    def get_spread_order(
        self, *, order_id: str | None = None, client_order_id: str | None = None
    ) -> dict[str, Any]:
        """Get one Nitro Spread order."""
        return self._native_private(
            "get_spread_order", self._native_params(ordId=order_id, clOrdId=client_order_id)
        )

    def get_spread_orders_pending(
        self, *, sprd_id: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Get pending Nitro Spread orders."""
        return self._native_private(
            "get_spread_orders_pending", self._native_params(sprdId=sprd_id, limit=limit)
        )

    def get_spread_orders_history(
        self, *, sprd_id: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Get recent Nitro Spread order history."""
        return self._native_private(
            "get_spread_orders_history", self._native_params(sprdId=sprd_id, limit=limit)
        )

    def set_spread_cancel_all_after(self, time_out: int) -> dict[str, Any]:
        """Arm or disarm Nitro Spread's server-side cancel timer."""
        return self._native_private(
            "set_spread_cancel_all_after", self._native_params(timeOut=time_out)
        )

    def get_spread_trades(
        self, *, sprd_id: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Get recent Nitro Spread fills."""
        return self._native_private(
            "get_spread_trades", self._native_params(sprdId=sprd_id, limit=limit)
        )

    def get_easy_convert_currencies(self, source: str | None = None) -> dict[str, Any]:
        """Return currencies eligible for OKX Easy Convert."""
        return self._native_private(
            "get_easy_convert_currencies", self._native_params(source=source)
        )

    def get_easy_convert_history(
        self, after: str | None = None, before: str | None = None, limit: int | None = None
    ) -> dict[str, Any]:
        """Return OKX Easy Convert transactions."""
        return self._native_private(
            "get_easy_convert_history",
            self._native_params(after=after, before=before, limit=limit),
        )

    def place_easy_convert(
        self, from_ccy: list[str], to_ccy: str, source: str | None = None
    ) -> dict[str, Any]:
        """Convert up to five small currency balances."""
        if not 1 <= len(from_ccy) <= 5:
            raise ValueError("from_ccy must contain one to five currencies")
        return self._native_private(
            "place_easy_convert",
            self._native_params(fromCcy=from_ccy, toCcy=to_ccy, source=source),
        )

    def place_order(
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
        reduceOnly: bool | str | None = None,
        tgtCcy: str | None = None,
        banAmend: bool | str | None = None,
        outcome: str | None = None,
        pxAmendType: str | None = None,
        tradeQuoteCcy: str | None = None,
        slippagePct: str | None = None,
        stpMode: str | None = None,
        isElpTakerAccess: bool | str | None = None,
        rpiTakerAccess: bool | str | None = None,
        rpiPxRound: bool | str | None = None,
        attachAlgoOrds: list[dict[str, Any]] | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        Place a new order.

        Args:
            product_symbol: Trading pair symbol
            tdMode: Trading mode (cash, cross, isolated)
            side: Order side (buy, sell)
            ordType: Order type (market, limit, post_only, etc.)
            sz: Order size
            ccy: Currency code
            clOrdId: Client order ID
            posSide: Position side (long, short)
            px: Order price
            pxUsd: Price in USD
            pxVol: Price in volume
            reduceOnly: Whether this is a reduce-only order
            tgtCcy: Target currency
            banAmend: Whether to ban order amendments
            stpMode: Stop loss mode
            tag: broker tag

        Returns:
            Dictionary containing order placement result.
        """
        return self._native_private(
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
                outcome=outcome,
                pxAmendType=pxAmendType,
                tradeQuoteCcy=tradeQuoteCcy,
                slippagePct=slippagePct,
                stpMode=stpMode,
                isElpTakerAccess=isElpTakerAccess,
                rpiTakerAccess=rpiTakerAccess,
                rpiPxRound=rpiPxRound,
                attachAlgoOrds=attachAlgoOrds,
                tag=tag,
            ),
        )

    def place_batch_orders(
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

        return self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders),
        )

    def place_market_order(
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
            reduceOnly: Whether this is a reduce-only order
            ccy: Currency code

        Returns:
            Dictionary containing order placement result.
        """
        return self._native_private(
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

    def place_market_buy_order(
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
        return self._native_private(
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

    def place_market_sell_order(
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
        return self._native_private(
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

    def place_limit_order(
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
        return self._native_private(
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

    def place_limit_buy_order(
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
        return self._native_private(
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

    def place_limit_sell_order(
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
        return self._native_private(
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

    def place_post_only_limit_order(
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
        return self._native_private(
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

    def place_post_only_limit_buy_order(
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
        return self._native_private(
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

    def place_post_only_limit_sell_order(
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
        return self._native_private(
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

    def cancel_order(
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
            Dictionary containing cancellation result.
        """
        return self._native_private(
            "cancel_order",
            self._native_params(product_symbol=product_symbol, ordId=ordId, clOrdId=clOrdId),
        )

    def cancel_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cancel multiple orders in batch.

        Args:
            orders: List of order dictionaries to cancel.

        Returns:
            Dictionary containing batch cancellation result.
        """
        return self._native_private(
            "cancel_batch_orders",
            self._native_params(orders=orders),
        )

    def cancel_all_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel all orders.

        Args:
            product_symbol: Product symbol. If None, cancels all orders.

        Returns:
            Dictionary containing cancellation result.
        """
        return self._native_private(
            "cancel_all_orders",
            self._native_params(product_symbol=product_symbol),
        )

    def amend_order(
        self,
        product_symbol: str,
        ordId: str | None = None,
        clOrdId: str | None = None,
        newSz: str | None = None,
        newPx: str | None = None,
        newPxUsd: str | None = None,
        newPxVol: str | None = None,
        cxlOnFail: bool | str | None = None,
        reqId: str | None = None,
        speedBump: str | None = None,
        rpiTakerAccess: bool | str | None = None,
        rpiPxRound: bool | str | None = None,
        pxAmendType: str | None = None,
        attachAlgoOrds: list[dict[str, Any]] | None = None,
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
            newPxVol: New price in volume
            cxlOnFail: Cancel on fail flag
            reqId: Request ID

        Returns:
            Dictionary containing order amendment result.
        """
        return self._native_private(
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
                speedBump=speedBump,
                rpiTakerAccess=rpiTakerAccess,
                rpiPxRound=rpiPxRound,
                pxAmendType=pxAmendType,
                attachAlgoOrds=attachAlgoOrds,
            ),
        )

    def amend_multiple_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Amend multiple orders.

        Args:
            orders: List of order amendment dictionaries.

        Returns:
            Dictionary containing multiple orders amendment result.
        """
        return self._native_private(
            "amend_multiple_orders",
            self._native_params(orders=orders),
        )

    def close_positions(
        self,
        product_symbol: str,
        mgnMode: str,
        posSide: str | None = None,
        autoCxl: bool | None = None,
        ccy: str | None = None,
        tag: str | None = None,
        clOrdId: str | None = None,
    ) -> dict[str, Any]:
        """
        Close positions.

        Args:
            product_symbol: Trading pair symbol
            mgnMode: Margin mode
            posSide: Position side
            autoCxl: Auto cancel flag
            ccy: Currency code
            tag: broker tag

        Returns:
            Dictionary containing position closing result.
        """
        return self._native_private(
            "close_positions",
            self._native_params(
                product_symbol=product_symbol,
                mgnMode=mgnMode,
                posSide=posSide,
                autoCxl=autoCxl,
                ccy=ccy,
                tag=tag,
                clOrdId=clOrdId,
            ),
        )

    def get_order(
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
            Dictionary containing order information.
        """
        return self._native_private(
            "get_order",
            self._native_params(product_symbol=product_symbol, ordId=ordId, clOrdId=clOrdId),
        )

    def get_order_list(
        self,
        instType: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get order list.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            instFamily: Instrument family
            product_symbol: Product symbol
            ordType: Order type
            state: Order state
            limit: Number of results to return

        Returns:
            Dictionary containing order list.
        """
        return self._native_private(
            "get_order_list",
            self._native_params(
                instType=instType,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_orders_history(
        self,
        instType: str,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        category: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get orders history.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            instFamily: Instrument family
            product_symbol: Product symbol
            ordType: Order type
            state: Order state
            category: Order category
            begin: Start time
            end: End time
            limit: Number of results to return

        Returns:
            Dictionary containing orders history.
        """
        return self._native_private(
            "get_orders_history",
            self._native_params(
                instType=instType,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                category=category,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    def get_orders_history_archive(
        self,
        instType: str,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordType: str | None = None,
        state: str | None = None,
        category: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get orders history archive.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            instFamily: Instrument family
            product_symbol: Product symbol
            ordType: Order type
            state: Order state
            category: Order category
            begin: Start time
            end: End time
            limit: Number of results to return

        Returns:
            Dictionary containing orders history archive.
        """
        return self._native_private(
            "get_orders_history_archive",
            self._native_params(
                instType=instType,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordType=ordType,
                state=state,
                category=category,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    def get_fills(
        self,
        instType: str | None = None,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordId: str | None = None,
        subType: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get fills information.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            instFamily: Instrument family
            product_symbol: Product symbol
            ordId: Order ID
            subType: Fill sub-type
            begin: Start time
            end: End time
            limit: Number of results to return

        Returns:
            Dictionary containing fills information.
        """
        return self._native_private(
            "get_fills",
            self._native_params(
                instType=instType,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordId=ordId,
                subType=subType,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    def get_fills_history(
        self,
        instType: str,
        instFamily: str | None = None,
        product_symbol: str | None = None,
        ordId: str | None = None,
        subType: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Get fills history.

        Args:
            instType: Instrument type (SPOT, MARGIN, SWAP, FUTURES, OPTION)
            instFamily: Instrument family
            product_symbol: Product symbol
            ordId: Order ID
            subType: Fill sub-type
            begin: Start time
            end: End time
            limit: Number of results to return

        Returns:
            Dictionary containing fills history.
        """
        return self._native_private(
            "get_fills_history",
            self._native_params(
                instType=instType,
                instFamily=instFamily,
                product_symbol=product_symbol,
                ordId=ordId,
                subType=subType,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    def get_account_rate_limit(self) -> dict[str, Any]:
        """
        Get account rate limit.

        Returns:
            Dictionary containing account rate limit information.
        """
        return self._native_private("get_account_rate_limit", [])

    def pre_check_order(
        self,
        product_symbol: str,
        tdMode: str,
        side: str,
        ordType: str,
        sz: str,
        **params: object,
    ) -> dict[str, Any]:
        """Validate an OKX order before it reaches the matching engine."""
        return self._native_private(
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

    def set_cancel_all_after(
        self,
        timeOut: int | str,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """Configure OKX countdown cancellation for outstanding orders."""
        return self._native_private(
            "set_cancel_all_after",
            self._native_params(timeOut=timeOut, tag=tag),
        )

    def place_algo_order(
        self,
        product_symbol: str,
        trade_mode: str,
        side: str,
        order_type: str,
        *,
        ccy: str | None = None,
        pos_side: str | None = None,
        sz: str | None = None,
        tag: str | None = None,
        tgt_ccy: str | None = None,
        algo_cl_ord_id: str | None = None,
        close_fraction: str | None = None,
        trade_quote_ccy: str | None = None,
        tp_trigger_px: str | None = None,
        tp_trigger_px_type: str | None = None,
        tp_ord_px: str | None = None,
        tp_ord_kind: str | None = None,
        sl_trigger_px: str | None = None,
        sl_trigger_px_type: str | None = None,
        sl_ord_px: str | None = None,
        chase_type: str | None = None,
        chase_val: str | None = None,
        max_chase_type: str | None = None,
        max_chase_val: str | None = None,
        trigger_px: str | None = None,
        order_px: str | None = None,
        advance_ord_type: str | None = None,
        trigger_px_type: str | None = None,
        callback_ratio: str | None = None,
        callback_spread: str | None = None,
        active_px: str | None = None,
        px_var: str | None = None,
        px_spread: str | None = None,
        sz_limit: str | None = None,
        px_limit: str | None = None,
        time_interval: str | None = None,
        lmt_order_number: str | None = None,
        aggressiveness: str | None = None,
        reduce_only: bool | None = None,
        cxl_on_close_pos: bool | None = None,
        attach_algo_ords: list[dict[str, Any]] | None = None,
        adv_chase_params: list[dict[str, Any]] | None = None,
        trigger_params: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Place a standalone TP/SL, trigger, trailing, chase, TWAP or iceberg order."""
        return self._native_private(
            "place_algo_order",
            self._native_params(
                product_symbol=product_symbol,
                tdMode=trade_mode,
                side=side,
                ordType=order_type,
                ccy=ccy,
                posSide=pos_side,
                sz=sz,
                tag=tag,
                tgtCcy=tgt_ccy,
                algoClOrdId=algo_cl_ord_id,
                closeFraction=close_fraction,
                tradeQuoteCcy=trade_quote_ccy,
                tpTriggerPx=tp_trigger_px,
                tpTriggerPxType=tp_trigger_px_type,
                tpOrdPx=tp_ord_px,
                tpOrdKind=tp_ord_kind,
                slTriggerPx=sl_trigger_px,
                slTriggerPxType=sl_trigger_px_type,
                slOrdPx=sl_ord_px,
                chaseType=chase_type,
                chaseVal=chase_val,
                maxChaseType=max_chase_type,
                maxChaseVal=max_chase_val,
                triggerPx=trigger_px,
                orderPx=order_px,
                advanceOrdType=advance_ord_type,
                triggerPxType=trigger_px_type,
                callbackRatio=callback_ratio,
                callbackSpread=callback_spread,
                activePx=active_px,
                pxVar=px_var,
                pxSpread=px_spread,
                szLimit=sz_limit,
                pxLimit=px_limit,
                timeInterval=time_interval,
                lmtOrderNumber=lmt_order_number,
                aggressiveness=aggressiveness,
                reduceOnly=reduce_only,
                cxlOnClosePos=cxl_on_close_pos,
                attachAlgoOrds=dumps(attach_algo_ords) if attach_algo_ords is not None else None,
                advChaseParams=dumps(adv_chase_params) if adv_chase_params is not None else None,
                triggerParams=dumps(trigger_params) if trigger_params is not None else None,
            ),
        )

    def amend_algo_order(
        self,
        product_symbol: str,
        *,
        algo_id: str | None = None,
        algo_cl_ord_id: str | None = None,
        req_id: str | None = None,
        new_sz: str | None = None,
        new_tp_trigger_px: str | None = None,
        new_tp_ord_px: str | None = None,
        new_sl_trigger_px: str | None = None,
        new_sl_ord_px: str | None = None,
        new_tp_trigger_px_type: str | None = None,
        new_sl_trigger_px_type: str | None = None,
        new_trigger_px: str | None = None,
        new_ord_px: str | None = None,
        new_trigger_px_type: str | None = None,
        cancel_on_fail: bool | None = None,
        attach_algo_ords: list[dict[str, Any]] | None = None,
        adv_chase_params: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Amend an untriggered stop or trigger order; zero TP/SL values remove that leg."""
        return self._native_private(
            "amend_algo_order",
            self._native_params(
                product_symbol=product_symbol,
                algoId=algo_id,
                algoClOrdId=algo_cl_ord_id,
                reqId=req_id,
                newSz=new_sz,
                newTpTriggerPx=new_tp_trigger_px,
                newTpOrdPx=new_tp_ord_px,
                newSlTriggerPx=new_sl_trigger_px,
                newSlOrdPx=new_sl_ord_px,
                newTpTriggerPxType=new_tp_trigger_px_type,
                newSlTriggerPxType=new_sl_trigger_px_type,
                newTriggerPx=new_trigger_px,
                newOrdPx=new_ord_px,
                newTriggerPxType=new_trigger_px_type,
                cxlOnFail=cancel_on_fail,
                attachAlgoOrds=dumps(attach_algo_ords) if attach_algo_ords is not None else None,
                advChaseParams=dumps(adv_chase_params) if adv_chase_params is not None else None,
            ),
        )

    def cancel_algo_orders(self, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """Cancel up to ten algo orders identified by instId and algoId or algoClOrdId."""
        return self._native_private(
            "cancel_algo_orders",
            self._native_params(orders=dumps(orders) if orders is not None else None),
        )

    def get_algo_order(
        self, *, algo_id: str | None = None, algo_client_order_id: str | None = None
    ) -> dict[str, Any]:
        """Query an algo order by its exchange or client identifier."""
        return self._native_private(
            "get_algo_order", self._native_params(algoId=algo_id, algoClOrdId=algo_client_order_id)
        )

    def get_pending_algo_orders(
        self,
        order_type: str,
        *,
        algo_id: str | None = None,
        instrument_type: str | None = None,
        product_symbol: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """List untriggered algo orders, including standalone TP/SL orders."""
        return self._native_private(
            "get_pending_algo_orders",
            self._native_params(
                ordType=order_type,
                algoId=algo_id,
                instType=instrument_type,
                product_symbol=product_symbol,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_algo_order_history(
        self,
        order_type: str,
        *,
        state: str | None = None,
        algo_id: str | None = None,
        instrument_type: str | None = None,
        product_symbol: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Query historical algo orders; state or algo_id is required."""
        return self._native_private(
            "get_algo_order_history",
            self._native_params(
                ordType=order_type,
                state=state,
                algoId=algo_id,
                instType=instrument_type,
                product_symbol=product_symbol,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def adjust_position_margin(
        self,
        product_symbol: str,
        position_side: str,
        type_: str,
        amount: str,
        *,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Add or reduce isolated position margin."""
        return self._native_private(
            "adjust_position_margin",
            self._native_params(
                product_symbol=product_symbol,
                posSide=position_side,
                type=type_,
                amt=amount,
                ccy=currency,
            ),
        )

    def set_isolated_mode(self, iso_mode: str, type_: str) -> dict[str, Any]:
        """Set isolated mode through ``POST /api/v5/account/set-isolated-mode``."""
        return self._native_private(
            "set_isolated_mode", self._native_params(isoMode=iso_mode, type=type_)
        )

    def get_account_risk_state(self) -> dict[str, Any]:
        """Get account risk state through ``GET /api/v5/account/risk-state``."""
        return self._native_private("get_account_risk_state", self._native_params())

    def get_greeks(self, ccy: str | None = None) -> dict[str, Any]:
        """Get greeks through ``GET /api/v5/account/greeks``."""
        return self._native_private("get_greeks", self._native_params(ccy=ccy))

    def get_pm_position_tiers(self, inst_type: str, inst_family: str) -> dict[str, Any]:
        """Get pm position tiers through ``GET /api/v5/account/position-tiers``."""
        return self._native_private(
            "get_pm_position_tiers", self._native_params(instType=inst_type, instFamily=inst_family)
        )

    def set_account_level(self, acct_lv: str) -> dict[str, Any]:
        """Set account level through ``POST /api/v5/account/set-account-level``."""
        return self._native_private("set_account_level", self._native_params(acctLv=acct_lv))

    def get_collateral_assets(
        self, ccy: str | None = None, collateral_enabled: bool | None = None
    ) -> dict[str, Any]:
        """Get collateral assets through ``GET /api/v5/account/collateral-assets``."""
        return self._native_private(
            "get_collateral_assets",
            self._native_params(ccy=ccy, collateralEnabled=collateral_enabled),
        )

    def amend_spread_order(
        self,
        ord_id: str | None = None,
        cl_ord_id: str | None = None,
        req_id: str | None = None,
        new_sz: str | None = None,
        new_px: str | None = None,
    ) -> dict[str, Any]:
        """Amend spread order through ``POST /api/v5/sprd/amend-order``."""
        return self._native_private(
            "amend_spread_order",
            self._native_params(
                ordId=ord_id, clOrdId=cl_ord_id, reqId=req_id, newSz=new_sz, newPx=new_px
            ),
        )

    def get_asset_bill_history(
        self,
        ccy: str | None = None,
        type_: str | None = None,
        third_party_type: str | None = None,
        client_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        paging_type: str | None = None,
    ) -> dict[str, Any]:
        """Get asset bill history through ``GET /api/v5/asset/bills-history``."""
        return self._native_private(
            "get_asset_bill_history",
            self._native_params(
                ccy=ccy,
                type=type_,
                thirdPartyType=third_party_type,
                clientId=client_id,
                after=after,
                before=before,
                limit=limit,
                pagingType=paging_type,
            ),
        )

    def get_convert_currency_pair(
        self, from_ccy: str, to_ccy: str, convert_mode: str | None = None
    ) -> dict[str, Any]:
        """Get convert currency pair through ``GET /api/v5/asset/convert/currency-pair``."""
        return self._native_private(
            "get_convert_currency_pair",
            self._native_params(fromCcy=from_ccy, toCcy=to_ccy, convertMode=convert_mode),
        )

    def estimate_convert_quote(
        self,
        base_ccy: str,
        quote_ccy: str,
        side: str,
        rfq_sz: str,
        rfq_sz_ccy: str,
        cl_q_req_id: str | None = None,
        convert_mode: str | None = None,
    ) -> dict[str, Any]:
        """Estimate convert quote through ``POST /api/v5/asset/convert/estimate-quote``."""
        return self._native_private(
            "estimate_convert_quote",
            self._native_params(
                baseCcy=base_ccy,
                quoteCcy=quote_ccy,
                side=side,
                rfqSz=rfq_sz,
                rfqSzCcy=rfq_sz_ccy,
                clQReqId=cl_q_req_id,
                convertMode=convert_mode,
            ),
        )

    def execute_convert_trade(
        self,
        quote_id: str,
        base_ccy: str,
        quote_ccy: str,
        side: str,
        sz: str,
        sz_ccy: str,
        cl_t_req_id: str | None = None,
        convert_mode: str | None = None,
    ) -> dict[str, Any]:
        """Execute convert trade through ``POST /api/v5/asset/convert/trade``."""
        return self._native_private(
            "execute_convert_trade",
            self._native_params(
                quoteId=quote_id,
                baseCcy=base_ccy,
                quoteCcy=quote_ccy,
                side=side,
                sz=sz,
                szCcy=sz_ccy,
                clTReqId=cl_t_req_id,
                convertMode=convert_mode,
            ),
        )

    def set_fee_type(self, *, fee_type: str) -> dict[str, Any]:
        """
        POST /api/v5/account/set-fee-type.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-fee-type
        """
        return self._native_private("set_fee_type", self._native_params(feeType=fee_type))

    def set_risk_offset_amount(self, *, ccy: str, cl_spot_in_use_amt: str) -> dict[str, Any]:
        """
        POST /api/v5/account/set-riskOffset-amt.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-risk-offset-amount
        """
        return self._native_private(
            "set_risk_offset_amount",
            self._native_params(ccy=ccy, clSpotInUseAmt=cl_spot_in_use_amt),
        )

    def activate_options(self) -> dict[str, Any]:
        """
        POST /api/v5/account/activate-option.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-activate-option
        """
        return self._native_private("activate_options", self._native_params())

    def set_auto_loan(self, *, auto_loan: bool | None = None) -> dict[str, Any]:
        """
        POST /api/v5/account/set-auto-loan.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-auto-loan
        """
        return self._native_private("set_auto_loan", self._native_params(autoLoan=auto_loan))

    def preset_account_level_switch(
        self, *, acct_lv: str, lever: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/account/account-level-switch-preset.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-preset-account-mode-switch
        """
        return self._native_private(
            "preset_account_level_switch", self._native_params(acctLv=acct_lv, lever=lever)
        )

    def precheck_account_level_switch(self, *, acct_lv: str) -> dict[str, Any]:
        """

        GET /api/v5/account/set-account-switch-precheck.

        Source:
        https://www.okx.com/docs-v5/en/#trading-account-rest-api-precheck-account-mode-switch

        """
        return self._native_private(
            "precheck_account_level_switch", self._native_params(acctLv=acct_lv)
        )

    def set_collateral_assets(
        self, *, type_: str, collateral_enabled: bool, ccy_list: list[str] | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/account/set-collateral-assets.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-collateral-assets
        """
        return self._native_private(
            "set_collateral_assets",
            self._native_params(type=type_, collateralEnabled=collateral_enabled, ccyList=ccy_list),
        )

    def set_settlement_currency(self, *, settle_ccy: str) -> dict[str, Any]:
        """
        POST /api/v5/account/set-settle-currency.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-settle-currency
        """
        return self._native_private(
            "set_settlement_currency", self._native_params(settleCcy=settle_ccy)
        )

    def set_trading_config(self, *, type_: str, stgy_type: str | None = None) -> dict[str, Any]:
        """
        POST /api/v5/account/set-trading-config.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-trading-config
        """
        return self._native_private(
            "set_trading_config", self._native_params(type=type_, stgyType=stgy_type)
        )

    def precheck_delta_neutral(self, *, stgy_type: str) -> dict[str, Any]:
        """
        GET /api/v5/account/precheck-set-delta-neutral.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-precheck-set-delta-neutral
        """
        return self._native_private(
            "precheck_delta_neutral", self._native_params(stgyType=stgy_type)
        )

    def get_repayment_currencies(self) -> dict[str, Any]:
        """

        GET /api/v5/trade/one-click-repay-currency-list-v2.

        Source:
        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-currency-list-new

        """
        return self._native_private("get_repayment_currencies", self._native_params())

    def repay_debt(self, *, debt_ccy: str, repay_ccy_list: list[str]) -> dict[str, Any]:
        """

        POST /api/v5/trade/one-click-repay-v2.

        Source:
        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-trade-one-click-repay-new

        """
        return self._native_private(
            "repay_debt", self._native_params(debtCcy=debt_ccy, repayCcyList=repay_ccy_list)
        )

    def get_repayment_history(
        self, *, after: str | None = None, before: str | None = None, limit: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v5/trade/one-click-repay-history-v2.

        Source:
        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-history-new

        """
        return self._native_private(
            "get_repayment_history", self._native_params(after=after, before=before, limit=limit)
        )

    def get_spread_order_history_archive(
        self,
        *,
        sprd_id: str | None = None,
        ord_type: str | None = None,
        state: str | None = None,
        inst_type: str | None = None,
        inst_family: str | None = None,
        begin_id: str | None = None,
        end_id: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """

        GET /api/v5/sprd/orders-history-archive.

        Source:
        https://www.okx.com/docs-v5/en/#spread-trading-rest-api-get-orders-history-last-3-months

        """
        return self._native_private(
            "get_spread_order_history_archive",
            self._native_params(
                sprdId=sprd_id,
                ordType=ord_type,
                state=state,
                instType=inst_type,
                instFamily=inst_family,
                beginId=begin_id,
                endId=end_id,
                begin=begin,
                end=end,
                limit=limit,
            ),
        )

    def get_bill_types(self, *, type_: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/account/subtypes. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bill-types
        """
        return self._native_private("get_bill_types", self._native_params(type=type_))

    def simulate_positions(
        self,
        *,
        acct_lv: str | None = None,
        incl_real_pos_and_eq: bool | None = None,
        lever: str | None = None,
        sim_pos: list[dict[str, Any]] | None = None,
        sim_asset: list[dict[str, Any]] | None = None,
        greeks_type: str | None = None,
        idx_vol: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/account/position-builder. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-new
        """
        return self._native_private(
            "simulate_positions",
            self._native_params(
                acctLv=acct_lv,
                inclRealPosAndEq=incl_real_pos_and_eq,
                lever=lever,
                simPos=sim_pos,
                simAsset=sim_asset,
                greeksType=greeks_type,
                idxVol=idx_vol,
            ),
        )

    def get_position_margin_graph(
        self,
        *,
        type_: str,
        mmr_config: dict[str, Any],
        incl_real_pos_and_eq: bool | None = None,
        sim_pos: list[dict[str, Any]] | None = None,
        sim_asset: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v5/account/position-builder-graph. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-trend-graph

        """
        return self._native_private(
            "get_position_margin_graph",
            self._native_params(
                inclRealPosAndEq=incl_real_pos_and_eq,
                simPos=sim_pos,
                simAsset=sim_asset,
                type=type_,
                mmrConfig=mmr_config,
            ),
        )

    def move_positions(
        self, *, from_acct: str, to_acct: str, legs: list[dict[str, Any]], client_id: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/account/move-positions. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-move-positions
        """
        return self._native_private(
            "move_positions",
            self._native_params(fromAcct=from_acct, toAcct=to_acct, legs=legs, clientId=client_id),
        )

    def get_move_positions_history(
        self,
        *,
        block_td_id: str | None = None,
        client_id: str | None = None,
        begin_ts: str | None = None,
        end_ts: str | None = None,
        limit: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/account/move-positions-history. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-move-positions-history
        """
        return self._native_private(
            "get_move_positions_history",
            self._native_params(
                blockTdId=block_td_id,
                clientId=client_id,
                beginTs=begin_ts,
                endTs=end_ts,
                limit=limit,
                state=state,
            ),
        )

    def adjust_demo_balance(
        self, *, type_: str, adjustments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        POST /api/v5/account/demo-adjust-balance. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-adjust-demo-account-balance
        """
        return self._native_private(
            "adjust_demo_balance", self._native_params(type=type_, adjustments=adjustments)
        )

    def rfq_create_rfq(
        self,
        *,
        counterparties: list[str],
        legs: list[dict[str, Any]],
        anonymous: bool | None = None,
        cl_rfq_id: str | None = None,
        tag: str | None = None,
        allow_partial_execution: bool | None = None,
        acct_alloc: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/rfq/create-rfq. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-create-rfq
        """
        return self._native_private(
            "rfq_create_rfq",
            self._native_params(
                counterparties=counterparties,
                anonymous=anonymous,
                clRfqId=cl_rfq_id,
                tag=tag,
                allowPartialExecution=allow_partial_execution,
                legs=legs,
                acctAlloc=acct_alloc,
            ),
        )

    def get_rfq_counterparties(self) -> dict[str, Any]:
        """
        GET /api/v5/rfq/counterparties. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-counterparties
        """
        return self._native_private("get_rfq_counterparties", self._native_params())

    def rfq_cancel_rfq(
        self, *, rfq_id: str | None = None, cl_rfq_id: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/rfq/cancel-rfq. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-rfq
        """
        return self._native_private(
            "rfq_cancel_rfq", self._native_params(rfqId=rfq_id, clRfqId=cl_rfq_id)
        )

    def rfq_cancel_batch_rfqs(
        self, *, rfq_ids: list[str] | None = None, cl_rfq_ids: list[str] | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/rfq/cancel-batch-rfqs. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-multiple-rfqs
        """
        return self._native_private(
            "rfq_cancel_batch_rfqs", self._native_params(rfqIds=rfq_ids, clRfqIds=cl_rfq_ids)
        )

    def rfq_cancel_all_rfqs(self) -> dict[str, Any]:
        """
        POST /api/v5/rfq/cancel-all-rfqs. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-all-rfqs
        """
        return self._native_private("rfq_cancel_all_rfqs", self._native_params())

    def rfq_execute_quote(
        self, *, rfq_id: str, quote_id: str, legs: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/rfq/execute-quote. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-execute-quote
        """
        return self._native_private(
            "rfq_execute_quote", self._native_params(rfqId=rfq_id, quoteId=quote_id, legs=legs)
        )

    def get_rfq_rfqs(
        self,
        *,
        rfq_id: str | None = None,
        cl_rfq_id: str | None = None,
        state: str | None = None,
        begin_id: str | None = None,
        end_id: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/rfq/rfqs. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-rfqs
        """
        return self._native_private(
            "get_rfq_rfqs",
            self._native_params(
                rfqId=rfq_id,
                clRfqId=cl_rfq_id,
                state=state,
                beginId=begin_id,
                endId=end_id,
                limit=limit,
            ),
        )

    def get_rfq_quotes(
        self,
        *,
        rfq_id: str | None = None,
        cl_rfq_id: str | None = None,
        quote_id: str | None = None,
        cl_quote_id: str | None = None,
        state: str | None = None,
        begin_id: str | None = None,
        end_id: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/rfq/quotes. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-quotes
        """
        return self._native_private(
            "get_rfq_quotes",
            self._native_params(
                rfqId=rfq_id,
                clRfqId=cl_rfq_id,
                quoteId=quote_id,
                clQuoteId=cl_quote_id,
                state=state,
                beginId=begin_id,
                endId=end_id,
                limit=limit,
            ),
        )

    def get_rfq_trades(
        self,
        *,
        rfq_id: str | None = None,
        cl_rfq_id: str | None = None,
        quote_id: str | None = None,
        block_td_id: str | None = None,
        cl_quote_id: str | None = None,
        begin_id: str | None = None,
        end_id: str | None = None,
        begin_ts: str | None = None,
        end_ts: str | None = None,
        limit: str | None = None,
        is_successful: bool | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/rfq/trades. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-trades
        """
        return self._native_private(
            "get_rfq_trades",
            self._native_params(
                rfqId=rfq_id,
                clRfqId=cl_rfq_id,
                quoteId=quote_id,
                blockTdId=block_td_id,
                clQuoteId=cl_quote_id,
                beginId=begin_id,
                endId=end_id,
                beginTs=begin_ts,
                endTs=end_ts,
                limit=limit,
                isSuccessful=is_successful,
            ),
        )

    def get_non_tradable_assets(self, *, ccy: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/asset/non-tradable-assets. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-non-tradable-assets
        """
        return self._native_private("get_non_tradable_assets", self._native_params(ccy=ccy))

    def create_sub_account(
        self, *, sub_acct: str, type_: str, label: str | None = None, pwd: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/users/subaccount/create-subaccount. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-create-sub-account
        """
        return self._native_private(
            "create_sub_account",
            self._native_params(subAcct=sub_acct, type=type_, label=label, pwd=pwd),
        )

    def create_sub_account_api_key(
        self,
        *,
        sub_acct: str,
        label: str,
        passphrase: str,
        perm: str | None = None,
        ip: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v5/users/subaccount/apikey. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#sub-account-rest-api-create-an-api-key-for-a-sub-account

        """
        return self._native_private(
            "create_sub_account_api_key",
            self._native_params(
                subAcct=sub_acct, label=label, passphrase=passphrase, perm=perm, ip=ip
            ),
        )

    def get_sub_account_api_keys(
        self, *, sub_acct: str, api_key: str | None = None
    ) -> dict[str, Any]:
        """

        GET /api/v5/users/subaccount/apikey. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#sub-account-rest-api-query-the-api-key-of-a-sub-account

        """
        return self._native_private(
            "get_sub_account_api_keys", self._native_params(subAcct=sub_acct, apiKey=api_key)
        )

    def modify_sub_account_api_key(
        self,
        *,
        sub_acct: str,
        api_key: str,
        label: str | None = None,
        perm: str | None = None,
        ip: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /api/v5/users/subaccount/modify-apikey. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#sub-account-rest-api-reset-the-api-key-of-a-sub-account

        """
        return self._native_private(
            "modify_sub_account_api_key",
            self._native_params(subAcct=sub_acct, apiKey=api_key, label=label, perm=perm, ip=ip),
        )

    def delete_sub_account_api_key(self, *, sub_acct: str, api_key: str) -> dict[str, Any]:
        """

        POST /api/v5/users/subaccount/delete-apikey. Use native instrument IDs.

        Source:
        https://www.okx.com/docs-v5/en/#sub-account-rest-api-delete-the-api-key-of-sub-accounts

        """
        return self._native_private(
            "delete_sub_account_api_key", self._native_params(subAcct=sub_acct, apiKey=api_key)
        )

    def set_sub_account_transfer_out(
        self, *, sub_acct: str, can_trans_out: bool | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/users/subaccount/set-transfer-out. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out
        """
        return self._native_private(
            "set_sub_account_transfer_out",
            self._native_params(subAcct=sub_acct, canTransOut=can_trans_out),
        )
