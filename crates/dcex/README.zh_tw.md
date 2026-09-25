# dcex — Rust 交易所函式庫

[English](https://github.com/pg56714/dcex/blob/main/crates/dcex/README.md) | **繁體中文**

`dcex` 是整合 DEX 與 CEX 的非同步 Rust 函式庫，提供交易所 HTTP 客戶端、公開與私人 WebSocket 資料流、簽章、回應驗證，以及統一商品資料的 Product Table。此 crate 也是 Python `dcex` 套件的核心。

**Broker code：**函式庫不預設或自動附加 broker code、broker tag；交易所 API 支援時，可由呼叫端明確指定。

> 本專案衍生自 [krex](https://github.com/kairosresearchio/krex)；krex 是 [ccxt](https://github.com/ccxt/ccxt) Python 函式庫的簡化版本。

[![Rust](https://img.shields.io/badge/rust-2021-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Crates.io](https://img.shields.io/crates/v/dcex)](https://crates.io/crates/dcex)

## 安裝

```sh
cargo add dcex
cargo add tokio --features macros,rt-multi-thread
```

以下範例使用 Tokio 的 `#[tokio::main]` 巨集。

## 主要功能

- 公開市場資料及需驗證身分的帳戶、訂單 HTTP API。
- 公開市場與私人使用者資料 WebSocket 資料流。
- Rust 核心內的交易所簽章、序列化與回應驗證。
- 透過 Product Table 查詢統一／原生商品代號及交易規格。

實際可用的端點依交易所而異。目前不封裝建立外部提領的端點。Product Table 包含 Binance、Bybit 與 OKX 已上市期權；期權交易使用各交易所專屬 API。

## 支援交易所

| 交易所 | HTTP | 公開 WS | 私人 WS |
| --- | --- | --- | --- |
| Binance | 支援 | 支援 | 支援 |
| Bybit | 支援 | 支援 | 支援 |
| OKX | 支援 | 支援 | 支援 |
| Bitget | 支援 | 支援 | 支援 |
| Kraken | 支援 | 支援 | 支援 |
| MEXC | 支援 | 支援 | 支援 |
| BingX | 支援 | 支援 | 支援 |
| KuCoin | 支援 | 支援 | 支援 |
| Hyperliquid | 支援 | 支援 | 支援 |
| Lighter (Mainnet + Robinhood) | 支援 | 支援 | 支援 |
| Backpack | 支援 | 支援 | 支援 |
| Aster | 支援 | 支援 | 支援 |
| Extended | 支援 | 支援 | 支援 |
| Ondo | 支援 | 支援 | 支援 |
| Arcus | 支援 | 支援 | 支援 |

私人 WebSocket 包含需驗證身分或指定地址的使用者資料流；Bybit 另提供可進行訂單操作的驗證交易 WebSocket。

Lighter 支援 Mainnet 與 Robinhood，兩者使用不同憑證；可逐一為客戶端選擇網路，預設為 Mainnet。Ondo 僅支援永續合約。Arcus Spot 使用獨立的 RFQ router，送出報價時須由外部錢包簽章；Arcus Perps 使用另一個客戶端，其私人交易流程尚未經實際環境驗證。

## Rust 快速開始

公開 HTTP 市場資料：

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

唯讀私人帳戶查詢（需 `BINANCE_API_KEY` 與 `BINANCE_API_SECRET`）：

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

沒有必填參數的 HTTP 方法不需傳入空參數列表；選填參數可使用 `.limit(100)` 或 `.param("key", value)` 等 builder 方法。

公開 WebSocket：

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

`BTC-USDT-SWAP` 這類統一 `product_symbol` 可跨交易所識別同一商品；`exchange_symbol` 是交易所原生代號。`ProductTable` 可取得單一或全部交易所的資料，並提供以下欄位：

| 欄位 | 說明 |
| --- | --- |
| `exchange`、`product_symbol`、`exchange_symbol` | 交易所及統一／原生商品代號 |
| `product_type`、`exchange_type` | 統一及交易所專屬市場類型 |
| `base_currency`、`quote_currency` | 商品幣別 |
| `price_precision`、`size_precision` | 價格及數量增量 |
| `min_size`、`min_notional` | 最小數量及名目金額 |
| `size_per_contract` | 每張合約的乘數 |

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

## 範例與授權

儲存庫中的 [Rust 範例](https://github.com/pg56714/dcex/tree/main/crates/dcex/examples) 以公開呼叫與唯讀私人查詢為主。在儲存庫根目錄執行：

```sh
cargo run -p dcex --example binance_public
cargo run -p dcex --example binance_ws_public
```

私人範例需相應憑證或使用者地址。[Python 套件 README](https://github.com/pg56714/dcex/blob/main/README.zh_tw.md) 說明 Python 用法。此 crate 採用 [MIT 授權](https://github.com/pg56714/dcex/blob/main/LICENSE)；其他授權資訊見[第三方聲明](https://github.com/pg56714/dcex/blob/main/THIRD_PARTY_NOTICES.md)。
