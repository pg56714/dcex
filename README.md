# dcex - DEX & CEX trading library

**Important**: No default broker tags are set. You may manually specify a broker tag within function arguments if needed.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

> Originally created and maintained by the same contributor, this fork continues active development, building upon the original foundation with enhanced design, unified DEX + CEX support, and fixes for previously unresolved issues.

A high-performance and lightweight Python and Rust library for interacting with cryptocurrency exchanges. dcex offers synchronous and asynchronous Python clients backed by a Rust core, plus direct Rust APIs for low-level HTTP, signing, and exchange integrations.

Scope note: dcex focuses on market data, account queries, and trading/order APIs. External withdrawal creation endpoints are not currently wrapped, and options support is limited to exchange-specific APIs rather than the unified Product Table Manager.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/dcex)](https://badge.fury.io/py/dcex)

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

Examples are under `examples/sync` and `examples/async`. See
[examples/README.md](examples/README.md) for the example conventions.

## Benchmarking

Local CPU-bound benchmarks isolate code paths where the Rust core can avoid
Python interpreter overhead. Benchmark scripts are kept in the repo, but
benchmark output files are not committed.

Recorded local CPU-bound sample (`.\.venv\Scripts\python.exe examples\benchmark_core_local.py --iterations 20`, 2026-06-19):

Speedups are measured against the pure Python fallback implementation for the
same local CPU-bound operation.

| Operation | PyO3 bridge speedup | Rust native speedup |
| --------- | ------------------- | ------------------- |
| Cryptographic hash | 89.06x | 85.50x |
| Schnorr signature | 496.43x | 448.37x |
| Transaction payload signing | 309.08x | 368.78x |

Public HTTP benchmarks are live network measurements, so results depend on
exchange latency and local network conditions.

Recorded sample (`uv run python examples/benchmark_public_http.py --iterations 20`, 2026-06-19):

| Target | Iterations | Median ms | Mean ms | Min ms | Max ms | Median vs main |
| ------ | ---------- | --------- | ------- | ------ | ------ | -------------- |
| main native Python | 20 | 49.275 | 50.212 | 47.293 | 55.561 | 1.00x |
| PyO3 Python wrapper | 20 | 46.998 | 48.918 | 45.664 | 86.677 | 1.05x |
| Rust native | 20 | 46.916 | 46.884 | 45.249 | 48.730 | 1.05x |

| Layer | Command | Output |
| ----- | ------- | ------ |
| Local CPU-bound Python vs PyO3 vs Rust native | `uv run python examples/benchmark_core_local.py --iterations 20` | Speedup table |
| Rust native local CPU-bound only | `cargo run -p dcex --example core_local_benchmark --release` | Timing table |
| main native Python vs PyO3 vs Rust native | `uv run python examples/benchmark_public_http.py --iterations 20` | Markdown table |
| Rust native only | `cargo run -p dcex --example public_http_benchmark --release` | Markdown table |
| Optional local CPU-bound CSV output | `uv run python examples/benchmark_core_local.py --csv benchmark_core.csv` | Ignored local CSV file |
| Optional public HTTP CSV output | `uv run python examples/benchmark_public_http.py --csv benchmark_public.csv` | Ignored local CSV file |

The public HTTP Python benchmark archives the local `main` git ref for the
native Python baseline, then measures the current PyO3-backed Python wrapper
and the Rust crate benchmark in one table. Use `--main-ref` when you need a
different local baseline ref. Use `DCEX_BENCH_ITERATIONS`, `DCEX_BENCH_WARMUP`,
`DCEX_BENCH_INNER_LOOPS`, and `DCEX_BENCH_OUTPUT=json` for Rust-only examples
when needed.

## Release Publishing

The Python release workflow publishes only when Commitizen creates a version
bump on `main`. A bumped Python release builds wheels and publishes the Python
package to PyPI. If no version bump is detected, PyPI is not updated.

The Rust crate has an independent version in `crates/dcex/Cargo.toml` and is
published from `rust-v*` tags. For example, `rust-v0.1.0` publishes crate
version `0.1.0` to crates.io and creates a separate GitHub Release.

## License

This project is licensed under the [MIT License](LICENSE).

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/pg56714/dcex/issues).
- **Discussions**: Discuss ideas and share your thoughts on [GitHub Discussions](https://github.com/pg56714/dcex/discussions).

## Disclaimer

Cryptocurrency trading involves significant risk. This library is provided as-is without any warranty. Users are responsible for their own trading decisions and risk management.
