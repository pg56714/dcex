"""Generated hyperliquid deployment HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._trade_http import TradeHTTP


class GeneratedDeploymentHTTP(TradeHTTP):
    """Deployment API methods."""

    def perp_deploy_register_asset2(
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
        return self._native_private(
            "perp_deploy_register_asset2",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_register_asset(
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
        return self._native_private(
            "perp_deploy_register_asset",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_oracle(
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
        return self._native_private(
            "perp_deploy_set_oracle",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_funding_multipliers(
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
        return self._native_private(
            "perp_deploy_set_funding_multipliers",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_funding_interest_rates(
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
        return self._native_private(
            "perp_deploy_set_funding_interest_rates",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_funding_clamps(
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
        return self._native_private(
            "perp_deploy_set_funding_clamps",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_halt_trading(
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
        return self._native_private(
            "perp_deploy_halt_trading",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_insert_margin_table(
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
        return self._native_private(
            "perp_deploy_insert_margin_table",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_margin_table_ids(
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
        return self._native_private(
            "perp_deploy_set_margin_table_ids",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_fee_recipient(
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
        return self._native_private(
            "perp_deploy_set_fee_recipient",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_open_interest_caps(
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
        return self._native_private(
            "perp_deploy_set_open_interest_caps",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_sub_deployers(
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
        return self._native_private(
            "perp_deploy_set_sub_deployers",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_margin_modes(
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
        return self._native_private(
            "perp_deploy_set_margin_modes",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_deployer_fees(
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
        return self._native_private(
            "perp_deploy_set_deployer_fees",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_set_perp_annotation(
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
        return self._native_private(
            "perp_deploy_set_perp_annotation",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def perp_deploy_disable_dex(
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
        return self._native_private(
            "perp_deploy_disable_dex",
            self._native_params(
                action=action,
                nonce=nonce,
                vaultAddress=vault_address,
                expiresAfter=expires_after,
                confirm=confirm,
            ),
        )

    def perp_deploy_star(
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
        return self._native_private(
            "perp_deploy_star",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_register_token2(
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
        return self._native_private(
            "spot_deploy_register_token2",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_user_genesis(
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
        return self._native_private(
            "spot_deploy_user_genesis",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_genesis(
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
        return self._native_private(
            "spot_deploy_genesis",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_register_spot(
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
        return self._native_private(
            "spot_deploy_register_spot",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_register_hyperliquidity(
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
        return self._native_private(
            "spot_deploy_register_hyperliquidity",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_set_deployer_trading_fee_share(
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
        return self._native_private(
            "spot_deploy_set_deployer_trading_fee_share",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_enable_quote_token(
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
        return self._native_private(
            "spot_deploy_enable_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_enable_aligned_quote_token(
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
        return self._native_private(
            "spot_deploy_enable_aligned_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_disable_quote_token(
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
        return self._native_private(
            "spot_deploy_disable_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_disable_aligned_quote_token(
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
        return self._native_private(
            "spot_deploy_disable_aligned_quote_token",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_set_token_annotation(
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
        return self._native_private(
            "spot_deploy_set_token_annotation",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def spot_deploy_set_deployer_label(
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
        return self._native_private(
            "spot_deploy_set_deployer_label",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def activate_outcome_deployer(
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
        return self._native_private(
            "activate_outcome_deployer",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )

    def outcome_deploy(
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
        return self._native_private(
            "outcome_deploy",
            self._native_params(
                action=action, nonce=nonce, vaultAddress=vault_address, expiresAfter=expires_after
            ),
        )
