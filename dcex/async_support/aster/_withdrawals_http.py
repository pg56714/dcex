"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from MarketHTTP."""

    _native_public: Any

    _params: Any

    async def get_spot_withdraw_fee(
        self,
        chainId: str,
        asset: str,
    ) -> dict[str, Any] | list[Any]:
        """Estimate the public Aster withdrawal fee without creating a withdrawal."""
        return await self._native_public(
            "get_spot_withdraw_fee",
            self._params(chainId=chainId, asset=asset),
        )

    async def get_chain_withdraw_fee(self, *, chain_id: int, asset: str) -> Any:  # noqa: ANN401
        """Estimate the Aster Chain withdrawal fee for an asset and chain."""
        return await self._native_public(
            "get_chain_withdraw_fee", self._params(chainId=chain_id, asset=asset)
        )


class TradeHTTPWithdrawalsHTTP(HTTPManager):
    """Withdrawals methods moved from TradeHTTP."""

    async def withdraw_spot_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str,
        user_signature: str,
        signature_type: str | None = None,
        signature_chain_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized spot withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_spot_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
                signatureType=signature_type,
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_spot_solana_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str | None = None,
        user_signature: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized spot withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_spot_solana_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
            ),
        )

    async def withdraw_futures_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str,
        user_signature: str,
        signature_type: str | None = None,
        signature_chain_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized futures withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_futures_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
                signatureType=signature_type,
                signatureChainId=signature_chain_id,
            ),
        )

    async def withdraw_futures_solana_signed(
        self,
        *,
        chain_id: int,
        asset: str,
        amount: str,
        fee: str,
        receiver: str,
        user_nonce: str | None = None,
        user_signature: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Submit a wallet-authorized futures withdrawal.

        API withdrawals have no second confirmation; they execute on submit.
        user_nonce and user_signature belong to the wallet authorization and are preserved
        verbatim; the client adds a separate V3 agent nonce/signature.
        Source: https://github.com/asterdex/api-docs/blob/master/demo/aster-deposit-withdrawal.md
        """
        return await self._native_private(
            "withdraw_futures_solana_signed",
            self._native_params(
                chainId=chain_id,
                asset=asset,
                amount=amount,
                fee=fee,
                receiver=receiver,
                userNonce=user_nonce,
                userSignature=user_signature,
            ),
        )
