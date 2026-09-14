"""Read both Lighter mainnet private account states."""

from dcex.lighter import Client, Network


def main() -> None:
    """Read private state from Lighter and Robinhood independently."""
    clients = {
        network: Client.from_env(network, preload_product_table=False)
        for network in (Network.MAINNET, Network.ROBINHOOD)
    }
    for network, client in clients.items():
        try:
            print(network.value, client.get_account(by="index", value=str(client.account_index)))
            print(network.value, client.get_account_limits())
            print(network.value, client.get_account_active_orders())
        finally:
            client.close()


if __name__ == "__main__":
    main()
