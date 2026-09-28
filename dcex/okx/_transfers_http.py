"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class AssetHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from AssetHTTP."""

    def funds_transfer(
        self,
        ccy: str,
        amt: str,
        from_account: str,
        to_account: str,
        type: str | None = None,
        subAcct: str | None = None,
        loanTrans: bool | str | None = None,
        omitPosRisk: bool | str | None = None,
        clientId: str | None = None,
    ) -> dict[str, Any]:
        """
        Transfer funds between accounts.

        Args:
            ccy: Currency code
            amt: Transfer amount
            from_account: Source account ("FUND" or "TRADING")
            to_account: Destination account ("FUND" or "TRADING")
            type: Transfer type
            subAcct: Sub-account name
            loanTrans: Loan transfer flag

        Returns:
            Dictionary containing transfer result.
        """
        return self._native_private(
            "funds_transfer",
            self._native_params(
                ccy=ccy,
                amt=amt,
                from_account=from_account,
                to_account=to_account,
                type=type,
                subAcct=subAcct,
                loanTrans=loanTrans,
                omitPosRisk=omitPosRisk,
                clientId=clientId,
            ),
        )

    def get_transfer_state(
        self,
        transId: str | None = None,
        clientId: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """
        Get transfer state information.

        Args:
            transId: Transfer ID
            clientId: Client ID
            type: Transfer type

        Returns:
            Dictionary containing transfer state information.
        """
        return self._native_private(
            "get_transfer_state",
            self._native_params(transId=transId, clientId=clientId, type=type),
        )


class SubaccountHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from SubaccountHTTP."""

    def transfer_between_subaccounts(
        self,
        ccy: str,
        amt: str,
        from_account: str,
        to_account: str,
        fromSubAccount: str,
        toSubAccount: str,
        *,
        loanTrans: bool | str | None = None,
        omitPosRisk: bool | str | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "transfer_between_subaccounts",
            self._native_params(
                ccy=ccy,
                amt=amt,
                from_account=from_account,
                to_account=to_account,
                fromSubAccount=fromSubAccount,
                toSubAccount=toSubAccount,
                loanTrans=loanTrans,
                omitPosRisk=omitPosRisk,
            ),
        )


class TradeHTTPTransfersHTTP(HTTPManager):
    """Transfers methods moved from TradeHTTP."""

    def set_sub_account_transfer_out(
        self, *, sub_acct: str, can_trans_out: bool | None = None
    ) -> dict[str, Any]:
        """
        POST /api/v5/users/subaccount/set-transfer-out. Use native instrument IDs.

        Source: https://www.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out
        """
        return self._native_private(
            "set_sub_account_transfer_out",
            self._native_params(subAcct=sub_acct, canTransOut=can_trans_out),
        )
