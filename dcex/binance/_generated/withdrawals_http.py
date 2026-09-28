"""Generated binance withdrawals HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedWithdrawalsHTTP(MarketHTTP, TradeHTTP):
    """Withdrawals API methods."""

    def fiat_withdraw(
        self,
        *,
        currency: str,
        api_payment_method: str,
        amount: int,
        account_info: dict[str, Any],
        recv_window: int | None = None,
        ext: dict[str, Any] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Fiat Withdraw (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#fiat-withdraw

        API withdrawals have no second confirmation; they execute on submit.
        """
        return self._native_private(
            "fiat_withdraw",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "currency": currency,
                        "apiPaymentMethod": api_payment_method,
                        "amount": amount,
                        "accountInfo": account_info,
                        "recvWindow": recv_window,
                        "ext": ext,
                    }
                ).items()
                if value is not None
            ],
        )

    def get_fiat_deposit_withdraw_history(
        self,
        *,
        transaction_type: str,
        begin_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        rows: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Fiat Deposit/Withdraw History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#get-fiat-deposit-withdraw-history
        """
        return self._native_private(
            "get_fiat_deposit_withdraw_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "transactionType": transaction_type,
                        "beginTime": begin_time,
                        "endTime": end_time,
                        "page": page,
                        "rows": rows,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    def prediction_apply_mm_withdraw(
        self,
        *,
        coin: str,
        network: str,
        amount: str,
        withdraw_order_id: str | None = None,
        wallet_type: str | None = None,
        name: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Apply MM Withdraw (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#apply-mm-withdraw

        API withdrawals have no second confirmation; they execute on submit.
        """
        return self._native_private(
            "prediction_apply_mm_withdraw",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "coin": coin,
                        "network": network,
                        "amount": amount,
                        "withdrawOrderId": withdraw_order_id,
                        "walletType": wallet_type,
                        "name": name,
                    }
                ).items()
                if value is not None
            ],
        )
