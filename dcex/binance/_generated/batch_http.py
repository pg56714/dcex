"""Generated binance batch HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedBatchHTTP(MarketHTTP, TradeHTTP):
    """Batch API methods."""

    def prediction_batch_redeem(
        self,
        *,
        wallet_address: str,
        wallet_id: str,
        token_ids: list[Any],
        chain_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Batch Redeem (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/redeem#batch-redeem
        """
        return self._native_private(
            "prediction_batch_redeem",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "walletId": wallet_id,
                        "tokenIds": token_ids,
                        "chainId": chain_id,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_batch_cancel_orders(
        self, *, wallet_address: str, wallet_id: str, cancel_info_list: list[Any] | None = None
    ) -> Any:  # noqa: ANN401
        """
        Batch Cancel Orders (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#batch-cancel-orders
        """
        return self._native_private(
            "prediction_batch_cancel_orders",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletAddress": wallet_address,
                        "walletId": wallet_id,
                        "cancelInfoList": cancel_info_list,
                    }
                ).items()
                if value is not None
            ],
        )
