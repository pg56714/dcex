"""Async Bybit Spot X Launchpool HTTP client backed by Rust."""

from typing import Any

from ..._native_http import request_native_json_async
from ._http_manager import HTTPManager


class SpotXHTTP(HTTPManager):
    """Read-only Launchpool project, staking, and account history methods."""

    async def get_launchpool_projects(
        self,
        status: int,
        *,
        activityCoin: str | None = None,
        projectId: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """List Launchpool projects by upcoming, ongoing, or ended status."""
        if self._native_client is None:
            raise RuntimeError("Bybit native client is required for Launchpool methods.")
        response, data = await request_native_json_async(
            self._native_client,
            "public_request",
            "get_launchpool_projects",
            self._native_params(
                status=status,
                activityCoin=activityCoin,
                projectId=projectId,
                cursor=cursor,
                limit=limit,
            ),
        )
        self._store_response_headers(response)
        return data

    async def get_launchpool_current_staking(self) -> dict[str, Any]:
        """Get active Launchpool staking positions and portfolio totals."""
        return await self._native_private("get_launchpool_current_staking", [])

    async def get_launchpool_activity_log(
        self,
        *,
        stakeCoin: str | None = None,
        type: int | None = None,
        status: int | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageSize: int | None = None,
        current: int | None = None,
    ) -> dict[str, Any]:
        """Get Launchpool staking operations; times are Unix milliseconds."""
        return await self._native_private(
            "get_launchpool_activity_log",
            self._native_params(
                stakeCoin=stakeCoin,
                type=type,
                status=status,
                startTime=startTime,
                endTime=endTime,
                pageSize=pageSize,
                current=current,
            ),
        )

    async def get_launchpool_history(
        self,
        *,
        stakeCoin: str | None = None,
        rewardCoin: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        pageSize: int | None = None,
        current: int | None = None,
    ) -> dict[str, Any]:
        """Get completed Launchpool staking positions."""
        return await self._native_private(
            "get_launchpool_history",
            self._native_params(
                stakeCoin=stakeCoin,
                rewardCoin=rewardCoin,
                startTime=startTime,
                endTime=endTime,
                pageSize=pageSize,
                current=current,
            ),
        )
