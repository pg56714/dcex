# dcex - DEX & CEX trading library

**Important**: No default broker tags are set. You may manually specify a broker tag within function arguments if needed.

> Forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

> Originally created and maintained by the same contributor, this fork continues active development, building upon the original foundation with enhanced design, unified DEX + CEX support, and fixes for previously unresolved issues.

A high-performance and lightweight Python and Rust library for interacting with cryptocurrency exchanges. dcex offers Python clients backed by a Rust core, plus direct Rust APIs for low-level HTTP, WebSocket, signing, and exchange integrations.

Scope note: dcex focuses on market data, account queries, trading/order APIs, and market/user-data streams. External withdrawal creation endpoints are not currently wrapped. The unified Product Table Manager includes listed options from Binance, Bybit, and OKX; option trading remains exchange-specific.

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
| **BingX**       | Yes       | Yes        | Yes       | Yes        |
| **KuCoin**      | Yes       | Yes        | Yes       | Yes        |
| **Hyperliquid** | Yes       | Yes        | Yes       | Yes        |
| **Lighter (Mainnet + Robinhood)** | Yes | Yes | Yes | Yes |
| **Backpack**    | Yes       | Yes        | Yes       | Yes        |
| **Aster**       | Yes       | Yes        | Yes       | Yes        |
| **Extended**    | Yes       | Yes        | Yes       | Yes        |
| **Ondo**        | Yes       | Yes        | Yes       | Yes        |
| **Arcus**       | Yes       | Yes        | Yes       | Yes        |

WS private support covers authenticated or address-scoped user-data streams.
Bybit additionally exposes an authenticated `/v5/trade` WebSocket for single
and batch order create/amend/cancel requests; its acknowledgement is not a fill
confirmation.

### Lighter networks

Lighter network selection is explicit per HTTP or WebSocket client. Mainnet and
Robinhood use independent credential groups, so both can run concurrently in a
single process. There is no global `LIGHTER_NETWORK` selector and the legacy
mainnet-only `LIGHTER_*` credential fallback is not accepted.

Private Mainnet clients read `LIGHTER_MAINNET_ACCOUNT_INDEX`,
`LIGHTER_MAINNET_API_KEY_INDEX`, and `LIGHTER_MAINNET_API_PRIVATE_KEY`.
Robinhood clients use the corresponding `LIGHTER_ROBINHOOD_*` variables.
Select the deployment for each client with `dcex.lighter.Network`; omitting it
keeps the Mainnet default.

### Ondo

The [official API](https://ondoperps.mintlify.app/) currently lists only
perpetual futures trading endpoints, not spot endpoints. dcex supports Ondo
perpetual futures only; private access uses `ONDO_API_KEY_ID` and
`ONDO_API_SECRET`.

### Arcus

[Arcus Spot](https://github.com/arcus-xyz/arcus-spot-sdk) uses a separate RFQ
router. `dcex.arcus()` supports token discovery, prices, firm quotes, validated
assembly and submission of an externally wallet-signed EIP-712 quote, and
status checks; public hosted quotes need no API key. Wallet signing and any
required token permit/approval remain the caller's responsibility.

Arcus Perps uses `dcex.arcus(market="perps")` and separate Ed25519 credentials.
Market/account queries, single-order placement and cancellation, fills,
positions, cancel-all, leverage changes, and same-wallet internal transfers
are implemented. Private Perps execution remains unverified until an account
with Perps access is available; external withdrawals are intentionally not
supported.

### Bitget Reality

Bitget Reality rTokens use the UTA V3 API. dcex supports instrument limits,
stock-session and closure metadata, regular UTA trading, dedicated Reality
place/cancel endpoints, and the authenticated Reality orderbook/fills REST
queries. `dcex.ws.bitget.reality_private(...)` exposes the UTA V3 Reality
orderbook channel. Bitget requires BD whitelist access for Reality depth and
platform fills; these are not required for order execution.

### MEXC stock-linked products

The public Spot `exchangeInfo` identifies tokenized stocks through the
`Tokenized Stocks` concept category. Futures `contract/detail` identifies stock
contracts through `mc-trade-zone-Stock` and reports `apiAllowed`. The Product
Table Manager keeps their standard Spot/Swap routing and marks their
`exchange_type` as `tokenized_stock` or `stock_perpetual`. These products are
distinct from MEXC RealStocks, whose separate API is not integrated.
Spot size precision comes from `baseAssetPrecision`, while
`quoteAmountPrecision` is the minimum order amount. Some stock tokens report
`baseSizePrecision=0`; their executable minimum quantity still depends on the
current price and order rules.

### Backpack stock RFQ limits

Stock RFQ quantity limits vary by market session. The Product Table Manager
reports the largest minimum quantity and step size across sessions as a
conservative summary; query `get_rfq_constraints(symbol, session_name)` before
trading to obtain the limits for the intended session.

### OKX X-Perps

OKX publishes X-Perps through `instType=FUTURES`; normal X-Perps use
`ruleType=xperp` and pre-market X-Perps use `ruleType=pre_market`.
`instCategory=3` denotes stocks. The product table preserves
the `FUTURES` API type and the reported `ctVal` contract size rather than
treating these products as ordinary `SWAP` instruments.

### Binance Options

Binance Options is available through the exchange-specific sync, async, and
Rust clients. Supported REST workflows include contract discovery, index and
mark prices with Greeks, klines, open interest, order books, trades, account
and position queries, single and batch order management, exercise records,
commissions, and user-data listen keys. Market-maker-only controls are not
wrapped. The Product Table Manager maps listed Binance options to normalized
symbols while the exchange-specific API still accepts native option symbols.

### Binance COIN-M Futures and Convert

The Binance exchange-specific Rust, synchronous Python, and asynchronous Python
clients expose COIN-M market data, balances, positions, and basic order
placement/query/cancellation through the official `dapi` host. COIN-M methods
currently require native symbols such as `BTCUSD_PERP`; they are not yet
mapped by the unified Product Table Manager. Convert covers pair limits, asset
precision, quotes, quote acceptance, order status/history, and limit-order
management through `sapi`. Balance-changing calls are not included in
read-only live tests.

### Binance Margin

Binance cross and isolated margin are available through the exchange-specific
sync, async, and Rust clients. The API covers margin assets and pairs, account
risk and liabilities, borrow/repay and interest history, borrowing and transfer
limits, and the full margin-order lifecycle. Margin orders support Binance's
`sideEffectType`, including `AUTO_BORROW_REPAY`; borrowing, repayment, and
order placement are never performed by the default test suite.

### Binance Simple Earn

Binance Simple Earn flexible and locked products are available through the
exchange-specific sync, async, and Rust clients. Supported workflows include
product discovery, account and position queries, subscriptions, redemptions,
and subscription, redemption, and reward histories. Live tests are read-only;
subscriptions and redemptions are covered by offline request tests only.

### Binance Crypto Loan

Binance Flexible Loan v2 is available through the exchange-specific sync,
async, and Rust clients. The API covers loanable and collateral assets,
interest rates, active loans, borrowing, repayment, LTV adjustment, liquidation
records, and history. Legacy stable-rate loan history remains queryable. Live
tests are read-only; borrowing, repayment, and collateral changes are covered
by offline request tests only.

### Binance Staking

Binance ETH Staking, SOL Staking, On-chain Yields, and Soft Staking are
available through the exchange-specific sync, async, and Rust clients. The
wrappers cover accounts, quotas, products, positions, subscriptions,
redemptions, wrapping, reward and rate histories, and product settings. Live
tests are read-only; staking, redemption, reward claims, and setting changes
are covered by offline request tests only.

### Binance Sub Account

Binance standard Sub Account queries and internal asset transfers are available
through the exchange-specific sync, async, and Rust clients. Supported queries
cover account lists and status, assets, spot, margin and futures summaries,
futures position risk, and transfer history. Transfers are limited to wallets
and accounts under the same master account. Account creation, product
activation, API-key or IP management, managed sub-accounts, deposits, and
withdrawals are intentionally not wrapped.

### KuCoin Margin and Lending

KuCoin cross and isolated margin are available through the exchange-specific
sync, async, and Rust clients. Supported workflows cover margin limits and
risk, borrowing, repayment, interest history, leverage settings, and margin
lending purchase, modification, redemption, and order history. Live tests are
read-only; all operations that change balances or liabilities are covered by
offline request tests only.

### KuCoin Earn and Sub Account

KuCoin Simple Earn, staking, structured Earn, and Dual Investment discovery
are available through the exchange-specific sync, async, and Rust clients.
The wrappers also cover Classic and UTA sub-account lists and balances plus
the existing internal transfer workflow. Live tests are read-only; Earn
purchases and redemptions are covered by offline request tests only. Account
creation, API-key management, deposits, and withdrawals are intentionally not
wrapped.

### Bybit Finance and Transfers

Bybit supports UTA manual borrowing and repayment, spot-margin risk and
interest queries, fixed-rate borrowing, Easy Earn, On-chain Earn, Fixed Saving,
Hold-to-Earn, BYUSDT, RWA Earn, and Advanced Earn workflows, plus
account-to-account asset transfers. Easy and On-Chain Earn include APR history,
coupons, and eligible On-Chain position auto-reinvestment. Fixed Saving covers
products, positions, orders, subscriptions, eligible early redemption, and
automatic reinvestment. Hold-to-Earn exposes
airdrop products and yield records. BYUSDT covers minting, redemption,
positions, orders, yield records, and APR history. RWA Earn exposes products,
NAV charts, positions, order history, and asynchronous staking/redemption;
mutation routes are not exercised live. Advanced Earn covers Dual Assets,
Smart Leverage, Double Win, and Discount Buy product discovery,
quotes, positions, order history, redemption estimates, leverage calculations,
and supported stake or redemption orders. Liquidity Mining supports pool
discovery, positions, orders, yield and liquidation history, liquidity changes,
reinvestment, margin top-ups, and interest claims. Spot X Launchpool supports
project discovery, current staking, operation logs, and completed position
history. Universal transfers can move assets between master and sub-account
UIDs; live tests only query balances, limits,
products, positions, histories, and transfer records and never create a loan,
Earn order, or transfer.

### Bybit RFQ

Bybit RFQ is available through the Rust core and exchange-specific sync and
async clients. The complete REST workflow covers configuration, public block
trades, real-time and historical RFQs and quotes, detailed RFQ records, trade
history, creation, cancellation, non-LP quote acceptance, quoting, and quote
execution. Bybit requires signed access for the public-trades route and limits
RFQ trading to eligible UTA 2.0 accounts; it is unavailable to Demo users.
Live tests call read-only endpoints only, while every state-changing route is
validated offline.

### Bitget Finance

Bitget supports Crypto Loans and Savings/Elite Earn through the Rust core and
exchange-specific sync and async clients. Loan discovery, interest,
liabilities, repayment and adjustment histories, Earn products, account
assets, order status, and record queries are included. Balance-changing
operations are covered offline only.

### Kraken Earn

Kraken Earn wrappers cover strategy discovery, allocations, allocation and
deallocation requests, and their status queries. Live coverage is read-only;
fund allocation changes are tested offline only.

Kraken Futures also exposes the dead man's switch
(`cancel_futures_all_orders_after`); a timeout of `0` disables it.

### OKX Finance and Sub Accounts

OKX wrappers cover Savings, staking, ETH/SOL staking, flexible loans, Dual
Investment, OKUSD, spot borrowing/repayment, option market analytics, and
sub-account balances, bills, interest limits, and internal transfers. Live
coverage is read-only; subscriptions, redemptions, loans, staking actions, and
transfers are tested offline only.

OKX Easy Convert currency discovery, conversion, and recent history are
available through the exchange-specific clients. Hyperliquid also exposes
agent-signed transfers between the owner's DEX balances; the destination
address is fixed to the configured wallet. Neither conversion nor transfer is
called by read-only live tests.

### MEXC and BingX Sub Accounts

MEXC and BingX expose master-account sub-account lists, balances/assets, and
internal transfer history through sync, async, and Rust clients. Their
master/sub-account transfer routes are implemented but are never called by the
default or read-only live suites. Account lifecycle and API-key administration
are intentionally not wrapped.

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
| product_type      | The normalized product type used by dcex, e.g. `spot`, `swap`, `futures`, `option`                                                                                                                                         |
| exchange_type     | The exchange-specific product type, e.g. `spot`, `linear`, `inverse`, `perpetual`, `delivery`                                                                                                                              |
| base_currency     | The base currency, e.g. `BTC`                                                                                                                                                                                              |
| quote_currency    | The quote currency, e.g. `USDT`                                                                                                                                                                                            |
| price_precision   | The price precision, e.g. `0.000001`                                                                                                                                                                                       |
| size_precision    | The size precision, e.g. `0.000001`                                                                                                                                                                                        |
| min_size          | The minimum size, e.g. `0.000001`                                                                                                                                                                                          |
| min_notional      | The minimum notional, e.g. `0.000001`                                                                                                                                                                                      |
| size_per_contract | The size per contract. Sometimes 1 contract is not the same as 1 unit in exchanges like OKX.                                                                                                                               |

Listed Binance, Bybit, and OKX options are included in PTM. Their normalized symbols use `BASE-QUOTE-YYMMDD-STRIKE-C|P-OPTION` (for example, `BTC-USDT-260925-145000-C-OPTION`); the original exchange symbol remains available in `exchange_symbol`. Quote currencies are part of the normalized symbol, while contract size remains exchange-specific metadata.

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

For live tests, copy `.env.example` to the ignored `.env` file and fill in only
the credentials you need. Leave the live-trading flags empty until intentionally
running those tests.

Live, private, stateful, and generated-report tests use the pytest markers
configured in `pyproject.toml`. These tests are opt-in because they can require
network access, exchange credentials, or account state.

Stateful order tests require `RUN_LIVE_TRADING_TESTS=1`. Tests that intentionally
seek a real fill additionally require `RUN_LIVE_FILL_TESTS=1` in both Python and
Rust. Use a dedicated account with no open orders or positions; a failed test
may still need manual order or position cleanup.

Lighter live tests can target Mainnet, Robinhood, or both. Stateful Lighter
tests create real orders and include post-test cancellation, reduce-only
position closing, and a final clean-account assertion. Use only dedicated,
initially empty accounts when enabling `RUN_LIVE_TRADING_TESTS=1`.

Ondo's opt-in tests cover post-only cancellation and, with the fill flag,
a small perpetual fill followed by a reduce-only close.

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
