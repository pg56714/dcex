"""Bitget Earn HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """HTTP client for Bitget Savings and On-chain Earn workflows."""

    def get_elite_earn_products(self) -> dict[str, Any]:
        return self._native_private("get_elite_earn_products", [])

    def get_elite_earn_subscription_info(self, product_id: str) -> dict[str, Any]:
        return self._native_private(
            "get_elite_earn_subscription_info", self._native_params(productId=product_id)
        )

    def subscribe_elite_earn(
        self,
        product_sub_id: str,
        amount: str,
        *,
        coin: str | None = None,
        payment_account: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "subscribe_elite_earn",
            self._native_params(
                productSubId=product_sub_id,
                amount=amount,
                coin=coin,
                paymentAccount=payment_account,
            ),
        )

    def get_elite_earn_subscription_result(self, order_id: str) -> dict[str, Any]:
        return self._native_private(
            "get_elite_earn_subscription_result", self._native_params(orderId=order_id)
        )

    def get_elite_earn_redemption_info(self, product_id: str) -> dict[str, Any]:
        return self._native_private(
            "get_elite_earn_redemption_info", self._native_params(productId=product_id)
        )

    def redeem_elite_earn(
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
        return self._native_private(
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

    def get_elite_earn_assets(self) -> dict[str, Any]:
        return self._native_private("get_elite_earn_assets", [])

    def get_elite_earn_records(
        self,
        type: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_elite_earn_records",
            self._native_params(
                type=type,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )
