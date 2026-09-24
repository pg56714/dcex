"""Async Bitget Earn HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """Async HTTP client for Bitget Savings and On-chain Earn workflows."""

    async def get_earn_account_assets(self, coin: str | None = None) -> dict[str, Any]:
        return await self._native_private("get_earn_account_assets", self._native_params(coin=coin))

    async def get_savings_account(self) -> dict[str, Any]:
        return await self._native_private("get_savings_account", [])

    async def get_savings_products(
        self, coin: str | None = None, filter: str | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_savings_products", self._native_params(coin=coin, filter=filter)
        )

    async def get_savings_assets(
        self,
        periodType: str,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
    ) -> dict[str, Any]:
        return await self._savings_history_query(
            "get_savings_assets",
            periodType,
            None,
            None,
            startTime,
            endTime,
            limit,
            idLessThan,
        )

    async def get_savings_records(
        self,
        periodType: str,
        *,
        coin: str | None = None,
        orderType: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        idLessThan: str | None = None,
    ) -> dict[str, Any]:
        return await self._savings_history_query(
            "get_savings_records",
            periodType,
            coin,
            orderType,
            startTime,
            endTime,
            limit,
            idLessThan,
        )

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

    async def get_savings_subscription_info(
        self, productId: str, periodType: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_savings_subscription_info",
            self._native_params(productId=productId, periodType=periodType),
        )

    async def subscribe_savings(
        self, productId: str, periodType: str, amount: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "subscribe_savings",
            self._native_params(productId=productId, periodType=periodType, amount=amount),
        )

    async def get_savings_subscription_result(
        self, orderId: str, periodType: str
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_savings_subscription_result",
            self._native_params(orderId=orderId, periodType=periodType),
        )

    async def redeem_savings(
        self,
        productId: str,
        periodType: str,
        amount: str,
        *,
        orderId: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_savings",
            self._native_params(
                productId=productId,
                periodType=periodType,
                amount=amount,
                orderId=orderId,
            ),
        )

    async def get_savings_redemption_result(self, orderId: str, periodType: str) -> dict[str, Any]:
        return await self._native_private(
            "get_savings_redemption_result",
            self._native_params(orderId=orderId, periodType=periodType),
        )

    async def get_elite_earn_products(self) -> dict[str, Any]:
        return await self._native_private("get_elite_earn_products", [])

    async def get_elite_earn_subscription_info(self, productId: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_subscription_info", self._native_params(productId=productId)
        )

    async def subscribe_elite_earn(
        self,
        productSubId: str,
        amount: str,
        *,
        coin: str | None = None,
        paymentAccount: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "subscribe_elite_earn",
            self._native_params(
                productSubId=productSubId,
                amount=amount,
                coin=coin,
                paymentAccount=paymentAccount,
            ),
        )

    async def get_elite_earn_subscription_result(self, orderId: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_subscription_result", self._native_params(orderId=orderId)
        )

    async def get_elite_earn_redemption_info(self, productId: str) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_redemption_info", self._native_params(productId=productId)
        )

    async def redeem_elite_earn(
        self,
        productId: str,
        productSubId: str,
        redeemType: str,
        amount: str,
        receiveAccount: str,
        *,
        advancedSettle: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "redeem_elite_earn",
            self._native_params(
                productId=productId,
                productSubId=productSubId,
                redeemType=redeemType,
                amount=amount,
                receiveAccount=receiveAccount,
                advancedSettle=advancedSettle,
                coin=coin,
            ),
        )

    async def get_elite_earn_assets(self) -> dict[str, Any]:
        return await self._native_private("get_elite_earn_assets", [])

    async def get_elite_earn_records(
        self,
        type: str,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_elite_earn_records",
            self._native_params(
                type=type,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )
