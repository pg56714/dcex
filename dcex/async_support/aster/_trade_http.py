"""Aster V3 private trading async HTTP client."""

from typing import Any

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

    async def exchange_futures_assets(self) -> dict[str, Any] | list[Any]:
        """POST /fapi/v3/assetExchange."""
        return await self._native_private("exchange_futures_assets", self._native_params())

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
