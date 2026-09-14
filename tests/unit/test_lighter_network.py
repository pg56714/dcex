# ruff: noqa: D100, D103

import pytest


def _create_order_params() -> list[tuple[str, str]]:
    return [
        ("market_index", "0"),
        ("client_order_index", "1"),
        ("base_amount", "10"),
        ("price", "100"),
        ("is_ask", "false"),
        ("order_type", "0"),
        ("time_in_force", "1"),
        ("reduce_only", "false"),
        ("trigger_price", "0"),
        ("order_expiry", "1800000000000"),
        ("nonce", "7"),
    ]


def test_lighter_network_profiles() -> None:
    from dcex.lighter import Network

    assert Network.MAINNET.api_url == "https://mainnet.zklighter.elliot.ai"
    assert Network.ROBINHOOD.api_url == "https://api.rh.lighter.xyz"
    assert Network.ROBINHOOD.ws_url == "wss://api.rh.lighter.xyz/stream"
    assert Network.ROBINHOOD.chain_id == 466_324
    assert Network.ROBINHOOD_TESTNET.chain_id == 300


def test_native_lighter_robinhood_profile() -> None:
    native = pytest.importorskip("dcex._native")

    client = native.LighterHttpClient(network="robinhood")

    assert client.network() == "robinhood"
    assert client.base_url() == "https://api.rh.lighter.xyz"
    assert client.chain_id() == 466_324


def test_native_lighter_rejects_unknown_network() -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="unsupported Lighter network"):
        native.LighterHttpClient(network="unknown")


def test_native_lighter_custom_signing_chain_is_explicit() -> None:
    native = pytest.importorskip("dcex._native")

    client = native.LighterHttpClient(base_url="http://localhost:8000", chain_id=466_324)

    assert client.network() is None
    assert client.chain_id() == 466_324


def test_native_lighter_rejects_mismatched_known_chain_id() -> None:
    native = pytest.importorskip("dcex._native")

    with pytest.raises(ValueError, match="does not match"):
        native.LighterHttpClient(
            base_url="https://api.rh.lighter.xyz",
            chain_id=304,
        )


def test_python_lighter_robinhood_private_signing() -> None:
    from dcex.lighter import Client, Network

    client = Client(
        account_index=12,
        api_key_index=3,
        api_private_key="01" + "00" * 39,
        network=Network.ROBINHOOD,
        preload_product_table=False,
    )

    tx_type, tx_info, tx_hash, error = client._native_sign(
        "sign_create_order",
        _create_order_params(),
    )

    assert tx_type == 14
    assert isinstance(tx_info, str)
    assert len(tx_hash) == 80
    assert error is None


def test_custom_url_requires_chain_id_before_private_signing() -> None:
    native = pytest.importorskip("dcex._native")
    client = native.LighterHttpClient(
        base_url="http://localhost:8000",
        account_index=12,
        api_key_index=3,
        api_private_key="01" + "00" * 39,
    )

    with pytest.raises(ValueError, match="require an explicit chain_id"):
        client.sign_request("sign_create_order", _create_order_params())


def test_native_lighter_robinhood_private_websocket_profile() -> None:
    native = pytest.importorskip("dcex._native")

    client = native.LighterPrivateWebSocketClient(
        account_index=12,
        api_key_index=3,
        api_private_key="01" + "00" * 39,
        network="robinhood",
    )

    assert client.account_index() == 12
    assert client.create_auth_token(api_key_index=3).split(":")[2] == "3"


def test_network_scoped_credentials_are_loaded_and_redacted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.lighter import LighterCredentials, Network

    private_key = "01" + "00" * 39
    monkeypatch.setenv("LIGHTER_ROBINHOOD_ACCOUNT_INDEX", "12")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_KEY_INDEX", "3")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_PRIVATE_KEY", private_key)

    credentials = LighterCredentials.from_env(Network.ROBINHOOD)

    assert credentials.account_index == 12
    assert credentials.api_key_index == 3
    assert credentials.api_private_key == private_key
    assert private_key not in repr(credentials)


def test_robinhood_credentials_never_use_legacy_mainnet_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.lighter import LighterCredentials, Network

    for suffix in ("ACCOUNT_INDEX", "API_KEY_INDEX", "API_PRIVATE_KEY"):
        monkeypatch.delenv(f"LIGHTER_ROBINHOOD_{suffix}", raising=False)
    monkeypatch.setenv("LIGHTER_ACCOUNT_INDEX", "12")
    monkeypatch.setenv("LIGHTER_API_KEY_INDEX", "3")
    monkeypatch.setenv("LIGHTER_API_PRIVATE_KEY", "01" + "00" * 39)

    with pytest.raises(ValueError, match="LIGHTER_ROBINHOOD_ACCOUNT_INDEX"):
        LighterCredentials.from_env(Network.ROBINHOOD)


def test_sync_client_from_env_uses_selected_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.lighter import Client, Network

    monkeypatch.setenv("LIGHTER_ROBINHOOD_ACCOUNT_INDEX", "12")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_KEY_INDEX", "3")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_PRIVATE_KEY", "01" + "00" * 39)

    client = Client.from_env(Network.ROBINHOOD, preload_product_table=False)

    assert client.network is Network.ROBINHOOD
    assert client.account_index == 12
    assert client.api_key_index == 3


def test_mainnet_and_robinhood_clients_coexist_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dcex.lighter import Client, Network

    private_key = "01" + "00" * 39
    monkeypatch.setenv("LIGHTER_MAINNET_ACCOUNT_INDEX", "11")
    monkeypatch.setenv("LIGHTER_MAINNET_API_KEY_INDEX", "2")
    monkeypatch.setenv("LIGHTER_MAINNET_API_PRIVATE_KEY", private_key)
    monkeypatch.setenv("LIGHTER_ROBINHOOD_ACCOUNT_INDEX", "12")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_KEY_INDEX", "3")
    monkeypatch.setenv("LIGHTER_ROBINHOOD_API_PRIVATE_KEY", private_key)

    mainnet = Client.from_env(Network.MAINNET, preload_product_table=False)
    robinhood = Client.from_env(Network.ROBINHOOD, preload_product_table=False)
    try:
        assert mainnet.base_url == Network.MAINNET.api_url
        assert mainnet.account_index == 11
        assert robinhood.base_url == Network.ROBINHOOD.api_url
        assert robinhood.account_index == 12
        assert mainnet._native_client.chain_id() == Network.MAINNET.chain_id
        assert robinhood._native_client.chain_id() == Network.ROBINHOOD.chain_id
    finally:
        mainnet.close()
        robinhood.close()
