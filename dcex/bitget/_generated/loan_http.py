"""Generated bitget loan HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedLoanHTTP(MarketHTTP):
    """Loan API methods."""

    def classic_common_apidata_margin_iso_borrow_ratio(
        self, *, symbol: str, period: str | None = None
    ) -> dict[str, Any]:
        """
        Get Isolated margin borrowing ratio Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-isolated-margin-borrowing-ratio-data
        """
        return self._native_public(
            "classic_common_apidata_margin_iso_borrow_ratio",
            self._native_params(**{"symbol": symbol, "period": period}),
        )

    def classic_common_apidata_margin_loan_growth(
        self, *, symbol: str, period: str | None = None, coin: str | None = None
    ) -> dict[str, Any]:
        """
        Get Margin loan growth rate Data.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-apidata/classic-common-apidata#get-margin-loan-growth-rate-data
        """
        return self._native_public(
            "classic_common_apidata_margin_loan_growth",
            self._native_params(**{"symbol": symbol, "period": period, "coin": coin}),
        )
