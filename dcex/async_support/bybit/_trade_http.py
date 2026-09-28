from json import dumps

"""Async Bybit trade HTTP client backed by Rust."""

from typing import Any

from ...enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Bybit trading operations."""

    async def place_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderType: str,
        qty: str,
        price: str | None = None,
        isLeverage: int | None = None,
        marketUnit: str | None = None,
        rpiTakerAccess: bool | None = None,
        slippageToleranceType: str | None = None,
        slippageTolerance: str | None = None,
        triggerDirection: int | None = None,
        orderFilter: str | None = None,
        triggerPrice: str | None = None,
        triggerBy: str | None = None,
        orderIv: str | None = None,
        timeInForce: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        reduceOnly: bool | None = None,
        closeOnTrigger: bool | None = None,
        tpslMode: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
        positionIdx: int | None = None,
        orderLinkId: str | None = None,
        smpType: str | None = None,
        mmp: bool | None = None,
        bboSideType: str | None = None,
        bboLevel: int | None = None,
    ) -> dict[str, Any]:
        """Place an order."""
        return await self._native_private(
            "place_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                price=price,
                isLeverage=isLeverage,
                marketUnit=marketUnit,
                rpiTakerAccess=rpiTakerAccess,
                slippageToleranceType=slippageToleranceType,
                slippageTolerance=slippageTolerance,
                triggerDirection=triggerDirection,
                orderFilter=orderFilter,
                triggerPrice=triggerPrice,
                triggerBy=triggerBy,
                orderIv=orderIv,
                timeInForce=timeInForce,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpTriggerBy=tpTriggerBy,
                slTriggerBy=slTriggerBy,
                reduceOnly=reduceOnly,
                closeOnTrigger=closeOnTrigger,
                tpslMode=tpslMode,
                tpLimitPrice=tpLimitPrice,
                slLimitPrice=slLimitPrice,
                tpOrderType=tpOrderType,
                slOrderType=slOrderType,
                positionIdx=positionIdx,
                orderLinkId=orderLinkId,
                smpType=smpType,
                mmp=mmp,
                bboSideType=bboSideType,
                bboLevel=bboLevel,
            ),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market order."""
        return await self._native_private(
            "place_market_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_market_buy_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market buy order."""
        return await self._native_private(
            "place_market_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_market_sell_order(
        self,
        product_symbol: str,
        qty: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a market sell order."""
        return await self._native_private(
            "place_market_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit order."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_buy_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit buy order."""
        return await self._native_private(
            "place_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_limit_sell_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        timeInForce: str | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a limit sell order."""
        return await self._native_private(
            "place_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                timeInForce=timeInForce,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit order."""
        return await self._native_private(
            "place_post_only_limit_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_buy_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit buy order."""
        return await self._native_private(
            "place_post_only_limit_buy_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def place_post_only_limit_sell_order(
        self,
        product_symbol: str,
        qty: str,
        price: str,
        reduceOnly: bool | None = None,
        isLeverage: int | None = None,
        positionIdx: int | None = None,
    ) -> dict[str, Any]:
        """Place a post-only limit sell order."""
        return await self._native_private(
            "place_post_only_limit_sell_order",
            self._native_params(
                product_symbol=product_symbol,
                qty=qty,
                price=price,
                reduceOnly=reduceOnly,
                isLeverage=isLeverage,
                positionIdx=positionIdx,
            ),
        )

    async def amend_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderIv: str | None = None,
        triggerPrice: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        tpslMode: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        triggerBy: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
    ) -> dict[str, Any]:
        """Amend an existing order."""
        return await self._native_private(
            "amend_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderIv=orderIv,
                triggerPrice=triggerPrice,
                qty=qty,
                price=price,
                tpslMode=tpslMode,
                takeProfit=takeProfit,
                stopLoss=stopLoss,
                tpTriggerBy=tpTriggerBy,
                slTriggerBy=slTriggerBy,
                triggerBy=triggerBy,
                tpLimitPrice=tpLimitPrice,
                slLimitPrice=slLimitPrice,
            ),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
    ) -> dict[str, Any]:
        """Cancel an order."""
        return await self._native_private(
            "cancel_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderFilter=orderFilter,
            ),
        )

    async def get_open_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        settleCoin: str | None = None,
        baseCoin: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        openOnly: int | None = None,
        orderFilter: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get open orders."""
        return await self._native_private(
            "get_open_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                settleCoin=settleCoin,
                baseCoin=baseCoin,
                orderId=orderId,
                orderLinkId=orderLinkId,
                openOnly=openOnly,
                orderFilter=orderFilter,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def cancel_batch_orders(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Cancel multiple orders in batch."""
        return await self._native_private(
            "cancel_batch_orders",
            self._native_params(request=request, category=category),
        )

    async def cancel_all_orders(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        orderFilter: str | None = None,
        stopOrderType: str | None = None,
    ) -> dict[str, Any]:
        """Cancel all orders."""
        return await self._native_private(
            "cancel_all_orders",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                orderFilter=orderFilter,
                stopOrderType=stopOrderType,
            ),
        )

    async def get_order_history(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
        orderStatus: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get order history."""
        return await self._native_private(
            "get_order_history",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                orderId=orderId,
                orderLinkId=orderLinkId,
                orderFilter=orderFilter,
                orderStatus=orderStatus,
                startTime=startTime,
                endTime=endTime,
                cursor=cursor,
                limit=limit,
            ),
        )

    async def get_execution_list(
        self,
        category: str = "linear",
        product_symbol: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        baseCoin: str | None = None,
        settleCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        execType: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get execution list."""
        return await self._native_private(
            "get_execution_list",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                orderId=orderId,
                orderLinkId=orderLinkId,
                baseCoin=baseCoin,
                settleCoin=settleCoin,
                startTime=startTime,
                endTime=endTime,
                execType=execType,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def place_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Place multiple orders in batch."""
        return await self._native_private(
            "place_batch_order",
            self._native_params(request=request, category=category),
        )

    async def amend_batch_order(
        self,
        request: list[dict[str, Any]],
        category: str = "linear",
    ) -> dict[str, Any]:
        """Amend multiple orders in batch."""
        return await self._native_private(
            "amend_batch_order",
            self._native_params(request=request, category=category),
        )

    async def get_borrow_quota(
        self,
        product_symbol: str,
        side: OrderSide | str,
    ) -> dict[str, Any]:
        """Get borrow quota for spot trading."""
        return await self._native_private(
            "get_borrow_quota",
            self._native_params(product_symbol=product_symbol, side=side),
        )

    async def get_vip_margin_data(
        self,
        vipLevel: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get VIP margin data."""
        return await self._native_private(
            "get_vip_margin_data",
            self._native_params(vipLevel=vipLevel, currency=currency),
        )

    async def get_collateral(
        self,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Get collateral information."""
        return await self._native_private(
            "get_collateral",
            self._native_params(currency=currency),
        )

    async def get_historical_interest_rate(
        self,
        currency: str,
        vipLevel: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
    ) -> dict[str, Any]:
        """Get historical interest rate."""
        return await self._native_private(
            "get_historical_interest_rate",
            self._native_params(
                currency=currency,
                vipLevel=vipLevel,
                startTime=startTime,
                endTime=endTime,
            ),
        )

    async def get_status_and_leverage(self) -> dict[str, Any]:
        """Get spot margin trading status and leverage."""
        return await self._native_private("get_status_and_leverage", [])

    async def get_margin_max_borrowable(self, currency: str) -> dict[str, Any]:
        """Get the maximum amount currently borrowable for a currency."""
        return await self._native_private(
            "get_margin_max_borrowable", self._native_params(currency=currency)
        )

    async def get_margin_position_tiers(self, currency: str | None = None) -> dict[str, Any]:
        """Get spot-margin position tiers and risk ratios."""
        return await self._native_private(
            "get_margin_position_tiers", self._native_params(currency=currency)
        )

    async def get_margin_coin_state(self, currency: str | None = None) -> dict[str, Any]:
        """Get spot-margin leverage state by currency."""
        return await self._native_private(
            "get_margin_coin_state", self._native_params(currency=currency)
        )

    async def get_margin_repayment_available_amount(self, currency: str) -> dict[str, Any]:
        """Get the debt amount repayable without asset conversion."""
        return await self._native_private(
            "get_margin_repayment_available_amount",
            self._native_params(currency=currency),
        )

    async def set_margin_auto_repay_mode(
        self, autoRepayMode: str, currency: str | None = None
    ) -> dict[str, Any]:
        """Enable or disable automatic no-conversion repayment."""
        return await self._native_private(
            "set_margin_auto_repay_mode",
            self._native_params(autoRepayMode=autoRepayMode, currency=currency),
        )

    async def get_margin_auto_repay_mode(self, currency: str | None = None) -> dict[str, Any]:
        """Get automatic repayment settings."""
        return await self._native_private(
            "get_margin_auto_repay_mode", self._native_params(currency=currency)
        )

    async def get_fixed_borrow_quote(
        self,
        orderCurrency: str,
        term: str | None = None,
        orderBy: str | None = None,
        sort: int | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Get available fixed-rate borrow quotes."""
        return await self._native_private(
            "get_fixed_borrow_quote",
            self._native_params(
                orderCurrency=orderCurrency,
                term=term,
                orderBy=orderBy,
                sort=sort,
                limit=limit,
            ),
        )

    async def borrow_fixed_rate(
        self,
        orderCurrency: str,
        orderAmount: str,
        annualRate: str,
        term: str,
        repayType: str | None = None,
        strategyType: str | None = None,
    ) -> dict[str, Any]:
        """Submit a fixed-rate spot-margin borrow order."""
        return await self._native_private(
            "borrow_fixed_rate",
            self._native_params(
                orderCurrency=orderCurrency,
                orderAmount=orderAmount,
                annualRate=annualRate,
                term=term,
                repayType=repayType,
                strategyType=strategyType,
            ),
        )

    async def renew_fixed_rate_borrow(self, loanId: str, qty: str | None = None) -> dict[str, Any]:
        """Renew a fixed-rate spot-margin loan."""
        return await self._native_private(
            "renew_fixed_rate_borrow", self._native_params(loanId=loanId, qty=qty)
        )

    async def get_fixed_borrow_orders(
        self,
        orderId: str | None = None,
        orderCurrency: str | None = None,
        state: str | None = None,
        term: str | None = None,
        limit: int = 10,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get fixed-rate borrow order history."""
        return await self._native_private(
            "get_fixed_borrow_orders",
            self._native_params(
                orderId=orderId,
                orderCurrency=orderCurrency,
                state=state,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_fixed_borrow_contracts(
        self,
        orderId: str | None = None,
        orderCurrency: str | None = None,
        term: str | None = None,
        limit: int = 10,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Get fixed-rate borrow contracts."""
        return await self._native_private(
            "get_fixed_borrow_contracts",
            self._native_params(
                orderId=orderId,
                orderCurrency=orderCurrency,
                term=term,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_margin_liability(self, currency: str) -> dict[str, Any]:
        """Get flexible and fixed-rate liabilities for a currency."""
        return await self._native_private(
            "get_margin_liability", self._native_params(currency=currency)
        )

    async def get_flexible_borrow_inventory(self, currency: str) -> dict[str, Any]:
        """Get available variable-rate borrowing inventory."""
        return await self._native_private(
            "get_flexible_borrow_inventory", self._native_params(currency=currency)
        )

    async def get_fixed_borrow_inventory(
        self, currency: str, term: str, annualRate: str
    ) -> dict[str, Any]:
        """Get available fixed-rate borrowing inventory."""
        return await self._native_private(
            "get_fixed_borrow_inventory",
            self._native_params(currency=currency, term=term, annualRate=annualRate),
        )

    async def pre_check_order(
        self,
        product_symbol: str,
        side: OrderSide | str,
        orderType: str,
        qty: str,
        **params: object,
    ) -> dict[str, Any]:
        """Preview UTA margin impact before submitting a Bybit order."""
        return await self._native_private(
            "pre_check_order",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                orderType=orderType,
                qty=qty,
                **params,
            ),
        )

    async def set_disconnected_cancel_all(
        self,
        timeWindow: int,
        product: str | None = None,
    ) -> dict[str, Any]:
        """Configure Bybit disconnect protection without placing an order."""
        return await self._native_private(
            "set_disconnected_cancel_all",
            self._native_params(timeWindow=timeWindow, product=product),
        )

    async def place_spread_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        *,
        price: str | None = None,
        order_link_id: str | None = None,
        time_in_force: str | None = None,
    ) -> dict[str, Any]:
        """Place a Bybit spread combination order."""
        return await self._native_private(
            "place_spread_order",
            self._native_params(
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=qty,
                price=price,
                orderLinkId=order_link_id,
                timeInForce=time_in_force,
            ),
        )

    async def amend_spread_order(
        self,
        symbol: str,
        *,
        order_id: str | None = None,
        order_link_id: str | None = None,
        qty: str | None = None,
        price: str | None = None,
    ) -> dict[str, Any]:
        """Amend a Bybit spread combination order."""
        return await self._native_private(
            "amend_spread_order",
            self._native_params(
                symbol=symbol,
                orderId=order_id,
                orderLinkId=order_link_id,
                qty=qty,
                price=price,
            ),
        )

    async def cancel_spread_order(
        self, *, order_id: str | None = None, order_link_id: str | None = None
    ) -> dict[str, Any]:
        """Cancel one Bybit spread combination order."""
        return await self._native_private(
            "cancel_spread_order",
            self._native_params(orderId=order_id, orderLinkId=order_link_id),
        )

    async def cancel_all_spread_orders(
        self, *, symbol: str | None = None, cancel_all: bool | None = None
    ) -> dict[str, Any]:
        """Cancel Bybit spread orders for a symbol or the entire account."""
        return await self._native_private(
            "cancel_all_spread_orders",
            self._native_params(symbol=symbol, cancelAll=cancel_all),
        )

    async def get_spread_open_orders(
        self,
        *,
        symbol: str | None = None,
        base_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List active Bybit spread orders."""
        return await self._native_private(
            "get_spread_open_orders",
            self._native_params(
                symbol=symbol,
                baseCoin=base_coin,
                orderId=order_id,
                orderLinkId=order_link_id,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_spread_order_history(
        self,
        *,
        symbol: str | None = None,
        base_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List historical Bybit spread orders."""
        return await self._native_private(
            "get_spread_order_history",
            self._native_params(
                symbol=symbol,
                baseCoin=base_coin,
                orderId=order_id,
                orderLinkId=order_link_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_spread_trade_history(
        self,
        *,
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List Bybit spread executions."""
        return await self._native_private(
            "get_spread_trade_history",
            self._native_params(
                symbol=symbol,
                orderId=order_id,
                orderLinkId=order_link_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_spread_max_qty(self, symbol: str, side: str, order_price: str) -> dict[str, Any]:
        """Get the maximum spread order quantity for a side and price."""
        return await self._native_private(
            "get_spread_max_qty",
            self._native_params(symbol=symbol, side=side, orderPrice=order_price),
        )

    async def create_strategy(
        self,
        category: str | None = None,
        product_symbol: str | None = None,
        side: str | None = None,
        strategy_type: str | None = None,
        *,
        size: str | None = None,
        position_value: str | None = None,
        duration: int | None = None,
        interval: int | None = None,
        reduce_only: bool | None = None,
        position_idx: int | None = None,
        leverage_type: int | None = None,
        is_random: bool | None = None,
        trigger_price: str | None = None,
        max_chase_price: str | None = None,
        chase_distance: str | None = None,
        chase_percent_e4: int | None = None,
        sub_size: str | None = None,
        sub_position_value: str | None = None,
        order_count: int | None = None,
        maker_only: bool | None = None,
        post_only: int | None = None,
        limit_price: str | None = None,
        pov_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a strategy; derive category from the canonical product_symbol when omitted.

        maker_only=True selects postOnly=0; False allows takers (postOnly=1).
        post_only is a deprecated raw exchange integer; do not combine it with maker_only.
        """
        if maker_only is not None and type(maker_only) is not bool:
            raise ValueError("maker_only must be a boolean")
        if post_only is not None:
            import warnings

            warnings.warn(
                "post_only is deprecated; use maker_only", DeprecationWarning, stacklevel=2
            )
        return await self._native_private(
            "create_strategy",
            self._native_params(
                category=category,
                product_symbol=product_symbol,
                side=side,
                strategyType=strategy_type,
                size=size,
                positionValue=position_value,
                duration=duration,
                interval=interval,
                reduceOnly=reduce_only,
                positionIdx=position_idx,
                leverageType=leverage_type,
                isRandom=is_random,
                triggerPrice=trigger_price,
                maxChasePrice=max_chase_price,
                chaseDistance=chase_distance,
                chasePercentE4=chase_percent_e4,
                subSize=sub_size,
                subPositionValue=sub_position_value,
                orderCount=order_count,
                postOnly=post_only,
                maker_only=maker_only,
                limitPrice=limit_price,
                povParams=dumps(pov_params) if pov_params is not None else None,
            ),
        )

    async def stop_strategy(self, strategy_id: str) -> dict[str, Any]:
        """Stop a strategy and cancel its unfilled child orders."""
        return await self._native_private(
            "stop_strategy", self._native_params(strategyId=strategy_id)
        )

    async def get_strategy_list(
        self,
        *,
        strategy_id: str | None = None,
        category: str | None = None,
        product_symbol: str | None = None,
        status: str | None = None,
        strategy_type: str | None = None,
        begin_time: int | None = None,
        end_time: int | None = None,
        page_size: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query strategies; begin_time and end_time are Unix seconds."""
        return await self._native_private(
            "get_strategy_list",
            self._native_params(
                strategyId=strategy_id,
                category=category,
                product_symbol=product_symbol,
                status=status,
                strategyType=strategy_type,
                beginTimeE0=begin_time,
                endTimeE0=end_time,
                pageSize=page_size,
                cursor=cursor,
            ),
        )

    async def get_strategy_orders(
        self,
        strategy_id: str,
        *,
        product_symbol: str | None = None,
        status: str | None = None,
        strategy_type: str | None = None,
        begin_time: int | None = None,
        end_time: int | None = None,
        page_size: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Query strategy child orders; times are Unix seconds."""
        return await self._native_private(
            "get_strategy_orders",
            self._native_params(
                strategyId=strategy_id,
                product_symbol=product_symbol,
                status=status,
                strategyType=strategy_type,
                beginTimeE0=begin_time,
                endTimeE0=end_time,
                pageSize=page_size,
                cursor=cursor,
            ),
        )
