"""Read Lighter private account state asynchronously."""

import asyncio

from dcex.async_support.lighter import Client, Network


async def read_network(network: Network) -> None:
    """Read private state from one Lighter network."""
    client = Client.from_env(network, preload_product_table=False)
    await client.async_init()
    try:
        print(network.value, await client.get_account(by="index", value=str(client.account_index)))
        print(network.value, await client.get_account_limits())
        print(network.value, await client.get_account_active_orders())
    finally:
        await client.close()


async def main() -> None:
    """Read Lighter and Robinhood private state concurrently."""
    await asyncio.gather(
        read_network(Network.MAINNET),
        read_network(Network.ROBINHOOD),
    )


if __name__ == "__main__":
    asyncio.run(main())
