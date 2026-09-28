from json import dumps
from typing import Any

from ..enums import OrderSide
from ._batch_http import TradeHTTPBatchHTTP
from ._http_manager import HTTPManager
from ._transfers_http import TradeHTTPTransfersHTTP
from ._withdrawals_http import TradeHTTPWithdrawalsHTTP


class TradeHTTP(TradeHTTPBatchHTTP, TradeHTTPTransfersHTTP, TradeHTTPWithdrawalsHTTP, HTTPManager):
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

    def trading_bot_grid_order_algo(
        self,
        *,
        inst_id: str,
        algo_ord_type: str,
        max_px: str,
        min_px: str,
        grid_num: str,
        run_type: str | None = None,
        tp_trigger_px: str | None = None,
        sl_trigger_px: str | None = None,
        algo_cl_ord_id: str | None = None,
        tag: str | None = None,
        profit_sharing_ratio: str | None = None,
        trigger_params: list[dict[str, Any]] | None = None,
        quote_sz: str | None = None,
        base_sz: str | None = None,
        trade_quote_ccy: str | None = None,
        sz: str | None = None,
        direction: str | None = None,
        lever: str | None = None,
        base_pos: bool | None = None,
        tp_ratio: str | None = None,
        sl_ratio: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-place-grid-algo-order
        """
        return self._native_private(
            "trading_bot_grid_order_algo",
            self._native_params(
                instId=inst_id,
                algoOrdType=algo_ord_type,
                maxPx=max_px,
                minPx=min_px,
                gridNum=grid_num,
                runType=run_type,
                tpTriggerPx=tp_trigger_px,
                slTriggerPx=sl_trigger_px,
                algoClOrdId=algo_cl_ord_id,
                tag=tag,
                profitSharingRatio=profit_sharing_ratio,
                triggerParams=trigger_params,
                quoteSz=quote_sz,
                baseSz=base_sz,
                tradeQuoteCcy=trade_quote_ccy,
                sz=sz,
                direction=direction,
                lever=lever,
                basePos=base_pos,
                tpRatio=tp_ratio,
                slRatio=sl_ratio,
            ),
        )

    def trading_bot_grid_amend_algo_basic_param(
        self,
        *,
        algo_id: str,
        min_px: str,
        max_px: str,
        grid_num: str,
        topup_amount: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/amend-algo-basic-param.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-amend-grid-algo-order-basic-param
        """
        return self._native_private(
            "trading_bot_grid_amend_algo_basic_param",
            self._native_params(
                algoId=algo_id,
                minPx=min_px,
                maxPx=max_px,
                gridNum=grid_num,
                topupAmount=topup_amount,
            ),
        )

    def trading_bot_grid_amend_order_algo(
        self,
        *,
        algo_id: str,
        inst_id: str,
        sl_trigger_px: str | None = None,
        tp_trigger_px: str | None = None,
        tp_ratio: str | None = None,
        sl_ratio: str | None = None,
        top_up_amt: str | None = None,
        trigger_params: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/amend-order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-amend-grid-algo-order
        """
        return self._native_private(
            "trading_bot_grid_amend_order_algo",
            self._native_params(
                algoId=algo_id,
                instId=inst_id,
                slTriggerPx=sl_trigger_px,
                tpTriggerPx=tp_trigger_px,
                tpRatio=tp_ratio,
                slRatio=sl_ratio,
                topUpAmt=top_up_amt,
                triggerParams=trigger_params,
            ),
        )

    def trading_bot_grid_stop_order_algo(self, *, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/stop-order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-stop-grid-algo-order
        """
        return self._native_private(
            "trading_bot_grid_stop_order_algo", self._native_params(orders=orders)
        )

    def trading_bot_grid_close_position(
        self, *, algo_id: str, mkt_close: bool, sz: str | None = None, px: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/close-position. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-close-position-for-contract-grid
        """
        return self._native_private(
            "trading_bot_grid_close_position",
            self._native_params(algoId=algo_id, mktClose=mkt_close, sz=sz, px=px),
        )

    def trading_bot_grid_cancel_close_order(self, *, algo_id: str, ord_id: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/cancel-close-order. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-cancel-close-position-order-for-contract-grid
        """
        return self._native_private(
            "trading_bot_grid_cancel_close_order", self._native_params(algoId=algo_id, ordId=ord_id)
        )

    def trading_bot_grid_order_instant_trigger(
        self, *, algo_id: str, top_up_amt: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/order-instant-trigger.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-instant-trigger-grid-algo-order
        """
        return self._native_private(
            "trading_bot_grid_order_instant_trigger",
            self._native_params(algoId=algo_id, topUpAmt=top_up_amt),
        )

    def get_trading_bot_grid_orders_algo_pending(
        self,
        *,
        algo_ord_type: str,
        algo_id: str | None = None,
        inst_id: str | None = None,
        inst_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/orders-algo-pending. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-list
        """
        return self._native_private(
            "get_trading_bot_grid_orders_algo_pending",
            self._native_params(
                algoOrdType=algo_ord_type,
                algoId=algo_id,
                instId=inst_id,
                instType=inst_type,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_trading_bot_grid_orders_algo_history(
        self,
        *,
        algo_ord_type: str,
        algo_id: str | None = None,
        inst_id: str | None = None,
        inst_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/orders-algo-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-history
        """
        return self._native_private(
            "get_trading_bot_grid_orders_algo_history",
            self._native_params(
                algoOrdType=algo_ord_type,
                algoId=algo_id,
                instId=inst_id,
                instType=inst_type,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_trading_bot_grid_orders_algo_details(
        self, *, algo_ord_type: str, algo_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/orders-algo-details. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-details
        """
        return self._native_private(
            "get_trading_bot_grid_orders_algo_details",
            self._native_params(algoOrdType=algo_ord_type, algoId=algo_id),
        )

    def get_trading_bot_grid_sub_orders(
        self,
        *,
        algo_ord_type: str,
        algo_id: str,
        type_: str,
        group_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/sub-orders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-sub-orders
        """
        return self._native_private(
            "get_trading_bot_grid_sub_orders",
            self._native_params(
                algoOrdType=algo_ord_type,
                algoId=algo_id,
                type=type_,
                groupId=group_id,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_trading_bot_grid_positions(self, *, algo_ord_type: str, algo_id: str) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/grid/positions. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-get-grid-algo-order-positions
        """
        return self._native_private(
            "get_trading_bot_grid_positions",
            self._native_params(algoOrdType=algo_ord_type, algoId=algo_id),
        )

    def trading_bot_grid_compute_margin_balance(
        self, *, algo_id: str, type_: str, amt: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/compute-margin-balance.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-compute-margin-balance
        """
        return self._native_private(
            "trading_bot_grid_compute_margin_balance",
            self._native_params(algoId=algo_id, type=type_, amt=amt),
        )

    def trading_bot_grid_margin_balance(
        self, *, algo_id: str, type_: str, amt: str | None = None, percent: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/margin-balance. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-adjust-margin-balance
        """
        return self._native_private(
            "trading_bot_grid_margin_balance",
            self._native_params(algoId=algo_id, type=type_, amt=amt, percent=percent),
        )

    def trading_bot_grid_adjust_investment(
        self, *, algo_id: str, amt: str, allow_reinvest_profit: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/adjust-investment. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-add-investment
        """
        return self._native_private(
            "trading_bot_grid_adjust_investment",
            self._native_params(algoId=algo_id, amt=amt, allowReinvestProfit=allow_reinvest_profit),
        )

    def trading_bot_grid_copy_order_algo(
        self,
        *,
        inst_id: str,
        algo_ord_type: str,
        source_algo_id: str,
        quote_sz: str | None = None,
        lever: str | None = None,
        auto_reserve: bool | None = None,
        sz: str | None = None,
        actual_margin_sz: str | None = None,
        extra_margin_sz: str | None = None,
        algo_cl_ord_id: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/grid/copy-order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-copy-grid-algo-order
        """
        return self._native_private(
            "trading_bot_grid_copy_order_algo",
            self._native_params(
                instId=inst_id,
                algoOrdType=algo_ord_type,
                sourceAlgoId=source_algo_id,
                quoteSz=quote_sz,
                lever=lever,
                autoReserve=auto_reserve,
                sz=sz,
                actualMarginSz=actual_margin_sz,
                extraMarginSz=extra_margin_sz,
                algoClOrdId=algo_cl_ord_id,
                tag=tag,
            ),
        )

    def trading_bot_dca_create(
        self,
        *,
        inst_id: str,
        algo_ord_type: str,
        init_ord_amt: str,
        max_safety_ords: str,
        tp_pct: str,
        lever: str,
        trigger_params: list[dict[str, Any]],
        allow_reinvest: str | None = None,
        safety_ord_amt: str | None = None,
        px_steps: str | None = None,
        px_steps_mult: str | None = None,
        vol_mult: str | None = None,
        sl_pct: str | None = None,
        sl_mode: str | None = None,
        direction: str | None = None,
        profit_sharing_ratio: str | None = None,
        tracking_mode: str | None = None,
        tag: str | None = None,
        algo_cl_ord_id: str | None = None,
        trade_quote_ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/create. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-place-dca-algo-order
        """
        return self._native_private(
            "trading_bot_dca_create",
            self._native_params(
                instId=inst_id,
                algoOrdType=algo_ord_type,
                initOrdAmt=init_ord_amt,
                allowReinvest=allow_reinvest,
                safetyOrdAmt=safety_ord_amt,
                maxSafetyOrds=max_safety_ords,
                pxSteps=px_steps,
                pxStepsMult=px_steps_mult,
                volMult=vol_mult,
                tpPct=tp_pct,
                slPct=sl_pct,
                slMode=sl_mode,
                direction=direction,
                lever=lever,
                triggerParams=trigger_params,
                profitSharingRatio=profit_sharing_ratio,
                trackingMode=tracking_mode,
                tag=tag,
                algoClOrdId=algo_cl_ord_id,
                tradeQuoteCcy=trade_quote_ccy,
            ),
        )

    def trading_bot_dca_amend_order_algo(
        self,
        *,
        algo_id: str,
        px_steps: str,
        px_steps_mult: str,
        vol_mult: str,
        tp_pct: str,
        sl_pct: str,
        init_ord_amt: str,
        safety_ord_amt: str,
        max_safety_ords: str,
        reserve_funds: bool,
        trigger_params: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/amend-order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-spot-dca-basic-param
        """
        return self._native_private(
            "trading_bot_dca_amend_order_algo",
            self._native_params(
                algoId=algo_id,
                pxSteps=px_steps,
                pxStepsMult=px_steps_mult,
                volMult=vol_mult,
                tpPct=tp_pct,
                slPct=sl_pct,
                initOrdAmt=init_ord_amt,
                safetyOrdAmt=safety_ord_amt,
                maxSafetyOrds=max_safety_ords,
                reserveFunds=reserve_funds,
                triggerParams=trigger_params,
            ),
        )

    def trading_bot_dca_stop(
        self, *, algo_id: str, algo_ord_type: str, stop_type: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/stop. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-stop-dca-algo-order
        """
        return self._native_private(
            "trading_bot_dca_stop",
            self._native_params(algoId=algo_id, algoOrdType=algo_ord_type, stopType=stop_type),
        )

    def get_trading_bot_dca_ongoing_list(
        self,
        *,
        algo_ord_type: str,
        algo_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/dca/ongoing-list. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-details
        """
        return self._native_private(
            "get_trading_bot_dca_ongoing_list",
            self._native_params(
                algoOrdType=algo_ord_type, algoId=algo_id, after=after, before=before, limit=limit
            ),
        )

    def get_trading_bot_dca_history_list(
        self,
        *,
        algo_ord_type: str,
        algo_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/dca/history-list. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-history
        """
        return self._native_private(
            "get_trading_bot_dca_history_list",
            self._native_params(
                algoOrdType=algo_ord_type, algoId=algo_id, after=after, before=before, limit=limit
            ),
        )

    def get_trading_bot_dca_orders(
        self,
        *,
        algo_id: str,
        algo_ord_type: str,
        cycle_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/dca/orders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-sub-orders
        """
        return self._native_private(
            "get_trading_bot_dca_orders",
            self._native_params(
                algoId=algo_id,
                algoOrdType=algo_ord_type,
                cycleId=cycle_id,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def trading_bot_dca_orders_manual_buy(
        self,
        *,
        algo_id: str,
        algo_ord_type: str,
        price: str,
        amt: str,
        ord_type: str | None = None,
        trade_quote_ccy: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/orders/manual-buy. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-add-investment
        """
        return self._native_private(
            "trading_bot_dca_orders_manual_buy",
            self._native_params(
                algoId=algo_id,
                algoOrdType=algo_ord_type,
                price=price,
                amt=amt,
                ordType=ord_type,
                tradeQuoteCcy=trade_quote_ccy,
            ),
        )

    def trading_bot_dca_settings_reinvestment(
        self, *, algo_id: str, algo_ord_type: str, allow_reinvest: bool
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/settings/reinvestment.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-dca-reinvestment
        """
        return self._native_private(
            "trading_bot_dca_settings_reinvestment",
            self._native_params(
                algoId=algo_id, algoOrdType=algo_ord_type, allowReinvest=allow_reinvest
            ),
        )

    def trading_bot_dca_settings_take_profit(
        self, *, algo_id: str, algo_ord_type: str, tp_price: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/settings/take-profit. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-amend-dca-take-profit-settings
        """
        return self._native_private(
            "trading_bot_dca_settings_take_profit",
            self._native_params(algoId=algo_id, algoOrdType=algo_ord_type, tpPrice=tp_price),
        )

    def get_trading_bot_dca_position_details(
        self, *, algo_id: str, algo_ord_type: str
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/dca/position-details. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-algo-order-position-details
        """
        return self._native_private(
            "get_trading_bot_dca_position_details",
            self._native_params(algoId=algo_id, algoOrdType=algo_ord_type),
        )

    def get_trading_bot_dca_cycle_list(
        self,
        *,
        algo_id: str,
        algo_ord_type: str,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/dca/cycle-list. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-get-dca-cycle-list
        """
        return self._native_private(
            "get_trading_bot_dca_cycle_list",
            self._native_params(
                algoId=algo_id,
                algoOrdType=algo_ord_type,
                instId=inst_id,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def trading_bot_dca_margin_add(self, *, algo_id: str, amt: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/margin/add. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-add-dca-margin
        """
        return self._native_private(
            "trading_bot_dca_margin_add", self._native_params(algoId=algo_id, amt=amt)
        )

    def trading_bot_dca_margin_reduce(self, *, algo_id: str, amt: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/dca/margin/reduce. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-dca-trading-post-reduce-dca-margin
        """
        return self._native_private(
            "trading_bot_dca_margin_reduce", self._native_params(algoId=algo_id, amt=amt)
        )

    def trading_bot_signal_create_signal(
        self, *, signal_chan_name: str, signal_chan_desc: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/create-signal. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-create-signal
        """
        return self._native_private(
            "trading_bot_signal_create_signal",
            self._native_params(signalChanName=signal_chan_name, signalChanDesc=signal_chan_desc),
        )

    def get_trading_bot_signal_signals(
        self,
        *,
        signal_source_type: str,
        signal_chan_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/signals. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signals
        """
        return self._native_private(
            "get_trading_bot_signal_signals",
            self._native_params(
                signalSourceType=signal_source_type,
                signalChanId=signal_chan_id,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def trading_bot_signal_order_algo(
        self,
        *,
        signal_chan_id: str,
        lever: str,
        invest_amt: str,
        sub_ord_type: str,
        include_all: bool | None = None,
        inst_ids: str | None = None,
        ratio: str | None = None,
        entry_setting_param: dict[str, Any] | None = None,
        exit_setting_param: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-create-signal-bot
        """
        return self._native_private(
            "trading_bot_signal_order_algo",
            self._native_params(
                signalChanId=signal_chan_id,
                lever=lever,
                investAmt=invest_amt,
                subOrdType=sub_ord_type,
                includeAll=include_all,
                instIds=inst_ids,
                ratio=ratio,
                entrySettingParam=entry_setting_param,
                exitSettingParam=exit_setting_param,
            ),
        )

    def trading_bot_signal_stop_order_algo(self, *, orders: list[dict[str, Any]]) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/stop-order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-cancel-signal-bots
        """
        return self._native_private(
            "trading_bot_signal_stop_order_algo", self._native_params(orders=orders)
        )

    def trading_bot_signal_margin_balance(
        self, *, algo_id: str, type_: str, amt: str, allow_reinvest: bool | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/margin-balance. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-adjust-margin-balance
        """
        return self._native_private(
            "trading_bot_signal_margin_balance",
            self._native_params(algoId=algo_id, type=type_, amt=amt, allowReinvest=allow_reinvest),
        )

    def trading_bot_signal_amend_tpsl(
        self, *, algo_id: str, exit_setting_param: dict[str, Any]
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/amendTPSL. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-amend-tpsl
        """
        return self._native_private(
            "trading_bot_signal_amend_tpsl",
            self._native_params(algoId=algo_id, exitSettingParam=exit_setting_param),
        )

    def trading_bot_signal_set_instruments(
        self, *, algo_id: str, inst_ids: list[str], include_all: bool
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/set-instruments. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-set-instruments
        """
        return self._native_private(
            "trading_bot_signal_set_instruments",
            self._native_params(algoId=algo_id, instIds=inst_ids, includeAll=include_all),
        )

    def get_trading_bot_signal_orders_algo_details(
        self, *, algo_ord_type: str, algo_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/orders-algo-details.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-order-details
        """
        return self._native_private(
            "get_trading_bot_signal_orders_algo_details",
            self._native_params(algoOrdType=algo_ord_type, algoId=algo_id),
        )

    def get_trading_bot_signal_orders_algo_pending(
        self,
        *,
        algo_ord_type: str,
        after: str,
        algo_id: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/orders-algo-pending.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-active-signal-bot
        """
        return self._native_private(
            "get_trading_bot_signal_orders_algo_pending",
            self._native_params(
                algoOrdType=algo_ord_type, algoId=algo_id, after=after, before=before, limit=limit
            ),
        )

    def get_trading_bot_signal_orders_algo_history(
        self,
        *,
        algo_ord_type: str,
        algo_id: str,
        after: str,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/orders-algo-history.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-history
        """
        return self._native_private(
            "get_trading_bot_signal_orders_algo_history",
            self._native_params(
                algoOrdType=algo_ord_type, algoId=algo_id, after=after, before=before, limit=limit
            ),
        )

    def get_trading_bot_signal_positions(
        self, *, algo_ord_type: str, algo_id: str
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/positions. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-order-positions
        """
        return self._native_private(
            "get_trading_bot_signal_positions",
            self._native_params(algoOrdType=algo_ord_type, algoId=algo_id),
        )

    def get_trading_bot_signal_positions_history(
        self,
        *,
        algo_id: str,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/positions-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-position-history
        """
        return self._native_private(
            "get_trading_bot_signal_positions_history",
            self._native_params(
                algoId=algo_id, instId=inst_id, after=after, before=before, limit=limit
            ),
        )

    def trading_bot_signal_close_position(self, *, algo_id: str, inst_id: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/close-position. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-close-position
        """
        return self._native_private(
            "trading_bot_signal_close_position", self._native_params(algoId=algo_id, instId=inst_id)
        )

    def trading_bot_signal_sub_order(
        self,
        *,
        inst_id: str,
        algo_id: str,
        side: str,
        ord_type: str,
        sz: str,
        px: str | None = None,
        reduce_only: bool | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/sub-order. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-place-sub-order
        """
        return self._native_private(
            "trading_bot_signal_sub_order",
            self._native_params(
                instId=inst_id,
                algoId=algo_id,
                side=side,
                ordType=ord_type,
                sz=sz,
                px=px,
                reduceOnly=reduce_only,
            ),
        )

    def trading_bot_signal_cancel_sub_order(
        self, *, algo_id: str, inst_id: str, signal_ord_id: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/signal/cancel-sub-order. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-post-cancel-sub-order
        """
        return self._native_private(
            "trading_bot_signal_cancel_sub_order",
            self._native_params(algoId=algo_id, instId=inst_id, signalOrdId=signal_ord_id),
        )

    def get_trading_bot_signal_sub_orders(
        self,
        *,
        algo_id: str,
        algo_ord_type: str,
        state: str | None = None,
        signal_ord_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
        type_: str | None = None,
        cl_ord_id: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/sub-orders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-sub-orders
        """
        return self._native_private(
            "get_trading_bot_signal_sub_orders",
            self._native_params(
                algoId=algo_id,
                algoOrdType=algo_ord_type,
                state=state,
                signalOrdId=signal_ord_id,
                after=after,
                before=before,
                begin=begin,
                end=end,
                limit=limit,
                type=type_,
                clOrdId=cl_ord_id,
            ),
        )

    def get_trading_bot_signal_event_history(
        self,
        *,
        algo_id: str,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/signal/event-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-signal-bot-trading-get-signal-bot-event-history
        """
        return self._native_private(
            "get_trading_bot_signal_event_history",
            self._native_params(algoId=algo_id, after=after, before=before, limit=limit),
        )

    def trading_bot_recurring_order_algo(
        self,
        *,
        stgy_name: str,
        recurring_list: list[dict[str, Any]],
        period: str,
        recurring_time: str,
        time_zone: str,
        amt: str,
        investment_ccy: str,
        td_mode: str,
        recurring_day: str | None = None,
        recurring_hour: str | None = None,
        algo_cl_ord_id: str | None = None,
        tag: str | None = None,
        trade_quote_ccy: str | None = None,
        source: list[str] | None = None,
        recurring_time_type: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/order-algo. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-place-recurring-buy-order
        """
        return self._native_private(
            "trading_bot_recurring_order_algo",
            self._native_params(
                stgyName=stgy_name,
                recurringList=recurring_list,
                period=period,
                recurringDay=recurring_day,
                recurringHour=recurring_hour,
                recurringTime=recurring_time,
                timeZone=time_zone,
                amt=amt,
                investmentCcy=investment_ccy,
                tdMode=td_mode,
                algoClOrdId=algo_cl_ord_id,
                tag=tag,
                tradeQuoteCcy=trade_quote_ccy,
                source=source,
                recurringTimeType=recurring_time_type,
            ),
        )

    def trading_bot_recurring_amend_order_algo(
        self, *, algo_id: str, stgy_name: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/amend-order-algo.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-order
        """
        return self._native_private(
            "trading_bot_recurring_amend_order_algo",
            self._native_params(algoId=algo_id, stgyName=stgy_name),
        )

    def trading_bot_recurring_stop_order_algo(
        self, *, orders: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/stop-order-algo.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-stop-recurring-buy-order
        """
        return self._native_private(
            "trading_bot_recurring_stop_order_algo", self._native_params(orders=orders)
        )

    def get_trading_bot_recurring_orders_algo_pending(
        self,
        *,
        algo_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/recurring/orders-algo-pending.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-list
        """
        return self._native_private(
            "get_trading_bot_recurring_orders_algo_pending",
            self._native_params(algoId=algo_id, after=after, before=before, limit=limit),
        )

    def get_trading_bot_recurring_orders_algo_history(
        self,
        *,
        algo_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/recurring/orders-algo-history.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-history
        """
        return self._native_private(
            "get_trading_bot_recurring_orders_algo_history",
            self._native_params(algoId=algo_id, after=after, before=before, limit=limit),
        )

    def get_trading_bot_recurring_orders_algo_details(self, *, algo_id: str) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/recurring/orders-algo-details.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-order-details
        """
        return self._native_private(
            "get_trading_bot_recurring_orders_algo_details", self._native_params(algoId=algo_id)
        )

    def get_trading_bot_recurring_sub_orders(
        self,
        *,
        algo_id: str,
        ord_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/tradingBot/recurring/sub-orders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-get-recurring-buy-sub-orders
        """
        return self._native_private(
            "get_trading_bot_recurring_sub_orders",
            self._native_params(
                algoId=algo_id, ordId=ord_id, after=after, before=before, limit=limit
            ),
        )

    def trading_bot_recurring_amend_recurring_time(
        self,
        *,
        algo_id: str,
        recurring_time_type: str,
        time_zone: str,
        period: str,
        recurring_hour: str | None = None,
        recurring_day: str | None = None,
        recurring_time: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/amend-recurring-time.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-time
        """
        return self._native_private(
            "trading_bot_recurring_amend_recurring_time",
            self._native_params(
                algoId=algo_id,
                recurringTimeType=recurring_time_type,
                timeZone=time_zone,
                period=period,
                recurringHour=recurring_hour,
                recurringDay=recurring_day,
                recurringTime=recurring_time,
            ),
        )

    def trading_bot_recurring_amend_recurring_amount(
        self, *, algo_id: str, amount: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/amend-recurring-amount.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-recurring-buy-amount
        """
        return self._native_private(
            "trading_bot_recurring_amend_recurring_amount",
            self._native_params(algoId=algo_id, amount=amount),
        )

    def trading_bot_recurring_add_investment(self, *, algo_id: str, amount: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/add-investment. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-add-investment
        """
        return self._native_private(
            "trading_bot_recurring_add_investment",
            self._native_params(algoId=algo_id, amount=amount),
        )

    def trading_bot_recurring_pause(self, *, algo_id: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/pause. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-pause-recurring-buy
        """
        return self._native_private(
            "trading_bot_recurring_pause", self._native_params(algoId=algo_id)
        )

    def trading_bot_recurring_restart(self, *, algo_id: str) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/restart. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-restart-recurring-buy
        """
        return self._native_private(
            "trading_bot_recurring_restart", self._native_params(algoId=algo_id)
        )

    def trading_bot_recurring_amend_price_range(
        self, *, algo_id: str, recurring_list: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        POST /api/v5/tradingBot/recurring/amend-price-range.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-recurring-buy-post-amend-price-range
        """
        return self._native_private(
            "trading_bot_recurring_amend_price_range",
            self._native_params(algoId=algo_id, recurringList=recurring_list),
        )

    def get_copytrading_current_subpositions(
        self,
        *,
        inst_type: str | None = None,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/current-subpositions. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-existing-lead-positions
        """
        return self._native_private(
            "get_copytrading_current_subpositions",
            self._native_params(
                instType=inst_type, instId=inst_id, after=after, before=before, limit=limit
            ),
        )

    def get_copytrading_subpositions_history(
        self,
        *,
        inst_type: str | None = None,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/subpositions-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-lead-position-history
        """
        return self._native_private(
            "get_copytrading_subpositions_history",
            self._native_params(
                instType=inst_type, instId=inst_id, after=after, before=before, limit=limit
            ),
        )

    def copytrading_algo_order(
        self,
        *,
        sub_pos_id: str,
        inst_type: str | None = None,
        tp_trigger_px: str | None = None,
        sl_trigger_px: str | None = None,
        tp_ord_px: str | None = None,
        sl_ord_px: str | None = None,
        tp_trigger_px_type: str | None = None,
        sl_trigger_px_type: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/algo-order. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-place-lead-stop-order
        """
        return self._native_private(
            "copytrading_algo_order",
            self._native_params(
                instType=inst_type,
                subPosId=sub_pos_id,
                tpTriggerPx=tp_trigger_px,
                slTriggerPx=sl_trigger_px,
                tpOrdPx=tp_ord_px,
                slOrdPx=sl_ord_px,
                tpTriggerPxType=tp_trigger_px_type,
                slTriggerPxType=sl_trigger_px_type,
                tag=tag,
            ),
        )

    def copytrading_close_subposition(
        self,
        *,
        sub_pos_id: str,
        inst_type: str | None = None,
        ord_type: str | None = None,
        px: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/close-subposition. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-close-lead-position
        """
        return self._native_private(
            "copytrading_close_subposition",
            self._native_params(
                instType=inst_type, subPosId=sub_pos_id, ordType=ord_type, px=px, tag=tag
            ),
        )

    def get_copytrading_instruments(self, *, inst_type: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/instruments. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-leading-instruments
        """
        return self._native_private(
            "get_copytrading_instruments", self._native_params(instType=inst_type)
        )

    def copytrading_set_instruments(
        self, *, inst_id: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/set-instruments. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-leading-instruments
        """
        return self._native_private(
            "copytrading_set_instruments", self._native_params(instType=inst_type, instId=inst_id)
        )

    def get_copytrading_profit_sharing_details(
        self,
        *,
        inst_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/profit-sharing-details. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-profit-sharing-details
        """
        return self._native_private(
            "get_copytrading_profit_sharing_details",
            self._native_params(instType=inst_type, after=after, before=before, limit=limit),
        )

    def get_copytrading_total_profit_sharing(
        self, *, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/total-profit-sharing. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-total-profit-sharing
        """
        return self._native_private(
            "get_copytrading_total_profit_sharing", self._native_params(instType=inst_type)
        )

    def get_copytrading_unrealized_profit_sharing_details(
        self, *, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/unrealized-profit-sharing-details.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-unrealized-profit-sharing-details
        """
        return self._native_private(
            "get_copytrading_unrealized_profit_sharing_details",
            self._native_params(instType=inst_type),
        )

    def get_copytrading_total_unrealized_profit_sharing(
        self, *, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/total-unrealized-profit-sharing.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-total-unrealized-profit-sharing
        """
        return self._native_private(
            "get_copytrading_total_unrealized_profit_sharing",
            self._native_params(instType=inst_type),
        )

    def copytrading_amend_profit_sharing_ratio(
        self, *, profit_sharing_ratio: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/amend-profit-sharing-ratio.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-profit-sharing-ratio
        """
        return self._native_private(
            "copytrading_amend_profit_sharing_ratio",
            self._native_params(instType=inst_type, profitSharingRatio=profit_sharing_ratio),
        )

    def get_copytrading_config(self) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/config. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-account-configuration
        """
        return self._native_private("get_copytrading_config", self._native_params())

    def copytrading_first_copy_settings(
        self,
        *,
        unique_code: str,
        copy_mgn_mode: str,
        copy_inst_id_type: str,
        copy_total_amt: str,
        sub_pos_close_type: str,
        inst_type: str | None = None,
        inst_id: str | None = None,
        copy_mode: str | None = None,
        copy_amt: str | None = None,
        copy_ratio: str | None = None,
        tp_ratio: str | None = None,
        sl_ratio: str | None = None,
        sl_total_amt: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/first-copy-settings. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-first-copy-settings
        """
        return self._native_private(
            "copytrading_first_copy_settings",
            self._native_params(
                instType=inst_type,
                uniqueCode=unique_code,
                copyMgnMode=copy_mgn_mode,
                copyInstIdType=copy_inst_id_type,
                instId=inst_id,
                copyMode=copy_mode,
                copyTotalAmt=copy_total_amt,
                copyAmt=copy_amt,
                copyRatio=copy_ratio,
                tpRatio=tp_ratio,
                slRatio=sl_ratio,
                slTotalAmt=sl_total_amt,
                subPosCloseType=sub_pos_close_type,
                tag=tag,
            ),
        )

    def copytrading_amend_copy_settings(
        self,
        *,
        unique_code: str,
        copy_mgn_mode: str,
        copy_inst_id_type: str,
        copy_total_amt: str,
        sub_pos_close_type: str,
        inst_type: str | None = None,
        inst_id: str | None = None,
        copy_mode: str | None = None,
        copy_amt: str | None = None,
        copy_ratio: str | None = None,
        tp_ratio: str | None = None,
        sl_ratio: str | None = None,
        sl_total_amt: str | None = None,
        tag: str | None = None,
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/amend-copy-settings. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-amend-copy-settings
        """
        return self._native_private(
            "copytrading_amend_copy_settings",
            self._native_params(
                instType=inst_type,
                uniqueCode=unique_code,
                copyMgnMode=copy_mgn_mode,
                copyInstIdType=copy_inst_id_type,
                instId=inst_id,
                copyMode=copy_mode,
                copyTotalAmt=copy_total_amt,
                copyAmt=copy_amt,
                copyRatio=copy_ratio,
                tpRatio=tp_ratio,
                slRatio=sl_ratio,
                slTotalAmt=sl_total_amt,
                subPosCloseType=sub_pos_close_type,
                tag=tag,
            ),
        )

    def copytrading_stop_copy_trading(
        self, *, unique_code: str, sub_pos_close_type: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/copytrading/stop-copy-trading. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-post-stop-copying
        """
        return self._native_private(
            "copytrading_stop_copy_trading",
            self._native_params(
                instType=inst_type, uniqueCode=unique_code, subPosCloseType=sub_pos_close_type
            ),
        )

    def get_copytrading_copy_settings(
        self, *, unique_code: str, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/copy-settings. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-copy-settings
        """
        return self._native_private(
            "get_copytrading_copy_settings",
            self._native_params(instType=inst_type, uniqueCode=unique_code),
        )

    def get_copytrading_current_lead_traders(
        self, *, inst_type: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/copytrading/current-lead-traders. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#order-book-trading-copy-trading-get-my-lead-traders
        """
        return self._native_private(
            "get_copytrading_current_lead_traders", self._native_params(instType=inst_type)
        )

    def get_fiat_deposit_payment_methods(self, *, ccy: str) -> dict[str, Any]:
        """
        GET /api/v5/fiat/deposit-payment-methods. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-payment-methods
        """
        return self._native_private(
            "get_fiat_deposit_payment_methods", self._native_params(ccy=ccy)
        )

    def get_fiat_deposit_order_history(
        self,
        *,
        ccy: str | None = None,
        payment_method: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/fiat/deposit-order-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-order-history
        """
        return self._native_private(
            "get_fiat_deposit_order_history",
            self._native_params(
                ccy=ccy,
                paymentMethod=payment_method,
                state=state,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_fiat_deposit(self, *, ord_id: str) -> dict[str, Any]:
        """
        GET /api/v5/fiat/deposit. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-order-detail
        """
        return self._native_private("get_fiat_deposit", self._native_params(ordId=ord_id))

    def get_fiat_buy_sell_currencies(self) -> dict[str, Any]:
        """
        GET /api/v5/fiat/buy-sell/currencies. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-currencies
        """
        return self._native_private("get_fiat_buy_sell_currencies", self._native_params())

    def get_fiat_buy_sell_currency_pair(self, *, from_ccy: str, to_ccy: str) -> dict[str, Any]:
        """
        GET /api/v5/fiat/buy-sell/currency-pair. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-currency-pair
        """
        return self._native_private(
            "get_fiat_buy_sell_currency_pair", self._native_params(fromCcy=from_ccy, toCcy=to_ccy)
        )

    def fiat_buy_sell_quote(
        self, *, side: str, from_ccy: str, to_ccy: str, rfq_amt: str, rfq_ccy: str
    ) -> dict[str, Any]:
        """
        POST /api/v5/fiat/buy-sell/quote. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-quote
        """
        return self._native_private(
            "fiat_buy_sell_quote",
            self._native_params(
                side=side, fromCcy=from_ccy, toCcy=to_ccy, rfqAmt=rfq_amt, rfqCcy=rfq_ccy
            ),
        )

    def fiat_buy_sell_trade(
        self,
        *,
        quote_id: str,
        side: str,
        from_ccy: str,
        to_ccy: str,
        rfq_amt: str,
        rfq_ccy: str,
        payment_method: str,
        cl_ord_id: str,
    ) -> dict[str, Any]:
        """
        POST /api/v5/fiat/buy-sell/trade. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-buy-sell-trade
        """
        return self._native_private(
            "fiat_buy_sell_trade",
            self._native_params(
                quoteId=quote_id,
                side=side,
                fromCcy=from_ccy,
                toCcy=to_ccy,
                rfqAmt=rfq_amt,
                rfqCcy=rfq_ccy,
                paymentMethod=payment_method,
                clOrdId=cl_ord_id,
            ),
        )

    def get_fiat_buy_sell_history(
        self,
        *,
        ord_id: str | None = None,
        cl_ord_id: str | None = None,
        state: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/fiat/buy-sell/history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-buy-sell-trade-history
        """
        return self._native_private(
            "get_fiat_buy_sell_history",
            self._native_params(
                ordId=ord_id, clOrdId=cl_ord_id, state=state, begin=begin, end=end, limit=limit
            ),
        )

    def get_asset_subaccount_managed_subaccount_bills(
        self,
        *,
        ccy: str | None = None,
        type_: str | None = None,
        sub_acct: str | None = None,
        sub_uid: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        GET /api/v5/asset/subaccount/managed-subaccount-bills.
        Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-history-of-managed-sub-account-transfer
        """
        return self._native_private(
            "get_asset_subaccount_managed_subaccount_bills",
            self._native_params(
                ccy=ccy,
                type=type_,
                subAcct=sub_acct,
                subUid=sub_uid,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_finance_stable_rewards_product_info(self, *, ccy: str) -> dict[str, Any]:
        """
        GET /api/v5/finance/stable-rewards/product-info. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-product-info
        """
        return self._native_private(
            "get_finance_stable_rewards_product_info", self._native_params(ccy=ccy)
        )

    def get_finance_stable_rewards_balance(self, *, ccy: str | None = None) -> dict[str, Any]:
        """
        GET /api/v5/finance/stable-rewards/balance. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-balance
        """
        return self._native_private(
            "get_finance_stable_rewards_balance", self._native_params(ccy=ccy)
        )

    def get_finance_stable_rewards_apy_history(
        self, *, ccy: str, days: str | None = None
    ) -> dict[str, Any]:
        """
        GET /api/v5/finance/stable-rewards/apy-history. Native instrument IDs and decimal strings.

        Source: https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-apy-history
        """
        return self._native_private(
            "get_finance_stable_rewards_apy_history", self._native_params(ccy=ccy, days=days)
        )

    def reset_mmp(
        self,
        *,
        inst_type: str | None = None,
        inst_family: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/account/mmp-reset.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-reset-mmp-status
        """
        return self._native_private(
            "reset_mmp",
            self._native_params(**{"instType": inst_type, "instFamily": inst_family}),
        )

    def set_mmp_config(
        self,
        *,
        inst_family: str,
        time_interval: str,
        frozen_interval: str,
        qty_limit: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/account/mmp-config.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-mmp
        """
        return self._native_private(
            "set_mmp_config",
            self._native_params(
                **{
                    "instFamily": inst_family,
                    "timeInterval": time_interval,
                    "frozenInterval": frozen_interval,
                    "qtyLimit": qty_limit,
                }
            ),
        )

    def get_mmp_config(
        self,
        *,
        inst_family: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/account/mmp-config.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-mmp-config
        """
        return self._native_private(
            "get_mmp_config",
            self._native_params(**{"instFamily": inst_family}),
        )

    def get_glp_today_performance(
        self,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/users/glp/todayperformance.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-get-glp-today-performance
        """
        return self._native_private(
            "get_glp_today_performance",
            self._native_params(**{}),
        )

    def get_glp_historical_performance(
        self,
        *,
        program: str,
        begin: str | None = None,
        end: str | None = None,
        limit: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/users/glp/historicalperformance.

        Source: https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-get-glp-historical-performance
        """
        return self._native_private(
            "get_glp_historical_performance",
            self._native_params(**{"program": program, "begin": begin, "end": end, "limit": limit}),
        )

    def mass_cancel_options_orders(
        self,
        *,
        inst_type: str,
        inst_family: str,
        lock_interval: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/trade/mass-cancel.

        Cancels all options orders for the specified instrument family.
        Source: https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-mass-cancel-order
        """
        return self._native_private(
            "mass_cancel_options_orders",
            self._native_params(
                **{"instType": inst_type, "instFamily": inst_family, "lockInterval": lock_interval}
            ),
        )

    def create_rfq_quote(
        self,
        *,
        rfq_id: str,
        cl_quote_id: str | None = None,
        tag: str | None = None,
        anonymous: bool | None = None,
        quote_side: str,
        expires_in: str | None = None,
        legs: list[Any],
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/create-quote.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-create-quote
        """
        return self._native_private(
            "create_rfq_quote",
            self._native_params(
                **{
                    "rfqId": rfq_id,
                    "clQuoteId": cl_quote_id,
                    "tag": tag,
                    "anonymous": anonymous,
                    "quoteSide": quote_side,
                    "expiresIn": expires_in,
                    "legs": legs,
                }
            ),
        )

    def cancel_rfq_quote(
        self,
        *,
        quote_id: str | None = None,
        cl_quote_id: str | None = None,
        rfq_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/cancel-quote.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-quote
        """
        return self._native_private(
            "cancel_rfq_quote",
            self._native_params(**{"quoteId": quote_id, "clQuoteId": cl_quote_id, "rfqId": rfq_id}),
        )

    def get_rfq_maker_instrument_settings(
        self,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/rfq/maker-instrument-settings.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-quote-products
        """
        return self._native_private(
            "get_rfq_maker_instrument_settings",
            self._native_params(**{}),
        )

    def set_rfq_maker_instrument_settings(
        self,
        *,
        inst_type: str,
        include_all: bool | None = None,
        data: list[Any],
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/maker-instrument-settings.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-set-quote-products
        """
        return self._native_private(
            "set_rfq_maker_instrument_settings",
            self._native_params(**{"instType": inst_type, "includeAll": include_all, "data": data}),
        )

    def reset_rfq_mmp(
        self,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/mmp-reset.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-reset-mmp-status
        """
        return self._native_private(
            "reset_rfq_mmp",
            self._native_params(**{}),
        )

    def set_rfq_mmp_config(
        self,
        *,
        time_interval: str,
        frozen_interval: str,
        count_limit: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/mmp-config.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-set-mmp
        """
        return self._native_private(
            "set_rfq_mmp_config",
            self._native_params(
                **{
                    "timeInterval": time_interval,
                    "frozenInterval": frozen_interval,
                    "countLimit": count_limit,
                }
            ),
        )

    def get_rfq_mmp_config(
        self,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/rfq/mmp-config.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-mmp-config
        """
        return self._native_private(
            "get_rfq_mmp_config",
            self._native_params(**{}),
        )

    def cancel_all_rfq_quotes(
        self,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/cancel-all-quotes.

        Cancels every open RFQ quote on the account.
        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-all-quotes
        """
        return self._native_private(
            "cancel_all_rfq_quotes",
            self._native_params(**{}),
        )

    def set_rfq_cancel_all_after(
        self,
        *,
        time_out: str,
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v5/rfq/cancel-all-after.

        Source: https://www.okx.com/docs-v5/en/#block-trading-rest-api-cancel-all-after
        """
        return self._native_private(
            "set_rfq_cancel_all_after",
            self._native_params(**{"timeOut": time_out}),
        )

    def get_affiliate_performance_summary(
        self,
        *,
        period_type: str | None = None,
        begin: str | None = None,
        end: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/performance/summary.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-performance-summary
        """
        return self._native_private(
            "get_affiliate_performance_summary",
            self._native_params(**{"periodType": period_type, "begin": begin, "end": end}),
        )

    def get_affiliate_invitee_detail(
        self,
        *,
        uid: str,
        period_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/invitee/detail.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-the-invitee-39-s-detail
        """
        return self._native_private(
            "get_affiliate_invitee_detail",
            self._native_params(**{"uid": uid, "periodType": period_type}),
        )

    def get_affiliate_invitee_list(
        self,
        *,
        page: str | None = None,
        limit: str | None = None,
        period_type: str | None = None,
        begin: str | None = None,
        end: str | None = None,
        keyword: str | None = None,
        commission_category: str | None = None,
        order_by: str | None = None,
        order_dir: str | None = None,
        kyc_status: str | None = None,
        sub_affiliate_uid: str | None = None,
        uid: str | None = None,
        join_time_begin: str | None = None,
        join_time_end: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/invitee/list.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-invitee-list
        """
        return self._native_private(
            "get_affiliate_invitee_list",
            self._native_params(
                **{
                    "page": page,
                    "limit": limit,
                    "periodType": period_type,
                    "begin": begin,
                    "end": end,
                    "keyword": keyword,
                    "commissionCategory": commission_category,
                    "orderBy": order_by,
                    "orderDir": order_dir,
                    "kycStatus": kyc_status,
                    "subAffiliateUid": sub_affiliate_uid,
                    "uid": uid,
                    "joinTimeBegin": join_time_begin,
                    "joinTimeEnd": join_time_end,
                }
            ),
        )

    def get_affiliate_links(
        self,
        *,
        page: str | None = None,
        limit: str | None = None,
        link_type: str | None = None,
        link_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/link/list.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-link-list
        """
        return self._native_private(
            "get_affiliate_links",
            self._native_params(
                **{"page": page, "limit": limit, "linkType": link_type, "linkStatus": link_status}
            ),
        )

    def get_affiliate_co_inviters(
        self,
        *,
        page: str | None = None,
        limit: str | None = None,
        link_status: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/co-inviter/list.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-co-inviter-link-list
        """
        return self._native_private(
            "get_affiliate_co_inviters",
            self._native_params(**{"page": page, "limit": limit, "linkStatus": link_status}),
        )

    def get_sub_affiliates(
        self,
        *,
        page: str | None = None,
        limit: str | None = None,
        keyword: str | None = None,
        commission_category: str | None = None,
        order_by: str | None = None,
        order_dir: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        GET /api/v5/affiliate/sub-affiliate/list.

        Source: https://www.okx.com/docs-v5/en/#affiliate-rest-api-get-sub-affiliate-list
        """
        return self._native_private(
            "get_sub_affiliates",
            self._native_params(
                **{
                    "page": page,
                    "limit": limit,
                    "keyword": keyword,
                    "commissionCategory": commission_category,
                    "orderBy": order_by,
                    "orderDir": order_dir,
                }
            ),
        )
