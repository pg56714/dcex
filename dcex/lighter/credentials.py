"""Network-scoped Lighter private credentials."""

from dataclasses import dataclass, field
from typing import Any, cast

from .._native_http import load_native
from .network_enums import Network, normalize_network

_native = load_native()

_CREDENTIAL_SUFFIXES = ("ACCOUNT_INDEX", "API_KEY_INDEX", "API_PRIVATE_KEY")


def credential_env_names(network: Network | str) -> tuple[str, str, str]:
    """Return the scoped environment variable names for one network."""
    prefix = normalize_network(network).credentials_env_prefix
    return cast(
        tuple[str, str, str],
        tuple(f"{prefix}_{suffix}" for suffix in _CREDENTIAL_SUFFIXES),
    )


@dataclass(frozen=True, slots=True)
class LighterCredentials:
    """A complete private credential set for one Lighter network."""

    account_index: int
    api_key_index: int
    api_private_key: str = field(repr=False)

    def __post_init__(self) -> None:
        """Validate credentials with the Rust core."""
        native_type = getattr(_native, "LighterCredentials", None)
        if native_type is None:
            raise RuntimeError("The dcex native extension is required.")
        native_type(
            account_index=self.account_index,
            api_key_index=self.api_key_index,
            api_private_key=self.api_private_key,
        )

    @classmethod
    def from_env(cls, network: Network | str = Network.MAINNET) -> "LighterCredentials":
        """Load credentials using the selected network's environment prefix."""
        resolved_network = normalize_network(network)
        native_type = getattr(_native, "LighterCredentials", None)
        if native_type is None:
            raise RuntimeError("The dcex native extension is required.")
        credentials: Any = native_type.from_env(resolved_network.value)
        return cls(
            account_index=int(credentials.account_index),
            api_key_index=int(credentials.api_key_index),
            api_private_key=str(credentials.api_private_key),
        )


__all__ = [
    "LighterCredentials",
    "credential_env_names",
]
