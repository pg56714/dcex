"""Lighter signed trading HTTP client backed by Rust."""

import json
from json import dumps
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for Lighter signed trading APIs."""

    def create_rfq(
        self,
        market_index: int,
        direction: int,
        base_amount: str | None = None,
        quote_amount: str | None = None,
        metadata: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Create a request for quote."""
        return self._native_private("create_rfq", self._native_params(**locals()))

    def get_rfq(self, rfq_id: int) -> dict[str, Any] | list[Any]:
        """Get a request for quote by ID."""
        return self._native_private("get_rfq", self._native_params(**locals()))

    def list_rfqs(
        self,
        account_index: int | None = None,
        status: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any] | list[Any]:
        """List requests for quote."""
        return self._native_private("list_rfqs", self._native_params(**locals()))

    def update_rfq(self, rfq_id: int, status: str) -> dict[str, Any] | list[Any]:
        """Update the status of a request for quote."""
        return self._native_private("update_rfq", self._native_params(**locals()))

    def send_tx(
        self,
        tx_type: int,
        tx_info: str,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit a signed Lighter transaction."""
        return self._native_private("send_tx", self._native_params(**locals()))

    def send_tx_batch(
        self,
        tx_types: str,
        tx_infos: str,
    ) -> dict[str, Any] | list[Any]:
        """Submit a batch of signed Lighter transactions."""
        return self._native_private("send_tx_batch", self._native_params(**locals()))

    def sign_create_order(
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
        return self._native_sign("sign_create_order", self._native_params(**locals()))

    def create_order(
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
        return self._native_private("create_order", self._native_params(**locals()))

    place_order = create_order

    def sign_cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter cancel-order transaction without submitting it."""
        return self._native_sign("sign_cancel_order", self._native_params(**locals()))

    def cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel a Lighter order."""
        return self._native_private("cancel_order", self._native_params(**locals()))

    def sign_modify_order(
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
        return self._native_sign("sign_modify_order", self._native_params(**locals()))

    def modify_order(
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
        return self._native_private("modify_order", self._native_params(**locals()))

    def sign_cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        cancel_all_market_index: int = 255,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter cancel-all-orders transaction without submitting it."""
        return self._native_sign("sign_cancel_all_orders", self._native_params(**locals()))

    def cancel_all_orders(
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
        return self._native_private("cancel_all_orders", self._native_params(**locals()))

    def sign_update_leverage(
        self,
        market_index: int,
        fraction: int,
        margin_mode: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter leverage update without submitting it."""
        return self._native_sign("sign_update_leverage", self._native_params(**locals()))

    def update_leverage(
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
        return self._native_private("update_leverage", self._native_params(**locals()))

    def sign_update_margin(
        self,
        market_index: int,
        usdc_amount: int,
        direction: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter isolated-margin update without submitting it."""
        return self._native_sign("sign_update_margin", self._native_params(**locals()))

    def update_margin(
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
        return self._native_private("update_margin", self._native_params(**locals()))

    def sign_create_grouped_orders(
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
        return self._native_sign("sign_create_grouped_orders", params)

    def create_grouped_orders(
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
        return self._native_private("create_grouped_orders", params)

    def update_account_config(
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
        return self._native_private("update_account_config", self._native_params(**locals()))

    def sign_update_account_config(
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
        return self._native_sign("sign_update_account_config", self._native_params(**locals()))

    def update_account_asset_config(
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
        return self._native_private("update_account_asset_config", self._native_params(**locals()))

    def sign_update_account_asset_config(
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
        return self._native_sign(
            "sign_update_account_asset_config", self._native_params(**locals())
        )

    def change_account_tier(
        self, *, account_index: int, new_tier: str, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/changeAccountTier.

        Source: https://github.com/elliottech/lighter-python/blob/main/lighter/api/account_api.py
        """
        return self._native_private(
            "change_account_tier",
            self._native_params(
                account_index=account_index, new_tier=new_tier, authorization=authorization
            ),
        )

    def create_read_only_token(
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
        return self._native_private(
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

    def revoke_read_only_token(
        self, *, token_id: int, account_index: int, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/tokens/revoke.

        Source: https://github.com/elliottech/lighter-python/blob/main/lighter/api/account_api.py
        """
        return self._native_private(
            "revoke_read_only_token",
            self._native_params(
                token_id=token_id, account_index=account_index, authorization=authorization
            ),
        )

    def acknowledge_notification(
        self, *, notif_id: str, account_index: int, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """

        POST /api/v1/notification/ack.

        Source:
        https://github.com/elliottech/lighter-python/blob/main/lighter/api/notification_api.py

        """
        return self._native_private(
            "acknowledge_notification",
            self._native_params(
                notif_id=notif_id, account_index=account_index, authorization=authorization
            ),
        )

    def create_sub_account(
        self, *, skip_nonce: int = 0, nonce: int | None = None, api_key_index: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """Sign/submit creation of a subaccount by its master account."""
        return self._native_private("create_sub_account", self._native_params(**locals()))

    def sign_create_sub_account(
        self, *, skip_nonce: int = 0, nonce: int | None = None, api_key_index: int | None = None
    ) -> tuple[Any, Any, Any, Any]:
        """Sign/submit creation of a subaccount by its master account."""
        return self._native_sign("sign_create_sub_account", self._native_params(**locals()))

    def change_api_key_signed(
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
        return self._native_private("change_api_key_signed", self._native_params(**locals()))

    def sign_change_api_key_signed(
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
        return self._native_sign("sign_change_api_key_signed", self._native_params(**locals()))

    def create_public_pool(
        self,
        *,
        operator_fee: int,
        initial_total_shares: int,
        min_operator_share_rate: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 10. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("create_public_pool", self._native_params(**locals()))

    def sign_create_public_pool(
        self,
        *,
        operator_fee: int,
        initial_total_shares: int,
        min_operator_share_rate: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 10. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_create_public_pool", self._native_params(**locals()))

    def update_public_pool(
        self,
        *,
        public_pool_index: int,
        status: int,
        operator_fee: int,
        min_operator_share_rate: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 11. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("update_public_pool", self._native_params(**locals()))

    def sign_update_public_pool(
        self,
        *,
        public_pool_index: int,
        status: int,
        operator_fee: int,
        min_operator_share_rate: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 11. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_update_public_pool", self._native_params(**locals()))

    def mint_shares(
        self,
        *,
        public_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 18. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("mint_shares", self._native_params(**locals()))

    def sign_mint_shares(
        self,
        *,
        public_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 18. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_mint_shares", self._native_params(**locals()))

    def burn_shares(
        self,
        *,
        public_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 19. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("burn_shares", self._native_params(**locals()))

    def sign_burn_shares(
        self,
        *,
        public_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 19. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_burn_shares", self._native_params(**locals()))

    def stake_assets(
        self,
        *,
        staking_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 35. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("stake_assets", self._native_params(**locals()))

    def sign_stake_assets(
        self,
        *,
        staking_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 35. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_stake_assets", self._native_params(**locals()))

    def unstake_assets(
        self,
        *,
        staking_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit Lighter transaction 36. Amounts use integer shares, not decimal token amounts."""
        return self._native_private("unstake_assets", self._native_params(**locals()))

    def sign_unstake_assets(
        self,
        *,
        staking_pool_index: int,
        share_amount: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign Lighter transaction 36. Amounts use integer shares, not decimal token amounts."""
        return self._native_sign("sign_unstake_assets", self._native_params(**locals()))

    def submit_lit_lease(
        self,
        *,
        tx_info: str,
        lease_amount: str,
        duration_days: int,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit caller-signed JSON. Lease amounts use raw LIT units (1 LIT = 100000000)."""
        return self._native_private("submit_lit_lease", self._native_params(**locals()))

    def export_historical_trades(
        self, *, l1_address: str, date: str, authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Request a historical export URL; server access requirements apply."""
        return self._native_private(
            "export_historical_trades",
            self._native_params(
                **{"authorization": authorization, "l1_address": l1_address, "date": date}
            ),
        )

    def transfer_l2_account(
        self,
        *,
        to_account_index: int,
        asset_index: int,
        from_route_type: int,
        to_route_type: int,
        amount: int,
        usdc_fee: int = 0,
        memo_hex: str | None = None,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Transfer between L2 account indices using raw integer amount and fee units.

        The recipient may be another user. Transfers have no second confirmation;
        they execute on submit. Account-family membership is not verified locally.
        The exchange enforces eligibility.
        """
        return self._native_private("transfer_l2_account", self._native_params(**locals()))

    def sign_transfer_l2_account(
        self,
        *,
        to_account_index: int,
        asset_index: int,
        from_route_type: int,
        to_route_type: int,
        amount: int,
        usdc_fee: int = 0,
        memo_hex: str | None = None,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Transfer between L2 account indices using raw integer amount and fee units.

        The recipient may be another user. Transfers have no second confirmation;
        they execute on submit. Account-family membership is not verified locally.
        The exchange enforces eligibility.
        """
        return self._native_sign("sign_transfer_l2_account", self._native_params(**locals()))

    def set_maker_only_api_keys(
        self, *, account_index: int, api_key_indexes: list[int], authorization: str | None = None
    ) -> dict[str, Any] | list[Any]:
        """Replace the complete maker-only key list; an empty list clears restrictions."""
        return self._native_private(
            "set_maker_only_api_keys",
            self._native_params(
                account_index=account_index,
                api_key_indexes=json.dumps(api_key_indexes, separators=(",", ":")),
                authorization=authorization,
            ),
        )

    transfer_same_master_account = transfer_l2_account
    sign_transfer_same_master_account = sign_transfer_l2_account

    def submit_fast_withdrawal(
        self,
        *,
        tx_info: str,
        to_address: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/fastwithdraw.

        API withdrawals have no second confirmation; they execute on submit.
        tx_info must be an already signed L2 transfer to the fast-withdraw service.

        https://apidocs.lighter.xyz/reference/fastwithdraw
        """
        return self._native_private("submit_fast_withdrawal", self._native_params(**locals()))

    def create_referral_code(
        self,
        *,
        account_index: int,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/referral/create.

        https://apidocs.lighter.xyz/reference/referral_create
        """
        return self._native_private("create_referral_code", self._native_params(**locals()))

    def get_referral_code(
        self,
        *,
        account_index: int,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v1/referral/get.

        https://apidocs.lighter.xyz/reference/referral_get
        """
        return self._native_private("get_referral_code", self._native_params(**locals()))

    def update_referral_kickback(
        self,
        *,
        account_index: int,
        kickback_percentage: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/referral/kickback/update.

        https://apidocs.lighter.xyz/reference/referral_kickback_update
        """
        return self._native_private("update_referral_kickback", self._native_params(**locals()))

    def get_referral_stats(
        self,
        *,
        l1_address: str,
        auth: str | None = None,
        is_eligible: bool | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        GET /api/v1/referral/stats.

        https://apidocs.lighter.xyz/reference/referral_stats
        """
        return self._native_private("get_referral_stats", self._native_params(**locals()))

    def update_referral_code(
        self,
        *,
        account_index: int,
        new_referral_code: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/referral/update.

        https://apidocs.lighter.xyz/reference/referral_update
        """
        return self._native_private("update_referral_code", self._native_params(**locals()))

    def use_referral_code(
        self,
        *,
        l1_address: str,
        referral_code: str,
        discord: str | None = None,
        telegram: str | None = None,
        x: str | None = None,
        signature: str | None = None,
        source: str | None = None,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/referral/use.

        Pass signature unchanged when required by the service; this method does not sign a wallet
        message.

        https://apidocs.lighter.xyz/reference/referral_use
        """
        return self._native_private("use_referral_code", self._native_params(**locals()))

    def respond_to_rfq(
        self,
        *,
        rfq_id: int,
        status: str,
        authorization: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v1/rfq/respond.

        https://apidocs.lighter.xyz/reference/rfq_respond
        """
        return self._native_private("respond_to_rfq", self._native_params(**locals()))

    def withdraw_l2(
        self,
        *,
        asset_index: int,
        route_type: int,
        amount: int,
        nonce: int | None = None,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit L2 withdrawal transaction 13; amount uses raw integer asset units.

        API withdrawals have no second confirmation; they execute on submit.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/withdraw.go
        """
        return self._native_private("withdraw_l2", self._native_params(**locals()))

    def sign_withdraw_l2(
        self,
        *,
        asset_index: int,
        route_type: int,
        amount: int,
        nonce: int | None = None,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Sign L2 withdrawal transaction 13; amount uses raw integer asset units.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/withdraw.go
        """
        return self._native_sign("sign_withdraw_l2", self._native_params(**locals()))

    def approve_integrator(
        self,
        *,
        integrator_account_index: int,
        max_perps_taker_fee: int,
        max_perps_maker_fee: int,
        max_spot_taker_fee: int,
        max_spot_maker_fee: int,
        approval_expiry: int,
        l1_signature: str,
        nonce: int,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> dict[str, Any] | list[Any]:
        """
        Submit integrator approval transaction 45; fee ticks use 1,000,000 per 100%.

        l1_signature is the caller-provided Ethereum signature of the official
        GetL1SignatureBody message, using the same nonce, account, key and chain.
        approval_expiry is the SDK millisecond timestamp; zero revokes approval
        and requires all four fee caps to be zero.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/approve_integrator.go
        """
        return self._native_private("approve_integrator", self._native_params(**locals()))

    def sign_approve_integrator(
        self,
        *,
        integrator_account_index: int,
        max_perps_taker_fee: int,
        max_perps_maker_fee: int,
        max_spot_taker_fee: int,
        max_spot_maker_fee: int,
        approval_expiry: int,
        l1_signature: str,
        nonce: int,
        api_key_index: int | None = None,
        skip_nonce: int = 0,
    ) -> tuple[Any, Any, Any, Any]:
        """
        Sign integrator approval transaction 45; fee ticks use 1,000,000 per 100%.

        l1_signature is the caller-provided Ethereum signature of the official
        GetL1SignatureBody message, using the same nonce, account, key and chain.
        approval_expiry is the SDK millisecond timestamp; zero revokes approval
        and requires all four fee caps to be zero.

        https://github.com/elliottech/lighter-go/blob/main/types/txtypes/approve_integrator.go
        """
        return self._native_sign("sign_approve_integrator", self._native_params(**locals()))
