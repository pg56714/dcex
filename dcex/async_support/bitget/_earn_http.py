"""Async Bitget Earn HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """Async HTTP client for Bitget Savings and On-chain Earn workflows."""

    async def _savings_history_query(
        self,
        method_name: str,
        period_type: str,
        coin: str | None,
        order_type: str | None,
        start_time: int | None,
        end_time: int | None,
        limit: int | None,
        id_less_than: str | None,
    ) -> dict[str, Any]:
        return await self._native_private(
            method_name,
            self._native_params(
                periodType=period_type,
                coin=coin,
                orderType=order_type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                idLessThan=id_less_than,
            ),
        )

    async def get_elite_earn_products(self) -> dict[str, Any]:
        return await self._native_private("get_elite_earn_products", [])

    async def get_elite_earn_subscription_info(self, product_id: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_subscription_info", self._native_params(productId=product_id)
        )

    async def subscribe_elite_earn(
        self,
        product_sub_id: str,
        amount: str,
        *,
        coin: str | None = None,
        payment_account: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "subscribe_elite_earn",
            self._native_params(
                productSubId=product_sub_id,
                amount=amount,
                coin=coin,
                paymentAccount=payment_account,
            ),
        )

    async def get_elite_earn_subscription_result(self, order_id: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_subscription_result", self._native_params(orderId=order_id)
        )

    async def get_elite_earn_redemption_info(self, product_id: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_redemption_info", self._native_params(productId=product_id)
        )

    async def redeem_elite_earn(
        self,
        product_id: str,
        product_sub_id: str,
        redeem_type: str,
        amount: str,
        receive_account: str,
        *,
        advanced_settle: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_elite_earn",
            self._native_params(
                productId=product_id,
                productSubId=product_sub_id,
                redeemType=redeem_type,
                amount=amount,
                receiveAccount=receive_account,
                advancedSettle=advanced_settle,
                coin=coin,
            ),
        )

    async def get_elite_earn_assets(self) -> dict[str, Any]:
        return await self._native_private("get_elite_earn_assets", [])

    async def get_elite_earn_records(
        self,
        type: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_records",
            self._native_params(
                type=type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )
