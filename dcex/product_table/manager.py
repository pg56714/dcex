"""Product table management module."""

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

    Fetching, normalization, indexing, and querying are implemented by the Rust
    core. This class preserves the synchronous Python query API without a
    heavy table runtime dependency.
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

    def _fetch_product_tables(self, exchange_name: str | None = None) -> _native.ProductTable:
        """
        Fetch product tables through the Rust core.
        """
        try:
            table = _native.fetch_product_table(exchange_name)
        except (RuntimeError, ValueError) as exc:
            raise ProductTableError(str(exc)) from exc
        if table.height == 0:
            raise ProductTableError("Failed to fetch product tables from any exchange")
        return table

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
