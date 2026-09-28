"""Fund movement and batch endpoint mixins."""

import json
from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

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
