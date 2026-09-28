"""Generated binance transfers HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedTransfersHTTP(MarketHTTP, TradeHTTP):
    """Transfers API methods."""

    async def prediction_create_inbound_transfer(
        self,
        *,
        wallet_id: str,
        wallet_address: str,
        from_token_amount: str,
        account_type: str,
        from_token: str | None = None,
        to_token: str | None = None,
        chain_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Create Inbound Transfer (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#create-inbound-transfer
        """
        return await self._native_private(
            "prediction_create_inbound_transfer",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletId": wallet_id,
                        "walletAddress": wallet_address,
                        "fromTokenAmount": from_token_amount,
                        "accountType": account_type,
                        "fromToken": from_token,
                        "toToken": to_token,
                        "chainId": chain_id,
                    }
                ).items()
                if value is not None
            ],
        )

    async def prediction_create_outbound_transfer(
        self,
        *,
        wallet_id: str,
        wallet_address: str,
        from_token_amount: str,
        account_type: str,
        source_biz: str,
        from_token: str | None = None,
        to_token: str | None = None,
        chain_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Create Outbound Transfer (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#create-outbound-transfer
        """
        return await self._native_private(
            "prediction_create_outbound_transfer",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "walletId": wallet_id,
                        "walletAddress": wallet_address,
                        "fromTokenAmount": from_token_amount,
                        "accountType": account_type,
                        "sourceBiz": source_biz,
                        "fromToken": from_token,
                        "toToken": to_token,
                        "chainId": chain_id,
                    }
                ).items()
                if value is not None
            ],
        )

    async def prediction_query_transfer_list(
        self,
        *,
        wallet_address: str,
        start_date: str,
        end_date: str,
        token_symbol: str | None = None,
        direction: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Transfer List (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#query-transfer-list
        """
        return await self._native_private(
            "prediction_query_transfer_list",
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
                        "startDate": start_date,
                        "endDate": end_date,
                        "tokenSymbol": token_symbol,
                        "direction": direction,
                        "offset": offset,
                        "limit": limit,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def prediction_query_transfer_status(
        self, *, transfer_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Transfer Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#query-transfer-status
        """
        return await self._native_private(
            "prediction_query_transfer_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"transferId": transfer_id, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )
