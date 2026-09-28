# ruff: noqa: ANN401
# Exchange responses retain their native, heterogeneous JSON schemas.
"""Trading-related HTTP API client for Hyperliquid exchange backed by Rust."""

import json
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTP(HTTPManager):
    """HTTP client for trading operations on Hyperliquid exchange."""

    async def transfer_between_dexes(
        self, source_dex: str, destination_dex: str, token: str, amount: str
    ) -> dict[str, Any]:
        """Move collateral between this wallet''s Spot and Perp DEX balances."""
        return await self._native_private(
            "transfer_between_dexes",
            self._native_params(
                sourceDex=source_dex,
                destinationDex=destination_dex,
                token=token,
                amount=amount,
            ),
        )

    async def place_order(
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
        return await self._native_private("place_order", self._native_params(**locals()))

    async def place_future_market_order(
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
        return await self._native_private(
            "place_future_market_order",
            self._native_params(**locals()),
        )

    async def place_future_market_buy_order(
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
        return await self._native_private(
            "place_future_market_buy_order",
            self._native_params(**locals()),
        )

    async def place_future_market_sell_order(
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
        return await self._native_private(
            "place_future_market_sell_order",
            self._native_params(**locals()),
        )

    async def place_future_limit_order(
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
        return await self._native_private(
            "place_future_limit_order",
            self._native_params(**locals()),
        )

    async def place_future_limit_buy_order(
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
        return await self._native_private(
            "place_future_limit_buy_order",
            self._native_params(**locals()),
        )

    async def place_future_limit_sell_order(
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
        return await self._native_private(
            "place_future_limit_sell_order",
            self._native_params(**locals()),
        )

    async def place_batch_orders(
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
        return await self._native_private("place_batch_orders", self._native_params(**locals()))

    async def cancel_batch_orders(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``oid`` each) in one action."""
        return await self._native_private("cancel_batch_orders", self._native_params(**locals()))

    async def cancel_batch_orders_by_cloid(
        self,
        cancels: list[dict[str, Any]],
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel several orders (``product_symbol`` + ``cloid`` each) in one action."""
        return await self._native_private(
            "cancel_batch_orders_by_cloid",
            self._native_params(**locals()),
        )

    async def cancel_order(
        self,
        product_symbol: str,
        oid: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by order ID."""
        return await self._native_private("cancel_order", self._native_params(**locals()))

    async def cancel_order_by_cloid(
        self,
        product_symbol: str,
        cloid: str,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel an order by client order ID."""
        return await self._native_private(
            "cancel_order_by_cloid",
            self._native_params(**locals()),
        )

    async def schedule_cancel(
        self,
        time: int | None = None,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Schedule order cancellation."""
        return await self._native_private("schedule_cancel", self._native_params(**locals()))

    async def modify_order(
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
        return await self._native_private("modify_order", self._native_params(**locals()))

    async def modify_batch_orders(
        self,
        modifies: list,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Modify multiple orders in batch."""
        return await self._native_private(
            "modify_batch_orders",
            self._native_params(**locals()),
        )

    async def update_leverage(
        self,
        product_symbol: str,
        isCross: bool,
        leverage: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update leverage for a product."""
        return await self._native_private("update_leverage", self._native_params(**locals()))

    async def update_isolate_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update isolated margin for a product."""
        return await self._native_private(
            "update_isolate_margin",
            self._native_params(**locals()),
        )

    async def update_isolated_margin(
        self,
        product_symbol: str,
        isBuy: bool,
        ntli: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Update isolated margin for a product (``updateIsolatedMargin``)."""
        return await self._native_private(
            "update_isolated_margin",
            self._native_params(**locals()),
        )

    async def place_twap_order(
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
        return await self._native_private("place_twap_order", self._native_params(**locals()))

    async def cancel_twap_order(
        self,
        product_symbol: str,
        twap_id: int,
        vaultAddress: str | None = None,
        expiresAfter: int | None = None,
    ) -> dict[str, Any]:
        """Cancel a TWAP order."""
        return await self._native_private("cancel_twap_order", self._native_params(**locals()))

    async def transfer_usdc_spot_perp(
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
        return await self._native_private(
            "transfer_usdc_spot_perp",
            self._native_params(
                amount=amount,
                toPerp=to_perp,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def noop(
        self, nonce: int, *, vault_address: str | None = None, expires_after: int | None = None
    ) -> dict[str, Any] | list[Any]:
        """
        Attempt to invalidate a pending request by signing the same nonce; success is not
        guaranteed.
        """
        return await self._native_private(
            "noop",
            self._native_params(
                nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def reserve_request_weight(self, weight: int, *, expires_after: int | None = None) -> Any:  # noqa: ANN401
        """Reserve actions for this account at 0.0005 USDC each, paid from its perps balance."""
        return await self._native_private(
            "reserve_request_weight", self._native_params(weight=weight, expiresAfter=expires_after)
        )

    async def set_agent_abstraction(
        self,
        abstraction: str,
        *,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Set account mode using agent signing: i=disabled, u=unified, p=portfolio margin."""
        return await self._native_private(
            "set_agent_abstraction",
            self._native_params(
                abstraction=abstraction, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def set_user_abstraction(
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
        return await self._native_private(
            "set_user_abstraction",
            self._native_params(
                user=user,
                abstraction=abstraction,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def transfer_vault_usd(
        self,
        *,
        target_vault: str | None = None,
        vault_address: str | None = None,
        is_deposit: bool,
        usd: int,
        nonce: int | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Transfer raw USD units to/from target_vault (1 USD = 1,000,000 units).

        vault_address is a compatibility alias for target_vault, not a signing vault.
        """
        if (target_vault is None) == (vault_address is None):
            raise ValueError("provide exactly one of target_vault or vault_address")
        return await self._native_private(
            "transfer_vault_usd",
            self._native_params(
                targetVault=target_vault if target_vault is not None else vault_address,
                isDeposit=is_deposit,
                usd=usd,
                nonce=nonce,
                expiresAfter=expires_after,
            ),
        )

    async def enable_agent_dex_abstraction(
        self, *, nonce: int | None = None, expires_after: int | None = None
    ) -> Any:  # noqa: ANN401
        """Enable DEX abstraction for this agent."""
        return await self._native_private(
            "enable_agent_dex_abstraction",
            self._native_params(nonce=nonce, expiresAfter=expires_after),
        )

    async def transfer_hip3_liquidator(
        self,
        *,
        dex: str,
        ntl: int,
        is_deposit: bool,
        nonce: int | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """hip3LiquidatorTransfer. Amounts use the integer units defined by Hyperliquid."""
        return await self._native_private(
            "transfer_hip3_liquidator",
            self._native_params(
                dex=dex, ntl=ntl, isDeposit=is_deposit, nonce=nonce, expiresAfter=expires_after
            ),
        )

    async def deposit_staking_signed(
        self, *, wei: int, nonce: int, signature: dict[str, Any], signature_chain_id: str
    ) -> Any:  # noqa: ANN401
        """
        cDeposit. Supply the documented wallet EIP-712 signature; nonce and chain ID are
        forwarded unchanged.
        """
        return await self._native_private(
            "deposit_staking_signed",
            self._native_params(
                wei=wei,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_staking_signed(
        self, *, wei: int, nonce: int, signature: dict[str, Any], signature_chain_id: str
    ) -> Any:  # noqa: ANN401
        """
        cWithdraw. Supply the documented wallet EIP-712 signature; nonce and chain ID are
        forwarded unchanged.
        """
        return await self._native_private(
            "withdraw_staking_signed",
            self._native_params(
                wei=wei,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    async def delegate_tokens_signed(
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
        return await self._native_private(
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

    async def set_user_dex_abstraction_signed(
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
        return await self._native_private(
            "set_user_dex_abstraction_signed",
            self._native_params(
                user=user,
                enabled=enabled,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
            ),
        )

    async def create_sub_account(
        self, *, account_name: str, nonce: int | None = None, expires_after: int | None = None
    ) -> Any:  # noqa: ANN401
        """createSubAccount within the authenticated master/subaccount family."""
        return await self._native_private(
            "create_sub_account",
            self._native_params(name=account_name, nonce=nonce, expiresAfter=expires_after),
        )

    async def transfer_sub_account_usd(
        self,
        *,
        sub_account_user: str,
        is_deposit: bool,
        usd: int,
        nonce: int | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        subAccountTransfer within the authenticated master/subaccount family.

        usd uses raw integer units: 1 USD = 1,000,000 units.
        """
        return await self._native_private(
            "transfer_sub_account_usd",
            self._native_params(
                subAccountUser=sub_account_user,
                isDeposit=is_deposit,
                usd=usd,
                nonce=nonce,
                expiresAfter=expires_after,
            ),
        )

    async def transfer_sub_account_spot(
        self,
        *,
        sub_account_user: str,
        is_deposit: bool,
        token: str,
        amount: str,
        nonce: int | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """subAccountSpotTransfer within the authenticated master/subaccount family."""
        return await self._native_private(
            "transfer_sub_account_spot",
            self._native_params(
                subAccountUser=sub_account_user,
                isDeposit=is_deposit,
                token=token,
                amount=amount,
                nonce=nonce,
                expiresAfter=expires_after,
            ),
        )

    async def approve_agent_signed(
        self,
        *,
        agent_address: str,
        nonce: int,
        signature: dict[str, Any],
        signature_chain_id: str,
        agent_name: str | None = None,
    ) -> Any:  # noqa: ANN401
        """Submit a caller-supplied wallet EIP-712 agent approval signature."""
        return await self._native_private(
            "approve_agent_signed",
            self._native_params(
                agentAddress=agent_address,
                nonce=nonce,
                signature=json.dumps(signature, separators=(",", ":"), allow_nan=False),
                signatureChainId=signature_chain_id,
                agentName=agent_name,
            ),
        )

    async def borrow_lend_signed(
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
        return await self._native_private(
            "borrow_lend_signed",
            self._native_params(
                action=action,
                nonce=nonce,
                signature=signature,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
            ),
        )

    async def send_asset_signed(
        self,
        *,
        destination: str,
        source_dex: str,
        destination_dex: str,
        token: str,
        amount: str,
        from_sub_account: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit sendAsset with a caller-provided wallet EIP-712 signature.

        The amount and signed strings are preserved exactly. Empty DEX names denote the default
        perpetual DEX.
        API withdrawals have no second confirmation; they execute on submit.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#send-asset
        """
        return await self._native_private(
            "send_asset_signed",
            self._native_params(
                destination=destination,
                sourceDex=source_dex,
                destinationDex=destination_dex,
                token=token,
                amount=amount,
                fromSubAccount=from_sub_account,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def send_usd_signed(
        self,
        *,
        destination: str,
        amount: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit usdSend with a caller-provided wallet EIP-712 signature.

        The amount and signed strings are preserved exactly. Empty DEX names denote the default
        perpetual DEX.
        API withdrawals have no second confirmation; they execute on submit.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#core-usdc-transfer
        """
        return await self._native_private(
            "send_usd_signed",
            self._native_params(
                destination=destination,
                amount=amount,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def send_spot_signed(
        self,
        *,
        destination: str,
        token: str,
        amount: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotSend with a caller-provided wallet EIP-712 signature.

        The amount and signed strings are preserved exactly. Empty DEX names denote the default
        perpetual DEX.
        API withdrawals have no second confirmation; they execute on submit.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#core-spot-transfer
        """
        return await self._native_private(
            "send_spot_signed",
            self._native_params(
                destination=destination,
                token=token,
                amount=amount,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_from_bridge_signed(
        self,
        *,
        destination: str,
        amount: str,
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit withdraw3 with a caller-provided wallet EIP-712 signature.

        The amount and signed strings are preserved exactly. Empty DEX names denote the default
        perpetual DEX.
        API withdrawals have no second confirmation; they execute on submit.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#initiate-a-withdrawal-request
        """
        return await self._native_private(
            "withdraw_from_bridge_signed",
            self._native_params(
                destination=destination,
                amount=amount,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def approve_builder_fee_signed(
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
        return await self._native_private(
            "approve_builder_fee_signed",
            self._native_params(
                builder=builder,
                maxFeeRate=max_fee_rate,
                nonce=nonce,
                signature=signature,
                signatureChainId=signature_chain_id,
            ),
        )

    async def send_to_evm_with_data_signed(
        self,
        *,
        action: dict[str, Any],
        nonce: int,
        signature: dict[str, str | int],
        signature_chain_id: str,
    ) -> Any:  # noqa: ANN401
        """
        Submit sendToEvmWithData with a caller-provided wallet EIP-712 signature.

        Supply the complete signed action. The official table calls data bytes without defining its
        JSON encoding; data is forwarded unchanged. Not verified live.
        API withdrawals have no second confirmation; they execute on submit.
        https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#send-to-evm-with-data
        """
        return await self._native_private(
            "send_to_evm_with_data_signed",
            self._native_params(
                action=action, nonce=nonce, signature=signature, signatureChainId=signature_chain_id
            ),
        )
