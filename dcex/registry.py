"""
Canonical registry of supported exchanges.

Single source of truth for which exchanges exist and which execution models
(sync / async) each one supports. The product table managers derive their
fetch lists from here, so the sync and async lists can no longer drift apart
or fall out of sync with the fetchers.

To add a new exchange, add one row here (plus its fetch function and client
package). ``sync``/``async`` reflect whether a corresponding fetcher exists in
``dcex.product_table.fetch`` / ``dcex.async_support.product_table.fetch``.
"""

from . import _native

# Insertion order is preserved and used as the fetch order; keep it alphabetical.
EXCHANGES: dict[str, dict[str, bool]] = {
    name: {"sync": True, "async": True} for name in _native.exchange_names()
}

#: Exchange names with a synchronous product-table fetcher.
SYNC_EXCHANGES: tuple[str, ...] = tuple(name for name, caps in EXCHANGES.items() if caps["sync"])

#: Exchange names with an asynchronous product-table fetcher.
ASYNC_EXCHANGES: tuple[str, ...] = tuple(name for name, caps in EXCHANGES.items() if caps["async"])
