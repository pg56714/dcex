from typing import Any

from ._http_manager import HTTPManager
from ._transfers_http import SubaccountHTTPTransfersHTTP


class SubaccountHTTP(SubaccountHTTPTransfersHTTP, HTTPManager):
    """OKX master-account operations for sub-account monitoring and transfers."""

    def get_subaccount_list(
        self,
        *,
        enable: bool | str | None = None,
        subAcct: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
            "get_subaccount_list",
            self._native_params(
                enable=enable,
                subAcct=subAcct,
                after=after,
                before=before,
                limit=limit,
            ),
        )

    def get_subaccount_trading_balance(self, subAcct: str) -> dict[str, Any]:
        return self._native_private(
            "get_subaccount_trading_balance", self._native_params(subAcct=subAcct)
        )

    def get_subaccount_funding_balance(
        self, subAcct: str, ccy: list[str] | None = None
    ) -> dict[str, Any]:
        return self._native_private(
            "get_subaccount_funding_balance",
            self._native_params(subAcct=subAcct, ccy=ccy),
        )

    def get_subaccount_bills(
        self,
        subAcct: str,
        *,
        ccy: str | None = None,
        type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        return self._native_private(
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

    def get_entrusted_subaccount_list(self, subAcct: str | None = None) -> dict[str, Any]:
        return self._native_private(
            "get_entrusted_subaccount_list", self._native_params(subAcct=subAcct)
        )

    def get_subaccount_interest_limits(
        self, subAcct: str, *, ccy: str | None = None
    ) -> dict[str, Any]:
        """
        Get a sub-account's borrow interest and limit.

        Deprecated: ``GET /api/v5/account/subaccount/interest-limits`` is no longer
        listed in the OKX v5 API docs. Kept for backward compatibility and may be
        rejected by OKX.
        """
        return self._native_private(
            "get_subaccount_interest_limits",
            self._native_params(subAcct=subAcct, ccy=ccy),
        )
