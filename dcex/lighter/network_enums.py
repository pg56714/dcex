"""Lighter endpoint profiles."""

from enum import StrEnum


class Network(StrEnum):
    """Supported Lighter protocol deployments."""

    MAINNET = "mainnet"
    TESTNET = "testnet"
    ROBINHOOD = "robinhood"
    ROBINHOOD_TESTNET = "robinhood_testnet"

    @property
    def api_url(self) -> str:
        """Return the REST base URL for this network."""
        return _ENDPOINTS[self][0]

    @property
    def ws_url(self) -> str:
        """Return the WebSocket URL for this network."""
        return _ENDPOINTS[self][1]

    @property
    def chain_id(self) -> int:
        """Return the L2 signing chain ID for this network."""
        return _ENDPOINTS[self][2]

    @property
    def credentials_env_prefix(self) -> str:
        """Return the environment prefix for this network's credentials."""
        return {
            Network.MAINNET: "LIGHTER_MAINNET",
            Network.TESTNET: "LIGHTER_TESTNET",
            Network.ROBINHOOD: "LIGHTER_ROBINHOOD",
            Network.ROBINHOOD_TESTNET: "LIGHTER_ROBINHOOD_TESTNET",
        }[self]


_ENDPOINTS: dict[Network, tuple[str, str, int]] = {
    Network.MAINNET: (
        "https://mainnet.zklighter.elliot.ai",
        "wss://mainnet.zklighter.elliot.ai/stream",
        304,
    ),
    Network.TESTNET: (
        "https://testnet.zklighter.elliot.ai",
        "wss://testnet.zklighter.elliot.ai/stream",
        300,
    ),
    Network.ROBINHOOD: (
        "https://api.rh.lighter.xyz",
        "wss://api.rh.lighter.xyz/stream",
        466_324,
    ),
    Network.ROBINHOOD_TESTNET: (
        "https://api.rh-testnet.lighter.xyz",
        "wss://api.rh-testnet.lighter.xyz/stream",
        300,
    ),
}


def normalize_network(network: Network | str) -> Network:
    """Normalize and validate a Lighter network value."""
    if isinstance(network, Network):
        return network
    normalized = str(network).strip().lower().replace("-", "_")
    try:
        return Network(normalized)
    except ValueError as exc:
        raise ValueError(f"Unsupported Lighter network: {network}") from exc


__all__ = ["Network"]
