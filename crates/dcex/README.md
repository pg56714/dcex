# dcex

Rust core library for low-latency cross-exchange crypto trading.

This crate contains the exchange HTTP, WebSocket, signing, serialization,
product-table, and response-validation implementation used by the Python
`dcex` package. It can also be used directly from Rust applications without the
Python layer.

## Example

```rust
use std::time::Duration;

use dcex::exchanges::binance::BinanceClient;

#[tokio::main]
async fn main() -> dcex::Result<()> {
    let client = BinanceClient::new(None, None, Duration::from_secs(10))?;
    let response = client.get_server_time("spot").await?;
    println!("{}", response.data);
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
| **Hyperliquid** | Yes  | No        | No         |
| **Lighter**     | Yes  | No        | No         |
| **Backpack**    | Yes  | No        | No         |
| **Aster**       | Yes  | No        | No         |

WS private support currently covers authenticated user-data streams. Order
placement and cancellation remain on HTTP clients.

## Exchange Examples

Read-only public examples are available for the migrated exchange clients:

```sh
cargo run -p dcex --example aster_public
cargo run -p dcex --example backpack_public
cargo run -p dcex --example binance_public
cargo run -p dcex --example bingx_public
cargo run -p dcex --example bitget_public
cargo run -p dcex --example bitmart_public
cargo run -p dcex --example bitmex_public
cargo run -p dcex --example bybit_public
cargo run -p dcex --example gateio_public
cargo run -p dcex --example hyperliquid_public
cargo run -p dcex --example kraken_public
cargo run -p dcex --example kucoin_public
cargo run -p dcex --example lighter_public
cargo run -p dcex --example mexc_public
cargo run -p dcex --example okx_public
```

WebSocket examples are available for exchanges that have stream support in the
Rust core:

```sh
cargo run -p dcex --example binance_ws_public
cargo run -p dcex --example bingx_ws_public
cargo run -p dcex --example bybit_ws_public
cargo run -p dcex --example okx_ws_public
cargo run -p dcex --example bitget_ws_public
cargo run -p dcex --example bitmart_ws_public
cargo run -p dcex --example bitmex_ws_public
cargo run -p dcex --example gateio_ws_public
cargo run -p dcex --example kraken_ws_public
cargo run -p dcex --example kucoin_ws_public
cargo run -p dcex --example mexc_ws_public
cargo run -p dcex --example binance_ws_private_readonly
cargo run -p dcex --example bingx_ws_private_readonly
cargo run -p dcex --example bitget_ws_private_readonly
cargo run -p dcex --example bitmart_ws_private_readonly
cargo run -p dcex --example bitmex_ws_private_readonly
cargo run -p dcex --example bybit_ws_private_readonly
cargo run -p dcex --example gateio_ws_private_readonly
cargo run -p dcex --example kraken_ws_private_readonly
cargo run -p dcex --example kucoin_ws_private_readonly
cargo run -p dcex --example mexc_ws_private_readonly
cargo run -p dcex --example okx_ws_private_readonly
```

Private read-only WebSocket examples require exchange credentials in environment
variables and only open user-data streams.

## Python Package Relationship

The PyPI package `dcex` exposes the existing Python sync and async APIs through
PyO3 bindings to this Rust crate. The internal `dcex-python` crate only builds
the Python extension module and is not published to crates.io.
