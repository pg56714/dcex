"""Offline Arcus Spot and Perps route tests; no request reaches Arcus."""

# ruff: noqa: D103

import asyncio
import json
from urllib.parse import parse_qs, urlsplit

import pytest

import dcex
import dcex.async_support as async_dcex
from dcex.arcus.client import Client as SyncPerpsClient
from dcex.arcus.spot import SpotClient as SyncSpotClient
from dcex.async_support.arcus.client import Client as AsyncPerpsClient
from dcex.async_support.arcus.spot import SpotClient as AsyncSpotClient
from tests.unit.native_http_helpers import _http_server

SELL = "0x" + "11" * 20
BUY = "0x" + "22" * 20
TAKER = "0x" + "33" * 20
SIGNATURE = "0x" + "44" * 65


def _signed_spot_quote(chain_id: int) -> dict[str, object]:
    return {
        "venue": "arcus",
        "chainId": chain_id,
        "taker": TAKER,
        "typedData": {
            "domain": {"chainId": chain_id},
            "primaryType": "PermitWitnessTransferFrom",
        },
        "signature": SIGNATURE,
    }


def _firm_spot_quote(chain_id: int) -> dict[str, object]:
    return {
        "venue": "arcus",
        "toSign": {
            "domain": {"chainId": chain_id},
            "primaryType": "PermitWitnessTransferFrom",
        },
    }


def test_arcus_spot_native_public_routes() -> None:
    native = pytest.importorskip("dcex._native")
    with _http_server({"ok": True}) as (base_url, received):
        client = native.ArcusSpotHttpClient(base_url=base_url, timeout=2)
        assert client.public_request_json("health", [])[2] == {"ok": True}
        assert received.get_nowait()["path"] == "/health"
        assert client.public_request_json("get_tokens", [])[2] == {"ok": True}
        assert received.get_nowait()["path"] == "/v1/tokens"
        assert client.public_request_json(
            "get_quote",
            [
                ("sellToken", SELL),
                ("buyToken", BUY),
                ("sellAmount", "1000000"),
                ("taker", TAKER),
                ("slippageBps", "50"),
            ],
        )[2] == {"ok": True}
        request = received.get_nowait()
        assert urlsplit(request["path"]).path == "/v1/quote"
        query = parse_qs(urlsplit(request["path"]).query)
        assert query["chainId"] == ["4663"]
        assert query["sellAmount"] == ["1000000"]
        assert query["slippageBps"] == ["50"]
        with pytest.raises(ValueError, match="chainId"):
            client.public_request_json(
                "get_price",
                [
                    ("sellToken", SELL),
                    ("buyToken", BUY),
                    ("sellAmount", "1"),
                    ("chainId", "46630"),
                ],
            )


def test_arcus_spot_python_sync_public_methods() -> None:
    with _http_server({"ok": True}) as (base_url, received):
        client = SyncSpotClient(base_url=base_url)
        assert client.health() == {"ok": True}
        assert client.get_tokens() == {"ok": True}
        assert client.get_price(SELL, BUY, "1000000") == {"ok": True}
        assert client.get_quote(SELL, BUY, "1000000", TAKER, slippage_bps=50) == {"ok": True}
        client.close()
        assert [urlsplit(received.get_nowait()["path"]).path for _ in range(4)] == [
            "/health",
            "/v1/tokens",
            "/v1/price",
            "/v1/quote",
        ]


def test_arcus_spot_key_is_explicit_and_separate_from_perps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARCUS_MAINNET_API_KEY", "perps-key")
    monkeypatch.setenv("ARCUS_SPOT_MAINNET_API_KEY", "old-router-key")
    with _http_server({"ok": True}) as (base_url, received):
        public_client = SyncSpotClient(base_url=base_url)
        assert public_client.health() == {"ok": True}
        assert "x-api-key" not in received.get_nowait()
        public_client.close()

        partner_client = SyncSpotClient(api_key="partner-key", base_url=base_url)
        assert partner_client.health() == {"ok": True}
        assert received.get_nowait()["x-api-key"] == "partner-key"
        partner_client.close()


def test_arcus_spot_signed_submit_and_status_routes_are_complete() -> None:
    """Exercise the real submit/status routes against a local server only."""
    with _http_server({"ok": True}) as (base_url, received):
        client = SyncSpotClient(base_url=base_url)
        signed_quote = _signed_spot_quote(4663)
        assert client.submit_signed_quote(signed_quote) == {"ok": True}
        submit = received.get_nowait()
        assert submit["path"] == "/v1/submit"
        assert json.loads(submit["body"]) == signed_quote

        tx_hash = "0x" + "55" * 32
        assert client.get_status(tx_hash) == {"ok": True}
        status = urlsplit(received.get_nowait()["path"])
        assert status.path == "/v1/status"
        assert parse_qs(status.query) == {
            "chainId": ["4663"],
            "id": [tx_hash],
            "venue": ["arcus"],
        }


def test_arcus_spot_builds_submit_body_from_external_signature() -> None:
    client = SyncSpotClient()
    body = client.build_signed_quote(
        _firm_spot_quote(4663),
        TAKER,
        SIGNATURE,
        permits=[{"token": SELL}],
        route_tag="strategy-a",
    )
    assert body == {
        "venue": "arcus",
        "chainId": 4663,
        "taker": TAKER,
        "typedData": _firm_spot_quote(4663)["toSign"],
        "signature": SIGNATURE,
        "permits": [{"token": SELL}],
        "routeTag": "strategy-a",
    }

    with pytest.raises(ValueError, match="selected network"):
        client.build_signed_quote(_firm_spot_quote(46630), TAKER, SIGNATURE)


def test_arcus_factories_select_spot_by_default() -> None:
    """Market selection is per client, with Spot as the public default."""
    assert isinstance(dcex.arcus(), SyncSpotClient)
    assert isinstance(dcex.arcus(market="perps"), SyncPerpsClient)
    with pytest.raises(ValueError, match="market"):
        dcex.arcus(market="unknown")


def test_arcus_spot_python_async_public_methods() -> None:
    async def check() -> None:
        with _http_server({"ok": True}) as (base_url, received):
            client = await AsyncSpotClient(testnet=True, base_url=base_url).async_init()
            assert await client.health() == {"ok": True}
            assert await client.get_tokens() == {"ok": True}
            assert await client.get_price(SELL, BUY, "1000000") == {"ok": True}
            assert await client.get_quote(SELL, BUY, "1000000", TAKER) == {"ok": True}
            await client.close()
            paths = [urlsplit(received.get_nowait()["path"]) for _ in range(4)]
            assert [path.path for path in paths] == [
                "/health",
                "/v1/tokens",
                "/v1/price",
                "/v1/quote",
            ]
            assert parse_qs(paths[-1].query)["chainId"] == ["46630"]

    asyncio.run(check())


def test_arcus_spot_async_key_is_explicit_and_separate_from_perps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARCUS_TESTNET_API_KEY", "perps-key")
    monkeypatch.setenv("ARCUS_SPOT_TESTNET_API_KEY", "old-router-key")

    async def check() -> None:
        with _http_server({"ok": True}) as (base_url, received):
            public_client = await AsyncSpotClient(testnet=True, base_url=base_url).async_init()
            assert await public_client.health() == {"ok": True}
            assert "x-api-key" not in received.get_nowait()
            await public_client.close()

            partner_client = await AsyncSpotClient(
                api_key="partner-key", testnet=True, base_url=base_url
            ).async_init()
            assert await partner_client.health() == {"ok": True}
            assert received.get_nowait()["x-api-key"] == "partner-key"
            await partner_client.close()

    asyncio.run(check())


def test_arcus_async_factory_market_selection() -> None:
    """The async entry point mirrors sync Spot and Perps selection."""

    async def check() -> None:
        assert isinstance(await async_dcex.arcus(), AsyncSpotClient)
        assert isinstance(await async_dcex.arcus(market="perps"), AsyncPerpsClient)
        with pytest.raises(ValueError, match="market"):
            await async_dcex.arcus(market="unknown")

    asyncio.run(check())


def test_arcus_perps_signed_order_and_cancel_routes_are_complete() -> None:
    """Verify Perps market lookup, signing, order and cancellation locally."""
    market_response = {
        "markets": [
            {
                "marketId": 1,
                "marketDisplayName": "BTC-USD",
                "baseAsset": "BTC",
                "quoteAsset": "USD",
                "status": "ONLINE",
                "tickSize": "0.1",
                "stepSize": "0.001",
                "minOrderSize": "0.001",
                "maxOrderSize": "100",
                "minOrderNotional": "1",
            }
        ]
    }
    with _http_server(market_response) as (base_url, received):
        client = SyncPerpsClient(
            api_secret="00" * 32,
            address="0x" + "66" * 20,
            base_url=base_url,
        )
        client.place_order("BTC-USD-SWAP", "BUY", "100", "0.01")
        assert urlsplit(received.get_nowait()["path"]).path == "/v1/markets"
        placed = received.get_nowait()
        assert urlsplit(placed["path"]).path == "/v1/placeOrder"
        assert placed["x-api-key"]
        assert placed["x-signature"]
        assert json.loads(placed["body"])["marketId"] == 1

        client.cancel_order("BTC-USD-SWAP", "order-1")
        assert urlsplit(received.get_nowait()["path"]).path == "/v1/markets"
        cancelled = received.get_nowait()
        assert urlsplit(cancelled["path"]).path == "/v1/cancelOrder"
        assert json.loads(cancelled["body"])["orderId"] == "order-1"
