"""Fund movement and batch endpoint mixins."""

from typing import Any

from ._http_manager import HTTPManager


class MarketHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from MarketHTTP."""

    def get_explorer_batches(self) -> dict[str, Any] | list[Any]:
        """Query the official Lighter explorer API."""
        return self._native_public("get_explorer_batches", self._native_params(**{}))

    def get_explorer_batch(self, *, batch_id: int) -> dict[str, Any] | list[Any]:
        """Query the official Lighter explorer API."""
        return self._native_public(
            "get_explorer_batch", self._native_params(**{"batchId": batch_id})
        )


class TradeHTTPBatchHTTP(HTTPManager):
    """Batch methods moved from TradeHTTP."""

    def send_tx_batch(
        self,
        tx_types: str,
        tx_infos: str,
    ) -> dict[str, Any] | list[Any]:
        """Submit a batch of signed Lighter transactions."""
        return self._native_private("send_tx_batch", self._native_params(**locals()))
