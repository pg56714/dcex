"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

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

    async def transfer_vault_usd(
        self,
        *,
        target_vault: str,
        is_deposit: bool,
        usd: int,
        nonce: int | None = None,
        expires_after: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Transfer raw USD units to/from target_vault (1 USD = 1,000,000 units).

        """
        return await self._native_private(
            "transfer_vault_usd",
            self._native_params(
                targetVault=target_vault,
                isDeposit=is_deposit,
                usd=usd,
                nonce=nonce,
                expiresAfter=expires_after,
            ),
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
