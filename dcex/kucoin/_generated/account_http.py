"""Generated kucoin account HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedAccountHTTP(TradeHTTP):
    """Account API methods."""

    def get_v1_accounts_account_id(self, *, account_id: str) -> Any:  # noqa: ANN401
        """
        Get Account Detail - Spot.

        Source: https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-account-detail-spot
        """
        return self._native_private(
            "get_v1_accounts_account_id", self._native_params(accountId=account_id)
        )
