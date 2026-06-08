"""Lighter signed trading HTTP client."""

from typing import Any

from ._http_manager import HTTPManager
from .endpoints.market import Public


class TradeHTTP(HTTPManager):
    """HTTP client for Lighter signed trading APIs."""

    def send_tx(
        self,
        tx_type: int,
        tx_info: str,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Submit a signed Lighter transaction."""
        return self._request(
            "POST",
            Public.SEND_TX,
            body={
                "tx_type": tx_type,
                "tx_info": tx_info,
                "price_protection": price_protection,
            },
            content_type="form",
        )

    def send_tx_batch(
        self,
        tx_types: str,
        tx_infos: str,
    ) -> dict[str, Any] | list[Any]:
        """Submit a batch of signed Lighter transactions."""
        return self._request(
            "POST",
            Public.SEND_TX_BATCH,
            body={"tx_types": tx_types, "tx_infos": tx_infos},
            content_type="form",
        )

    def _nonce(self, nonce: int | None = None, api_key_index: int | None = None) -> int:
        if nonce is not None:
            return int(nonce)
        res = self._request(
            "GET",
            Public.NEXT_NONCE,
            {
                "account_index": self._private_account_index(),
                "api_key_index": self._private_api_key_index(api_key_index),
            },
        )
        if not isinstance(res, dict) or "nonce" not in res:
            raise ValueError(f"Unexpected Lighter nonce response: {res!r}")
        return int(res["nonce"])

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
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter create-order transaction without submitting it."""
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_create_order(
            market_index=market_index,
            client_order_index=client_order_index,
            base_amount=base_amount,
            price=price,
            is_ask=is_ask,
            order_type=order_type,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            trigger_price=trigger_price,
            order_expiry=order_expiry,
            integrator_account_index=integrator_account_index,
            integrator_taker_fee=integrator_taker_fee,
            integrator_maker_fee=integrator_maker_fee,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

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
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Create a Lighter order."""
        return self._signed_tx(
            self.sign_create_order(
                market_index=market_index,
                client_order_index=client_order_index,
                base_amount=base_amount,
                price=price,
                is_ask=is_ask,
                order_type=order_type,
                time_in_force=time_in_force,
                reduce_only=reduce_only,
                trigger_price=trigger_price,
                order_expiry=order_expiry,
                integrator_account_index=integrator_account_index,
                integrator_taker_fee=integrator_taker_fee,
                integrator_maker_fee=integrator_maker_fee,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )

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
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_cancel_order(
            market_index=market_index,
            order_index=order_index,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

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
        return self._signed_tx(
            self.sign_cancel_order(
                market_index=market_index,
                order_index=order_index,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )

    def sign_modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter modify-order transaction without submitting it."""
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_modify_order(
            market_index=market_index,
            order_index=order_index,
            base_amount=base_amount,
            price=price,
            trigger_price=trigger_price,
            integrator_account_index=integrator_account_index,
            integrator_taker_fee=integrator_taker_fee,
            integrator_maker_fee=integrator_maker_fee,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

    def modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Modify a Lighter order."""
        return self._signed_tx(
            self.sign_modify_order(
                market_index=market_index,
                order_index=order_index,
                base_amount=base_amount,
                price=price,
                trigger_price=trigger_price,
                integrator_account_index=integrator_account_index,
                integrator_taker_fee=integrator_taker_fee,
                integrator_maker_fee=integrator_maker_fee,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )

    def sign_cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
    ) -> tuple[Any, Any, Any, Any]:
        """Sign a Lighter cancel-all-orders transaction without submitting it."""
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_cancel_all_orders(
            time_in_force=time_in_force,
            timestamp_ms=timestamp_ms,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

    def cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        skip_nonce: int = 0,
        nonce: int | None = None,
        api_key_index: int | None = None,
        price_protection: bool | None = None,
    ) -> dict[str, Any] | list[Any]:
        """Cancel all Lighter orders."""
        return self._signed_tx(
            self.sign_cancel_all_orders(
                time_in_force=time_in_force,
                timestamp_ms=timestamp_ms,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )

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
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_update_leverage(
            market_index=market_index,
            fraction=fraction,
            margin_mode=margin_mode,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

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
        return self._signed_tx(
            self.sign_update_leverage(
                market_index=market_index,
                fraction=fraction,
                margin_mode=margin_mode,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )

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
        api_key_index = self._private_api_key_index(api_key_index)
        return self._private_signer().sign_update_margin(
            market_index=market_index,
            usdc_amount=usdc_amount,
            direction=direction,
            skip_nonce=skip_nonce,
            nonce=self._nonce(nonce, api_key_index),
            api_key_index=api_key_index,
        )

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
        return self._signed_tx(
            self.sign_update_margin(
                market_index=market_index,
                usdc_amount=usdc_amount,
                direction=direction,
                skip_nonce=skip_nonce,
                nonce=nonce,
                api_key_index=api_key_index,
            ),
            price_protection=price_protection,
        )
