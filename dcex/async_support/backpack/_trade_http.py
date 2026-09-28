"""Backpack private trade async HTTP client."""

from typing import Any

from ..._operation_guards import require_scope
from ...utils.common import Common
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Backpack private trading operations."""

    async def get_rfqs(
        self,
        product_symbol: str | None = None,
        rfq_id: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve active RFQs."""
        return await self._native_private(
            "get_rfqs",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def submit_rfq(
        self,
        product_symbol: str,
        side: str,
        *,
        quantity: str | None = None,
        quote_quantity: str | None = None,
        execution_mode: str = "AwaitAccept",
        price: str | None = None,
        client_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Submit an RFQ. Stock RFQs require quantity, not quote_quantity."""
        return await self._native_private(
            "submit_rfq",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                quantity=quantity,
                quoteQuantity=quote_quantity,
                executionMode=execution_mode,
                price=price,
                clientId=client_id,
            ),
        )

    async def accept_rfq_quote(
        self,
        quote_id: str,
        *,
        rfq_id: str | None = None,
        client_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Accept a firm quote using exactly one RFQ or client ID."""
        if (rfq_id is None) == (client_id is None):
            raise ValueError("Specify exactly one of rfq_id or client_id.")
        return await self._native_private(
            "accept_rfq_quote",
            self._native_params(quoteId=quote_id, rfqId=rfq_id, clientId=client_id),
        )

    async def refresh_rfq(self, rfq_id: str) -> dict[str, Any] | list[Any] | str:
        """Refresh an RFQ."""
        return await self._native_private("refresh_rfq", self._native_params(rfqId=rfq_id))

    async def cancel_rfq(
        self, *, rfq_id: str | None = None, client_id: int | None = None
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel an RFQ using exactly one RFQ or client ID."""
        if (rfq_id is None) == (client_id is None):
            raise ValueError("Specify exactly one of rfq_id or client_id.")
        return await self._native_private(
            "cancel_rfq", self._native_params(rfqId=rfq_id, clientId=client_id)
        )

    async def get_rfq_history(
        self,
        product_symbol: str | None = None,
        *,
        rfq_id: str | None = None,
        status: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get historical RFQs."""
        return await self._native_private(
            "get_rfq_history",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                status=status,
                side=side,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_quote_history(
        self,
        product_symbol: str | None = None,
        *,
        quote_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get historical RFQ quotes."""
        return await self._native_private(
            "get_quote_history",
            self._native_params(
                product_symbol=product_symbol,
                quoteId=quote_id,
                status=status,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_rfq_fill_history(
        self,
        product_symbol: str | None = None,
        *,
        rfq_id: str | None = None,
        quote_id: str | None = None,
        side: str | None = None,
        fill_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
        deferred_settlement: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get RFQ fills."""
        return await self._native_private(
            "get_rfq_fill_history",
            self._native_params(
                product_symbol=product_symbol,
                rfqId=rfq_id,
                quoteId=quote_id,
                side=side,
                fillType=fill_type,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
                deferredSettlement=deferred_settlement,
            ),
        )

    async def get_quote_fill_history(
        self,
        product_symbol: str | None = None,
        *,
        quote_id: str | None = None,
        side: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sort_direction: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get quote fills."""
        return await self._native_private(
            "get_quote_fill_history",
            self._native_params(
                product_symbol=product_symbol,
                quoteId=quote_id,
                side=side,
                limit=limit,
                offset=offset,
                sortDirection=sort_direction,
            ),
        )

    def _symbol(self, product_symbol: str) -> str:
        if "_" in product_symbol:
            return product_symbol
        return self.ptm.get_exchange_symbol(Common.BACKPACK, product_symbol)

    async def get_open_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve one Backpack open order."""
        if (orderId is None) == (clientId is None):
            raise ValueError("Specify exactly one of orderId or clientId.")
        return await self._native_private(
            "get_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientId=clientId,
            ),
        )

    async def place_order(
        self,
        product_symbol: str,
        side: str,
        orderType: str,
        quantity: str | None = None,
        price: str | None = None,
        quoteQuantity: str | None = None,
        clientId: int | None = None,
        timeInForce: str | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack order."""
        return await self._native_private(
            "place_order",
            self._native_params(**locals()),
        )

    async def place_market_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str | None = None,
        quoteQuantity: str | None = None,
        clientId: int | None = None,
        timeInForce: str | None = None,
        reduceOnly: bool | None = None,
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack market order."""
        return await self._native_private(
            "place_market_order",
            self._native_params(**locals()),
        )

    async def place_limit_order(
        self,
        product_symbol: str,
        side: str,
        quantity: str,
        price: str,
        timeInForce: str = "GTC",
        clientId: int | None = None,
        postOnly: bool | None = None,
        reduceOnly: bool | None = None,
        selfTradePrevention: str | None = None,
        autoBorrow: bool | None = None,
        autoBorrowRepay: bool | None = None,
        autoLend: bool | None = None,
        autoLendRedeem: bool | None = None,
        stopLossLimitPrice: str | None = None,
        stopLossTriggerBy: str | None = None,
        stopLossTriggerPrice: str | None = None,
        takeProfitLimitPrice: str | None = None,
        takeProfitTriggerBy: str | None = None,
        takeProfitTriggerPrice: str | None = None,
        triggerBy: str | None = None,
        triggerPrice: str | None = None,
        triggerQuantity: str | None = None,
        slippageTolerance: str | None = None,
        slippageToleranceType: str | None = None,
        brokerId: int | None = None,
        brokerKey: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place a Backpack limit order."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(**locals()),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        orderId: str | None = None,
        clientId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel one Backpack open order."""
        if (orderId is None) == (clientId is None):
            raise ValueError("Specify exactly one of orderId or clientId.")
        return await self._native_private(
            "cancel_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                clientId=clientId,
            ),
        )

    async def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
        brokerId: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Place Backpack batch orders."""
        return await self._native_private(
            "place_batch_orders",
            self._native_params(orders=orders, brokerId=brokerId),
        )

    async def get_open_orders(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open orders."""
        return await self._native_private(
            "get_open_orders",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    async def cancel_open_orders(
        self,
        product_symbol: str,
        orderType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel Backpack open orders."""
        return await self._native_private(
            "cancel_open_orders",
            self._native_params(product_symbol=product_symbol, orderType=orderType),
        )

    async def get_fill_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        strategyId: str | None = None,
        from_: int | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        fillType: str | None = None,
        marketType: list[str] | None = None,
        assetClass: str | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack fill history."""
        return await self._native_private(
            "get_fill_history",
            self._native_params(**locals()),
        )

    async def get_order_history(
        self,
        product_symbol: str | None = None,
        orderId: str | None = None,
        strategyId: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        marketType: list[str] | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack order history."""
        return await self._native_private(
            "get_order_history",
            self._native_params(**locals()),
        )

    async def get_open_positions(
        self,
        product_symbol: str | None = None,
        marketType: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack open positions."""
        return await self._native_private(
            "get_open_positions",
            self._native_params(product_symbol=product_symbol, marketType=marketType),
        )

    async def get_funding_payments(
        self,
        product_symbol: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack funding payments."""
        return await self._native_private(
            "get_funding_payments",
            self._native_params(**locals()),
        )

    async def get_position_history(
        self,
        product_symbol: str | None = None,
        state: str | None = None,
        marketType: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        sortDirection: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Retrieve Backpack position history."""
        return await self._native_private(
            "get_position_history",
            self._native_params(**locals()),
        )

    async def create_strategy(
        self,
        product_symbol: str,
        side: str,
        *,
        strategy_type: str = "Scheduled",
        quantity: str | None = None,
        price: str | None = None,
        duration: int | None = None,
        interval: int | None = None,
        client_strategy_id: int | None = None,
        randomized_interval_quantity: bool | None = None,
        time_in_force: str | None = None,
        post_only: bool | None = None,
        reduce_only: bool | None = None,
        self_trade_prevention: str | None = None,
        slippage_tolerance: str | None = None,
        slippage_tolerance_type: str | None = None,
        auto_lend: bool | None = None,
        auto_lend_redeem: bool | None = None,
        auto_borrow: bool | None = None,
        auto_borrow_repay: bool | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Create strategy using the dedicated Strategy API instruction."""
        return await self._native_private(
            "create_strategy",
            self._native_params(
                product_symbol=product_symbol,
                side=side,
                strategyType=strategy_type,
                quantity=quantity,
                price=price,
                duration=duration,
                interval=interval,
                clientStrategyId=client_strategy_id,
                randomizedIntervalQuantity=randomized_interval_quantity,
                timeInForce=time_in_force,
                postOnly=post_only,
                reduceOnly=reduce_only,
                selfTradePrevention=self_trade_prevention,
                slippageTolerance=slippage_tolerance,
                slippageToleranceType=slippage_tolerance_type,
                autoLend=auto_lend,
                autoLendRedeem=auto_lend_redeem,
                autoBorrow=auto_borrow,
                autoBorrowRepay=auto_borrow_repay,
            ),
        )

    async def get_open_strategy(
        self,
        product_symbol: str,
        *,
        strategy_id: str | None = None,
        client_strategy_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get open strategy using the dedicated Strategy API instruction."""
        return await self._native_private(
            "get_open_strategy",
            self._native_params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                clientStrategyId=client_strategy_id,
            ),
        )

    async def cancel_strategy(
        self,
        product_symbol: str,
        *,
        strategy_id: str | None = None,
        client_strategy_id: int | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Cancel strategy using the dedicated Strategy API instruction."""
        return await self._native_private(
            "cancel_strategy",
            self._native_params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                clientStrategyId=client_strategy_id,
            ),
        )

    async def get_open_strategies(
        self,
        product_symbol: str | None = None,
        *,
        market_type: str | None = None,
        strategy_type: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get open strategies using the dedicated Strategy API instruction."""
        return await self._native_private(
            "get_open_strategies",
            self._native_params(
                product_symbol=product_symbol, marketType=market_type, strategyType=strategy_type
            ),
        )

    async def cancel_open_strategies(
        self,
        product_symbol: str | None = None,
        *,
        strategy_type: str | None = None,
        all_symbols: bool = False,
    ) -> dict[str, Any] | list[Any] | str:
        """
        Cancel open strategies using the dedicated Strategy API instruction.

        Provide a product symbol or all_symbols=True to cancel across all symbols.
        """
        require_scope(product_symbol, all_symbols)
        return await self._native_private(
            "cancel_open_strategies",
            self._native_params(
                all_symbols=all_symbols, product_symbol=product_symbol, strategyType=strategy_type
            ),
        )

    async def get_strategy_history(
        self,
        product_symbol: str | None = None,
        *,
        strategy_id: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        market_type: list[str] | None = None,
        sort_direction: str | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Get strategy history using the dedicated Strategy API instruction."""
        return await self._native_private(
            "get_strategy_history",
            self._native_params(
                product_symbol=product_symbol,
                strategyId=strategy_id,
                limit=limit,
                offset=offset,
                marketType=market_type,
                sortDirection=sort_direction,
            ),
        )

    async def vault_mint(
        self,
        *,
        vault_id: int,
        symbol: str,
        quantity: str,
        auto_borrow: bool | None = None,
        auto_lend_redeem: bool | None = None,
    ) -> Any:  # noqa: ANN401
        """POST /api/v1/vault/mint. Native asset symbols; vault operator permissions may apply."""
        return await self._native_private(
            "vault_mint",
            self._native_params(
                vaultId=vault_id,
                symbol=symbol,
                quantity=quantity,
                autoBorrow=auto_borrow,
                autoLendRedeem=auto_lend_redeem,
            ),
        )

    async def vault_redeem(
        self, *, vault_id: int, vault_token_quantity: str | None = None, all: bool = False
    ) -> Any:  # noqa: ANN401
        """
        POST /api/v1/vault/redeem.

        Provide vault_token_quantity, or all=True to redeem the entire vault token balance.
        Vault operator permissions may apply.
        """
        require_scope(vault_token_quantity, all, flag="all")
        return await self._native_private(
            "vault_redeem",
            self._native_params(all=all, vaultId=vault_id, vaultTokenQuantity=vault_token_quantity),
        )

    async def vault_redeem_cancel(self, *, vault_id: int) -> Any:  # noqa: ANN401
        """
        DELETE /api/v1/vault/redeem. Native asset symbols; vault operator permissions may apply.
        """
        return await self._native_private(
            "vault_redeem_cancel", self._native_params(vaultId=vault_id)
        )

    async def get_vault_pending_redeems(self, *, vault_id: int) -> Any:  # noqa: ANN401
        """
        GET /api/v1/vault/redeems/pending. Native asset symbols; vault operator permissions may
        apply.
        """
        return await self._native_private(
            "get_vault_pending_redeems", self._native_params(vaultId=vault_id)
        )

    async def get_vault_nav(self) -> Any:  # noqa: ANN401
        """GET /api/v1/vault/nav. Native asset symbols; vault operator permissions may apply."""
        return await self._native_private("get_vault_nav", self._native_params())

    async def execute_borrow_lend(self, *, quantity: str, side: str, symbol: str) -> Any:  # noqa: ANN401
        """
        Borrow or lend; positions net against existing balances. Margin capability is required.
        """
        return await self._native_private(
            "execute_borrow_lend", self._native_params(quantity=quantity, side=side, symbol=symbol)
        )

    async def submit_rfq_quote(
        self,
        *,
        rfq_id: str,
        bid_price: str,
        ask_price: str,
        client_id: int | None = None,
        auto_lend: bool | None = None,
        auto_lend_redeem: bool | None = None,
        auto_borrow: bool | None = None,
        auto_borrow_repay: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit a maker quote before the RFQ submission deadline.

        API quotes settle immediately on acceptance; inventory must be available.
        Source: https://docs.backpack.exchange/#tag/RFQ/operation/submit_quote
        """
        return await self._native_private(
            "submit_rfq_quote",
            self._native_params(
                **{
                    "rfqId": rfq_id,
                    "bidPrice": bid_price,
                    "askPrice": ask_price,
                    "clientId": client_id,
                    "autoLend": auto_lend,
                    "autoLendRedeem": auto_lend_redeem,
                    "autoBorrow": auto_borrow,
                    "autoBorrowRepay": auto_borrow_repay,
                }
            ),
        )

    async def create_withdrawal(
        self,
        *,
        address: str,
        blockchain: str,
        quantity: str,
        symbol: str,
        client_id: str | None = None,
        two_factor_token: str | None = None,
        auto_borrow: bool | None = None,
        auto_lend_redeem: bool | None = None,
        recipient_information: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit a withdrawal with the documented withdraw signing instruction.

        API withdrawals have no second confirmation; they execute on submit.
        two_factor_token is required unless the exchange exempts the destination.
        recipient_information is sent in the body but excluded from the signature.
        Source: https://docs.backpack.exchange/#tag/Capital/operation/request_withdrawal
        """
        return await self._native_private(
            "create_withdrawal",
            self._native_params(
                **{
                    "address": address,
                    "blockchain": blockchain,
                    "quantity": quantity,
                    "symbol": symbol,
                    "clientId": client_id,
                    "twoFactorToken": two_factor_token,
                    "autoBorrow": auto_borrow,
                    "autoLendRedeem": auto_lend_redeem,
                    "recipientInformation": recipient_information,
                }
            ),
        )
