"""Aster V3 private trading async HTTP client."""

from typing import Any

from ..._operation_guards import require_confirmation
from ...enums import OrderSide
from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Aster V3 private trading operations."""

    async def place_spot_order(
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
        nonce: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster spot order."""
        return await self._native_private(
            "place_spot_order",
            self._native_params(
                nonce=nonce,
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

    async def cancel_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "cancel_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def get_spot_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "get_spot_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def get_spot_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster spot order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "get_spot_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def get_spot_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster spot orders."""
        return await self._native_private(
            "get_spot_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    async def cancel_all_spot_open_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all or selected open Aster spot orders for a symbol."""
        return await self._native_private(
            "cancel_all_spot_open_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    async def get_spot_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot order history."""
        return await self._native_private(
            "get_spot_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def get_spot_user_trades(
        self,
        product_symbol: str | None = None,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        fromId: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster spot account trades."""
        return await self._native_private(
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

    async def place_futures_order(
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
        nonce: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures order."""
        return await self._native_private(
            "place_futures_order",
            self._native_params(
                nonce=nonce,
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

    async def modify_futures_order(
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
        return await self._native_private(
            "modify_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
                quantity=quantity,
                price=price,
            ),
        )

    async def place_futures_chase_order(
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
        return await self._native_private(
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

    async def place_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],
        nonce: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place multiple Aster futures orders."""
        return await self._native_private(
            "place_futures_batch_orders",
            self._native_params(batchOrders=batchOrders, nonce=nonce),
        )

    async def get_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "get_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def cancel_futures_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel an Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "cancel_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def cancel_all_futures_open_orders(
        self,
        product_symbol: str,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all open Aster futures orders for a symbol."""
        return await self._native_private(
            "cancel_all_futures_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    async def modify_futures_batch_orders(
        self,
        batchOrders: list[dict[str, Any]],  # noqa: N803
    ) -> dict[str, Any] | list[Any]:
        """Amend up to five futures orders independently."""
        return await self._native_private(
            "modify_futures_batch_orders", self._native_params(batchOrders=batchOrders)
        )

    async def cancel_futures_batch_orders(
        self,
        product_symbol: str,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel multiple Aster futures orders."""
        return await self._native_private(
            "cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    async def set_futures_countdown_cancel_all(
        self,
        product_symbol: str,
        countdownTime: int,
    ) -> dict[str, Any] | list[Any]:
        """Set automatic cancellation of Aster futures open orders."""
        return await self._native_private(
            "set_futures_countdown_cancel_all",
            self._native_params(product_symbol=product_symbol, countdownTime=countdownTime),
        )

    async def get_futures_open_order(
        self,
        product_symbol: str,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query one current Aster futures order."""
        if orderId is None and origClientOrderId is None:
            raise ValueError("Specify orderId or origClientOrderId.")
        return await self._native_private(
            "get_futures_open_order",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def get_futures_open_orders(
        self,
        product_symbol: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve current Aster futures orders."""
        return await self._native_private(
            "get_futures_open_orders",
            self._native_params(product_symbol=product_symbol),
        )

    async def get_futures_all_orders(
        self,
        product_symbol: str,
        orderId: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Retrieve Aster futures order history."""
        return await self._native_private(
            "get_futures_all_orders",
            self._native_params(
                product_symbol=product_symbol,
                orderId=orderId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
            ),
        )

    async def set_futures_leverage(
        self,
        product_symbol: str,
        leverage: int,
    ) -> dict[str, Any] | list[Any]:
        """Change Aster futures initial leverage."""
        return await self._native_private(
            "set_futures_leverage",
            self._native_params(product_symbol=product_symbol, leverage=leverage),
        )

    async def set_futures_margin_type(
        self,
        product_symbol: str,
        marginType: str,
    ) -> dict[str, Any] | list[Any]:
        """Change an Aster futures symbol margin type."""
        return await self._native_private(
            "set_futures_margin_type",
            self._native_params(product_symbol=product_symbol, marginType=marginType),
        )

    async def place_futures_strategy_order(
        self,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
        clientStrategyId: str | None = None,
        builder: str | None = None,
        feeRate: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Place an Aster futures strategy order."""
        return await self._native_private(
            "place_futures_strategy_order",
            self._native_params(
                clientStrategyId=clientStrategyId,
                strategyType=strategyType,
                subOrderList=subOrderList,
                builder=builder,
                feeRate=feeRate,
            ),
        )

    async def update_futures_strategy_order(
        self,
        strategyId: int,
        strategyType: str,
        subOrderList: list[dict[str, Any]],
    ) -> dict[str, Any] | list[Any]:
        """Update an Aster futures strategy order."""
        return await self._native_private(
            "update_futures_strategy_order",
            self._native_params(
                strategyId=strategyId,
                strategyType=strategyType,
                subOrderList=subOrderList,
            ),
        )

    async def get_futures_strategy_open_order(
        self,
        strategyType: str,
        strategyId: int | None = None,
        clientStrategyId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query an open Aster futures strategy order."""
        return await self._native_private(
            "get_futures_strategy_open_order",
            self._native_params(
                strategyId=strategyId,
                clientStrategyId=clientStrategyId,
                strategyType=strategyType,
            ),
        )

    async def get_futures_strategy_history_order(
        self,
        strategyType: str,
        strategyId: int | None = None,
        clientStrategyId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Query Aster futures strategy-order history."""
        return await self._native_private(
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

    async def noop_spot(self, nonce: int) -> dict[str, Any] | list[Any]:
        """
        Attempt to invalidate a pending request using its original nonce.

        Success is not guaranteed if the original request has already executed.
        """
        return await self._native_private("noop_spot", self._native_params(nonce=nonce))

    async def noop_futures(self, nonce: int) -> dict[str, Any] | list[Any]:
        """
        Attempt to invalidate a pending request using its original nonce.

        Success is not guaranteed if the original request has already executed.
        """
        return await self._native_private("noop_futures", self._native_params(nonce=nonce))

    async def guarded_cancel_futures_order(
        self,
        product_symbol: str,
        nonce: int,
        *,
        orderId: int | None = None,
        origClientOrderId: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel using the nonce of the original order placement."""
        return await self._native_private(
            "guarded_cancel_futures_order",
            self._native_params(
                product_symbol=product_symbol,
                nonce=nonce,
                orderId=orderId,
                origClientOrderId=origClientOrderId,
            ),
        )

    async def guarded_cancel_futures_batch_orders(
        self,
        product_symbol: str,
        nonce: int,
        *,
        orderIdList: list[int] | None = None,
        origClientOrderIdList: list[str] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel using the nonce of the original batch placement."""
        return await self._native_private(
            "guarded_cancel_futures_batch_orders",
            self._native_params(
                product_symbol=product_symbol,
                nonce=nonce,
                orderIdList=orderIdList,
                origClientOrderIdList=origClientOrderIdList,
            ),
        )

    async def transfer_sub_account(
        self,
        to_account_address: str,
        asset: str,
        amount: str,
        kind_type: str,
        *,
        from_account_address: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Transfer within one master/sub-account family using the approved agent.

        Aster enforces account-family membership; external transfers are not supported.

        Not verified live: the official signature template includes both user and signer,
        while its parameter notes require only one. This method sends signer only.
        """
        return await self._native_private(
            "transfer_sub_account",
            self._native_params(
                toAccountAddress=to_account_address,
                asset=asset,
                amount=amount,
                kindType=kind_type,
                fromAccountAddress=from_account_address,
            ),
        )

    async def trigger_futures_asset_exchange(
        self, *, confirm: bool = False
    ) -> dict[str, Any] | list[Any]:
        """
        POST /fapi/v3/assetExchange.

        Requires confirm=True. This immediately converts Multi-Assets balances.
        """
        require_confirmation(confirm)
        return await self._native_private(
            "trigger_futures_asset_exchange", self._native_params(confirm=confirm)
        )

    exchange_futures_assets = trigger_futures_asset_exchange

    async def get_sub_accounts(self) -> dict[str, Any] | list[Any]:
        """GET /fapi/v3/getSubAccountList."""
        return await self._native_private("get_sub_accounts", self._native_params())

    async def get_direct_announcements(
        self, *, page: int | None = None, size: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /fapi/v3/announcement/direct."""
        return await self._native_private(
            "get_direct_announcements", self._native_params(page=page, size=size)
        )

    async def get_direct_announcement(self, *, id: int) -> dict[str, Any] | list[Any]:
        """GET /fapi/v3/announcement/directById."""
        return await self._native_private("get_direct_announcement", self._native_params(id=id))

    async def create_sub_account_signed(
        self,
        *,
        sub_account_name: str,
        sub_source_addr: str,
        nonce: int,
        user: str,
        signer: str,
        child_signature: str,
        signature: str,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /fapi/v3/createSubAccount. Supply wallet signatures created exactly as documented
        by Aster; the nonce and signatures are forwarded unchanged.
        """
        return await self._native_private(
            "create_sub_account_signed",
            self._native_params(
                subAccountName=sub_account_name,
                subSourceAddr=sub_source_addr,
                nonce=nonce,
                user=user,
                signer=signer,
                childSignature=child_signature,
                signature=signature,
            ),
        )

    async def update_sub_account_signed(
        self,
        *,
        sub_source_addr: str,
        nonce: int,
        user: str,
        signer: str,
        signature: str,
        sub_account_name: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /fapi/v3/updateSubAccount. Supply wallet signatures created exactly as documented
        by Aster; the nonce and signatures are forwarded unchanged.
        """
        return await self._native_private(
            "update_sub_account_signed",
            self._native_params(
                subSourceAddr=sub_source_addr,
                nonce=nonce,
                user=user,
                signer=signer,
                subAccountName=sub_account_name,
                status=status,
                signature=signature,
            ),
        )

    async def bind_sub_account_signed(
        self,
        *,
        child_address: str,
        name: str,
        nonce: int,
        user: str,
        child_signature: str,
        signature: str,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /fapi/v3/sub-accounts/bind. Supply wallet signatures created exactly as documented
        by Aster; the nonce and signatures are forwarded unchanged.
        """
        return await self._native_private(
            "bind_sub_account_signed",
            self._native_params(
                childAddress=child_address,
                name=name,
                nonce=nonce,
                user=user,
                childSignature=child_signature,
                signature=signature,
            ),
        )

    async def register_agent_signed(
        self,
        *,
        user: str,
        nonce: int,
        agent_name: str,
        agent_address: str,
        expired: int,
        signature_chain_id: int,
        can_spot_trade: bool,
        can_perp_trade: bool,
        can_withdraw: bool,
        signature: str,
        ip_whitelist: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /fapi/v3/registerAndApproveAgent. Supply wallet signatures created exactly as
        documented by Aster; the nonce and signatures are forwarded unchanged.
        """
        return await self._native_private(
            "register_agent_signed",
            self._native_params(
                user=user,
                nonce=nonce,
                agentName=agent_name,
                agentAddress=agent_address,
                expired=expired,
                signatureChainId=signature_chain_id,
                canSpotTrade=can_spot_trade,
                canPerpTrade=can_perp_trade,
                canWithdraw=can_withdraw,
                ipWhitelist=ip_whitelist,
                signature=signature,
            ),
        )

    async def get_prediction_commission_rate(self, *, symbol: str) -> dict[str, Any] | list[Any]:
        """GET /api/v3/commissionRate on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_commission_rate", self._native_params(symbol=symbol)
        )

    async def create_prediction_order(
        self,
        *,
        symbol: str,
        side: str,
        type_: str,
        time_in_force: str | None = None,
        quantity: str | None = None,
        quote_order_qty: str | None = None,
        price: str | None = None,
        new_client_order_id: str | None = None,
        stop_price: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """POST /api/v3/order on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "create_prediction_order",
            self._native_params(
                symbol=symbol,
                side=side,
                type=type_,
                timeInForce=time_in_force,
                quantity=quantity,
                quoteOrderQty=quote_order_qty,
                price=price,
                newClientOrderId=new_client_order_id,
                stopPrice=stop_price,
            ),
        )

    async def cancel_prediction_order(
        self, *, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """DELETE /api/v3/order on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "cancel_prediction_order",
            self._native_params(
                symbol=symbol, orderId=order_id, origClientOrderId=orig_client_order_id
            ),
        )

    async def get_prediction_order(
        self, *, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/order on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_order",
            self._native_params(
                symbol=symbol, orderId=order_id, origClientOrderId=orig_client_order_id
            ),
        )

    async def get_prediction_open_order(
        self, *, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/openOrder on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_open_order",
            self._native_params(
                symbol=symbol, orderId=order_id, origClientOrderId=orig_client_order_id
            ),
        )

    async def get_prediction_open_orders(
        self, *, symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/openOrders on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_open_orders", self._native_params(symbol=symbol)
        )

    async def get_prediction_all_orders(
        self,
        *,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/allOrders on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_all_orders",
            self._native_params(
                symbol=symbol, orderId=order_id, startTime=start_time, endTime=end_time, limit=limit
            ),
        )

    async def create_prediction_asset_wallet_transfer(
        self, *, amount: str, asset: str, client_tran_id: str, kind_type: str
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v3/asset/wallet/transfer on the prediction host. Use native prediction
        symbols.
        """
        return await self._native_private(
            "create_prediction_asset_wallet_transfer",
            self._native_params(
                amount=amount, asset=asset, clientTranId=client_tran_id, kindType=kind_type
            ),
        )

    async def create_prediction_mint(
        self, *, symbol: str, quantity: str, new_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """POST /api/v3/prediction/mint on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "create_prediction_mint",
            self._native_params(
                symbol=symbol, quantity=quantity, newClientOrderId=new_client_order_id
            ),
        )

    async def create_prediction_burn(
        self, *, symbol: str, quantity: str, new_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """POST /api/v3/prediction/burn on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "create_prediction_burn",
            self._native_params(
                symbol=symbol, quantity=quantity, newClientOrderId=new_client_order_id
            ),
        )

    async def create_prediction_split(
        self, *, event: str, symbol: str, quantity: str, new_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """POST /api/v3/prediction/split on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "create_prediction_split",
            self._native_params(
                event=event, symbol=symbol, quantity=quantity, newClientOrderId=new_client_order_id
            ),
        )

    async def create_prediction_merge(
        self, *, event: str, quantity: str, new_client_order_id: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """POST /api/v3/prediction/merge on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "create_prediction_merge",
            self._native_params(
                event=event, quantity=quantity, newClientOrderId=new_client_order_id
            ),
        )

    async def get_prediction_positions(
        self, *, symbol: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v3/prediction/positions on the prediction host. Use native prediction symbols.
        """
        return await self._native_private(
            "get_prediction_positions", self._native_params(symbol=symbol)
        )

    async def get_prediction_position_histories(
        self,
        *,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v3/prediction/positionHistories on the prediction host. Use native prediction
        symbols.
        """
        return await self._native_private(
            "get_prediction_position_histories",
            self._native_params(symbol=symbol, startTime=start_time, endTime=end_time, limit=limit),
        )

    async def get_prediction_settlement_histories(
        self,
        *,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v3/prediction/settlementHistories on the prediction host. Use native prediction
        symbols.
        """
        return await self._native_private(
            "get_prediction_settlement_histories",
            self._native_params(symbol=symbol, startTime=start_time, endTime=end_time, limit=limit),
        )

    async def get_prediction_account(self) -> dict[str, Any] | list[Any]:
        """GET /api/v3/account on the prediction host. Use native prediction symbols."""
        return await self._native_private("get_prediction_account", self._native_params())

    async def get_prediction_user_trades(
        self,
        *,
        symbol: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """GET /api/v3/userTrades on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "get_prediction_user_trades",
            self._native_params(
                symbol=symbol,
                orderId=order_id,
                startTime=start_time,
                endTime=end_time,
                fromId=from_id,
                limit=limit,
            ),
        )

    async def create_prediction_listen_key(self) -> dict[str, Any] | list[Any]:
        """POST /api/v3/listenKey on the prediction host. Use native prediction symbols."""
        return await self._native_private("create_prediction_listen_key", self._native_params())

    async def update_prediction_listen_key(self, *, listen_key: str) -> dict[str, Any] | list[Any]:
        """PUT /api/v3/listenKey on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "update_prediction_listen_key", self._native_params(listenKey=listen_key)
        )

    async def cancel_prediction_listen_key(self, *, listen_key: str) -> dict[str, Any] | list[Any]:
        """DELETE /api/v3/listenKey on the prediction host. Use native prediction symbols."""
        return await self._native_private(
            "cancel_prediction_listen_key", self._native_params(listenKey=listen_key)
        )

    async def get_asset_migration_history(self, *, batch_id: str) -> dict[str, Any] | list[Any]:
        """Query a migration batch with the authenticated destination account."""
        return await self._native_private(
            "get_asset_migration_history", self._native_params(batchId=batch_id)
        )

    async def place_spot_batch_orders_raw(self, **params: object) -> Any:  # noqa: ANN401
        """
        Submit caller-supplied batch order parameters.

        Official spec incomplete; not verified live. Inspect every item in the response;
        an HTTP success does not imply every order succeeded.
        """
        return await self._native_private(
            "place_spot_batch_orders_raw", self._native_params(**params)
        )

    async def cancel_spot_batch_orders_raw(self, **params: object) -> Any:  # noqa: ANN401
        """
        Cancel a batch using caller-supplied wire parameters.

        Official spec incomplete; not verified live. Inspect every item in the response.
        """
        return await self._native_private(
            "cancel_spot_batch_orders_raw", self._native_params(**params)
        )

    async def noop_prediction(self, nonce: int) -> Any:  # noqa: ANN401
        """
        Attempt to cancel an unprocessed Prediction transaction with the same nonce.

        Uses the Prediction host. Cancellation is not guaranteed by the exchange.
        """
        return await self._native_private("noop_prediction", self._native_params(nonce=nonce))

    async def get_builder_user_accounts(
        self,
        *,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userAccounts for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_accounts",
            self._native_params(
                userAddresses=user_addresses,
                symbol=symbol,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_open_orders(
        self,
        *,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userOpenOrders for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_open_orders",
            self._native_params(
                userAddresses=user_addresses,
                symbol=symbol,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_balances(
        self,
        *,
        user_addresses: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userBalances for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_balances",
            self._native_params(
                userAddresses=user_addresses,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_position_risk(
        self,
        *,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userPositionRisk for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_position_risk",
            self._native_params(
                userAddresses=user_addresses,
                symbol=symbol,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_commission_rates(
        self,
        *,
        user_addresses: str | None = None,
        symbol: str,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userCommissionRates for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_commission_rates",
            self._native_params(
                userAddresses=user_addresses,
                symbol=symbol,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_trades(
        self,
        *,
        user_addresses: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userTrades for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_trades",
            self._native_params(
                userAddresses=user_addresses,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_user_all_orders(
        self,
        *,
        user_addresses: str | None = None,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query userAllOrders for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_user_all_orders",
            self._native_params(
                userAddresses=user_addresses,
                symbol=symbol,
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
            ),
        )

    async def get_builder_approved_users(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query approvedUserList for users who approved this builder.

        Uses the authenticated builder identity; pagination and eligibility are enforced by Aster.
        Source: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        return await self._native_private(
            "get_builder_approved_users",
            self._native_params(
                startTime=start_time,
                endTime=end_time,
                page=page,
                limit=limit,
            ),
        )

    async def withdraw_spot_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str,
        user_signature: str,
        signature_type: str | None = None,
        signature_chain_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized spot withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_spot_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
                signatureType=signature_type,
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_spot_solana_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str | None = None,
        user_signature: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized spot withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_spot_solana_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
            ),
        )

    async def withdraw_futures_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str,
        user_signature: str,
        signature_type: str | None = None,
        signature_chain_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized futures withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_futures_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
                signatureType=signature_type,
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_futures_solana_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str | None = None,
        user_signature: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized futures withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_futures_solana_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
            ),
        )
