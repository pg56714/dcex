"""
Product table management module.

This module provides the ProductTableManager class for managing exchange product
mapping tables and standardized product information across different exchanges.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed

import polars as pl

from ..registry import SYNC_EXCHANGES
from . import fetch
from ._query import ProductTableError, ProductTableQueryMixin

# Re-exported so ``from dcex.product_table.manager import ProductTableError`` keeps working.
__all__ = ["ProductTableError", "ProductTableManager", "VALID_EXCHANGES"]

# Derived from the canonical registry so the sync fetch list cannot drift from
# the async one or from the registry. Order follows SYNC_EXCHANGES.
VALID_EXCHANGES = [getattr(fetch, name) for name in SYNC_EXCHANGES]


class ProductTableManager(ProductTableQueryMixin):
    """
    Exchange Product Mapping Table.

    This table provides a structured mapping between product symbols and their
    corresponding exchange-specific symbols, along with key trading attributes.
    It helps standardize the representation of products across different exchanges.

    Columns:
        - product_symbol: Standardized product identifier used internally.
        - exchange_symbol: The product symbol as recognized on the exchange.
        - exchange: The name of the exchange where the product is traded.
        - product_type: The category of the product (e.g., SPOT, SWAP, FUTURES).
        - price_precision: The decimal precision allowed for price values (if applicable).
        - size_precision: The decimal precision allowed for order sizes (if applicable).
        - contract_value: The notional value of one contract (for derivatives).
        - min_size: The minimum order size allowed on the exchange.
        - min_notional: The minimum notional value required for an order.

    The pure query/index methods live in :class:`ProductTableQueryMixin`; this
    class only adds the synchronous fetch/initialise layer.
    """

    _instance = {}

    @classmethod
    def get_instance(cls, exchange_name: str | None = None) -> "ProductTableManager":
        """
        Get or create a ProductTableManager instance for the specified exchange.

        Args:
            exchange_name: Name of the exchange to initialize for

        Returns:
            ProductTableManager: The singleton instance
        """
        if exchange_name not in cls._instance:
            cls._instance[exchange_name] = cls()
            cls._instance[exchange_name]._initialize(exchange_name=exchange_name)
        return cls._instance[exchange_name]

    def _initialize(self, exchange_name: str | None = None) -> None:
        """Initialize the product table by fetching data from valid exchanges."""
        self.product_table = self._fetch_product_tables(exchange_name)
        self._build_indexes()

    def _fetch_product_tables(self, exchange_name: str | None = None) -> pl.DataFrame:
        """
        Fetch product tables from all valid exchanges and combine them into a single DataFrame.
        """
        functions = (
            list(VALID_EXCHANGES)
            if exchange_name is None
            else [func for func in VALID_EXCHANGES if func.__name__ == exchange_name]
        )

        tables: list[pl.DataFrame] = []
        # Use threads to parallelize synchronous HTTP calls
        with ThreadPoolExecutor(max_workers=min(8, max(1, len(functions)))) as executor:
            future_to_name = {executor.submit(func): func.__name__ for func in functions}
            for future in as_completed(future_to_name):
                try:
                    table = future.result()
                    if isinstance(table, pl.DataFrame):
                        tables.append(table)
                except Exception as exc:
                    # Skip failed exchanges; align with async version behavior
                    _ = exc  # avoid unused var warning
                    continue

        if not tables:
            raise ProductTableError("Failed to fetch product tables from any exchange")

        return pl.concat(tables, how="vertical")

    def refresh(self, exchange_name: str | None = None) -> None:
        """
        Refresh product table and indexes.

        If exchange_name is provided, only that exchange is fetched.
        """
        self._initialize(exchange_name=exchange_name)
