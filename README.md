# dcex - DEX & CEX trading library

**Important**: No default broker tags are set. You may manually specify a broker tag within function arguments if needed.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

> Originally created and maintained by the same contributor, this fork continues active development, building upon the original foundation with enhanced design, unified DEX + CEX support, and fixes for previously unresolved issues.

A high-performance and lightweight Python and Rust library for interacting with cryptocurrency exchanges. dcex offers Python clients backed by a Rust core, plus direct Rust APIs for low-level HTTP, WebSocket, signing, and exchange integrations.

Scope note: dcex focuses on market data, account queries, trading/order APIs, and market/user-data streams. External withdrawal creation endpoints are not currently wrapped, and options support is limited to exchange-specific APIs rather than the unified Product Table Manager.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/dcex)](https://badge.fury.io/py/dcex)
[![Crates.io](https://img.shields.io/crates/v/dcex)](https://crates.io/crates/dcex)

## Installation

Python:

```bash
pip install dcex
```

or use `uv` to manage the project:

```bash
uv add dcex
```

Rust:

```bash
cargo add dcex
```

Direct Rust usage is also documented in [crates/dcex/README.md](crates/dcex/README.md).

## Quick Start

### Python Synchronous Usage

```python
import dcex

client = dcex.binance()

klines = client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m")
print(klines)
```

### Python Asynchronous Usage

```python
import os
import asyncio
import dcex.async_support as dcex
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

async def main():
    client = await dcex.binance(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET
    )

    try:
        result = await client.get_income_history()
        print(result)

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Python WebSocket Usage

```python
import asyncio

from dcex.ws import binance


async def main():
    async with binance.public() as ws:
        await ws.subscribe_agg_trades("BTC-USDT-SPOT")
        print(await ws.recv())


if __name__ == "__main__":
    asyncio.run(main())
```

### Rust Usage

```rust
use std::time::Duration;

use dcex::exchanges::binance::BinanceClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let api_key = std::env::var("BINANCE_API_KEY").expect("Set BINANCE_API_KEY");
    let api_secret = std::env::var("BINANCE_API_SECRET").expect("Set BINANCE_API_SECRET");
    let client = BinanceClient::new(Some(api_key), Some(api_secret), Duration::from_secs(10))?;
    let response = client.get_income_history().await?;
    println!("{}", response.data);
    Ok(())
}
```

Rust HTTP methods that do not require endpoint parameters can be called without
passing `None` or an empty parameter list. Optional query/body parameters are
added with builder setters such as `.limit(100)` or `.param("key", value)`.

## Supported Exchanges

| Exchange        | HTTP Sync | HTTP Async | WS Public | WS Private |
| --------------- | --------- | ---------- | --------- | ---------- |
| **Binance**     | Yes       | Yes        | Yes       | Yes        |
| **Bybit**       | Yes       | Yes        | Yes       | Yes        |
| **OKX**         | Yes       | Yes        | Yes       | Yes        |
| **Bitget**      | Yes       | Yes        | Yes       | Yes        |
| **Kraken**      | Yes       | Yes        | Yes       | Yes        |
| **MEXC**        | Yes       | Yes        | Yes       | Yes        |
| **BitMEX**      | Yes       | Yes        | Yes       | Yes        |
| **BingX**       | Yes       | Yes        | Yes       | Yes        |
| **KuCoin**      | Yes       | Yes        | Yes       | Yes        |
| **Hyperliquid** | Yes       | Yes        | Yes       | Yes        |
| **Lighter**     | Yes       | Yes        | Yes       | Yes        |
| **Backpack**    | Yes       | Yes        | Yes       | Yes        |
| **Aster**       | Yes       | Yes        | Yes       | Yes        |
| **Extended**    | Yes       | Yes        | Yes       | Yes        |

WS private support currently covers authenticated or address-scoped user-data
streams. Order placement and cancellation remain on HTTP clients.

## Key Features

- Product Table Manager for unifying trading instruments across exchanges
- HTTP clients with consistent sync and async interfaces where available
- Native Rust core for exchange HTTP, WebSocket, signing, serialization, and response validation
- Public and private WebSocket stream clients across the supported exchanges
- Direct Rust crate (`dcex`) for applications that do not need the Python layer
- Opt-in live test suites for public, private, stateful, and generated-report endpoints

## What is Product Table Manager (PTM)?

PTM is a utility that standardizes and unifies trading instrument metadata across different exchanges, making cross-exchange strategy development easier.

It is a table that contains the following columns:

| Column            | Description                                                                                                                                                                                                                |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| exchange          | The exchange name                                                                                                                                                                                                          |
| product_symbol    | The symbol we use to identify the product, it will be the same in different exchanges. For example, `BTC-USDT-SWAP` is the same product in Binance and Bybit, which named `BTCUSDT` in Binance and `BTC-USDT-SWAP` in OKX. |
| exchange_symbol   | The symbol that the exchange actually uses                                                                                                                                                                                 |
| product_type      | The normalized product type used by dcex, e.g. `spot`, `swap`, `futures`                                                                                                                                                   |
| exchange_type     | The exchange-specific product type, e.g. `spot`, `linear`, `inverse`, `perpetual`, `delivery`                                                                                                                              |
| base_currency     | The base currency, e.g. `BTC`                                                                                                                                                                                              |
| quote_currency    | The quote currency, e.g. `USDT`                                                                                                                                                                                            |
| price_precision   | The price precision, e.g. `0.000001`                                                                                                                                                                                       |
| size_precision    | The size precision, e.g. `0.000001`                                                                                                                                                                                        |
| min_size          | The minimum size, e.g. `0.000001`                                                                                                                                                                                          |
| min_notional      | The minimum notional, e.g. `0.000001`                                                                                                                                                                                      |
| size_per_contract | The size per contract. Sometimes 1 contract is not the same as 1 unit in exchanges like OKX.                                                                                                                               |

Options are not currently included in the unified PTM output. Some exchange-specific clients expose option-related parameters or market endpoints, but options are not normalized across exchanges.

## How to use Product Table Manager?

In most cases, dcex handles product-symbol mapping internally. If you have a specific use case, you can use `ptm` to get the information you need.

```python
from dcex.utils.common import Common
from dcex.product_table.manager import ProductTableManager

ptm = ProductTableManager.get_instance(Common.BINANCE)

product_symbol = ptm.get_product_symbol(
    exchange=Common.BINANCE,
    exchange_symbol="BTCUSDT",
    product_type="swap",
)

print(product_symbol)

rows = ptm.rows()
ptm.write_csv("binance_product_table.csv")
```

## Contributing

Contributions are welcome through GitHub issues and pull requests. Run the
default test suite before opening a pull request.

## Testing

The default test suite is offline and does not require exchange API keys or network access:

```bash
uv run pytest
```

Live, private, stateful, and generated-report tests use the pytest markers
configured in `pyproject.toml`. These tests are opt-in because they can require
network access, exchange credentials, or account state.

## Benchmarking

Local CPU-bound benchmarks isolate Lighter signing and hashing hot paths. The
recorded sample below compares an older native-Python baseline with current
published Rust-backed artifacts and keeps package versions fixed so the
comparison is repeatable on the same machine. The benchmark auto-calibrates
per-operation inner loops and aggregates multiple process runs to reduce timer,
GC, and scheduler noise.

Recorded sample (`uv run python scripts/benchmark_core_local.py --iterations 50 --warmup 5 --target-batch-ms 100 --process-runs 3 --python-baseline-version 0.21.2 --pyo3-version 0.26.3 --rust-crate-version 0.4.4`, 2026-07-03):

Baseline: PyPI `dcex==0.21.2` native Python implementation = 1.00x.
Rust-backed Python: PyPI `dcex==0.26.3`; Rust native: crates.io `dcex==0.4.4`.

| Operation | Rust-backed Python | Rust native |
| --------- | ------------------ | ----------- |
| Cryptographic hash | 92.45x | 113.10x |
| Schnorr signature | 607.72x | 596.91x |
| Transaction payload signing | 491.29x | 514.83x |

| Layer | Command | Output |
| ----- | ------- | ------ |
| Local CPU-bound release artifacts | `uv run python scripts/benchmark_core_local.py --iterations 50 --warmup 5 --target-batch-ms 100 --process-runs 3 --python-baseline-version 0.21.2 --pyo3-version 0.26.3 --rust-crate-version 0.4.4` | Speedup table |
| Optional local CPU-bound CSV output | `uv run python scripts/benchmark_core_local.py --csv benchmark_core.csv` | Ignored local CSV file |

The Python benchmark scripts install PyPI packages into temporary target
directories with `uv pip install --target`, then compile the Rust benchmark
harness against the requested crates.io package version. They do not mutate the
current environment. Use `--python-baseline-version`, `--pyo3-version`, and
`--rust-crate-version` when you need to compare against other published
artifacts.

## Release Publishing

The release workflow detects Conventional Commit changes on `main` and plans
Python and Rust releases independently. A bumped Python release builds wheels
and publishes the Python package to PyPI. If no Python version bump is
detected, PyPI is not updated.

The Rust crate has an independent version in `crates/dcex/Cargo.toml` and is
published from `rust-v*` tags. For example, `rust-vX.Y.Z` publishes crate
version `X.Y.Z` to crates.io and creates a separate GitHub Release.
The `crates/dcex-python` package is an internal PyO3 build crate and is not
published to crates.io; the Python package version is managed only in
`pyproject.toml`.

## License

This project is licensed under the [MIT License](LICENSE).

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/pg56714/dcex/issues).
- **Discussions**: Discuss ideas and share your thoughts on [GitHub Discussions](https://github.com/pg56714/dcex/discussions).

## Disclaimer

Cryptocurrency trading involves significant risk. This library is provided as-is without any warranty. Users are responsible for their own trading decisions and risk management.
