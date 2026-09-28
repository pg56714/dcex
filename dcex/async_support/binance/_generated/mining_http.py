"""Generated binance mining HTTP methods."""

from json import dumps
from typing import Any

from dcex._schema_codec import normalize_params

from .._market_http import MarketHTTP
from .._trade_http import TradeHTTP


class GeneratedMiningHTTP(MarketHTTP, TradeHTTP):
    """Mining API methods."""

    async def account_list(
        self, *, algo: str, user_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Account List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#account-list
        """
        return await self._native_private(
            "account_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"algo": algo, "userName": user_name, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )

    async def acquiring_algorithm(self) -> Any:  # noqa: ANN401
        """
        Acquiring Algorithm (MARKET_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#acquiring-algorithm
        """
        return await self._native_public(
            "acquiring_algorithm",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({}).items()
                if value is not None
            ],
        )

    async def acquiring_coinname(self) -> Any:  # noqa: ANN401
        """
        Acquiring CoinName (MARKET_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#acquiring-coinname
        """
        return await self._native_public(
            "acquiring_coinname",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params({}).items()
                if value is not None
            ],
        )

    async def cancel_hashrate_resale_configuration(
        self, *, config_id: int, user_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Cancel hashrate resale configuration (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#cancel-hashrate-resale-configuration
        """
        return await self._native_private(
            "cancel_hashrate_resale_configuration",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"configId": config_id, "userName": user_name, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )

    async def earnings_list(
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
        return await self._native_private(
            "earnings_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "algo": algo,
                        "userName": user_name,
                        "coin": coin,
                        "startDate": start_date,
                        "endDate": end_date,
                        "pageIndex": page_index,
                        "pageSize": page_size,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def extra_bonus_list(
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
        return await self._native_private(
            "extra_bonus_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "algo": algo,
                        "userName": user_name,
                        "coin": coin,
                        "startDate": start_date,
                        "endDate": end_date,
                        "pageIndex": page_index,
                        "pageSize": page_size,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def hashrate_resale_detail(
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
        return await self._native_private(
            "hashrate_resale_detail",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "configId": config_id,
                        "pageIndex": page_index,
                        "pageSize": page_size,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def hashrate_resale_list(
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
        return await self._native_private(
            "hashrate_resale_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"pageIndex": page_index, "pageSize": page_size, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )

    async def hashrate_resale_request(
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
        return await self._native_private(
            "hashrate_resale_request",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "userName": user_name,
                        "algo": algo,
                        "endDate": end_date,
                        "startDate": start_date,
                        "toPoolUser": to_pool_user,
                        "hashRate": hash_rate,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def mining_account_earning(
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
        return await self._native_private(
            "mining_account_earning",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "algo": algo,
                        "startDate": start_date,
                        "endDate": end_date,
                        "pageIndex": page_index,
                        "pageSize": page_size,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def request_for_detail_miner_list(
        self, *, algo: str, user_name: str, worker_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Request for Detail Miner List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#request-for-detail-miner-list
        """
        return await self._native_private(
            "request_for_detail_miner_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "algo": algo,
                        "userName": user_name,
                        "workerName": worker_name,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def request_for_miner_list(
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
        return await self._native_private(
            "request_for_miner_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {
                        "algo": algo,
                        "userName": user_name,
                        "pageIndex": page_index,
                        "sort": sort,
                        "sortColumn": sort_column,
                        "workerStatus": worker_status,
                        "recvWindow": recv_window,
                    }
                ).items()
                if value is not None
            ],
        )

    async def statistic_list(
        self, *, algo: str, user_name: str, recv_window: int | None = None
    ) -> Any:  # noqa: ANN401
        """
        Statistic List (USER_DATA).

        Native symbols and caller-provided field values are preserved.
        Source: https://developers.binance.com/en/docs/catalog/investment-and-services-mining/api/rest-api/~#statistic-list
        """
        return await self._native_private(
            "statistic_list",
            [
                (
                    key,
                    dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list, bool))
                    else str(value),
                )
                for key, value in normalize_params(
                    {"algo": algo, "userName": user_name, "recvWindow": recv_window}
                ).items()
                if value is not None
            ],
        )
