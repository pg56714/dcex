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

## Benchmark

Run the live public HTTP benchmark from the workspace root:

```sh
cargo run -p dcex --example public_http_benchmark --release
```

Set `DCEX_BENCH_ITERATIONS` and `DCEX_BENCH_WARMUP` to change the run length.
