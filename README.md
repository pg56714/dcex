# dcex - DEX & CEX trading library

**Important**: No default broker tags are set. You may manually specify a broker tag within function arguments if needed.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

> Originally created and maintained by the same contributor, this fork continues active development, building upon the original foundation with enhanced design, unified DEX + CEX support, and fixes for previously unresolved issues.

A high-performance and lightweight Python and Rust library for interacting with cryptocurrency exchanges. dcex offers synchronous and asynchronous Python clients backed by a Rust core, plus direct Rust APIs for low-level HTTP, signing, and exchange integrations.

Scope note: dcex focuses on market data, account queries, and trading/order APIs. External withdrawal creation endpoints are not currently wrapped, and options support is limited to exchange-specific APIs rather than the unified Product Table Manager.

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

or add it manually:

```toml
[dependencies]
dcex = "0.1.0"
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

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

### Rust Usage

```rust
use std::time::Duration;

use dcex::exchanges::binance::{BinanceClient, BinanceMarket};
use dcex::http::HttpMethod;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BinanceClient::new(None, None, Duration::from_secs(10))?;
    let response = client
        .request_raw(
            HttpMethod::Get,
            BinanceMarket::Spot,
            "/api/v3/time",
            Vec::new(),
            false,
        )
        .await?;
    println!("{}", response.text()?);
    Ok(())
}
```

## Supported Exchanges

| Exchange        | Sync Support | Async Support |
| --------------- | ------------ | ------------- |
| **Binance**     | Yes          | Yes           |
| **Bybit**       | Yes          | Yes           |
| **OKX**         | Yes          | Yes           |
| **Bitget**      | Yes          | Yes           |
| **Kraken**      | Yes          | Yes           |
| **MEXC**        | Yes          | Yes           |
| **BitMart**     | Yes          | Yes           |
| **BitMEX**      | Yes          | Yes           |
| **Gate.io**     | Yes          | Yes           |
| **BingX**       | Yes          | Yes           |
| **KuCoin**      | Yes          | Yes           |
| **Hyperliquid** | Yes          | Yes           |
| **Lighter**     | Yes          | Yes           |
| **Backpack**    | Yes          | Yes           |
| **Aster**       | Yes          | Yes           |

## Key Features

- Product Table Manager for unifying trading instruments across exchanges
- Sync and async Python API clients with consistent interfaces where available
- Native Rust core for exchange HTTP, signing, serialization, and response validation
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

## Examples

Python examples are under `examples/sync` and `examples/async`. Rust examples
are under `crates/dcex/examples`. See [examples/README.md](examples/README.md)
for the example conventions.

## Benchmarking

Local CPU-bound benchmarks isolate Lighter signing and hashing hot paths. The
baseline is the PyPI `dcex==0.21.2` native Python implementation, fixed at
`1.00x`; this keeps the comparison reproducible after this branch is merged
into `main`. Rust-backed Python is the current Python API calling the Rust core
through PyO3. The baseline is identified by package source and version because
the current working tree may still report the same Python package version until
the next release bump.

Recorded sample (`uv run python examples/benchmark_core_local.py --iterations 50 --warmup 5 --baseline-version 0.21.2`, 2026-06-20):

Baseline: PyPI `dcex==0.21.2` native Python implementation = 1.00x.

| Operation | Rust-backed Python | Rust native |
| --------- | ------------------ | ----------- |
| Cryptographic hash | 135.87x | 142.05x |
| Schnorr signature | 648.68x | 672.18x |
| Transaction payload signing | 395.80x | 595.90x |

Public HTTP benchmarks install the same PyPI baseline and compare live Binance
server-time calls against the current PyO3-backed Python wrapper and Rust
native example. Treat those results as an end-to-end latency check, not as the
primary evidence for CPU-bound signing speed, because exchange latency and
local network conditions dominate the measurement.

| Layer | Command | Output |
| ----- | ------- | ------ |
| Local CPU-bound PyPI baseline vs current core | `uv run python examples/benchmark_core_local.py --iterations 50 --warmup 5 --baseline-version 0.21.2` | Speedup table |
| Rust native local CPU-bound only | `cargo run -p dcex --example core_local_benchmark --release` | Timing table |
| Public HTTP PyPI baseline vs current core | `uv run python examples/benchmark_public_http.py --iterations 20 --baseline-version 0.21.2` | Markdown table |
| Rust native only | `cargo run -p dcex --example public_http_benchmark --release` | Markdown table |
| Optional local CPU-bound CSV output | `uv run python examples/benchmark_core_local.py --csv benchmark_core.csv` | Ignored local CSV file |
| Optional public HTTP CSV output | `uv run python examples/benchmark_public_http.py --csv benchmark_public.csv` | Ignored local CSV file |

The Python benchmark scripts install the PyPI baseline into a temporary target
directory with `uv pip install --target`; they do not mutate the current
environment. Use `--baseline-version` when you need to compare against another
published Python package version. Use `DCEX_BENCH_ITERATIONS`,
`DCEX_BENCH_WARMUP`, `DCEX_BENCH_INNER_LOOPS`, and `DCEX_BENCH_OUTPUT=json` for
Rust-only examples when needed.

## Release Publishing

The release workflow detects Conventional Commit changes on `main` and plans
Python and Rust releases independently. A bumped Python release builds wheels
and publishes the Python package to PyPI. If no Python version bump is
detected, PyPI is not updated.

The Rust crate has an independent version in `crates/dcex/Cargo.toml` and is
published from `rust-v*` tags. For example, `rust-v0.1.0` publishes crate
version `0.1.0` to crates.io and creates a separate GitHub Release.
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
