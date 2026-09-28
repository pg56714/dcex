"""Generated kucoin affiliate HTTP methods."""

from typing import Any

from .._trade_http import TradeHTTP


class GeneratedAffiliateHTTP(TradeHTTP):
    """Affiliate API methods."""

    def get_ua_v2_affiliate_query_invitees(
        self,
        *,
        user_type: str | None = None,
        referral_code: str | None = None,
        uid: str | None = None,
        registration_end_at: int | None = None,
        registration_start_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Invited.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/invited
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_invitees",
            self._native_params(
                userType=user_type,
                referralCode=referral_code,
                uid=uid,
                registrationEndAt=registration_end_at,
                registrationStartAt=registration_start_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_my_commission(
        self,
        *,
        site_type: str | None = None,
        rebate_type: int | None = None,
        rebate_start_at: int | None = None,
        rebate_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        data_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Commission.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/commission
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_my_commission",
            self._native_params(
                siteType=site_type,
                rebateType=rebate_type,
                rebateStartAt=rebate_start_at,
                rebateEndAt=rebate_end_at,
                page=page,
                pageSize=page_size,
                dataType=data_type,
            ),
        )

    def get_ua_v2_affiliate_query_transaction_by_uid(
        self,
        *,
        uid: str,
        trade_type: str | None = None,
        trade_start_at: int | None = None,
        trade_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Trade History.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/trade-history
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_transaction_by_uid",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_transaction_by_time(
        self,
        *,
        uid: str | None = None,
        trade_type: str | None = None,
        trade_start_at: int,
        trade_end_at: int,
        last_id: int | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Transaction.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/transaction
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_transaction_by_time",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_ua_v2_affiliate_query_kumining(
        self,
        *,
        uid: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Kumining.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/kumining
        """
        return self._native_private(
            "get_ua_v2_affiliate_query_kumining",
            self._native_params(
                uid=uid,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_invitees(
        self,
        *,
        user_type: str | None = None,
        referral_code: str | None = None,
        uid: str | None = None,
        registration_start_at: int | None = None,
        registration_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Invited.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-invited
        """
        return self._native_private(
            "get_v2_affiliate_query_invitees",
            self._native_params(
                userType=user_type,
                referralCode=referral_code,
                uid=uid,
                registrationStartAt=registration_start_at,
                registrationEndAt=registration_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_my_commission(
        self,
        *,
        site_type: str | None = None,
        rebate_type: int | None = None,
        rebate_start_at: int | None = None,
        rebate_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        user_id: str | None = None,
        data_type: str | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Commission.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-commission
        """
        return self._native_private(
            "get_v2_affiliate_query_my_commission",
            self._native_params(
                siteType=site_type,
                rebateType=rebate_type,
                rebateStartAt=rebate_start_at,
                rebateEndAt=rebate_end_at,
                page=page,
                pageSize=page_size,
                userId=user_id,
                dataType=data_type,
            ),
        )

    def get_v2_affiliate_query_transaction_by_uid(
        self,
        *,
        uid: str,
        trade_type: str | None = None,
        trade_start_at: int | None = None,
        trade_end_at: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Trade History.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-trade-history
        """
        return self._native_private(
            "get_v2_affiliate_query_transaction_by_uid",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                page=page,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_transaction_by_time(
        self,
        *,
        uid: str | None = None,
        trade_type: str | None = None,
        trade_start_at: int,
        trade_end_at: int,
        last_id: int | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Transaction.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-transaction
        """
        return self._native_private(
            "get_v2_affiliate_query_transaction_by_time",
            self._native_params(
                uid=uid,
                tradeType=trade_type,
                tradeStartAt=trade_start_at,
                tradeEndAt=trade_end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )

    def get_v2_affiliate_query_kumining(
        self,
        *,
        uid: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: str | None = None,
        direction: str | None = None,
        page_size: int | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Get Kumining.

        Source: https://www.kucoin.com/docs-new/rest/affiliate/get-kumining
        """
        return self._native_private(
            "get_v2_affiliate_query_kumining",
            self._native_params(
                uid=uid,
                startAt=start_at,
                endAt=end_at,
                lastId=last_id,
                direction=direction,
                pageSize=page_size,
            ),
        )
