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

# Insertion order is preserved and used as the fetch order; keep it alphabetical.
EXCHANGES: dict[str, dict[str, bool]] = {
    "binance": {"sync": True, "async": True},
    "bingx": {"sync": True, "async": True},
    "bitget": {"sync": True, "async": True},
    "bitmart": {"sync": True, "async": True},
    "bitmex": {"sync": True, "async": True},
    "bybit": {"sync": True, "async": True},
    "gateio": {"sync": True, "async": True},
    "hyperliquid": {"sync": True, "async": True},
    "kucoin": {"sync": True, "async": True},
    "kraken": {"sync": True, "async": True},
    "lighter": {"sync": True, "async": True},
    "mexc": {"sync": True, "async": True},
    "okx": {"sync": True, "async": True},
}

#: Exchange names with a synchronous product-table fetcher.
SYNC_EXCHANGES: tuple[str, ...] = tuple(name for name, caps in EXCHANGES.items() if caps["sync"])

#: Exchange names with an asynchronous product-table fetcher.
ASYNC_EXCHANGES: tuple[str, ...] = tuple(name for name, caps in EXCHANGES.items() if caps["async"])
