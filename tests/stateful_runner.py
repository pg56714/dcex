"""Opt-in entry point for the existing per-exchange stateful test modules."""

import importlib
import inspect
import logging
import os

import pytest
from dotenv import load_dotenv

from scripts.live.redaction import redact
from tests.live_gate import stateful_tests_enabled
from tests.stateful_adapters import CexAdapter
from tests.stateful_arcus import ARCUS_SPOT_NA, ArcusAdapter
from tests.stateful_dex import ExtendedAdapter, HyperliquidAdapter, LighterAdapter, OndoAdapter
from tests.stateful_lifecycle import (
    InsufficientBalance,
    MarketUnavailable,
    NotApplicable,
    not_applicable,
    run_lifecycle,
)

MARKETS = {
    "binance": [("spot", "BTC-USDC-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "bybit": [("spot", "DOGE-USDT-SPOT"), ("linear", "DOGE-USDT-SWAP")],
    "okx": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "bitget": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "bingx": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "mexc": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "kucoin": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USDT-SWAP")],
    "kraken": [("spot", "DOGE-USDT-SPOT"), ("swap", "DOGE-USD-SWAP")],
    "backpack": [("spot", "SOL-USDC-SPOT"), ("swap", "SOL-USDC-SWAP")],
    "aster": [("spot", "USDC-USDT-SPOT"), ("swap", "ASTER-USDT-SWAP")],
    "extended": [("spot", "BTC-USD-SPOT"), ("swap", "BTC-USD-SWAP")],
    "ondo": [("swap", "BTC-USD-SWAP")],
    "hyperliquid": [("spot", "PURR-USDC-SPOT"), ("swap", "BTC-USD-SWAP")],
    "lighter": [("mainnet", "ETH"), ("robinhood", "ETH")],
    "arcus": [("spot", ""), ("swap", "BTC-USD")],
}

ADAPTERS = {
    "extended": ExtendedAdapter,
    "ondo": OndoAdapter,
    "hyperliquid": HyperliquidAdapter,
    "lighter": LighterAdapter,
    "arcus": ArcusAdapter,
}


def client_options(exchange):
    """Read credentials only when the explicitly opted-in test actually runs."""
    if exchange == "extended":
        names = {
            name: "EXTENDED_" + name.upper()
            for name in ("api_key", "stark_private_key", "stark_public_key", "vault_number")
        }
    elif exchange == "ondo":
        names = {"api_key_id": "ONDO_API_KEY_ID", "api_secret": "ONDO_API_SECRET"}
    elif exchange == "hyperliquid":
        names = {
            "wallet_address": "HYPERLIQUID_WALLET_ADDRESS",
            "private_key": "HYPERLIQUID_PRIVATE_KEY",
        }
    elif exchange == "arcus":
        names = {
            "api_key": "ARCUS_API_KEY",
            "api_secret": "ARCUS_API_SIGNING_KEY",
            "address": "ARCUS_ADDRESS",
        }
    elif exchange == "aster":
        names = {
            name: "ASTER_" + name.upper()
            for name in ("user_address", "signer_address", "private_key")
        }
    elif exchange == "kraken":
        names = {
            name: "KRAKEN_" + name.upper()
            for name in ("spot_api_key", "spot_api_secret", "futures_api_key", "futures_api_secret")
        }
    else:
        names = {
            "api_key": exchange.upper() + "_API_KEY",
            "api_secret": exchange.upper() + "_API_SECRET",
        }
        if exchange in {"okx", "bitget", "kucoin"}:
            names["passphrase"] = exchange.upper() + (
                "_API_PASSPHRASE" if exchange == "kucoin" else "_PASSPHRASE"
            )
    missing = [name for name in names.values() if not os.getenv(name)]
    if missing:
        pytest.skip("Missing credential environment variables: " + ", ".join(missing))
    logger = logging.Logger("stateful-no-payload-logging")
    logger.disabled = True
    values = {key: os.environ[name] for key, name in names.items()}
    if "vault_number" in values:
        values["vault_number"] = int(values["vault_number"])
    return dict(
        logger=logger,
        timeout=20,
        preload_product_table=exchange != "arcus",
        **values,
    )


async def run_case(exchange, mode, market, symbol, result, case="lifecycle"):
    """Create a client only after opt-in; report sanitized errors without traceback locals."""
    result.update(exchange=exchange, mode=mode, market=market, case=case, stage="setup")
    if not stateful_tests_enabled():
        pytest.skip("Set RUN_LIVE_TRADING_TESTS=1 to run stateful tests.")
    if exchange == "arcus" and market == "spot":
        result.update(stage="not_applicable", status="N/A", skip_reason=ARCUS_SPOT_NA)
        pytest.skip(ARCUS_SPOT_NA)
    reason = not_applicable(exchange, market, case)
    if reason:
        # Decided before any credential is read or client constructed.
        result.update(stage="not_applicable", status="N/A", skip_reason=reason)
        pytest.skip(reason)
    load_dotenv()
    client = None
    try:
        module = "dcex." + ("async_support." if mode == "async" else "") + exchange + ".client"
        cls = importlib.import_module(module).Client
        if exchange == "lighter":
            from dcex.lighter.credentials import credential_env_names

            if any(not os.getenv(name) for name in credential_env_names(market)):
                pytest.skip(f"lighter {market}: missing network-scoped credentials")
            logger = logging.Logger("stateful-no-payload-logging")
            logger.disabled = True
            client = cls.from_env(network=market, preload_product_table=False, logger=logger)
        else:
            client = cls(**client_options(exchange))
        if mode == "async":
            await client.async_init()
        adapter = ADAPTERS.get(exchange, CexAdapter)(client, exchange, market, symbol)
        await run_lifecycle(adapter, result, case=case)
    except NotApplicable as error:
        result.update(stage="not_applicable", status="N/A", skip_reason=redact(error))
        pytest.skip(redact(error))
    except (InsufficientBalance, MarketUnavailable) as error:
        pytest.skip(redact(error))
    except Exception as error:
        result["error_code"] = result.get("error_code") or redact(getattr(error, "code", ""))
        result["error_message"] = result.get("error_message") or redact(error)
        pytest.fail(result["error_message"], pytrace=False)
    finally:
        if client is not None:
            try:
                closed = client.close()
                if inspect.isawaitable(closed):
                    await closed
            except Exception as error:
                pytest.fail("Client close failed: " + redact(error), pytrace=False)
