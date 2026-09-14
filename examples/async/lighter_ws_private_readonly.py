"""Open a Lighter private WebSocket user-data stream."""

import asyncio

from dcex.lighter import Network
from dcex.ws import lighter


async def read_network(network: Network) -> None:
    """Read one private order event from a Lighter network."""
    async with lighter.private_from_env(network=network) as ws:
        await ws.subscribe_account_all_orders()
        print(network.value, await ws.recv())


async def main() -> None:
    """Open Lighter and Robinhood private streams concurrently."""
    await asyncio.gather(
        read_network(Network.MAINNET),
        read_network(Network.ROBINHOOD),
    )


if __name__ == "__main__":
    asyncio.run(main())
