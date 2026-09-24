from typing import Any

from ._http_manager import HTTPManager


class SubaccountHTTP(HTTPManager):
    """Asynchronous OKX sub-account monitoring and transfer operations."""

    async def get_subaccount_list(
        self,
        *,
        enable: bool | str | None = None,
        subAcct: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_subaccount_list",
            self._native_params(
                enable=enable,
                subAcct=subAcct,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def get_subaccount_trading_balance(self, subAcct: str) -> dict[str, Any]:
        return await self._native_private(
            "get_subaccount_trading_balance", self._native_params(subAcct=subAcct)
        )

    async def get_subaccount_funding_balance(
        self, subAcct: str, ccy: list[str] | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_subaccount_funding_balance",
            self._native_params(subAcct=subAcct, ccy=ccy),
        )

    async def get_subaccount_bills(
        self,
        subAcct: str,
        *,
        ccy: str | None = None,
        type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_subaccount_bills",
            self._native_params(
                subAcct=subAcct,
                ccy=ccy,
                type=type,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    async def transfer_between_subaccounts(
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
        return await self._native_private(
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

    async def get_entrusted_subaccount_list(self, subAcct: str | None = None) -> dict[str, Any]:
        return await self._native_private(
            "get_entrusted_subaccount_list", self._native_params(subAcct=subAcct)
        )

    async def get_subaccount_interest_limits(
        self, subAcct: str, *, ccy: str | None = None
    ) -> dict[str, Any]:
        return await self._native_private(
            "get_subaccount_interest_limits",
            self._native_params(subAcct=subAcct, ccy=ccy),
        )
