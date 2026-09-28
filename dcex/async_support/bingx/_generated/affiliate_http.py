"""Generated bingx affiliate HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedAffiliateHTTP(MarketHTTP):
    """Affiliate API methods."""

    async def get_agent_v1_asset_partner_data(
        self,
        *,
        uid: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Query partner information.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Query%20partner%20information
        """
        return await self._native_private(
            "get_agent_v1_asset_partner_data",
            self._native_params(
                **{
                    "uid": uid,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def get_agent_v2_reward_commission_data_list(
        self,
        *,
        start_time: str,
        end_time: str,
        page_index: int,
        page_size: int,
        recv_window: int,
        uid: int | None = None,
        invitation_code: str | None = None,
        business_type: str | None = None,
        distance_type: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Daily commission details.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Daily%20commission%20details
        """
        return await self._native_private(
            "get_agent_v2_reward_commission_data_list",
            self._native_params(
                **{
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                    "uid": uid,
                    "invitationCode": invitation_code,
                    "businessType": business_type,
                    "distanceType": distance_type,
                }
            ),
        )

    async def get_agent_v1_reward_third_commission_data_list(
        self,
        *,
        commission_biz_type: int,
        start_time: str,
        end_time: str,
        page_index: int,
        page_size: int,
        uid: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Query API transaction commission （non-invitation relationship）.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Query%20API%20transaction%20commission%20%EF%BC%88non-invitation%20relationship%EF%BC%89
        """
        return await self._native_private(
            "get_agent_v1_reward_third_commission_data_list",
            self._native_params(
                **{
                    "commissionBizType": commission_biz_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "uid": uid,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def get_agent_v1_commission_data_list_referral_code(
        self,
        *,
        direct_invitation: str,
        referral_code: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_index: int | None = None,
        page_size: int | None = None,
        recv_window: int | None = None,
    ) -> Any:  # noqa: ANN401
        """Invitation code data.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://bingx-api.github.io/docs-v3/#/en/Agent/Invitation%20code%20data
        """
        return await self._native_private(
            "get_agent_v1_commission_data_list_referral_code",
            self._native_params(
                **{
                    "directInvitation": direct_invitation,
                    "referralCode": referral_code,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "recvWindow": recv_window,
                }
            ),
        )

    async def get_agent_v1_account_invite_account_list(
        self,
        *,
        page_index: int,
        page_size: int,
        start_time: int | None = None,
        end_time: int | None = None,
        last_uid: int | None = None,
    ) -> Any:  # noqa: ANN401
        """1. Query Invited Users.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L14
        """
        return await self._native_private(
            "get_agent_v1_account_invite_account_list",
            self._native_params(
                **{
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "startTime": start_time,
                    "endTime": end_time,
                    "lastUid": last_uid,
                }
            ),
        )

    async def get_agent_v1_account_invite_relation_check(self, *, uid: int) -> Any:  # noqa: ANN401
        """3. Query Agent User Information.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L115
        """
        return await self._native_private(
            "get_agent_v1_account_invite_relation_check", self._native_params(**{"uid": uid})
        )

    async def get_agent_v1_asset_deposit_detail_list(
        self,
        *,
        uid: int,
        biz_type: int,
        start_time: int,
        end_time: int,
        page_index: int,
        page_size: int,
    ) -> Any:  # noqa: ANN401
        """6. Query Deposit Details of Invited Users.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L242
        """
        return await self._native_private(
            "get_agent_v1_asset_deposit_detail_list",
            self._native_params(
                **{
                    "uid": uid,
                    "bizType": biz_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "pageIndex": page_index,
                    "pageSize": page_size,
                }
            ),
        )

    async def get_agent_v1_account_superior_check(self, *, uid: int) -> Any:  # noqa: ANN401
        """8. Superior Verification.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/agent/api-reference.md#L333
        """
        return await self._native_private(
            "get_agent_v1_account_superior_check", self._native_params(**{"uid": uid})
        )
