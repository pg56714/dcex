"""Named HIP deployer and administrative action methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from ._trade_http import TradeHTTP


class InventoryHTTP(TradeHTTP):
    """Methods preserve action field order and caller-signed envelopes."""

    async def top_up_isolated_only_margin(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit topUpIsolatedOnlyMargin.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#update-isolated-margin
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "top_up_isolated_only_margin",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def user_outcome(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit userOutcome.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#split-outcome
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "user_outcome",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def validator_l1_stream(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit validatorL1Stream.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#validator-vote-on-risk-free-rate-for-aligned-quote-asset
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "validator_l1_stream",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def authorize_aqav2_role(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit authorizeAqav2Role.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#authorize-aqav2-role
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "authorize_aqav2_role",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def claim_rewards(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit claimRewards.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint#claim-rewards
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "claim_rewards",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_register_asset2(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/registerAsset2.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_register_asset2",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_register_asset(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/registerAsset.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_register_asset",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_oracle(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setOracle.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_oracle",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_funding_multipliers(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setFundingMultipliers.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_funding_multipliers",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_funding_interest_rates(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setFundingInterestRates.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_funding_interest_rates",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_funding_clamps(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setFundingClamps.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_funding_clamps",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_halt_trading(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/haltTrading.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_halt_trading",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_insert_margin_table(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/insertMarginTable.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_insert_margin_table",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_margin_table_ids(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setMarginTableIds.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_margin_table_ids",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_fee_recipient(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setFeeRecipient.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_fee_recipient",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_open_interest_caps(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setOpenInterestCaps.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_open_interest_caps",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_sub_deployers(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setSubDeployers.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_sub_deployers",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_margin_modes(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setMarginModes.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_margin_modes",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_deployer_fees(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setDeployerFees.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_deployer_fees",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_set_perp_annotation(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/setPerpAnnotation.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "perp_deploy_set_perp_annotation",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def perp_deploy_disable_dex(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
        confirm: bool = False,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/disableDex.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        This irreversible account operation requires confirm=True.
        """
        require_confirmation(confirm)
        return await self._native_private(
            "perp_deploy_disable_dex",
            self._native_params(
                action=action,
                nonce=nonce,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
                confirm=confirm,
            ),
        )

    async def perp_deploy_star(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit perpDeploy/star.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        This action is documented for testnet only.
        """
        return await self._native_private(
            "perp_deploy_star",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_register_token2(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/registerToken2.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_register_token2",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_user_genesis(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/userGenesis.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_user_genesis",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_genesis(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/genesis.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_genesis",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_register_spot(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/registerSpot.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_register_spot",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_register_hyperliquidity(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/registerHyperliquidity.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_register_hyperliquidity",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_set_deployer_trading_fee_share(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/setDeployerTradingFeeShare.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_set_deployer_trading_fee_share",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_enable_quote_token(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/enableQuoteToken.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_enable_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_enable_aligned_quote_token(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/enableAlignedQuoteToken.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_enable_aligned_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_disable_quote_token(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/disableQuoteToken.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_disable_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_disable_aligned_quote_token(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/disableAlignedQuoteToken.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_disable_aligned_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_set_token_annotation(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/setTokenAnnotation.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_set_token_annotation",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def spot_deploy_set_deployer_label(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit spotDeploy/setDeployerLabel.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "spot_deploy_set_deployer_label",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def activate_outcome_deployer(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit activateOutcomeDeployer.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions#action-format
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        This action is documented for testnet only.
        """
        return await self._native_private(
            "activate_outcome_deployer",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def outcome_deploy(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit outcomeDeploy.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions#action-format
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        This action is documented for testnet only.
        """
        return await self._native_private(
            "outcome_deploy",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def get_outcome_templates(self) -> Any:  # noqa: ANN401
        """
        Query outcomeTemplates.

        Source: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions#action-format
        """
        return await self._native_public("get_outcome_templates", self._native_params())

    async def get_user_to_multi_sig_signers(self, *, user: str) -> Any:  # noqa: ANN401
        """
        Query userToMultiSigSigners.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/info.py#L626
        """
        return await self._native_public(
            "get_user_to_multi_sig_signers", self._native_params(user=user)
        )

    async def get_extra_agents(self, *, user: str) -> Any:  # noqa: ANN401
        """
        Query extraAgents.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/info.py#L763
        """
        return await self._native_public("get_extra_agents", self._native_params(user=user))

    async def set_referrer(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit setReferrer.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L437
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "set_referrer",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def convert_to_multi_sig_user_signed(
        self,
        *,
        action: dict[str, Any],
        nonce: int,
        signature: dict[str, str | int],
        vault_address: str | None = None,
        expires_after: int | None = None,
        confirm: bool = False,
    ) -> Any:  # noqa: ANN401
        """
        Submit convertToMultiSigUser.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L674
        Supply the complete documented action; field order is preserved.
        The signature must already cover the supplied action and envelope.
        Tuple lists must be sorted before submission, as required by the API.
        This irreversible account operation requires confirm=True.
        """
        require_confirmation(confirm)
        return await self._native_private(
            "convert_to_multi_sig_user_signed",
            self._native_params(
                action=action,
                nonce=nonce,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
                signature=signature,
                confirm=confirm,
            ),
        )

    async def c_signer_action(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit CSignerAction.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L984
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "c_signer_action",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def c_validator_action(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit CValidatorAction.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L1014
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "c_validator_action",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def multi_sig_signed(
        self,
        *,
        action: dict[str, Any],
        nonce: int,
        signature: dict[str, str | int],
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit multiSig.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L1103
        Supply the complete documented action; field order is preserved.
        The signature must already cover the supplied action and envelope.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "multi_sig_signed",
            self._native_params(
                action=action,
                nonce=nonce,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
                signature=signature,
            ),
        )

    async def evm_user_modify(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit evmUserModify.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L1130
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "evm_user_modify",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    async def gossip_priority_bid(
        self,
        *,
        action: dict[str, Any],
        nonce: int | None = None,
        vault_address: str | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit gossipPriorityBid.

        Source: https://github.com/hyperliquid-dex/hyperliquid-python-sdk/blob/2fdb18f9517675ea03695a0962bd19eece9c83f0/hyperliquid/exchange.py#L1225
        Supply the complete documented action; field order is preserved.
        The native client signs the action with its configured private key.
        Tuple lists must be sorted before submission, as required by the API.
        """
        return await self._native_private(
            "gossip_priority_bid",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )
