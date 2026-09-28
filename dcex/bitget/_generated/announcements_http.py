"""Generated bitget announcements HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedAnnouncementsHTTP(MarketHTTP):
    """Announcements API methods."""

    def classic_common_notice_get_all_notices(
        self,
        *,
        language: str,
        ann_type: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        cursor: str | None = None,
        limit: str | None = None,
    ) -> dict[str, Any]:
        """
        Query Announcements.

        Use native exchange symbols. Optional fields retain their documented types.
        Source: https://www.bitget.com/docs/catalog/classic-common-notice/classic-common-notice#query-announcements
        """
        return self._native_public(
            "classic_common_notice_get_all_notices",
            self._native_params(
                **{
                    "language": language,
                    "annType": ann_type,
                    "startTime": start_time,
                    "endTime": end_time,
                    "cursor": cursor,
                    "limit": limit,
                }
            ),
        )
