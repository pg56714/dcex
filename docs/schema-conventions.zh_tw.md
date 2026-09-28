# 端點 schema 與請求 adapter 慣例

一般 REST 端點使用 `crates/dcex/src/exchanges/schema.rs` 的共用請求引擎，
集中處理欄位型別、十進位格式、必填與重複欄位、遞迴 JSON 約束、陣列及表單編碼。
Python 的 `dcex/_schema_codec.py` 在轉成 native 字串參數前檢查原始值：
拒絕財務數字的 `float`，並將 `Decimal` 無損轉成固定小數格式。

交易所 adapter 保留主機選擇、商品代碼轉換、認證、跨欄位業務條件，以及官方指定的
欄位位置與 wire 型別。密碼學簽署內容、呼叫者已簽署交易、多步驟操作及跨欄位條件
仍使用手寫程式，但也必須通過共用欄位與數字編碼器。不要新增另一套通用 JSON
驗證器，也不要將十進位輸入轉成浮點數後再序列化。

## 檔案配置

- `schemas/*.json`：納入版本控制的端點及欄位資料。`table_*.json` 為固定傳輸表；
  `routes_*.json` 為需要條件 adapter 的路由。各業務 catalog 同時保留官方來源與
  Python 名稱。共用讀取器以 wire 名稱優先於 Python 名稱。
- `generated/*.rs` 與 Python `_generated/*_http.py`：產生的宣告與 adapter。
  修改來源 schema 或產生器後重新產生。
- `schema_requests.rs` 與 `schema_requests/`：交易所連接共用引擎的 adapter。
  商品專屬 adapter 可留在對應商品模組。
- `private.rs`：所有交易所統一使用此名稱放置私有方法分派。
- `withdrawals.rs`／`_withdrawals_http.py`：提領及轉給其他使用者；
  `transfers.rs`／`_transfers_http.py`：自有帳戶之間的轉移；
  `batch.rs`／`_batch_http.py`：批次操作。公開方法名稱保持相容。
- Rust `tests.rs` 僅宣告測試模組；路由覆蓋統一放在 `tests/endpoint_coverage.rs`，
  其餘測試依主題拆分。
- Python client 由 `_http_manager.py`、`_market_http.py`、`_trade_http.py`、
  `_account_http.py` 與商品 mixin 組成。Arcus 現貨及永續保留各自公開類別，
  採用相同的檔案職責。

## 數字與 wire 格式

價格、數量與金額使用一般十進位字串；在送出前拒絕 Python 浮點數、科學記號字串、
不合法負值與非數字。整數、布林值與識別碼保留原有型別；可帶負號的識別碼不是金額。
保證金增減值及 OKX `tpOrdPx`／`slOrdPx=-1` 市價選擇值保留原有契約；
一般 schema 金額仍須為非負數。
原本允許的零值仍由各端點條件檢查。明確宣告 JSON `number` 的 schema 可將精確的
一般十進位字串編碼為 JSON number；Rust 使用 `serde_json` 任意精度功能，
不經過 `f64` 中介值。範圍比較與值的序列化分開處理。
Kraken EditOrder 相對價格、RFQ／portfolio 的帶正負號數量，以及 Bitget TPSL
空白 size 選擇值保留各自端點語意。可帶負號的 JSON number 以 `x-signed`
明確宣告；呼叫者提供精確字串或 `Decimal`。

陣列的位置與編碼方式（JSON、重複 query key 或索引 key）屬於傳輸 adapter。
Binance prediction 批次取消要求非空 `cancelInfoList`；共用表單編碼器保留
key 中的原始括號，仍正常跳脫 value。簽章與實際送出的位元組完全一致。

## 重新產生與驗證

在儲存庫根目錄執行：

```powershell
uv run --no-sync python -m scripts.build_binance_wrappers
uv run --no-sync python -m scripts.build_bitget_wrappers
uv run --no-sync python -m scripts.build_bybit_wrappers
uv run --no-sync python -m scripts.build_bingx_wrappers
uv run --no-sync python -m scripts.build_hyperliquid_wrappers
uv run --no-sync python -m scripts.build_kucoin_wrappers
uv run --no-sync python -m scripts.build_schema_tables
uv run --no-sync ruff format dcex scripts
uv run --no-sync ruff check dcex scripts --fix
uv run --no-sync ruff format dcex scripts
cargo fmt --all
```

再次執行後檔案必須一致。執行既有端點 wire／簽章測試、共用同步／非同步 wrapper
測試及 schema codec 回歸測試。更新 evidence 路徑後，重新執行
`scripts/build_endpoint_docs.py` 及其 `--check`。重建 native 前，檢查已載入的
`.pyd` 模組並確認可以獨占開啟。行為修正與純搬檔必須分開提交；不得手動修改
`CHANGELOG.md`。
