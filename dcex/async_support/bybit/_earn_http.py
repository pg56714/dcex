"""Async Bybit Earn HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class EarnHTTP(HTTPManager):
    """Async HTTP client for Bybit Flexible Saving and OnChain Earn workflows."""

    async def _earn_native_public(self, method_name: str, params: list[tuple[str, str]]) -> Any:  # noqa: ANN401
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for public Earn methods.")
        response, data = await request_native_json_async(
            self._native_client, "public_request", method_name, params
        )
        self._store_response_headers(response)
        return data

    async def get_earn_products(self, category: str, coin: str | None = None) -> dict[str, Any]:
        """List public Bybit Earn products."""
        return await self._earn_native_public(
            "get_earn_products",
            self._native_params(category=category, coin=coin),
        )

    async def place_earn_order(
        self,
        category: str,
        orderType: str,
        accountType: str,
        amount: str,
        coin: str,
        productId: str,
        orderLinkId: str,
        *,
        redeemPositionId: str | None = None,
        toAccountType: str | None = None,
        interestCard: dict[str, object] | None = None,
    ) -> dict[str, Any]:
        """Stake into or redeem from a Bybit Earn product."""
        return await self._native_private(
            "place_earn_order",
            self._native_params(
                category=category,
                orderType=orderType,
                accountType=accountType,
                amount=amount,
                coin=coin,
                productId=productId,
                orderLinkId=orderLinkId,
                redeemPositionId=redeemPositionId,
                toAccountType=toAccountType,
                interestCard=interestCard,
            ),
        )

    async def get_earn_order_history(
        self,
        category: str,
        *,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return Bybit Earn stake and redemption history."""
        return await self._native_private(
            "get_earn_order_history",
            self._native_params(
                category=category,
                orderId=orderId,
                orderLinkId=orderLinkId,
                productId=productId,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    async def get_earn_positions(
        self,
        category: str,
        *,
        productId: str | None = None,
        coin: str | None = None,
    ) -> dict[str, Any]:
        """Return Bybit Earn positions."""
        return await self._native_private(
            "get_earn_positions",
            self._native_params(category=category, productId=productId, coin=coin),
        )

    async def get_earn_yield_history(
        self,
        category: str,
        *,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return daily Bybit Earn yield history."""
        return await self._earn_yield_query(
            "get_earn_yield_history",
            category,
            productId,
            startTime,
            endTime,
            limit,
            cursor,
        )

    async def get_earn_hourly_yield_history(
        self,
        category: str = "FlexibleSaving",
        *,
        productId: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return hourly Flexible Saving yield history."""
        return await self._earn_yield_query(
            "get_earn_hourly_yield_history",
            category,
            productId,
            startTime,
            endTime,
            limit,
            cursor,
        )

    async def _earn_yield_query(
        self,
        method_name: str,
        category: str,
        product_id: str | None,
        start_time: int | None,
        end_time: int | None,
        limit: int | None,
        cursor: str | None,
    ) -> dict[str, Any]:
        return await self._native_private(
            method_name,
            self._native_params(
                category=category,
                productId=product_id,
                startTime=start_time,
                endTime=end_time,
                limit=limit,
                cursor=cursor,
            ),
        )
