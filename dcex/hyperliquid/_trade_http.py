# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Trading-related HTTP API client for Hyperliquid exchange backed by Rust."""

import json
from typing import Any

from ._batch_http import TradeHTTPBatchHTTP
from ._http_manager import HTTPManager
from ._transfers_http import TradeHTTPTransfersHTTP
from ._withdrawals_http import TradeHTTPWithdrawalsHTTP


class TradeHTTP(TradeHTTPTransfersHTTP, TradeHTTPBatchHTTP, TradeHTTPWithdrawalsHTTP, HTTPManager):
    """HTTP client for trading operations on Hyperliquid exchange."""

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

    def reserve_request_weight(self, weight: int, *, expires_after: int | None = None) -> Any:  # noqa: ANN401
        """Reserve actions for this account at 0.0005 USDC each, paid from its perps balance."""
        return self._native_private(
            "reserve_request_weight", self._native_params(weight=weight, expiresAfter=expires_after)
        )

    def set_agent_abstraction(
        self,
        abstraction: str,
        *,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Set account mode using agent signing: i=disabled, u=unified, p=portfolio margin."""
        return self._native_private(
            "set_agent_abstraction",
            self._native_params(
                abstraction=abstraction, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def set_user_abstraction(
        self,
        user: str,
        abstraction: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
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

    def enable_agent_dex_abstraction(
        self, *, nonce: int | None = None, expires_after: int | None = None
    ) -> Any:  # noqa: ANN401
        """Enable DEX abstraction for this agent."""
        return self._native_private(
            "enable_agent_dex_abstraction",
            self._native_params(nonce=nonce, expiresAfter=expires_after),
        )

    def deposit_staking_signed(
        self, *, wei: int, nonce: int, signature: dict[str, Any], signature_chain_id: str
    ) -> Any:  # noqa: ANN401
        """
        cDeposit. Supply the documented wallet EIP-712 signature; nonce and chain ID are
        forwarded unchanged.
        """
        return self._native_private(
            "deposit_staking_signed",
            self._native_params(
                wei=wei,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    def delegate_tokens_signed(
        self,
        *,
        validator: str,
        wei: int,
        is_undelegate: bool,
        nonce: int,
        signature: dict[str, Any],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        tokenDelegate. Supply the documented wallet EIP-712 signature; nonce and chain ID are
        forwarded unchanged.
        """
        return self._native_private(
            "delegate_tokens_signed",
            self._native_params(
                validator=validator,
                wei=wei,
                isUndelegate=is_undelegate,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    def set_user_dex_abstraction_signed(
        self,
        *,
        user: str,
        enabled: bool,
        nonce: int,
        signature: dict[str, Any],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        userDexAbstraction. Supply the documented wallet EIP-712 signature; nonce and chain ID
        are forwarded unchanged.
        """
        return self._native_private(
            "set_user_dex_abstraction_signed",
            self._native_params(
                user=user,
                enabled=enabled,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    def create_sub_account(
        self, *, account_name: str, nonce: int | None = None, expires_after: int | None = None
    ) -> Any:  # noqa: ANN401
        """createSubAccount within the authenticated master/subaccount family."""
        return self._native_private(
            "create_sub_account",
            self._native_params(name=account_name, nonce=nonce, expiresAfter=expires_after),
        )

    def approve_agent_signed(
        self,
        *,
        agent_address: str,
        nonce: int,
        signature: dict[str, Any],
        signature_chain_id: str,
        agent_name: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Submit a caller-supplied wallet EIP-712 agent approval signature."""
        return self._native_private(
            "approve_agent_signed",
            self._native_params(
                agentAddress=agent_address,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
                agentName=agent_name,
            ),
        )

    def borrow_lend_signed(
        self,
        action: dict[str, Any],
        *,
        nonce: int,
        signature: dict[str, str | int],
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a caller-signed borrowLend action through HTTP /exchange.

        Official spec incomplete; not verified live. Supply the complete action
        and its matching signature. No signing scheme or additional action fields
        are inferred locally; action.type must be borrowLend.
        """
        return self._native_private(
            "borrow_lend_signed",
            self._native_params(
                action=action,
                nonce=nonce,
                signature=signature,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
            ),
        )

    def approve_builder_fee_signed(
        self,
        *,
        builder: str,
        max_fee_rate: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit approveBuilderFee with a caller-provided wallet EIP-712 signature.

        The amount and signed strings are preserved exactly. Empty DEX names denote the default
        perpetual DEX.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#approve-a-builder-fee
        """
        return self._native_private(
            "approve_builder_fee_signed",
            self._native_params(
                builder=builder,
                maxFeeRate=max_fee_rate,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )
