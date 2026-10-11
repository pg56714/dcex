"""Async product table manager module."""

from ... import _native
from ...product_table._query import ProductTableError, ProductTableQueryMixin, instance_key
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

    Fetching, normalization, indexing, and querying are implemented by the Rust
    core. This class preserves the asynchronous Python query API without a
    heavy table runtime dependency.
    """

    _instance = {}

    @classmethod
    async def get_instance(
        cls, exchange_name: str | None = None, perp_dexs: list[str] | None = None
    ) -> "ProductTableManager":
        """
        Get or create a ProductTableManager instance.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.
            perp_dexs: Hyperliquid only. Builder-deployed (HIP-3) perp DEXs to load; the
                first perp DEX and spot always load. None loads every DEX.

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

        key = instance_key(exchange_name, perp_dexs)
        if key not in cls._instance:
            instance = cls()
            await instance._initialize(exchange_name=exchange_name, perp_dexs=perp_dexs)
            cls._instance[key] = instance
        return cls._instance[key]

    async def _initialize(
        self, exchange_name: str | None = None, perp_dexs: list[str] | None = None
    ) -> None:
        """
        Initialize the product table by fetching data from valid exchanges.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.
        """
        self.product_table = await self._fetch_product_tables(exchange_name, perp_dexs)
        self._build_indexes()

    async def _fetch_product_tables(
        self, exchange_name: str | None = None, perp_dexs: list[str] | None = None
    ) -> _native.ProductTable:
        """
        Fetch product tables from the Rust core.

        Args:
            exchange_name: Optional exchange name to filter data for specific exchange.

        Returns:
            Product rows containing all product information.
        """
        try:
            if perp_dexs is None:
                table = await _native.fetch_product_table_async(exchange_name)
            else:
                table = await _native.fetch_product_table_async(exchange_name, perp_dexs=perp_dexs)
        except (RuntimeError, ValueError) as exc:
            raise ProductTableError(str(exc)) from exc
        if table.height == 0:
            raise ProductTableError("Failed to fetch product tables from any exchange")
        return table

    async def refresh(
        self, exchange_name: str | None = None, perp_dexs: list[str] | None = None
    ) -> None:
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
        await self._initialize(exchange_name=exchange_name, perp_dexs=perp_dexs)
