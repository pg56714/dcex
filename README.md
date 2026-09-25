# dcex - DEX & CEX trading library

**English** | [繁體中文](README.zh_tw.md)

dcex is a Rust-backed exchange library with synchronous and asynchronous Python clients and a standalone Rust crate. It covers market data, account queries, order APIs, and public and private WebSocket streams.

**Broker codes:** dcex does not set or attach a broker code or broker tag by default. You can specify one explicitly when the exchange API supports it.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Rust](https://img.shields.io/badge/rust-2024-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/dcex)](https://badge.fury.io/py/dcex)
[![Crates.io](https://img.shields.io/crates/v/dcex)](https://crates.io/crates/dcex)

## Installation

Python:

```sh
pip install dcex
# or, in a uv-managed project:
uv add dcex
```

Rust:

```sh
cargo add dcex
```

## Key features

- Synchronous and asynchronous Python HTTP clients, plus public and private WebSocket clients.
- HTTP, WebSocket, and signing APIs for direct use from Rust.
- A Product Table Manager (PTM) that normalizes exchange symbols and trading specifications.
- Support for multiple CEX and DEX platforms; available endpoints vary by exchange.

External withdrawal creation endpoints are not wrapped. PTM includes listed options from Binance, Bybit, and OKX; option trading remains exchange-specific.

## Supported exchanges

| Exchange | HTTP Sync | HTTP Async | WS Public | WS Private |
| --- | --- | --- | --- | --- |
| Binance | Yes | Yes | Yes | Yes |
| Bybit | Yes | Yes | Yes | Yes |
| OKX | Yes | Yes | Yes | Yes |
| Bitget | Yes | Yes | Yes | Yes |
| Kraken | Yes | Yes | Yes | Yes |
| MEXC | Yes | Yes | Yes | Yes |
| BingX | Yes | Yes | Yes | Yes |
| KuCoin | Yes | Yes | Yes | Yes |
| Hyperliquid | Yes | Yes | Yes | Yes |
| Lighter (Mainnet + Robinhood) | Yes | Yes | Yes | Yes |
| Backpack | Yes | Yes | Yes | Yes |
| Aster | Yes | Yes | Yes | Yes |
| Extended | Yes | Yes | Yes | Yes |
| Ondo | Yes | Yes | Yes | Yes |
| Arcus | Yes | Yes | Yes | Yes |

Private WebSocket support includes authenticated or address-scoped user-data streams. Bybit also provides an authenticated trade WebSocket for order operations. Lighter Mainnet and Robinhood use separate credential profiles; select the network per client (Mainnet is the default); see [.env.example](.env.example) and the [Lighter examples](examples/async/lighter_private_readonly.py). Ondo support covers perpetual futures only.

## Python quick start

Synchronous HTTP:

```python
import dcex

client = dcex.binance()
print(client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m"))
```

Asynchronous HTTP:

```python
import asyncio
import dcex.async_support as dcex

async def main():
    client = await dcex.binance()
    try:
        print(await client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m"))
    finally:
        await client.close()

asyncio.run(main())
```

Public WebSocket:

```python
import asyncio
from dcex.ws import binance

async def main():
    async with binance.public() as ws:
        await ws.subscribe_agg_trades("BTC-USDT-SPOT")
        print(await ws.recv())

asyncio.run(main())
```

## Product Table Manager

PTM maps normalized `product_symbol` values, such as `BTC-USDT-SWAP`, to exchange-native `exchange_symbol` values and exposes trading metadata. Clients use this mapping where applicable.

| Fields | Meaning |
| --- | --- |
| `exchange`, `product_symbol`, `exchange_symbol` | Exchange and normalized/native symbols |
| `product_type`, `exchange_type` | Normalized and exchange-specific market types |
| `base_currency`, `quote_currency` | Product currencies |
| `price_precision`, `size_precision` | Price and size increments |
| `min_size`, `min_notional` | Minimum size and notional |
| `size_per_contract` | Contract multiplier |

```python
from dcex.product_table.manager import ProductTableManager

table = ProductTableManager.get_instance("binance")
print(table.get_exchange_symbol("binance", "BTC-USDT-SWAP"))
print(table.get_product_symbol("binance", "BTCUSDT", product_type="swap"))
print(table.rows()[0])
```

## More examples and development

Runnable examples are in [Python sync](examples/sync), [Python async and WebSocket](examples/async), and [Rust](crates/dcex/examples). They focus on public data or read-only account queries. Private HTTP examples require credentials; private stream examples require credentials or a user address.

```sh
uv run python examples/sync/binance_public.py
uv run python examples/async/binance_ws_public.py
cargo run -p dcex --example binance_ws_public
```

For direct Rust usage, see the [crate README](crates/dcex/README.md). The default test suite runs offline with `uv run pytest`; live suites are opt-in. See the [contributing guide](.github/CONTRIBUTING.md) for development and testing details.

This project uses the [MIT License](LICENSE); see the [third-party notices](THIRD_PARTY_NOTICES.md) for additional licenses.
