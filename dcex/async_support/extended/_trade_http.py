"""Extended async trade HTTP client backed by Rust."""

from collections.abc import Mapping
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Extended order endpoints."""

    async def get_open_orders(
        self,
        market: str | None = None,
        type: str | None = None,  # noqa: A002
        side: str | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_open_orders",
            self._native_params(market=market, type=type, side=side),
        )

    async def get_orders_history(
        self,
        market: str | None = None,
        type: str | None = None,  # noqa: A002
        side: str | None = None,
        cursor: int | None = None,
        limit: int | None = None,
        sort: str | None = None,
    ) -> Any:  # noqa: ANN401
        return await self._native_private(
            "get_orders_history",
            self._native_params(
                market=market,
                type=type,
                side=side,
                cursor=cursor,
                limit=limit,
                sort=sort,
            ),
        )

    async def get_order(self, id: int | str) -> Any:  # noqa: A002, ANN401
        return await self._native_private("get_order", self._native_params(id=id))

    async def get_order_by_external_id(self, externalId: int | str) -> Any:  # noqa: N803, ANN401
        return await self._request(
            "GET",
            f"/api/v1/user/orders/external/{externalId}",
            signed=True,
        )

    async def get_orders_by_external_id(self, externalId: int | str) -> Any:  # noqa: N803, ANN401
        return await self.get_order_by_external_id(externalId)

    async def sign_create_order(
        self,
        *,
        market: str | None = None,
        product_symbol: str | None = None,
        side: str,
        qty: Any,  # noqa: ANN401
        price: Any,  # noqa: ANN401
        type_: str = "LIMIT",
        post_only: bool = False,
        time_in_force: str = "GTT",
        reduce_only: bool = False,
        expiry_epoch_millis: int | None = None,
        nonce: int | None = None,
        fee: Any | None = None,  # noqa: ANN401
        self_trade_protection_level: str = "ACCOUNT",
        external_id: str | None = None,
        builder_fee: Any | None = None,  # noqa: ANN401
        builder_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Build and sign an Extended order body using the Rust core."""
        return await self._native_private(
            "sign_create_order",
            self._native_params(
                market=market,
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                type_=type_,
                post_only=post_only,
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                expiry_epoch_millis=expiry_epoch_millis,
                nonce=nonce,
                fee=fee,
                self_trade_protection_level=self_trade_protection_level,
                external_id=external_id,
                builder_fee=builder_fee,
                builder_id=builder_id,
            ),
        )

    async def place_limit_order(
        self,
        *,
        market: str | None = None,
        product_symbol: str | None = None,
        side: str,
        qty: Any,  # noqa: ANN401
        price: Any,  # noqa: ANN401
        type_: str = "LIMIT",
        post_only: bool = False,
        time_in_force: str = "GTT",
        reduce_only: bool = False,
        expiry_epoch_millis: int | None = None,
        nonce: int | None = None,
        fee: Any | None = None,  # noqa: ANN401
        self_trade_protection_level: str = "ACCOUNT",
        external_id: str | None = None,
        builder_fee: Any | None = None,  # noqa: ANN401
        builder_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Place an Extended LIMIT order signed by the Rust core."""
        return await self._native_private(
            "place_limit_order",
            self._native_params(
                market=market,
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                type_=type_,
                post_only=post_only,
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                expiry_epoch_millis=expiry_epoch_millis,
                nonce=nonce,
                fee=fee,
                self_trade_protection_level=self_trade_protection_level,
                external_id=external_id,
                builder_fee=builder_fee,
                builder_id=builder_id,
            ),
        )

    async def place_order(
        self,
        body: Mapping[str, Any] | None = None,
        *,
        market: str | None = None,
        product_symbol: str | None = None,
        side: str | None = None,
        qty: Any | None = None,  # noqa: ANN401
        price: Any | None = None,  # noqa: ANN401
        type_: str = "LIMIT",
        post_only: bool = False,
        time_in_force: str = "GTT",
        reduce_only: bool = False,
        expiry_epoch_millis: int | None = None,
        nonce: int | None = None,
        fee: Any | None = None,  # noqa: ANN401
        self_trade_protection_level: str = "ACCOUNT",
        external_id: str | None = None,
        builder_fee: Any | None = None,  # noqa: ANN401
        builder_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Submit a pre-signed body or build/sign a LIMIT order in Rust."""
        if body is not None:
            return await self._native_private("place_order", self._native_params(body=body))
        if side is None or qty is None or price is None:
            raise ValueError("place_order requires body or side, qty, and price.")
        return await self._native_private(
            "place_order",
            self._native_params(
                market=market,
                product_symbol=product_symbol,
                side=side,
                qty=qty,
                price=price,
                type_=type_,
                post_only=post_only,
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                expiry_epoch_millis=expiry_epoch_millis,
                nonce=nonce,
                fee=fee,
                self_trade_protection_level=self_trade_protection_level,
                external_id=external_id,
                builder_fee=builder_fee,
                builder_id=builder_id,
            ),
        )

    async def cancel_order(self, id: int | str) -> Any:  # noqa: A002, ANN401
        return await self._native_private("cancel_order", self._native_params(id=id))

    async def cancel_order_by_external_id(self, externalId: str) -> Any:  # noqa: N803, ANN401
        return await self._native_private(
            "cancel_order_by_external_id",
            self._native_params(externalId=externalId),
        )

    async def mass_cancel(self, body: Mapping[str, Any]) -> Any:  # noqa: ANN401
        return await self._native_private("mass_cancel", self._native_params(body=body))

    async def set_deadmanswitch(self, countdownTime: int) -> Any:  # noqa: N803, ANN401
        return await self._request(
            "POST",
            "/api/v1/user/deadmanswitch",
            {"countdownTime": countdownTime},
            signed=True,
        )
