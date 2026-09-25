# dcex - Rust exchange library

**English** | [繁體中文](https://github.com/pg56714/dcex/blob/main/crates/dcex/README.zh_tw.md)

`dcex` is an async Rust library for DEX and CEX integrations. It provides exchange HTTP clients, public and private WebSocket streams, signing, response validation, and a Product Table for normalized instrument metadata. This crate also powers the Python `dcex` package.

**Broker codes:** The library does not set or attach a broker code or broker tag by default. Callers can provide one explicitly where the exchange API supports it.

> This project is forked from [krex](https://github.com/kairosresearchio/krex), a simplified version of the [ccxt](https://github.com/ccxt/ccxt) Python library.

[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Crates.io](https://img.shields.io/crates/v/dcex)](https://crates.io/crates/dcex)

## Installation

```sh
cargo add dcex
cargo add tokio --features macros,rt-multi-thread
```

The examples below use Tokio's `#[tokio::main]` macro.

## Key features

- Public market data and authenticated account and order HTTP APIs.
- Public market and private user-data WebSocket streams.
- Exchange signing, serialization, and response validation in the Rust core.
- Product Table lookups between normalized and exchange-native symbols, with trading metadata.

Available endpoints differ by exchange. External withdrawal creation endpoints are not wrapped. The Product Table includes listed options from Binance, Bybit, and OKX; option trading uses exchange-specific APIs.

## Supported exchanges

| Exchange | HTTP | WS Public | WS Private |
| --- | --- | --- | --- |
| Binance | Yes | Yes | Yes |
| Bybit | Yes | Yes | Yes |
| OKX | Yes | Yes | Yes |
| Bitget | Yes | Yes | Yes |
| Kraken | Yes | Yes | Yes |
| MEXC | Yes | Yes | Yes |
| BingX | Yes | Yes | Yes |
| KuCoin | Yes | Yes | Yes |
| Hyperliquid | Yes | Yes | Yes |
| Lighter (Mainnet + Robinhood) | Yes | Yes | Yes |
| Backpack | Yes | Yes | Yes |
| Aster | Yes | Yes | Yes |
| Extended | Yes | Yes | Yes |
| Ondo | Yes | Yes | Yes |
| Arcus | Yes | Yes | Yes |

Private WebSocket support includes authenticated or address-scoped user-data streams. Bybit also exposes an authenticated trade WebSocket for order operations.

Lighter supports Mainnet and Robinhood with separate credentials; select the network for each client (Mainnet is the default). Ondo supports perpetual futures only. Arcus Spot uses a separate RFQ router and an externally wallet-signed quote; Arcus Perps is a separate client whose private execution has not yet been live-verified.

## Rust quick start

Public HTTP market data:

```rust
use std::time::Duration;

use dcex::exchanges::binance::BinanceClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BinanceClient::public(Duration::from_secs(10))?;
    let response = client.get_spot_orderbook("BTC-USDT-SPOT").await?;
    println!("{}", response.data);
    Ok(())
}
```

Read-only private account query (requires `BINANCE_API_KEY` and `BINANCE_API_SECRET`):

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

HTTP methods without required parameters need no empty parameter list. Optional parameters use builder setters such as `.limit(100)` or `.param("key", value)`.

Public WebSocket:

```rust
use std::time::Duration;

use dcex::ws::binance::BinancePublicWebSocket;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let mut ws = BinancePublicWebSocket::new(Duration::from_secs(10))?;
    ws.connect().await?;
    ws.subscribe_agg_trades("BTC-USDT-SPOT").await?;
    println!("{}", ws.recv().await?);
    ws.close().await?;
    Ok(())
}
```

## Product Table

A normalized `product_symbol` such as `BTC-USDT-SWAP` identifies the same product across exchanges; `exchange_symbol` is the native symbol. `ProductTable` can fetch one exchange or all exchanges and exposes these fields:

| Fields | Meaning |
| --- | --- |
| `exchange`, `product_symbol`, `exchange_symbol` | Exchange and normalized/native symbols |
| `product_type`, `exchange_type` | Normalized and exchange-specific market types |
| `base_currency`, `quote_currency` | Product currencies |
| `price_precision`, `size_precision` | Price and size increments |
| `min_size`, `min_notional` | Minimum size and notional |
| `size_per_contract` | Contract multiplier |

```rust
use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::product_table::ProductTable;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let table = ProductTable::fetch(Some(Exchange::Binance), Duration::from_secs(10)).await?;
    let native = table.get_exchange_symbol("binance", "BTC-USDT-SWAP")?;
    let normalized = table.get_product_symbol("binance", &native, Some("swap"), None)?;
    println!("{native} -> {normalized}");
    println!("{:?}", table.rows().first());
    Ok(())
}
```

## Examples and license

The repository's [Rust examples](https://github.com/pg56714/dcex/tree/main/crates/dcex/examples) focus on public calls and read-only private queries. From the repository root:

```sh
cargo run -p dcex --example binance_public
cargo run -p dcex --example binance_ws_public
```

Private examples require the corresponding credentials or user address. The [Python package README](https://github.com/pg56714/dcex/blob/main/README.md) covers Python usage. This crate uses the [MIT License](https://github.com/pg56714/dcex/blob/main/LICENSE); see the [third-party notices](https://github.com/pg56714/dcex/blob/main/THIRD_PARTY_NOTICES.md) for additional licenses.
