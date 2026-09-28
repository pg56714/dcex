"""Additional Binance endpoints from the official SDK request tables."""

from json import dumps
from typing import Any

from ._market_http import MarketHTTP
from ._trade_http import TradeHTTP


class InventoryHTTP(MarketHTTP, TradeHTTP):
    """Alpha, fiat, mining, gift card, VIP loan and prediction endpoints."""

    def alpha_aggregated_trades(
        self,
        *,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Aggregated Trades.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#aggregated-trades
        """
        return self._native_public(
            "alpha_aggregated_trades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "symbol": symbol,
                    "fromId": from_id,
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                }.items()
                if value is not None
            ],
        )

    def alpha_full_depth(self, *, symbol: str, limit: str | None = None) -> Any:  # noqa: ANN401
        """
        Full Depth.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#full-depth
        """
        return self._native_public(
            "alpha_full_depth",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"symbol": symbol, "limit": limit}.items()
                if value is not None
            ],
        )

    def alpha_get_exchange_info(self) -> Any:  # noqa: ANN401
        """
        Get Exchange Info.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#get-exchange-info
        """
        return self._native_public(
            "alpha_get_exchange_info",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {}.items()
                if value is not None
            ],
        )

    def alpha_klines(
        self,
        *,
        symbol: str,
        interval: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Klines.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#klines
        """
        return self._native_public(
            "alpha_klines",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit,
                    "startTime": start_time,
                    "endTime": end_time,
                }.items()
                if value is not None
            ],
        )

    def alpha_ticker(self, *, symbol: str) -> Any:  # noqa: ANN401
        """
        Ticker.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#ticker
        """
        return self._native_public(
            "alpha_ticker",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"symbol": symbol}.items()
                if value is not None
            ],
        )

    def alpha_token_list(self) -> Any:  # noqa: ANN401
        """
        Token List.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/advanced-trading-alpha-trading/api/rest-api/market-data#token-list
        """
        return self._native_public(
            "alpha_token_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {}.items()
                if value is not None
            ],
        )

    def get_c2_c_trade_history(
        self,
        *,
        trade_type: str | None = None,
        start_timestamp: int | None = None,
        end_timestamp: int | None = None,
        page: int | None = None,
        rows: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get C2C Trade History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-c2-c/api/rest-api/~#get-c2-ctrade-history
        """
        return self._native_private(
            "get_c2_c_trade_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "tradeType": trade_type,
                    "startTimestamp": start_timestamp,
                    "endTimestamp": end_timestamp,
                    "page": page,
                    "rows": rows,
                }.items()
                if value is not None
            ],
        )

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
                for key, value in {
                    "currency": currency,
                    "apiPaymentMethod": api_payment_method,
                    "amount": amount,
                    "recvWindow": recv_window,
                    "ext": ext,
                }.items()
                if value is not None
            ],
        )

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
                for key, value in {
                    "currency": currency,
                    "apiPaymentMethod": api_payment_method,
                    "amount": amount,
                    "accountInfo": account_info,
                    "recvWindow": recv_window,
                    "ext": ext,
                }.items()
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
                for key, value in {
                    "transactionType": transaction_type,
                    "beginTime": begin_time,
                    "endTime": end_time,
                    "page": page,
                    "rows": rows,
                    "recvWindow": recv_window,
                }.items()
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
                for key, value in {
                    "transactionType": transaction_type,
                    "beginTime": begin_time,
                    "endTime": end_time,
                    "page": page,
                    "rows": rows,
                    "recvWindow": recv_window,
                }.items()
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
                for key, value in {"orderNo": order_no, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )

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

    def account_list(self, *, algo: str, user_name: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Account List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#account-list
        """
        return self._native_private(
            "account_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def acquiring_algorithm(self) -> Any:  # noqa: ANN401
        """
        Acquiring Algorithm (MARKET_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#acquiring-algorithm
        """
        return self._native_public(
            "acquiring_algorithm",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {}.items()
                if value is not None
            ],
        )

    def acquiring_coinname(self) -> Any:  # noqa: ANN401
        """
        Acquiring CoinName (MARKET_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#acquiring-coinname
        """
        return self._native_public(
            "acquiring_coinname",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {}.items()
                if value is not None
            ],
        )

    def cancel_hashrate_resale_configuration(
        self, *, config_id: int, user_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Cancel hashrate resale configuration (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#cancel-hashrate-resale-configuration
        """
        return self._native_private(
            "cancel_hashrate_resale_configuration",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "configId": config_id,
                    "userName": user_name,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def earnings_list(
        self,
        *,
        algo: str,
        user_name: str,
        coin: str | None = None,
        start_date: int | None = None,
        end_date: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Earnings List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#earnings-list
        """
        return self._native_private(
            "earnings_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "coin": coin,
                    "startDate": start_date,
                    "endDate": end_date,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def extra_bonus_list(
        self,
        *,
        algo: str,
        user_name: str,
        coin: str | None = None,
        start_date: int | None = None,
        end_date: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Extra Bonus List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#extra-bonus-list
        """
        return self._native_private(
            "extra_bonus_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "coin": coin,
                    "startDate": start_date,
                    "endDate": end_date,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def hashrate_resale_detail(
        self,
        *,
        config_id: int,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Hashrate Resale Detail (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#hashrate-resale-detail
        """
        return self._native_private(
            "hashrate_resale_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "configId": config_id,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def hashrate_resale_list(
        self,
        *,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Hashrate Resale List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#hashrate-resale-list
        """
        return self._native_private(
            "hashrate_resale_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def hashrate_resale_request(
        self,
        *,
        user_name: str,
        algo: str,
        end_date: int,
        start_date: int,
        to_pool_user: str,
        hash_rate: int,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Hashrate Resale Request (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#hashrate-resale-request
        """
        return self._native_private(
            "hashrate_resale_request",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "userName": user_name,
                    "algo": algo,
                    "endDate": end_date,
                    "startDate": start_date,
                    "toPoolUser": to_pool_user,
                    "hashRate": hash_rate,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def mining_account_earning(
        self,
        *,
        algo: str,
        start_date: int | None = None,
        end_date: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Mining Account Earning (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#mining-account-earning
        """
        return self._native_private(
            "mining_account_earning",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "startDate": start_date,
                    "endDate": end_date,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def request_for_detail_miner_list(
        self, *, algo: str, user_name: str, worker_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Request for Detail Miner List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#request-for-detail-miner-list
        """
        return self._native_private(
            "request_for_detail_miner_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "workerName": worker_name,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def request_for_miner_list(
        self,
        *,
        algo: str,
        user_name: str,
        page_index: int | None = None,
        sort: int | None = None,
        sort_column: int | None = None,
        worker_status: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Request for Miner List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#request-for-miner-list
        """
        return self._native_private(
            "request_for_miner_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "pageIndex": page_index,
                    "sort": sort,
                    "sortColumn": sort_column,
                    "workerStatus": worker_status,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def statistic_list(self, *, algo: str, user_name: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Statistic List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#statistic-list
        """
        return self._native_private(
            "statistic_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "algo": algo,
                    "userName": user_name,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_pay_trade_history(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Pay Trade History.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-pay/api/rest-api/~#get-pay-trade-history
        """
        return self._native_private(
            "get_pay_trade_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_spot_rebate_history_records(
        self,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Spot Rebate History Records (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-rebate/api/rest-api/~#get-spot-rebate-history-records
        """
        return self._native_private(
            "get_spot_rebate_history_records",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "startTime": start_time,
                    "endTime": end_time,
                    "page": page,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_borrow_interest_rate(self, *, loan_coin: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Borrow Interest Rate (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-borrow-interest-rate
        """
        return self._native_private(
            "get_borrow_interest_rate",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"loanCoin": loan_coin, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )

    def get_collateral_asset_data(
        self, *, collateral_coin: str | None = None, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Collateral Asset Data (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-collateral-asset-data
        """
        return self._native_private(
            "get_collateral_asset_data",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "collateralCoin": collateral_coin,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_loanable_assets_data(
        self,
        *,
        loan_coin: str | None = None,
        vip_level: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Loanable Assets Data (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-loanable-assets-data
        """
        return self._native_private(
            "get_loanable_assets_data",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanCoin": loan_coin,
                    "vipLevel": vip_level,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_interest_rate_history(
        self,
        *,
        coin: str,
        recv_window: int,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Interest Rate History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-viploan-interest-rate-history
        """
        return self._native_private(
            "get_vip_loan_interest_rate_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "coin": coin,
                    "recvWindow": recv_window,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                }.items()
                if value is not None
            ],
        )

    def query_vip_loan_fixed_rate_market(
        self,
        *,
        loan_coin: str,
        duration: int | None = None,
        current: int | None = None,
        size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query VIP Loan Fixed Rate Market (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#query-viploan-fixed-rate-market
        """
        return self._native_private(
            "query_vip_loan_fixed_rate_market",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanCoin": loan_coin,
                    "duration": duration,
                    "current": current,
                    "size": size,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_borrow(
        self,
        *,
        loan_account_id: int,
        loan_coin: str,
        loan_amount: str,
        collateral_account_id: str,
        collateral_coin: str,
        is_flexible_rate: bool,
        loan_term: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Borrow (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-borrow
        """
        return self._native_private(
            "vip_loan_borrow",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "loanAccountId": loan_account_id,
                    "loanCoin": loan_coin,
                    "loanAmount": loan_amount,
                    "collateralAccountId": collateral_account_id,
                    "collateralCoin": collateral_coin,
                    "isFlexibleRate": is_flexible_rate,
                    "loanTerm": loan_term,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_fixed_rate_borrow(
        self,
        *,
        supply_request: str,
        borrow_coin: str,
        loan_term: int,
        borrow_uid: int,
        collateral_coin: str,
        collateral_account_id: str,
        auto_repay: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Fixed Rate Borrow (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-fixed-rate-borrow
        """
        return self._native_private(
            "vip_loan_fixed_rate_borrow",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "supplyRequest": supply_request,
                    "borrowCoin": borrow_coin,
                    "loanTerm": loan_term,
                    "borrowUid": borrow_uid,
                    "collateralCoin": collateral_coin,
                    "collateralAccountId": collateral_account_id,
                    "autoRepay": auto_repay,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_renew(
        self, *, order_id: int, loan_term: int, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        VIP Loan Renew (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-renew
        """
        return self._native_private(
            "vip_loan_renew",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanTerm": loan_term,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def vip_loan_repay(self, *, order_id: int, amount: str, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        VIP Loan Repay (TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/trade#vip-loan-repay
        """
        return self._native_private(
            "vip_loan_repay",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "amount": amount,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def check_vip_loan_collateral_account(
        self,
        *,
        order_id: int | None = None,
        collateral_account_id: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Check VIP Loan Collateral Account (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#check-viploan-collateral-account
        """
        return self._native_private(
            "check_vip_loan_collateral_account",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "collateralAccountId": collateral_account_id,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_accrued_interest(
        self,
        *,
        order_id: int | None = None,
        loan_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Accrued Interest (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-accrued-interest
        """
        return self._native_private(
            "get_vip_loan_accrued_interest",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanCoin": loan_coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_ongoing_orders(
        self,
        *,
        order_id: int | None = None,
        collateral_account_id: int | None = None,
        loan_coin: str | None = None,
        collateral_coin: str | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Ongoing Orders (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-ongoing-orders
        """
        return self._native_private(
            "get_vip_loan_ongoing_orders",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "collateralAccountId": collateral_account_id,
                    "loanCoin": loan_coin,
                    "collateralCoin": collateral_coin,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def get_vip_loan_repayment_history(
        self,
        *,
        order_id: int | None = None,
        loan_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get VIP Loan Repayment History (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#get-viploan-repayment-history
        """
        return self._native_private(
            "get_vip_loan_repayment_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "orderId": order_id,
                    "loanCoin": loan_coin,
                    "startTime": start_time,
                    "endTime": end_time,
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def query_application_status(
        self,
        *,
        current: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Application Status (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/user-information#query-application-status
        """
        return self._native_private(
            "query_application_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "current": current,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_get_market_detail(self, *, market_topic_id: int) -> Any:  # noqa: ANN401
        """
        Get Market Detail.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#get-market-detail
        """
        return self._native_public(
            "prediction_get_market_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"marketTopicId": market_topic_id}.items()
                if value is not None
            ],
        )

    def prediction_list_prediction_categories(self) -> Any:  # noqa: ANN401
        """
        List Prediction Categories.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#list-prediction-categories
        """
        return self._native_public(
            "prediction_list_prediction_categories",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {}.items()
                if value is not None
            ],
        )

    def prediction_list_prediction_markets(
        self,
        *,
        l1_category: str | None = None,
        l2_category: str | None = None,
        sort_by: str | None = None,
        order_by: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        List Prediction Markets.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#list-prediction-markets
        """
        return self._native_public(
            "prediction_list_prediction_markets",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "l1Category": l1_category,
                    "l2Category": l2_category,
                    "sortBy": sort_by,
                    "orderBy": order_by,
                    "offset": offset,
                    "limit": limit,
                }.items()
                if value is not None
            ],
        )

    def prediction_market_search(self, *, query: str, top_k: int | None = None) -> Any:  # noqa: ANN401
        """
        Market Search.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#market-search
        """
        return self._native_public(
            "prediction_market_search",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"query": query, "topK": top_k}.items()
                if value is not None
            ],
        )

    def prediction_query_last_trade_price(self, *, market_id: int) -> Any:  # noqa: ANN401
        """
        Query Last Trade Price.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#query-last-trade-price
        """
        return self._native_public(
            "prediction_query_last_trade_price",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"marketId": market_id}.items()
                if value is not None
            ],
        )

    def prediction_query_order_book(self, *, vendor: str, market_id: int, token_id: str) -> Any:  # noqa: ANN401
        """
        Query Order Book.

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/market-data#query-order-book
        """
        return self._native_public(
            "prediction_query_order_book",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "vendor": vendor,
                    "marketId": market_id,
                    "tokenId": token_id,
                }.items()
                if value is not None
            ],
        )

    def prediction_create_otc_blocktrade(
        self,
        *,
        market_id: str,
        token_id: str,
        side: str,
        maker_amount: str,
        taker_amount: str,
        price_per_share: str,
        expiration: int,
    ) -> Any:  # noqa: ANN401
        """
        Create OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#create-otc-blocktrade
        """
        return self._native_private(
            "prediction_create_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "marketId": market_id,
                    "tokenId": token_id,
                    "side": side,
                    "makerAmount": maker_amount,
                    "takerAmount": taker_amount,
                    "pricePerShare": price_per_share,
                    "expiration": expiration,
                }.items()
                if value is not None
            ],
        )

    def prediction_fulfil_otc_blocktrade(self, *, order_id: str, secret_token: str) -> Any:  # noqa: ANN401
        """
        Fulfil OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#fulfil-otc-blocktrade
        """
        return self._native_private(
            "prediction_fulfil_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"orderId": order_id, "secretToken": secret_token}.items()
                if value is not None
            ],
        )

    def prediction_get_otc_blocktrade_detail(self, *, order_id: str) -> Any:  # noqa: ANN401
        """
        Get OTC Blocktrade Detail (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-blocktrade-detail
        """
        return self._native_private(
            "prediction_get_otc_blocktrade_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"orderId": order_id}.items()
                if value is not None
            ],
        )

    def prediction_get_otc_blocktrade_events(
        self,
        *,
        first: int | None = None,
        after: str | None = None,
        event_types: list[Any] | None = None,
        market_id: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get OTC Blocktrade Events (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-blocktrade-events
        """
        return self._native_private(
            "prediction_get_otc_blocktrade_events",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "first": first,
                    "after": after,
                    "eventTypes": event_types,
                    "marketId": market_id,
                }.items()
                if value is not None
            ],
        )

    def prediction_get_otc_reserved_balances(self, *, assets: list[Any]) -> Any:  # noqa: ANN401
        """
        Get OTC Reserved Balances (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#get-otc-reserved-balances
        """
        return self._native_private(
            "prediction_get_otc_reserved_balances",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"assets": assets}.items()
                if value is not None
            ],
        )

    def prediction_list_otc_blocktrades(
        self, *, first: int | None = None, after: str | None = None, status: str | None = None
    ) -> Any:  # noqa: ANN401
        """
        List OTC Blocktrades (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#list-otc-blocktrades
        """
        return self._native_private(
            "prediction_list_otc_blocktrades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"first": first, "after": after, "status": status}.items()
                if value is not None
            ],
        )

    def prediction_preview_otc_blocktrade(self, *, secret_token: str) -> Any:  # noqa: ANN401
        """
        Preview OTC Blocktrade (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#preview-otc-blocktrade
        """
        return self._native_private(
            "prediction_preview_otc_blocktrade",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"secretToken": secret_token}.items()
                if value is not None
            ],
        )

    def prediction_remove_otc_blocktrades(self, *, order_ids: list[Any]) -> Any:  # noqa: ANN401
        """
        Remove OTC Blocktrades (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/otc#remove-otc-blocktrades
        """
        return self._native_private(
            "prediction_remove_otc_blocktrades",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"orderIds": order_ids}.items()
                if value is not None
            ],
        )

    def prediction_get_position_by_token(
        self, *, wallet_address: str, token_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Position by Token (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#get-position-by-token
        """
        return self._native_private(
            "prediction_get_position_by_token",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tokenId": token_id,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_pn_l(
        self,
        *,
        wallet_address: str,
        token_id: str | None = None,
        market_id: int | None = None,
        market_topic_id: int | None = None,
        active_only: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query PnL (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-pn-l
        """
        return self._native_private(
            "prediction_query_pn_l",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tokenId": token_id,
                    "marketId": market_id,
                    "marketTopicId": market_topic_id,
                    "activeOnly": active_only,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_positions(
        self,
        *,
        wallet_address: str,
        tab: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Positions (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-positions
        """
        return self._native_private(
            "prediction_query_positions",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tab": tab,
                    "offset": offset,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_positions_by_filter(
        self,
        *,
        wallet_address: str | None = None,
        market_topic_id: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Positions by Filter (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-positions-by-filter
        """
        return self._native_private(
            "prediction_query_positions_by_filter",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "marketTopicId": market_topic_id,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_settled_position_history(
        self,
        *,
        wallet_address: str,
        l1_category: str | None = None,
        result: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Settled Position History (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/position#query-settled-position-history
        """
        return self._native_private(
            "prediction_query_settled_position_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "l1Category": l1_category,
                    "result": result,
                    "startDate": start_date,
                    "endDate": end_date,
                    "offset": offset,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

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
                for key, value in {
                    "walletAddress": wallet_address,
                    "walletId": wallet_id,
                    "tokenIds": token_ids,
                    "chainId": chain_id,
                }.items()
                if value is not None
            ],
        )

    def prediction_get_redeem_status(
        self, *, wallet_address: str, tx_hash: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Get Redeem Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/redeem#get-redeem-status
        """
        return self._native_private(
            "prediction_get_redeem_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "txHash": tx_hash,
                    "recvWindow": recv_window,
                }.items()
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
                for key, value in {
                    "walletAddress": wallet_address,
                    "walletId": wallet_id,
                    "cancelInfoList": cancel_info_list,
                }.items()
                if value is not None
            ],
        )

    def prediction_get_quote(
        self,
        *,
        wallet_address: str,
        token_id: str,
        side: str,
        amount_in: str,
        order_type: str,
        slippage_bps: int,
        price_limit: str | None = None,
        chain_id: str | None = None,
        fee_rate_bps: int | None = None,
        funding_source: str | None = None,
        fund_transfer_amount: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Quote (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#get-quote
        """
        return self._native_private(
            "prediction_get_quote",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tokenId": token_id,
                    "side": side,
                    "amountIn": amount_in,
                    "orderType": order_type,
                    "slippageBps": slippage_bps,
                    "priceLimit": price_limit,
                    "chainId": chain_id,
                    "feeRateBps": fee_rate_bps,
                    "fundingSource": funding_source,
                    "fundTransferAmount": fund_transfer_amount,
                }.items()
                if value is not None
            ],
        )

    def prediction_place_order(
        self,
        *,
        wallet_address: str,
        wallet_id: str,
        quote_id: str,
        time_in_force: str,
        account_type: str,
        order_type: str,
        slippage_bps: int,
        price_limit: str | None = None,
        funding_source: str | None = None,
        fund_transfer_amount: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Place Order (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#place-order
        """
        return self._native_private(
            "prediction_place_order",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "walletId": wallet_id,
                    "quoteId": quote_id,
                    "timeInForce": time_in_force,
                    "accountType": account_type,
                    "orderType": order_type,
                    "slippageBps": slippage_bps,
                    "priceLimit": price_limit,
                    "fundingSource": funding_source,
                    "fundTransferAmount": fund_transfer_amount,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_active_orders(
        self,
        *,
        wallet_address: str,
        trade_side: str | None = None,
        l1_category: str | None = None,
        market_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Active Orders (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#query-active-orders
        """
        return self._native_private(
            "prediction_query_active_orders",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tradeSide": trade_side,
                    "l1Category": l1_category,
                    "marketId": market_id,
                    "offset": offset,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_order_history(
        self,
        *,
        wallet_address: str,
        l1_category: str | None = None,
        order_type: str | None = None,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Query Order History (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/trade#query-order-history
        """
        return self._native_private(
            "prediction_query_order_history",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "l1Category": l1_category,
                    "orderType": order_type,
                    "status": status,
                    "startDate": start_date,
                    "endDate": end_date,
                    "offset": offset,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_apply_mm_deposit(
        self,
        *,
        from_token: str,
        from_token_amount: str,
        to_token: str,
        account_type: str,
        chain_id: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Apply MM Deposit (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#apply-mm-deposit
        """
        return self._native_private(
            "prediction_apply_mm_deposit",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "fromToken": from_token,
                    "fromTokenAmount": from_token_amount,
                    "toToken": to_token,
                    "accountType": account_type,
                    "chainId": chain_id,
                }.items()
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
                for key, value in {
                    "coin": coin,
                    "network": network,
                    "amount": amount,
                    "withdrawOrderId": withdraw_order_id,
                    "walletType": wallet_type,
                    "name": name,
                }.items()
                if value is not None
            ],
        )

    def prediction_create_inbound_transfer(
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
        return self._native_private(
            "prediction_create_inbound_transfer",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletId": wallet_id,
                    "walletAddress": wallet_address,
                    "fromTokenAmount": from_token_amount,
                    "accountType": account_type,
                    "fromToken": from_token,
                    "toToken": to_token,
                    "chainId": chain_id,
                }.items()
                if value is not None
            ],
        )

    def prediction_create_outbound_transfer(
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
        return self._native_private(
            "prediction_create_outbound_transfer",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletId": wallet_id,
                    "walletAddress": wallet_address,
                    "fromTokenAmount": from_token_amount,
                    "accountType": account_type,
                    "sourceBiz": source_biz,
                    "fromToken": from_token,
                    "toToken": to_token,
                    "chainId": chain_id,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_transfer_list(
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
        return self._native_private(
            "prediction_query_transfer_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "startDate": start_date,
                    "endDate": end_date,
                    "tokenSymbol": token_symbol,
                    "direction": direction,
                    "offset": offset,
                    "limit": limit,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_query_transfer_status(
        self, *, transfer_id: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Query Transfer Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/transfer#query-transfer-status
        """
        return self._native_private(
            "prediction_query_transfer_status",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {"transferId": transfer_id, "recvWindow": recv_window}.items()
                if value is not None
            ],
        )

    def prediction_get_portfolio(
        self,
        *,
        wallet_address: str,
        token_id: str | None = None,
        market_id: int | None = None,
        market_topic_id: int | None = None,
        active_only: bool | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Portfolio (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#get-portfolio
        """
        return self._native_private(
            "prediction_get_portfolio",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in {
                    "walletAddress": wallet_address,
                    "tokenId": token_id,
                    "marketId": market_id,
                    "marketTopicId": market_topic_id,
                    "activeOnly": active_only,
                    "recvWindow": recv_window,
                }.items()
                if value is not None
            ],
        )

    def prediction_get_quota_status(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Get Quota Status (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#get-quota-status
        """
        return self._native_private(
            "prediction_get_quota_status",
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

    def prediction_list_prediction_wallets(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        List Prediction Wallets (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#list-prediction-wallets
        """
        return self._native_private(
            "prediction_list_prediction_wallets",
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

    def prediction_query_payment_option_balances(self, *, recv_window: int | None = None) -> Any:  # noqa: ANN401
        """
        Query Payment Option Balances (PREDICTION_TRADE).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/web3-wallet-prediction-trading/api/rest-api/wallet#query-payment-option-balances
        """
        return self._native_private(
            "prediction_query_payment_option_balances",
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
