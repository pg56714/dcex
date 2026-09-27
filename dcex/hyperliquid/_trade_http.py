# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Trading-related HTTP API client for Hyperliquid exchange backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for trading operations on Hyperliquid exchange."""

    def transfer_between_dexes(
        self, source_dex: str, destination_dex: str, token: str, amount: str
    ) -> dict[str, Any]:
        """Move collateral between this wallet''s Spot and Perp DEX balances."""
        return self._native_private(
            "transfer_between_dexes",
            self._native_params(
                sourceDex=source_dex,
                destinationDex=destination_dex,
                token=token,
                amount=amount,
            ),
        )

    def place_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place an order on the exchange."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private("place_order", self._native_params(**locals()))

    def place_future_market_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
        reduceOnly: bool = False,
        slippage: float = 0.05,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_market_order",
            self._native_params(**locals()),
        )

    def place_future_market_buy_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
        reduceOnly: bool = False,
        slippage: float = 0.05,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market buy order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_market_buy_order",
            self._native_params(**locals()),
        )

    def place_future_market_sell_order(
        self,
        product_symbol: str,
        size: str,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
        reduceOnly: bool = False,
        slippage: float = 0.05,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
    ) -> dict[str, Any]:
        """Place a future market sell order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_market_sell_order",
            self._native_params(**locals()),
        )

    def place_future_limit_order(
        self,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        tif: str,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future limit order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_limit_order",
            self._native_params(**locals()),
        )

    def place_future_limit_buy_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future limit buy order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_limit_buy_order",
            self._native_params(**locals()),
        )

    def place_future_limit_sell_order(
        self,
        product_symbol: str,
        price: str,
        size: str,
        tif: str,
        cloid: str | None = None,
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a future limit sell order."""
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private(
            "place_future_limit_sell_order",
            self._native_params(**locals()),
        )

    def place_batch_orders(
        self,
        orders: list[dict[str, Any]],
        grouping: str = "na",
        builder_address: str | None = None,
        fee_ten_bp: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """
        Place several orders in one signed ``order`` action.

        Each order uses the ``place_order`` keys (``product_symbol``, ``isBuy``,
        ``price``, ``size``, optional ``reduceOnly``, ``tif`` or
        ``isMarket``/``triggerPx``/``tpsl``, ``cloid``). ``grouping`` may be
        ``normalTpsl`` or ``positionTpsl`` to send an entry with its TP/SL orders.
        """
        if (builder_address is None) != (fee_ten_bp is None):
            raise ValueError("builder_address and fee_ten_bp must be provided together")
        return self._native_private("place_batch_orders", self._native_params(**locals()))

    def cancel_batch_orders(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``oid`` each) in one action."""
        return self._native_private("cancel_batch_orders", self._native_params(**locals()))

    def cancel_batch_orders_by_cloid(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``cloid`` each) in one action."""
        return self._native_private(
            "cancel_batch_orders_by_cloid",
            self._native_params(**locals()),
        )

    def cancel_order(
        self,
        product_symbol: str,
        oid: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by order ID."""
        return self._native_private("cancel_order", self._native_params(**locals()))

    def cancel_order_by_cloid(
        self,
        product_symbol: str,
        cloid: str,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by client order ID."""
        return self._native_private(
            "cancel_order_by_cloid",
            self._native_params(**locals()),
        )

    def schedule_cancel(
        self,
        time: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Schedule order cancellation."""
        return self._native_private("schedule_cancel", self._native_params(**locals()))

    def modify_order(
        self,
        oid: int | str,
        product_symbol: str,
        isBuy: bool,
        price: str,
        size: str,
        reduceOnly: bool,
        tif: str | None = None,
        isMarket: bool | None = None,
        triggerPx: str | None = None,
        tpsl: str | None = None,
        cloid: str | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify an existing order."""
        return self._native_private("modify_order", self._native_params(**locals()))

    def modify_batch_orders(
        self,
        modifies: list,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify multiple orders in batch."""
        return self._native_private(
            "modify_batch_orders",
            self._native_params(**locals()),
        )

    def update_leverage(
        self,
        product_symbol: str,
        isCross: bool,
        leverage: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update leverage for a product."""
        return self._native_private("update_leverage", self._native_params(**locals()))

    def update_isolate_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update isolated margin for a product."""
        return self._native_private(
            "update_isolate_margin",
            self._native_params(**locals()),
        )

    def update_isolated_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update isolated margin for a product (``updateIsolatedMargin``)."""
        return self._native_private(
            "update_isolated_margin",
            self._native_params(**locals()),
        )

    def place_twap_order(
        self,
        product_symbol: str,
        isBuy: bool,
        size: str,
        reduceOnly: bool,
        minutes: int,
        randomize: bool,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Place a TWAP order."""
        return self._native_private("place_twap_order", self._native_params(**locals()))

    def cancel_twap_order(
        self,
        product_symbol: str,
        twap_id: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel a TWAP order."""
        return self._native_private("cancel_twap_order", self._native_params(**locals()))

    def transfer_usdc_spot_perp(
        self,
        amount: str,
        to_perp: bool,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> dict[str, Any]:
        """
        Submit a wallet-signed USDC transfer between the user's spot and perp accounts.

        The signature must be EIP-712 signed by the user's wallet for this exact
        usdClassTransfer action and nonce. API agent signatures are not accepted.
        """
        return self._native_private(
            "transfer_usdc_spot_perp",
            self._native_params(
                amount=amount,
                toPerp=to_perp,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    def noop(
        self, nonce: int, *, vault_address: str | None = None, expires_after: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        Attempt to invalidate a pending request by signing the same nonce; success is not
        guaranteed.
        """
        return self._native_private(
            "noop",
            self._native_params(
                nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def reserve_request_weight(self, weight: int, *, expires_after: int | None = None) -> Any:
        """Reserve actions for this account at 0.0005 USDC each, paid from its perps balance."""
        return self._native_private(
            "reserve_request_weight", self._native_params(weight=weight, expiresAfter=expires_after)
        )

    def set_agent_abstraction(self, abstraction: str) -> Any:
        """Set account mode using agent signing: i=disabled, u=unified, p=portfolio margin."""
        return self._native_private(
            "set_agent_abstraction", self._native_params(abstraction=abstraction)
        )

    def set_user_abstraction(
        self,
        user: str,
        abstraction: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:
        """
        Submit a wallet-signed userSetAbstraction action for this user or its subaccount.

        Modes: disabled, unifiedAccount, portfolioMargin. Sign the exact action,
        chain and nonce with the wallet; an API-agent signature is insufficient.
        """
        return self._native_private(
            "set_user_abstraction",
            self._native_params(
                user=user,
                abstraction=abstraction,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )
