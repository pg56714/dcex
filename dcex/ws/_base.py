"""Shared helpers for async WebSocket wrappers."""

from typing import Any


class AsyncWebSocketMixin:
    """Common async context manager and iterator behavior."""

    async def connect(self) -> None:
        """Open the WebSocket connection."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close the WebSocket connection."""
        raise NotImplementedError

    async def recv(self) -> dict[str, Any] | list[Any]:
        """Receive one WebSocket event."""
        raise NotImplementedError

    async def __aenter__(self) -> "AsyncWebSocketMixin":
        """Open the WebSocket connection when entering an async context."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,  # noqa: ANN401
    ) -> None:
        """Close the WebSocket connection when leaving an async context."""
        await self.close()

    def __aiter__(self) -> "AsyncWebSocketMixin":
        """Return the async iterator."""
        return self

    async def __anext__(self) -> dict[str, Any] | list[Any]:
        """Receive the next WebSocket event."""
        try:
            return await self.recv()
        except RuntimeError as exc:
            if "connection closed" in str(exc).lower():
                raise StopAsyncIteration from exc
            raise
