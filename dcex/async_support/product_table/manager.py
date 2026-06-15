"""
Product table manager module for managing exchange product mappings.

This module provides the ProductTableManager class for managing standardized
product information across multiple cryptocurrency exchanges.
"""

import polars as pl

from ... import _native
from ...product_table._query import ProductTableError, ProductTableQueryMixin
from ...registry import ASYNC_EXCHANGES
from . import fetch

# Re-exported so ``from ...product_table.manager import ProductTableError`` keeps working,
# and so it is the same class as the sync side (except ProductTableError catches both).
__all__ = ["ProductTableError", "ProductTableManager", "VALID_EXCHANGES"]

# Derived from the canonical registry so the async fetch list cannot drift from
# the sync one or from the registry. Order follows ASYNC_EXCHANGES.
VALID_EXCHANGES = [getattr(fetch, name) for name in ASYNC_EXCHANGES]


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
        - price_precision: The decimal precision allowed for price values.
        - size_precision: The decimal precision allowed for order sizes.
        - contract_value: The notional value of one contract (for derivatives).
        - min_size: The minimum order size allowed on the exchange.
        - min_notional: The minimum notional value required for an order.

    Fetching, normalization, indexing, and querying are implemented by the Rust
    core. This class preserves the asynchronous Python API and Polars output.
    """

    _instance = {}

    @classmethod
    async def get_instance(cls, exchange_name: str | None = None) -> "ProductTableManager":
        """
        Get or create a ProductTableManager instance.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.

        Returns:
            ProductTableManager instance.
        """
        # Validate exchange_name if provided
        if exchange_name is not None:
            valid_names = {func.__name__ for func in VALID_EXCHANGES}
            if exchange_name not in valid_names:
                raise ProductTableError(
                    f"Invalid exchange_name: {exchange_name}. Valid: {sorted(valid_names)}"
                )

        if exchange_name not in cls._instance:
            instance = cls()
            await instance._initialize(exchange_name=exchange_name)
            cls._instance[exchange_name] = instance
        return cls._instance[exchange_name]

    async def _initialize(self, exchange_name: str | None = None) -> None:
        """
        Initialize the product table by fetching data from valid exchanges.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.
        """
        self.product_table = await self._fetch_product_tables(exchange_name)
        self._build_indexes()

    async def _fetch_product_tables(self, exchange_name: str | None = None) -> pl.DataFrame:
        """
        Fetch product tables from all valid exchanges and combine them into a single DataFrame.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.

        Returns:
            Combined Polars DataFrame containing all product information.
        """
        try:
            rows = await _native.fetch_product_table_async(exchange_name)
        except (RuntimeError, ValueError) as exc:
            raise ProductTableError(str(exc)) from exc
        if not rows:
            raise ProductTableError("Failed to fetch product tables from any exchange")
        return pl.DataFrame(rows)

    async def refresh(self, exchange_name: str | None = None) -> None:
        """
        Refresh product table and indexes.
        If exchange_name is provided, only that exchange is fetched.
        """
        if exchange_name is not None:
            valid_names = {func.__name__ for func in VALID_EXCHANGES}
            if exchange_name not in valid_names:
                raise ProductTableError(
                    f"Invalid exchange_name: {exchange_name}. Valid: {sorted(valid_names)}"
                )
        await self._initialize(exchange_name=exchange_name)
