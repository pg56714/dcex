"""Generated bingx announcements HTTP methods."""

from typing import Any

from .._market_http import MarketHTTP


class GeneratedAnnouncementsHTTP(MarketHTTP):
    """Announcements API methods."""

    async def get_content_v1_announcement(
        self,
        *,
        content_type: str | None = None,
        language: str | None = None,
        page: int | None = None,
    ) -> Any:  # noqa: ANN401
        """1. Get Announcements.

        Use native BingX symbols. Decimal fields are strings to preserve precision.
        Source: https://github.com/BingX-API/api-ai-skills/blob/5fb44d121b7e10ef3493bb4de21fedf7e5c98ac6/skills/announcement/api-reference.md#L7
        """
        return await self._native_public(
            "get_content_v1_announcement",
            self._native_params(
                **{"contentType": content_type, "language": language, "page": page}
            ),
        )
