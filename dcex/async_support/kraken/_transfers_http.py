"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    async def wallet_transfer_to_futures(
        self,
        asset: str,
        amount: str,
        from_: str = "Spot Wallet",
        to: str = "Futures Wallet",
    ) -> dict[str, Any]:
        """Transfer funds from Kraken spot wallet to Futures wallet."""
        return await self._native_private(
            "wallet_transfer_to_futures",
            self._native_params(asset=asset, amount=amount, from_=from_, to=to),
        )

    async def futures_wallet_transfer(
        self,
        amount: str,
        fromAccount: str,
        toAccount: str,
        unit: str,
    ) -> dict[str, Any]:
        """Transfer funds between Kraken Futures cash and margin accounts."""
        return await self._native_private(
            "futures_wallet_transfer",
            self._native_params(
                amount=amount,
                fromAccount=fromAccount,
                toAccount=toAccount,
                unit=unit,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    async def transfer_spot_sub_account(
        self,
        *,
        asset: str,
        amount: str,
        from_account: str,
        to_account: str,
        asset_class: str | None = None,
    ) -> dict[str, Any]:
        """

        POST /0/private/AccountTransfer. Master account API key and Kraken subaccount
        eligibility are required.

        Source: https://docs.kraken.com/api-reference/subaccounts/account-transfer

        """
        return await self._native_private(
            "transfer_spot_sub_account",
            self._native_params(
                asset=asset,
                amount=amount,
                to=to_account,
                asset_class=asset_class,
                **{"from": from_account},
            ),
        )

    async def transfer_futures_sub_account(
        self,
        *,
        from_user: str,
        to_user: str,
        from_account: str,
        to_account: str,
        unit: str,
        amount: str,
    ) -> dict[str, Any]:
        """
        POST /derivatives/api/v3/transfer/subaccount.

        Source: https://docs.kraken.com/api-reference/transfers/initiate-sub-account-transfer
        """
        return await self._native_private(
            "transfer_futures_sub_account",
            self._native_params(
                fromUser=from_user,
                toUser=to_user,
                fromAccount=from_account,
                toAccount=to_account,
                unit=unit,
                amount=amount,
            ),
        )
