"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AccountHTTP."""

    def transfer_spot_futures(
        self,
        amount: str,
        asset: str,
        clientTranId: str,
        kindType: str,
        market: str = "spot",
    ) -> dict[str, Any] | list[Any]:
        """Transfer assets between the Aster spot and futures wallets."""
        return self._native_private(
            "transfer_spot_futures",
            self._native_params(
                amount=amount,
                asset=asset,
                clientTranId=clientTranId,
                kindType=kindType,
                market=market,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    def transfer_sub_account(
        self,
        to_account_address: str,
        asset: str,
        amount: str,
        kind_type: str,
        *,
        from_account_address: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Transfer within one master/sub-account family using the approved agent.

        Aster enforces account-family membership; external transfers are not supported.

        Not verified live: the official signature template includes both user and signer,
        while its parameter notes require only one. This method sends signer only.
        """
        return self._native_private(
            "transfer_sub_account",
            self._native_params(
                toAccountAddress=to_account_address,
                asset=asset,
                amount=amount,
                kindType=kind_type,
                fromAccountAddress=from_account_address,
            ),
        )

    def create_prediction_asset_wallet_transfer(
        self, *, amount: str, asset: str, client_tran_id: str, kind_type: str
    ) -> dict[str, Any] | list[Any]:
        """
        POST /api/v3/asset/wallet/transfer on the prediction host. Use native prediction
        symbols.
        """
        return self._native_private(
            "create_prediction_asset_wallet_transfer",
            self._native_params(
                amount=amount, asset=asset, clientTranId=client_tran_id, kindType=kind_type
            ),
        )
