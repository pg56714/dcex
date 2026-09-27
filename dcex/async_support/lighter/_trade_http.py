"""Lighter async signed trading HTTP client backed by Rust."""

from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """Async HTTP client for Lighter signed trading APIs."""

    async def create_rfq(
        self,
        market_index: int,
        direction: int,
        base_amount: str | None = None,
        quote_amount: str | None = None,
        metadata: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Create a request for quote."""
        return await self._native_private("create_rfq", self._native_params(**locals()))

    async def get_rfq(self, rfq_id: int) -> dict[str, Any] | list[Any]:
        """Get a request for quote by ID."""
        return await self._native_private("get_rfq", self._native_params(**locals()))

    async def list_rfqs(
        self,
        account_index: int | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """List requests for quote."""
        return await self._native_private("list_rfqs", self._native_params(**locals()))

    async def update_rfq(self, rfq_id: int, status: str) -> dict[str, Any] | list[Any]:
        """Update the status of a request for quote."""
        return await self._native_private("update_rfq", self._native_params(**locals()))

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

    async def sign_create_grouped_orders(
        self,
        grouping_type: int,
        orders: list[dict[str, Any]],
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
        """
        Sign OTO (1), OCO (2), or OTOCO (3) as one type-28 transaction.

        Orders use the snake_case fields of create_order. Child orders are
        reduce-only TP/SL orders; OTO/OTOCO children use base_amount=0.
        """
        params = self._native_params(
            **{key: value for key, value in locals().items() if key != "orders"}
        )
        params.append(("orders", dumps(orders, separators=(",", ":"))))
        return await self._native_sign("sign_create_grouped_orders", params)

    async def create_grouped_orders(
        self,
        grouping_type: int,
        orders: list[dict[str, Any]],
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
        """
        Submit OTO (1), OCO (2), or OTOCO (3) as one type-28 transaction.

        Orders use the snake_case fields of create_order. Child orders are
        reduce-only TP/SL orders; OTO/OTOCO children use base_amount=0.
        """
        params = self._native_params(
            **{key: value for key, value in locals().items() if key != "orders"}
        )
        params.append(("orders", dumps(orders, separators=(",", ":"))))
        return await self._native_private("create_grouped_orders", params)

    async def update_account_config(
        self,
        account_trading_mode: int,
        *,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """

        Submit account trading mode (0 or 1) as transaction 41.

        Source:
        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/update_account_config.go

        """
        return await self._native_private("update_account_config", self._native_params(**locals()))

    async def sign_update_account_config(
        self,
        account_trading_mode: int,
        *,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """

        Sign account trading mode (0 or 1) as transaction 41.

        Source:
        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/update_account_config.go

        """
        return await self._native_sign(
            "sign_update_account_config", self._native_params(**locals())
        )

    async def update_account_asset_config(
        self,
        asset_index: int,
        asset_margin_mode: int,
        *,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """

        Submit account asset margin mode (0 disabled, 1 enabled) as transaction 42.

        Source:
        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/update_account_asset_config.go

        """
        return await self._native_private(
            "update_account_asset_config", self._native_params(**locals())
        )

    async def sign_update_account_asset_config(
        self,
        asset_index: int,
        asset_margin_mode: int,
        *,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """

        Sign account asset margin mode (0 disabled, 1 enabled) as transaction 42.

        Source:
        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/update_account_asset_config.go

        """
        return await self._native_sign(
            "sign_update_account_asset_config", self._native_params(**locals())
        )

    async def change_account_tier(
        self, *, account_index: int, new_tier: str, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/changeAccountTier.

        Source: https://github.com/elliottech/lighter-python/blob/main/lighter/api/account_api.py
        """
        return await self._native_private(
            "change_account_tier",
            self._native_params(
                account_index=account_index, new_tier=new_tier, authorization=authorization
            ),
        )

    async def create_read_only_token(
        self,
        *,
        name: str,
        account_index: int,
        expiry: int,
        sub_account_access: bool,
        authorization: str | None = None,
        scopes: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/tokens/create.

        Source: https://github.com/elliottech/lighter-python/blob/main/lighter/api/account_api.py
        """
        return await self._native_private(
            "create_read_only_token",
            self._native_params(
                name=name,
                account_index=account_index,
                expiry=expiry,
                sub_account_access=sub_account_access,
                authorization=authorization,
                scopes=scopes,
            ),
        )

    async def revoke_read_only_token(
        self, *, token_id: int, account_index: int, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/tokens/revoke.

        Source: https://github.com/elliottech/lighter-python/blob/main/lighter/api/account_api.py
        """
        return await self._native_private(
            "revoke_read_only_token",
            self._native_params(
                token_id=token_id, account_index=account_index, authorization=authorization
            ),
        )

    async def acknowledge_notification(
        self, *, notif_id: str, account_index: int, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """

        POST /api/v1/notification/ack.

        Source:
        https://github.com/elliottech/lighter-python/blob/main/lighter/api/notification_api.py

        """
        return await self._native_private(
            "acknowledge_notification",
            self._native_params(
                notif_id=notif_id, account_index=account_index, authorization=authorization
            ),
        )

    async def create_sub_account(
        self, *, skip_nonce: int = 0, nonce: int | None = None, api_key_index: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """Sign/submit creation of a subaccount by its master account."""
        return await self._native_private("create_sub_account", self._native_params(**locals()))

    async def sign_create_sub_account(
        self, *, skip_nonce: int = 0, nonce: int | None = None, api_key_index: int | None = None
    ) -> tuple[Any, Any, Any, Any]:
        """Sign/submit creation of a subaccount by its master account."""
        return await self._native_sign("sign_create_sub_account", self._native_params(**locals()))

    async def change_api_key_signed(
        self,
        new_pubkey: str,
        l1_signature: str,
        nonce: int,
        *,
        skip_nonce: int = 0,
        api_key_index: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Sign/submit key rotation with an explicit nonce and caller-signed L1 authorization.
        Recreate the client with the new key after confirmation.
        """
        return await self._native_private("change_api_key_signed", self._native_params(**locals()))

    async def sign_change_api_key_signed(
        self,
        new_pubkey: str,
        l1_signature: str,
        nonce: int,
        *,
        skip_nonce: int = 0,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Sign/submit key rotation with an explicit nonce and caller-signed L1 authorization.
        Recreate the client with the new key after confirmation.
        """
        return await self._native_sign(
            "sign_change_api_key_signed", self._native_params(**locals())
        )
