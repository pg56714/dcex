"""Generated binance gift card HTTP methods."""

from json import dumps
from typing import Any

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedGiftCardHTTP(MarketHTTP, TradeHTTP):
    """Gift card API methods."""

    def create_a_dual_token_gift_card(
        self,
        *,
        base_token: str,
        face_token: str,
        base_token_amount: str,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Create a dual-token gift card (fixed value, discount feature) (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#create-adual-token-gift-card
        """
        return self._native_private(
            "create_a_dual_token_gift_card",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "baseToken": base_token,
                    "faceToken": face_token,
                    "baseTokenAmount": base_token_amount,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def create_a_single_token_gift_card(
        self, *, token: str, amount: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Create a single-token gift card (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#create-asingle-token-gift-card
        """
        return self._native_private(
            "create_a_single_token_gift_card",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "token": token,
                    "amount": amount,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def fetch_rsa_public_key(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fetch RSA Public Key (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#fetch-rsa-public-key
        """
        return self._native_private(
            "fetch_rsa_public_key",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"recvWindow": recv_window}.items()
                if value is not None
            ],
        )

    def fetch_token_limit(self, *, base_token: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Fetch Token Limit (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#fetch-token-limit
        """
        return self._native_private(
            "fetch_token_limit",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"baseToken": base_token, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )

    def redeem_a_binance_gift_card(
        self, *, code: str, external_uid: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Redeem a Binance Gift Card (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#redeem-abinance-gift-card
        """
        return self._native_private(
            "redeem_a_binance_gift_card",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "code": code,
                    "externalUid": external_uid,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def verify_binance_gift_card_by_gift_card_number(
        self, *, reference_no: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Verify Binance Gift Card by Gift Card Number (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-gift-card/api/rest-api/market-data#verify-binance-gift-card-by-gift-card-number
        """
        return self._native_private(
            "verify_binance_gift_card_by_gift_card_number",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"referenceNo": reference_no, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )
