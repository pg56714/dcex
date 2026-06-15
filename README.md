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
dcex = "0.21.2"
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

We welcome contributions. Please see our [Contributing Guide](.github/CONTRIBUTING.md) for details.

## Testing

The default test suite is offline and does not require exchange API keys or network access:

```bash
uv run pytest
```

For live, private, stateful, and generated-report test commands, see the
[Contributing Guide](.github/CONTRIBUTING.md#testing).

## Examples

Examples are under `examples/sync` and `examples/async`. See
[examples/README.md](examples/README.md) for the example conventions.

## Benchmarking

Public HTTP benchmarks are live network measurements, so results depend on
exchange latency and local network conditions. Benchmark scripts are kept in the
repo, but benchmark output files are not committed.

| Layer | Command | Output |
| ----- | ------- | ------ |
| Rust direct crate | `cargo run -p dcex --example public_http_benchmark --release` | Markdown table |
| Python wrapper + PyO3 bridge | `uv run python examples/benchmark_public_http.py --iterations 20` | Markdown table |
| Optional local CSV output | `uv run python examples/benchmark_public_http.py --csv benchmark.csv` | Ignored local CSV file |

Use `DCEX_BENCH_ITERATIONS` and `DCEX_BENCH_WARMUP` for the Rust example when
you need a longer run.

## Release Publishing

The release workflow publishes only when Commitizen creates a version bump on
`main`. A bumped release builds Python wheels, publishes the Rust crate
(`dcex`) to crates.io, and publishes the Python package to PyPI after the crate
publish succeeds. If no version bump is detected, neither registry is updated.

## License

This project is licensed under the [MIT License](LICENSE).

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/pg56714/dcex/issues).
- **Discussions**: Discuss ideas and share your thoughts on [GitHub Discussions](https://github.com/pg56714/dcex/discussions).

## Disclaimer

Cryptocurrency trading involves significant risk. This library is provided as-is without any warranty. Users are responsible for their own trading decisions and risk management.
