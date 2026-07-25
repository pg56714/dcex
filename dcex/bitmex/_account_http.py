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
        currency: str = "XBt",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get BitMEX wallet summary information."""
        params = self._native_params(
            currency=currency,
            startTime=start_time,
            endTime=end_time,
        )
        return self._native_private("get_wallet_summary", params)
