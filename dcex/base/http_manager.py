"""
Shared, protocol-agnostic helpers for exchange HTTP managers.

Each exchange keeps its own ``_request``/``_sign``/header logic because those
differ for real protocol reasons (how the signature is built, how the base URL
is chosen, batch-order formats). What is genuinely identical across exchanges
is pulled together here:

- logger setup (previously copy-pasted into every ``__post_init__``)
- an ``EXCHANGE`` marker so call sites stop hard-coding ``Common.BINANCE`` etc.
- ``drop_none`` for building request payloads without ``None`` values

Mixing :class:`BaseHTTPManager` in does not change any request behaviour; it
only removes duplicated boilerplate.
"""

import logging
from typing import Any, ClassVar

from ..utils.common import Common


def drop_none(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of ``payload`` with keys whose value is ``None`` removed.

    Optional API parameters must be omitted entirely rather than sent as
    ``None``: exchanges that fold parameters into the request signature (e.g.
    Binance urlencodes them) would otherwise sign and send the literal string
    ``"None"`` and the request would be rejected. Keys whose value is ``0``,
    ``""`` or ``False`` are kept, because those are valid API values.

    Args:
        payload: The raw payload, possibly containing ``None`` values.

    Returns:
        A new dict containing only the entries whose value is not ``None``.
    """
    return {key: value for key, value in payload.items() if value is not None}


class BaseHTTPManager:
    """
    Mixin providing shared, non-networking helpers for HTTP managers.

    Subclasses set the class-level :attr:`EXCHANGE` and call
    :meth:`_setup_logger` from their ``__post_init__``. Everything related to
    actually performing or signing requests stays in the per-exchange manager.
    """

    #: The exchange this manager talks to. Overridden by each subclass.
    EXCHANGE: ClassVar[Common | None] = None

    def _setup_logger(self, logger: logging.Logger | None) -> logging.Logger:
        """
        Resolve the logger to use, preserving the previous naming behaviour.

        When no logger is supplied a module-named logger is used, matching the
        old ``logging.getLogger(__name__)`` call that lived in each manager's
        ``__post_init__`` (``__class__.__module__`` equals that ``__name__``).

        Args:
            logger: A caller-supplied logger, or ``None`` to use the default.

        Returns:
            The logger instance to store on the manager.
        """
        return logger if logger is not None else logging.getLogger(self.__class__.__module__)
