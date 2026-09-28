# 端點 schema 與請求 adapter 慣例

一般 REST 端點使用 `crates/dcex/src/exchanges/schema.rs` 的共用請求引擎，
集中處理欄位型別、十進位格式、必填與重複欄位、遞迴 JSON 約束、陣列及表單編碼。
`input_contracts.json` 是 Rust `input_contracts.rs` 與 Python `_input_codec.py`／
`_input_validation.py` 共用的明確輸入 schema 來源；`_schema_codec.py` 保留相容匯入。
Python 在轉成 native 字串參數前，依端點宣告檢查原始值。

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

Rust 共同核心為 `mod.rs`、`client.rs`、`market.rs`、`trade.rs`、
`params.rs`、`signing.rs`、`private.rs`、`tests.rs` 與
`tests/endpoint_coverage.rs`。每個 Python 同步／非同步套件均有 `client.py`
及上述四個 HTTP 模組。所有私有 dispatch 入口（含 Arcus 現貨）放在
`private.rs`，商品處理邏輯保留在所屬模組。僅在有獨立實作時才需要
account／商品檔案。`tests/unit/test_exchange_structure.py` 依原生註冊清單
檢查每個交易所是否遵守此配置。

## 數字與 wire 格式

數值驗證依交易所、端點與欄位的 `format: decimal` 明確宣告，包含巢狀 properties／
items 及 Python 別名。不得依欄位名稱推測數值語意或套用例外。手寫 adapter 也必須在
同一份輸入 catalog 宣告欄位。各端點的 `input_schema` 由 catalog 重新產生；
wire schema 保留既有型別與結構約束。

已宣告的 decimal 拒絕 Python float／bool、科學記號字串及非數字；呼叫者提供精確
字串或 `Decimal`，整數值仍遵循既有端點規則。負數預設拒絕，僅明確標示 `x-signed`
的欄位允許。`x-positive` 排除零值，其他零值限制仍由端點檢查。
Kraken 已宣告的 REST place／edit／amend 與 V1 addOrder／editOrder 價格欄位使用
`x-relative: kraken_relative_price`，共用規則為 `[+\-#][0-9]+(\.[0-9]+)?%?`；
其他交易所不繼承此例外。`x-decimal-sentinels` 明確列出 OKX 市價選擇值，以及
Bitget／Bybit 不變更或未使用投資欄位的空字串。Hyperliquid builder 費率以
`x-percent` 明確允許百分比尾碼。保證金增減值、價差價格及 RFQ／portfolio 數量
逐欄位允許負號。識別碼、token、布林值及未宣告欄位不因名稱而被視為金額，
仍須通過各端點原有型別檢查。

明確宣告 JSON `number` 的 schema 可將精確的
一般十進位字串編碼為 JSON number；Rust 使用 `serde_json` 任意精度功能，
不經過 `f64` 中介值。範圍比較與值的序列化分開處理。

陣列的位置與編碼方式（JSON、重複 query key 或索引 key）屬於傳輸 adapter。
Binance prediction 批次取消要求非空 `cancelInfoList`；共用表單編碼器保留
key 中的原始括號，仍正常跳脫 value。簽章與實際送出的位元組完全一致。

## 重新產生與驗證

在儲存庫根目錄執行：

```powershell
uv run --no-sync python -m scripts.build_input_contracts --write
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
uv run --no-sync python -m scripts.build_input_contracts --check
```

再次執行後檔案必須一致。執行既有端點 wire／簽章測試、共用同步／非同步 wrapper
測試及 schema codec 回歸測試。Decimal 測試逐一走訪 REST／WS 的所有宣告欄位，
並驗證已接入的 Python 公開方法；新增欄位須補宣告及實際請求回歸。更新 evidence 路徑後，重新執行
`scripts/build_endpoint_docs.py` 及其 `--check`。重建 native 前，檢查已載入的
`.pyd` 模組並確認可以獨占開啟。行為修正與純搬檔必須分開提交；不得手動修改
`CHANGELOG.md`。

### 明確驗證邊界與證據粒度

未宣告欄位**完全不進行數值驗證**。完整性守門獨立盤點公開簽章、wire 別名、
可變參數操作及 list/dict 參數；非數值例外逐項記錄於
`tests/fixtures/input_contract_exemptions.json`。新增數值參數而未補宣告會使測試失敗。
`format: decimal` 預設允許零；`x-positive: true` 要求嚴格大於零。
無零值控制語意的訂單數量及轉帳金額採正值限制，取消設定所用零值及官方哨兵值保留原語意。

Kraken V1 `amendOrder` 的限價／觸發價也允許相對價格。
條件平倉 `close[price]`／`close[price2]`（Python `close_price`／`close_price2`）
繼承對應價格規則，依據 [Kraken V1 addOrder 官方文件](https://docs-legacy.kraken.com/api/docs/websocket-v1/addorder/)。
[Kraken 期貨偏移值](https://docs.kraken.com/api-reference/order-management/send-order)允許正負十進位值，單位由另一欄位指定。
[OKX 模擬 idxVol](https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder)為 -0.99 至 1 的有號十進位值。
[Backpack 官方文件](https://docs.backpack.exchange/)將 triggerQuantity 描述為字串數量，
但未明確說明百分比後綴；目前不知道是否支援，因此不據此新增百分比例外（查核日期：2026-09-29）。

Rust ledger 中沒有 `::symbol` 的引用刻意維持**檔案層級證據**：
只證明來源檔存在，不代表特定函式已覆蓋該路由。有符號引用時仍驗證符號；
路由層級的證據由專屬 wire 測試提供。superseded 理由須包含至少四個不同單字，
不能用重複單一字串填滿長度門檻。
