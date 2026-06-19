"""
Shared, protocol-agnostic helpers for exchange HTTP managers.

Each exchange keeps its own ``_request``/``_sign``/header logic because those
differ for real protocol reasons (how the signature is built, how the base URL
is chosen, batch-order formats). What is genuinely identical across exchanges
is pulled together here:

- logger setup (previously copy-pasted into every ``__post_init__``)
- an ``EXCHANGE`` marker so call sites stop hard-coding ``Common.BINANCE`` etc.
- request/error logging helpers used on each manager's request path

Mixing :class:`BaseHTTPManager` in does not change any request behaviour; it
only removes duplicated boilerplate.
"""

import logging
import re
from typing import ClassVar

from ..utils.common import Common
from ..utils.errors import sanitize_message, sanitize_url


class BaseHTTPManager:
    """
    Mixin providing shared, non-networking helpers for HTTP managers.

    Subclasses set the class-level :attr:`EXCHANGE` and call
    :meth:`_setup_logger` from their ``__post_init__``. Everything related to
    actually performing or signing requests stays in the per-exchange manager.
    """

    #: The exchange this manager talks to. Overridden by each subclass.
    EXCHANGE: ClassVar[Common | None] = None
    last_response_headers: dict[str, str] | None = None

    def _setup_logger(self, logger: logging.Logger | None) -> logging.Logger:
        """
        Resolve the logger to use, preserving the previous naming behaviour.

        When no logger is supplied a module-named logger is used, matching the
        old ``logging.getLogger(__name__)`` call that lived in each manager's
        ``__post_init__`` (``__class__.__module__`` equals that ``__name__``).

        A :class:`logging.NullHandler` is attached to the default logger so the
        library stays silent unless the application configures logging, while
        still emitting records that the application can opt into. A
        caller-supplied logger is returned untouched.

        Args:
            logger: A caller-supplied logger, or ``None`` to use the default.

        Returns:
            The logger instance to store on the manager.
        """
        if logger is not None:
            return logger
        resolved = logging.getLogger(self.__class__.__module__)
        if not any(isinstance(handler, logging.NullHandler) for handler in resolved.handlers):
            resolved.addHandler(logging.NullHandler())
        return resolved

    def _log_request(self, method: str, url: str) -> None:
        """Emit a debug record for an outgoing request."""
        logger = getattr(self, "_logger", None)
        if logger is not None:
            logger.debug("%s request: %s %s", self.EXCHANGE, method.upper(), sanitize_url(url))

    def _log_failed_request(self, message: str, status_code: object) -> None:
        """Emit an error record just before a failed request is raised."""
        logger = getattr(self, "_logger", None)
        if logger is not None:
            logger.error(
                "%s request failed [%s]: %s",
                self.EXCHANGE,
                status_code,
                sanitize_message(message),
            )

    def _store_response_headers(self, response: object) -> dict[str, str]:
        """Store raw HTTP response headers from the latest completed response."""
        headers = dict(getattr(response, "headers", {}) or {})
        self.last_response_headers = headers
        return headers

    @staticmethod
    def _exception_response_details(
        exception: BaseException,
    ) -> tuple[str | int, dict[str, str] | None]:
        """Extract response metadata carried by a transport exception."""
        raw_status = getattr(exception, "status_code", None)
        if raw_status is not None:
            status_code = raw_status if isinstance(raw_status, (str, int)) else str(raw_status)
            headers = getattr(exception, "resp_headers", None)
            return status_code, dict(headers) if headers is not None else None

        response = getattr(exception, "response", None)
        if response is None:
            match = re.search(r"HTTP request failed with status (\d+)", str(exception))
            if match is not None:
                return int(match.group(1)), None
            return "Unknown", None

        raw_status = getattr(response, "status_code", "Unknown")
        status_code = raw_status if isinstance(raw_status, (str, int)) else str(raw_status)
        headers = dict(getattr(response, "headers", {}) or {})
        return status_code, headers
