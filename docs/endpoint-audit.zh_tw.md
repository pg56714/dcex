# 端點覆蓋與驗證

[English](endpoint-audit.md) | **繁體中文**

核對日期：2026-09-29。原始報表有 3,180 列；目前清冊共 4,846 列，另保存 15 家交易所的官方文件清冊。

所有官方端點均納入範圍，包含提款、地址管理、做市商、RFQ、經紀商、推薦與合作夥伴操作。原先 111 個 excluded 列已處理，沒有保留範圍排除；這不代表所有新發現端點均已實作。

API 提款沒有第二次確認，送出即執行。建議交易用 API 金鑰不要開啟提款權限。需要錢包授權的操作保留呼叫端提供的簽章；不臆測未公開的簽章規格。

[互動覆蓋表](endpoint-coverage.html) · [逐列證據](endpoint-coverage-ledger.json) · [待處理項目](endpoint-recheck.zh_tw.md) · [方法索引](endpoint-methods.zh_tw.md)

## 覆蓋狀態

清冊可能包含歷史列、分組列與重疊操作，不能用列數計算官方端點覆蓋百分比。

| 狀態 | 列數 | 定義 |
| --- | ---: | --- |
| `implemented` | 3,696 | 具備精確離線 HTTP 路由證據及 Rust／Python 公開方法 |
| `protocol` | 403 | 非同步 WebSocket 協定支援，附離線驗證證據；不代表線上認證 |
| `superseded` | 686 | 歷史端點或群組列，已由目前的明確列取代 |
| `unavailable` | 19 | 官方停用、目前不可用的操作，或沒有獨立端點的文件章節 |
| `unverified` | 11 | 已有包裝，但部分官方規格不完整 |
| `blocked` | 30 | 缺少必要簽章或授權規格 |
| `partial` | 1 | 群組能力仍有明確記錄的缺口 |
| `pending` | 0 | 已列入官方清冊，待實作或專屬驗證 |

## 交易所與 Python 方法

方法數包含別名與簽章輔助方法，不是端點數；新增數以 `d0bbf8b0` 為基準。

| 交易所 | 公開方法 | 新增 | 已實作列 | 待處理列 |
| --- | ---: | ---: | ---: | ---: |
| [binance](official-endpoint-inventory/binance.json) | 758 | 449 | 748 | 0 |
| [bybit](official-endpoint-inventory/bybit.json) | 448 | 278 | 434 | 0 |
| [okx](official-endpoint-inventory/okx.json) | 404 | 228 | 388 | 0 |
| [bitget](official-endpoint-inventory/bitget.json) | 638 | 500 | 610 | 0 |
| [bingx](official-endpoint-inventory/bingx.json) | 210 | 121 | 191 | 0 |
| [kraken](official-endpoint-inventory/kraken.json) | 164 | 98 | 148 | 0 |
| [mexc](official-endpoint-inventory/mexc.json) | 176 | 56 | 157 | 0 |
| [kucoin](official-endpoint-inventory/kucoin.json) | 368 | 252 | 340 | 0 |
| [hyperliquid](official-endpoint-inventory/hyperliquid.json) | 146 | 100 | 118 | 0 |
| [lighter](official-endpoint-inventory/lighter.json) | 136 | 64 | 110 | 0 |
| [backpack](official-endpoint-inventory/backpack.json) | 82 | 18 | 79 | 0 |
| [aster](official-endpoint-inventory/aster.json) | 157 | 69 | 152 | 0 |
| [extended](official-endpoint-inventory/extended.json) | 72 | 31 | 72 | 0 |
| [ondo](official-endpoint-inventory/ondo.json) | 78 | 7 | 72 | 0 |
| [arcus](official-endpoint-inventory/arcus.json) | 90 | 50 | 77 | 0 |

## 驗證與限制

<!-- VERIFICATION -->
- Rust 通過: `685`
- Rust 線上測試略過: `53`
- Python 通過: `21985`
- Python 未選取: `944`
- Python 略過: `0`
- Python 預期失敗: `0`
- 未解決測試失敗: `0`
- 原生擴充已重建: `True`
- 原生建置模式: `release`
- 既有 Clippy 警告: `14`
<!-- /VERIFICATION -->

離線測試驗證路由、HTTP 方法、參數、簽章、WebSocket 訊息與回應處理，不能證明真實帳戶權限或交易所線上可用性。沒有送出真實訂單、提款或帳戶管理操作。

- OKX/Bitget SBE 回傳原始位元組，未內建解碼器。
- Lighter explorer 使用獨立 base URL；歷史匯出不會自動付費。
- `unverified` 與 `blocked` 的具體缺口及解除條件保留在清冊中。
