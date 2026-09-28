"""Generated binance fiat HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedFiatHTTP(MarketHTTP, TradeHTTP):
    """Fiat API methods."""

    def fiat_deposit(
        self,
        *,
        currency: str,
        api_payment_method: str,
        amount: str,
        recv_window: int | None = None,
        ext: dict[str, Any] | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Deposit (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#deposit
        """
        return self._native_private(
            "fiat_deposit",
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
                        "recvWindow": recv_window,
                        "ext": ext,
                    }
                ).items()
                if value is not None
            ],
        )

    def get_fiat_payments_history(
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
        Get Fiat Payments History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#get-fiat-payments-history
        """
        return self._native_private(
            "get_fiat_payments_history",
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

    def get_order_detail(self, *, order_no: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Order Detail (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-fiat/api/rest-api/~#get-order-detail
        """
        return self._native_private(
            "get_order_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"orderNo": order_no, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )
