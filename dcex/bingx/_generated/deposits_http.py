"""Generated bingx deposits HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedDepositsHTTP(MarketHTTP):
    """Deposits API methods."""

    def get_wallets_v1_capital_deposit_query_sub_address(
        self,
        *,
        coin: str,
        sub_uid: int,
        network: str,
        wallet_type: int,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Sub-account Deposit Address.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Account%20and%20Wallet/Sub-account%20Management/Query%20Sub-account%20Deposit%20Address
        """
        return self._native_private(
            "get_wallets_v1_capital_deposit_query_sub_address",
            self._native_params(
                **{
                    "coin": coin,
                    "subUid": sub_uid,
                    "network": network,
                    "walletType": wallet_type,
                    "recvWindow": recv_window,
                }
            ),
        )
