import asyncio
from pathlib import Path

from dcex.async_support.product_table.manager import ProductTableManager
from dcex.utils.common import Common


async def main() -> None:
    output_dir = Path("product_tables")
    output_dir.mkdir(exist_ok=True)

    for exchange in Common:
        manager = await ProductTableManager.get_instance(exchange)
        output_path = output_dir / f"{exchange.value}_product_table.csv"
        manager.df.write_csv(output_path)
        print(output_path)


if __name__ == "__main__":
    asyncio.run(main())
