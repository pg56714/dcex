# dcex

Rust core library for low-latency cross-exchange crypto trading.

This crate contains the exchange HTTP, WebSocket, signing, serialization,
product-table, and response-validation implementation used by the Python
`dcex` package. It can also be used directly from Rust applications without the
Python layer.

## Installation

```sh
cargo add dcex
```

## Example

The examples use Tokio for async execution.

HTTP:

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

HTTP methods that do not require endpoint parameters can be called without an
empty parameter list. Optional query/body parameters are added with builder
setters such as `.limit(100)` or `.param("key", value)`.

WebSocket:

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

Canonical product symbols and exchange-specific symbols are resolved by the
Rust product table:

```rust
use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::product_table::ProductTable;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let table =
        ProductTable::fetch(Some(Exchange::Binance), Duration::from_secs(10)).await?;
    let symbol = table.get_exchange_symbol("binance", "BTC-USDT-SWAP")?;
    println!("{symbol}");
    Ok(())
}
```

## Supported Exchanges

| Exchange        | HTTP | WS Public | WS Private |
| --------------- | ---- | --------- | ---------- |
| **Binance**     | Yes  | Yes       | Yes        |
| **Bybit**       | Yes  | Yes       | Yes        |
| **OKX**         | Yes  | Yes       | Yes        |
| **Bitget**      | Yes  | Yes       | Yes        |
| **Kraken**      | Yes  | Yes       | Yes        |
| **MEXC**        | Yes  | Yes       | Yes        |
| **BitMart**     | Yes  | Yes       | Yes        |
| **BitMEX**      | Yes  | Yes       | Yes        |
| **Gate.io**     | Yes  | Yes       | Yes        |
| **BingX**       | Yes  | Yes       | Yes        |
| **KuCoin**      | Yes  | Yes       | Yes        |
| **Hyperliquid** | Yes  | Yes       | Yes        |
| **Lighter**     | Yes  | Yes       | Yes        |
| **Backpack**    | Yes  | Yes       | Yes        |
| **Aster**       | Yes  | Yes       | Yes        |
| **Extended**    | Yes  | Yes       | Yes        |

WS private support currently covers authenticated or address-scoped user-data
streams. Order placement and cancellation remain on HTTP clients.

Extended private REST reads require `EXTENDED_API_KEY`. Rust-backed LIMIT order
signing additionally requires `EXTENDED_STARK_PRIVATE_KEY`,
`EXTENDED_STARK_PUBLIC_KEY`, and `EXTENDED_VAULT_NUMBER`; `EXTENDED_CLIENT_ID`
is kept for reference but is not sent in normal order requests.

## Python Package Relationship

The PyPI package `dcex` exposes the existing Python sync and async APIs through
PyO3 bindings to this Rust crate. The internal `dcex-python` crate only builds
the Python extension module and is not published to crates.io.

## Disclaimer

Cryptocurrency trading involves significant risk. This library is provided
as-is without any warranty. Users are responsible for their own trading
decisions and risk management.
