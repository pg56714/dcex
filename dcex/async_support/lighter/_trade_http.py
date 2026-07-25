"""Lighter async signed trading HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Lighter signed trading APIs."""

    async def send_tx(
        self,
        tx_type: int,
        tx_info: str,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit a signed Lighter transaction."""
        return await self._native_private("send_tx", self._native_params(**locals()))

    async def send_tx_batch(
        self,
        tx_types: str,
        tx_infos: str,
    ) -> dict[str, Any] | list[Any]:
        """Submit a batch of signed Lighter transactions."""
        return await self._native_private("send_tx_batch", self._native_params(**locals()))

    async def sign_create_order(
        self,
        market_index: int,
        client_order_index: int,
        base_amount: int,
        price: int,
        is_ask: bool,
        order_type: int,
        time_in_force: int,
        reduce_only: bool = False,
        trigger_price: int = 0,
        order_expiry: int = -1,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        self_trade_behavior_mode: int = 0,
        self_trade_equality_mode: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter create-order transaction without submitting it."""
        return await self._native_sign("sign_create_order", self._native_params(**locals()))

    async def create_order(
        self,
        market_index: int,
        client_order_index: int,
        base_amount: int,
        price: int,
        is_ask: bool,
        order_type: int,
        time_in_force: int,
        reduce_only: bool = False,
        trigger_price: int = 0,
        order_expiry: int = -1,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        self_trade_behavior_mode: int = 0,
        self_trade_equality_mode: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Create a Lighter order."""
        return await self._native_private("create_order", self._native_params(**locals()))

    place_order = create_order

    async def sign_cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter cancel-order transaction without submitting it."""
        return await self._native_sign("sign_cancel_order", self._native_params(**locals()))

    async def cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a Lighter order."""
        return await self._native_private("cancel_order", self._native_params(**locals()))

    async def sign_modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        self_trade_behavior_mode: int = 0,
        self_trade_equality_mode: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter modify-order transaction without submitting it."""
        return await self._native_sign("sign_modify_order", self._native_params(**locals()))

    async def modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        self_trade_behavior_mode: int = 0,
        self_trade_equality_mode: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Modify a Lighter order."""
        return await self._native_private("modify_order", self._native_params(**locals()))

    async def sign_cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        cancel_all_market_index: int = 255,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter cancel-all-orders transaction without submitting it."""
        return await self._native_sign("sign_cancel_all_orders", self._native_params(**locals()))

    async def cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        cancel_all_market_index: int = 255,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all Lighter orders."""
        return await self._native_private("cancel_all_orders", self._native_params(**locals()))

    async def sign_update_leverage(
        self,
        market_index: int,
        fraction: int,
        margin_mode: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter leverage update without submitting it."""
        return await self._native_sign("sign_update_leverage", self._native_params(**locals()))

    async def update_leverage(
        self,
        market_index: int,
        fraction: int,
        margin_mode: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Update Lighter leverage."""
        return await self._native_private("update_leverage", self._native_params(**locals()))

    async def sign_update_margin(
        self,
        market_index: int,
        usdc_amount: int,
        direction: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter isolated-margin update without submitting it."""
        return await self._native_sign("sign_update_margin", self._native_params(**locals()))

    async def update_margin(
        self,
        market_index: int,
        usdc_amount: int,
        direction: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Update Lighter isolated margin."""
        return await self._native_private("update_margin", self._native_params(**locals()))
