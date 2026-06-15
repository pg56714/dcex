"""
Product table management module.

This module provides the ProductTableManager class for managing exchange product
mapping tables and standardized product information across different exchanges.
"""

import polars as pl

from .. import _native
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

    Fetching, normalization, indexing, and querying are implemented by the Rust
    core. This class preserves the synchronous Python API and Polars output.
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
        if exchange_name is not None:
            valid_names = {func.__name__ for func in VALID_EXCHANGES}
            if exchange_name not in valid_names:
                raise ProductTableError(
                    f"Invalid exchange_name: {exchange_name}. Valid: {sorted(valid_names)}"
                )

        if exchange_name not in cls._instance:
            instance = cls()
            instance._initialize(exchange_name=exchange_name)
            cls._instance[exchange_name] = instance
        return cls._instance[exchange_name]

    def _initialize(self, exchange_name: str | None = None) -> None:
        """Initialize the product table by fetching data from valid exchanges."""
        self.product_table = self._fetch_product_tables(exchange_name)
        self._build_indexes()

    def _fetch_product_tables(self, exchange_name: str | None = None) -> pl.DataFrame:
        """
        Fetch product tables through the Rust core.
        """
        try:
            rows = _native.fetch_product_table(exchange_name)
        except (RuntimeError, ValueError) as exc:
            raise ProductTableError(str(exc)) from exc
        if not rows:
            raise ProductTableError("Failed to fetch product tables from any exchange")
        return pl.DataFrame(rows)

    def refresh(self, exchange_name: str | None = None) -> None:
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
        self._initialize(exchange_name=exchange_name)
