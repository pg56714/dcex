"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AssetHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AssetHTTP."""

    async def funds_transfer(
        self,
        ccy: str,
        amt: str,
        from_: str,
        to: str,
        type: str | None = None,
        subAcct: str | None = None,
        loanTrans: bool | str | None = None,
        omitPosRisk: bool | str | None = None,
        clientId: str | None = None,
    ) -> dict[str, Any]:
        """
        Transfer funds between accounts.

        Args:
            ccy: Currency code for the transfer.
            amt: Amount to transfer.
            from_: Source account ID, 6 (funding) or 18 (trading).
            to: Destination account ID, 6 (funding) or 18 (trading).
            type: Transfer type (optional).
            subAcct: Sub-account name (optional).
            loanTrans: Loan transfer flag (optional).

        Returns:
            Dict containing transfer result from OKX API.
        """
        return await self._native_private(
            "funds_transfer",
            self._native_params(
                ccy=ccy,
                amt=amt,
                from_=from_,
                to=to,
                type=type,
                subAcct=subAcct,
                loanTrans=loanTrans,
                omitPosRisk=omitPosRisk,
                clientId=clientId,
            ),
        )

    async def get_transfer_state(
        self,
        transId: str | None = None,
        clientId: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get transfer state information.

        Args:
            transId: Transfer ID to query (optional).
            clientId: Client ID to query (optional).
            type: Transfer type to query (optional).

        Returns:
            Dict containing transfer state information from OKX API.
        """
        return await self._native_private(
            "get_transfer_state",
            self._native_params(transId=transId, clientId=clientId, type=type),
        )


class SubaccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from SubaccountHTTP."""

    async def transfer_between_subaccounts(
        self,
        ccy: str,
        amt: str,
        from_: str,
        to: str,
        fromSubAccount: str,
        toSubAccount: str,
        *,
        loanTrans: bool | str | None = None,
        omitPosRisk: bool | str | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "transfer_between_subaccounts",
            self._native_params(
                ccy=ccy,
                amt=amt,
                from_=from_,
                to=to,
                fromSubAccount=fromSubAccount,
                toSubAccount=toSubAccount,
                loanTrans=loanTrans,
                omitPosRisk=omitPosRisk,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    async def set_sub_account_transfer_out(
        self, *, sub_acct: str, can_trans_out: bool | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/users/subaccount/set-transfer-out. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out
        """
        return await self._native_private(
            "set_sub_account_transfer_out",
            self._native_params(subAcct=sub_acct, canTransOut=can_trans_out),
        )
