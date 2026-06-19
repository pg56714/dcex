# dcex

Rust trading library for dcex exchange integrations.

The crate contains the Rust implementation used by the Python `dcex` package
and can also be used directly from Rust applications.

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

## Exchange Examples

Read-only public examples are available for the migrated exchange clients:

```sh
cargo run -p dcex --example binance_public
cargo run -p dcex --example bybit_public
cargo run -p dcex --example okx_public
cargo run -p dcex --example bitget_public
cargo run -p dcex --example kraken_public
cargo run -p dcex --example mexc_public
cargo run -p dcex --example bitmart_public
cargo run -p dcex --example bitmex_public
```

## Benchmark

Run the live public HTTP benchmark from the workspace root:

```sh
cargo run -p dcex --example public_http_benchmark --release
```

Run the local CPU-bound benchmark from the workspace root:

```sh
cargo run -p dcex --example core_local_benchmark --release
```

Set `DCEX_BENCH_ITERATIONS`, `DCEX_BENCH_WARMUP`, and
`DCEX_BENCH_INNER_LOOPS` to change the run length.
Set `DCEX_BENCH_OUTPUT=json` when another script needs machine-readable
results.
