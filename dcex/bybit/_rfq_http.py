"""Bybit RFQ HTTP client backed by Rust."""

from typing import Any

from ._http_manager import HTTPManager


class RFQHTTP(HTTPManager):
    """HTTP client for Bybit Request for Quote workflows."""

    def get_rfq_public_trades(
        self,
        *,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return public RFQ block trades."""
        return self._native_private(
            "get_rfq_public_trades",
            self._native_params(startTime=startTime, endTime=endTime, limit=limit, cursor=cursor),
        )

    def get_rfq_config(self) -> dict[str, Any]:
        """Return RFQ account configuration and available counterparties."""
        return self._native_private("get_rfq_config", [])

    def create_rfq(
        self,
        counterparties: list[str],
        legs: list[dict[str, object]],
        *,
        rfqLinkId: str | None = None,
        anonymous: bool | None = None,
        strategyType: str | None = None,
        hedge: list[dict[str, object]] | None = None,
    ) -> dict[str, Any]:
        """Create an RFQ."""
        return self._native_private(
            "create_rfq",
            self._native_params(
                counterparties=counterparties,
                list=legs,
                rfqLinkId=rfqLinkId,
                anonymous=anonymous,
                strategyType=strategyType,
                hedge=hedge,
            ),
        )

    def cancel_rfq(
        self, *, rfqId: str | None = None, rfqLinkId: str | None = None
    ) -> dict[str, Any]:
        """Cancel an RFQ by exchange or client identifier."""
        return self._native_private(
            "cancel_rfq", self._native_params(rfqId=rfqId, rfqLinkId=rfqLinkId)
        )

    def cancel_all_rfqs(self) -> dict[str, Any]:
        """Cancel every active RFQ."""
        return self._native_private("cancel_all_rfqs", [])

    def accept_other_rfq_quote(self, rfqId: str) -> dict[str, Any]:
        """Allow a non-LP quote for an RFQ."""
        return self._native_private("accept_other_rfq_quote", self._native_params(rfqId=rfqId))

    def create_rfq_quote(
        self,
        rfqId: str,
        *,
        quoteBuyList: list[dict[str, object]] | None = None,
        quoteSellList: list[dict[str, object]] | None = None,
        quoteLinkId: str | None = None,
        anonymous: bool | None = None,
        expireIn: int | None = None,
    ) -> dict[str, Any]:
        """Create a buy, sell, or two-sided RFQ quote."""
        return self._native_private(
            "create_rfq_quote",
            self._native_params(
                rfqId=rfqId,
                quoteBuyList=quoteBuyList,
                quoteSellList=quoteSellList,
                quoteLinkId=quoteLinkId,
                anonymous=anonymous,
                expireIn=expireIn,
            ),
        )

    def execute_rfq_quote(
        self,
        rfqId: str,
        quoteId: str,
        quoteSide: str,
        *,
        isHedge: bool | None = None,
    ) -> dict[str, Any]:
        """Execute a selected RFQ quote."""
        return self._native_private(
            "execute_rfq_quote",
            self._native_params(rfqId=rfqId, quoteId=quoteId, quoteSide=quoteSide, isHedge=isHedge),
        )

    def cancel_rfq_quote(
        self,
        *,
        quoteId: str | None = None,
        quoteLinkId: str | None = None,
        rfqId: str | None = None,
    ) -> dict[str, Any]:
        """Cancel an RFQ quote."""
        return self._native_private(
            "cancel_rfq_quote",
            self._native_params(quoteId=quoteId, quoteLinkId=quoteLinkId, rfqId=rfqId),
        )

    def cancel_all_rfq_quotes(self) -> dict[str, Any]:
        """Cancel every active quote."""
        return self._native_private("cancel_all_rfq_quotes", [])

    def get_realtime_rfqs(
        self,
        *,
        rfqId: str | None = None,
        rfqLinkId: str | None = None,
        traderType: str | None = None,
    ) -> dict[str, Any]:
        """Return non-final RFQs from the real-time engine."""
        return self._native_private(
            "get_realtime_rfqs",
            self._native_params(rfqId=rfqId, rfqLinkId=rfqLinkId, traderType=traderType),
        )

    def get_rfqs(
        self,
        *,
        rfqId: str | None = None,
        rfqLinkId: str | None = None,
        traderType: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return historical RFQs."""
        return self._native_private(
            "get_rfqs",
            self._native_params(
                rfqId=rfqId,
                rfqLinkId=rfqLinkId,
                traderType=traderType,
                status=status,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_rfq_details(
        self,
        *,
        rfqId: str | None = None,
        rfqLinkId: str | None = None,
        traderType: str | None = None,
        status: str | None = None,
        startTime: int | None = None,
        endTime: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return detailed historical RFQs, quotes, and executed legs."""
        return self._native_private(
            "get_rfq_details",
            self._native_params(
                rfqId=rfqId,
                rfqLinkId=rfqLinkId,
                traderType=traderType,
                status=status,
                startTime=startTime,
                endTime=endTime,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_realtime_rfq_quotes(
        self,
        *,
        rfqId: str | None = None,
        quoteId: str | None = None,
        quoteLinkId: str | None = None,
        traderType: str | None = None,
    ) -> dict[str, Any]:
        """Return non-final RFQ quotes from the real-time engine."""
        return self._native_private(
            "get_realtime_rfq_quotes",
            self._native_params(
                rfqId=rfqId,
                quoteId=quoteId,
                quoteLinkId=quoteLinkId,
                traderType=traderType,
            ),
        )

    def get_rfq_quotes(
        self,
        *,
        rfqId: str | None = None,
        quoteId: str | None = None,
        quoteLinkId: str | None = None,
        traderType: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return historical RFQ quotes."""
        return self._native_private(
            "get_rfq_quotes",
            self._native_params(
                rfqId=rfqId,
                quoteId=quoteId,
                quoteLinkId=quoteLinkId,
                traderType=traderType,
                status=status,
                limit=limit,
                cursor=cursor,
            ),
        )

    def get_rfq_trade_history(
        self,
        *,
        rfqId: str | None = None,
        rfqLinkId: str | None = None,
        quoteId: str | None = None,
        quoteLinkId: str | None = None,
        traderType: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """Return filled or failed RFQ executions."""
        return self._native_private(
            "get_rfq_trade_history",
            self._native_params(
                rfqId=rfqId,
                rfqLinkId=rfqLinkId,
                quoteId=quoteId,
                quoteLinkId=quoteLinkId,
                traderType=traderType,
                status=status,
                limit=limit,
                cursor=cursor,
            ),
        )
