"""BitMEX private account HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class AccountHTTP(HTTPManager):
    """HTTP client for BitMEX account APIs."""

    def get_futures_fee_rates(self) -> list[dict[str, Any]]:
        """Retrieve current BitMEX Futures maker and taker fee rates."""
        return self._native_private("get_futures_fee_rates", [])

    def get_wallet_summary(
        self,
        currency: str = "all",
        start_time: str | None = None,
        end_time: str | None = None,
        target_account_id: int | None = None,
        target_account_ids: list[str] | str | None = None,
    ) -> dict[str, Any]:
        """Get BitMEX wallet summary information."""
        params = self._native_params(
            currency=currency,
            startTime=start_time,
            endTime=end_time,
            targetAccountId=target_account_id,
        )
        if isinstance(target_account_ids, list):
            params.append(("targetAccountIds[]", self._native_params(ids=target_account_ids)[0][1]))
        elif isinstance(target_account_ids, str):
            params.append(("targetAccountIds", target_account_ids))
        return self._native_private("get_wallet_summary", params)
