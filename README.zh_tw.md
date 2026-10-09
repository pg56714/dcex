# dcex — DEX 與 CEX 交易函式庫

[English](README.md) | **繁體中文**

dcex 是以 Rust 為核心的交易所函式庫，提供 Python 同步／非同步介面及可直接使用的 Rust crate。它涵蓋市場資料、帳戶查詢、訂單 API 與公開／私人 WebSocket 資料流。

**Broker code：**dcex 不預設或自動附加 broker code、broker tag。若交易所 API 支援相關欄位，可由呼叫端明確指定。

> 本專案衍生自 [krex](https://github.com/kairosresearchio/krex)；krex 是 [ccxt](https://github.com/ccxt/ccxt) Python 函式庫的簡化版本。

[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://python.org)
[![Rust](https://img.shields.io/badge/rust-2024-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/dcex)](https://badge.fury.io/py/dcex)
[![Crates.io](https://img.shields.io/crates/v/dcex)](https://crates.io/crates/dcex)

## 安裝

Python：

```sh
pip install dcex
# 或在使用 uv 管理的專案中：
uv add dcex
```

Rust：

```sh
cargo add dcex
```

## 主要功能

- Python 同步與非同步 HTTP 客戶端，以及公開與私人 WebSocket 客戶端。
- 可直接用於 Rust 專案的 HTTP、WebSocket 與簽章實作。
- Product Table Manager（PTM）統一交易所商品代號與交易規格。
- 支援多個 CEX 與 DEX；實際可用的端點依交易所而異。

官方提款、做市商與合作夥伴端點均納入範圍；實作覆蓋與規格缺口以端點清冊為準。API 提款沒有第二次確認，送出即執行；建議交易用 API 金鑰不要開啟提款權限。PTM 包含 Binance、Bybit 與 OKX 已上市期權；期權交易仍使用各交易所專屬 API。

## 支援交易所

| 交易所 | 同步 HTTP | 非同步 HTTP | 公開 WS | 私人 WS |
| --- | --- | --- | --- | --- |
| Binance | 支援 | 支援 | 支援 | 支援 |
| Bybit | 支援 | 支援 | 支援 | 支援 |
| OKX | 支援 | 支援 | 支援 | 支援 |
| Bitget | 支援 | 支援 | 支援 | 支援 |
| Kraken | 支援 | 支援 | 支援 | 支援 |
| MEXC | 支援 | 支援 | 支援 | 支援 |
| BingX | 支援 | 支援 | 支援 | 支援 |
| KuCoin | 支援 | 支援 | 支援 | 支援 |
| Hyperliquid | 支援 | 支援 | 支援 | 支援 |
| Lighter (Mainnet + Robinhood) | 支援 | 支援 | 支援 | 支援 |
| Backpack | 支援 | 支援 | 支援 | 支援 |
| Aster | 支援 | 支援 | 支援 | 支援 |
| Extended | 支援 | 支援 | 支援 | 支援 |
| Ondo | 支援 | 支援 | 支援 | 支援 |
| Arcus | 支援 | 支援 | 支援 | 支援 |

Bitget 自 2026-09-15 起遷移至 UTA；本函式庫已移除 Bitget 對 UTA 帳戶回傳錯誤 40085 的 classic 帳戶私有端點，仍可使用的公開行情、稅務與機構借貸端點則保留。交易請使用 UTA 帳戶。參閱 [官方 UTA 升級指南](https://www.bitget.com/docs/classic/uta-api-upgrade-guide) 與 [帳戶設定](https://www.bitget.com/docs/catalog/account/account-settings)。

私人 WebSocket 包含需驗證身分或指定地址的使用者資料流；Binance、Bybit、Bitget、OKX、KuCoin 與 Kraken 現貨提供交易 WebSocket；Hyperliquid 與 Lighter 可提交已簽名操作，Arcus 提供簽名請求建立介面。Lighter Mainnet 與 Robinhood 使用不同憑證；可逐一為客戶端選擇網路，預設為 Mainnet；參閱 [.env.example](.env.example) 與 [Lighter 範例](examples/async/lighter_private_readonly.py)。Ondo 現貨目前僅支援公開行情（depth、trades、symbol_info、history 與 WS 現貨頻道）；官方尚未公布現貨交易 API，因此下單、撤單等私有操作傳入 `-SPOT` symbol 會在本地報錯，不會送出請求。

## Python 快速開始

同步 HTTP：

```python
import dcex

client = dcex.binance()
print(client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m"))
```

非同步 HTTP：

```python
import asyncio
import dcex.async_support as dcex

async def main():
    client = await dcex.binance()
    try:
        print(await client.get_klines(product_symbol="BTC-USDT-SWAP", interval="1m"))
    finally:
        await client.close()

asyncio.run(main())
```

另提供 Binance Alpha、Aster Prediction、KuCoin Classic／Pro 與 Kraken 現貨 V1 介面。Bitget SBE 回傳原始二進位封包，由呼叫端解碼。

公開 WebSocket：

```python
import asyncio
from dcex.ws import binance

async def main():
    async with binance.public() as ws:
        await ws.subscribe_agg_trades("BTC-USDT-SPOT")
        print(await ws.recv())

asyncio.run(main())
```

## Product Table Manager

PTM 將 `BTC-USDT-SWAP` 這類統一 `product_symbol` 對應到交易所原生 `exchange_symbol`，並提供交易規格；客戶端在適用時會使用此對應。

| 商品 | `product_symbol` | 範例 |
| --- | --- | --- |
| 現貨 | `BASE-QUOTE-SPOT` | `BTC-USDT-SPOT` |
| 永續 | `BASE-QUOTE-SWAP` | `BTC-USDT-SWAP` |
| 到期期貨 | `BASE-QUOTE-YYMMDD-FUTURES`（UTC 交割日） | `BTC-USD-261225-FUTURES` |

| 欄位 | 說明 |
| --- | --- |
| `exchange`、`product_symbol`、`exchange_symbol` | 交易所及統一／原生商品代號 |
| `product_type`、`exchange_type` | 統一及交易所專屬市場類型 |
| `base_currency`、`quote_currency` | 商品幣別 |
| `price_precision`、`size_precision` | 價格及數量增量 |
| `min_size`、`min_notional` | 最小數量及名目金額 |
| `size_per_contract` | 每張合約的乘數 |

```python
from dcex.product_table.manager import ProductTableManager

table = ProductTableManager.get_instance("binance")
print(table.get_exchange_symbol("binance", "BTC-USDT-SWAP"))
print(table.get_product_symbol("binance", "BTCUSDT", product_type="swap"))
print(table.rows()[0])
```

## 更多範例與開發

可執行範例位於 [Python 同步](examples/sync)、[Python 非同步及 WebSocket](examples/async) 與 [Rust](crates/dcex/examples)。範例以公開資料或唯讀帳戶查詢為主；私人 HTTP 範例需憑證，私人資料流範例需憑證或使用者地址。

```sh
uv run python examples/sync/binance_public.py
uv run python examples/async/binance_ws_public.py
cargo run -p dcex --example binance_ws_public
```

直接使用 Rust 的說明見 [crate README](crates/dcex/README.zh_tw.md)。預設測試套件可透過 `uv run pytest` 離線執行；即時測試須自行啟用。開發與測試詳情見[貢獻指南](.github/CONTRIBUTING.md)。

本專案採用 [MIT 授權](LICENSE)；其他授權資訊見[第三方聲明](THIRD_PARTY_NOTICES.md)。

[端點覆蓋、限制與驗證紀錄](docs/endpoint-audit.zh_tw.md)。
