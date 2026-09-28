"""Generated hyperliquid administration HTTP methods."""

from typing import Any

from dcex._operation_guards import require_confirmation

from .._trade_http import TradeHTTP


class GeneratedAdministrationHTTP(TradeHTTP):
    """Administration API methods."""

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
