# 端點覆蓋與驗證

[English](endpoint-audit.md) | **繁體中文**

核對日期：2026-09-27。依提供的 3,180 列報告、官方 API 文件及目前原始碼逐列核對。範圍包括一般行情、交易、帳戶、同帳戶體系轉帳、投資與風控。

[完整可搜尋表](endpoint-coverage.html) · [逐列 JSON 與證據](endpoint-coverage-ledger.json) · [剩餘項目](endpoint-recheck.zh_tw.md) · [新增方法索引](endpoint-methods.zh_tw.md)

## 覆蓋狀態

**所有列都有處理結果，但尚未全部實作。** 列數可能包含重複或合併操作，不能換算為官方端點完成率。

| Status | Rows | Meaning |
| --- | ---: | --- |
| `implemented` | 2838 | Rust 與 Python sync/async 封裝及路由證據 |
| `protocol` | 173 | 共用非同步 WebSocket 協定支援；非每個主題都有專用封裝 |
| `superseded` | 37 | 舊路徑已由目前 API 取代；見各列對應 |
| `excluded` | 111 | 依先前確認的範圍排除 |
| `unavailable` | 9 | 已停用、維護中或缺乏有效官方介面 |
| `blocked` | 10 | 必要規格或權限範圍未確認 |
| `partial` | 2 | 合併列部分完成，仍有明確缺口 |

## 交易所與 Python 方法數

方法數包含公開便利方法、別名與簽章輔助方法，非官方端點數；新增數相對 `d0bbf8b0`。同步與非同步名稱集合已比較一致。

| Exchange / official docs | Sync | Async | New | Implemented rows | Protocol rows | Blocked / partial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [binance](https://developers.binance.com/en/docs) | 645 | 645 | 335 | 645 | 12 | 0 / 1 |
| [bybit](https://bybit-exchange.github.io/docs/v5/intro) | 301 | 301 | 130 | 287 | 23 | 0 / 0 |
| [okx](https://www.okx.com/docs-v5/en/#overview-rest-authentication-making-requests) | 378 | 378 | 201 | 361 | 0 | 0 / 0 |
| [bitget](https://www.bitget.com/docs/catalog/classic-contract-market/classic-contract-market) | 400 | 400 | 261 | 380 | 19 | 0 / 0 |
| [bingx](https://github.com/BingX-API/api-ai-skills) | 169 | 169 | 79 | 149 | 11 | 1 / 0 |
| [kraken](https://docs.kraken.com/api-reference/) | 130 | 130 | 63 | 97 | 29 | 1 / 0 |
| [mexc](https://www.mexc.com/api-docs/spot-v3/introduction) | 156 | 156 | 35 | 128 | 26 | 0 / 0 |
| [kucoin](https://www.kucoin.com/docs-new/v2/rest/ua/get-announcements) | 311 | 311 | 194 | 292 | 4 | 1 / 0 |
| [hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) | 91 | 91 | 44 | 63 | 23 | 0 / 0 |
| [lighter](https://apidocs.lighter.xyz/) | 122 | 122 | 49 | 80 | 14 | 1 / 1 |
| [backpack](https://docs.backpack.exchange/#tag/Account) | 81 | 81 | 16 | 77 | 0 | 1 / 0 |
| [aster](https://github.com/asterdex/api-docs) | 135 | 135 | 46 | 107 | 2 | 5 / 0 |
| [extended](https://api.docs.extended.exchange/) | 64 | 64 | 22 | 47 | 3 | 0 / 0 |
| [ondo](https://docs.ondoperps.xyz/api-reference) | 77 | 77 | 5 | 70 | 3 | 0 / 0 |
| [arcus](https://docs.arcus.xyz/api-reference) | 58 | 58 | 31 | 55 | 4 | 0 / 0 |

## 這次補齊的主要項目

- **Binance:** 子帳戶與帳戶管理、入金問卷／唯讀歷史、PM Earn、逐倉啟停；多市場 WS profiles、COIN-M 時間查詢及呼叫端 token 訂閱。
- **Bybit / OKX / Bitget:** 借貸、槓桿代幣、伺服器時間；網格、DCA、Signal、定投與跟單；UTA 網格與 Reality 基本面。
- **Kraken / MEXC / KuCoin / BingX:** Kraken EditOrder、圖表與市場歷史／資金池統計；MEXC STP、子帳戶 API key、入金及 listen-key；KuCoin UTA/OES/OTC 與各家唯讀對帳查詢。
- **Hyperliquid / Lighter:** 資訊查詢、資金池、質押、帳戶抽象；Lighter 同主帳戶轉帳、租用、explorer、匯出與 maker-only API key。
- **Backpack / Aster / Extended / Arcus:** Backpack vault／prediction／借貸；Aster prediction；Extended 圖表／利息／vault；Arcus api-meta 與排行榜。

## Binance WebSocket 市場選擇

`dcex.ws.binance.PublicClient(profile=...)`：

| Profile | Base URL |
| --- | --- |
| `spot` (default) | `wss://stream.binance.com:9443/ws` |
| `futures_public`, `options_public` | `wss://fstream.binance.com/public/ws` |
| `futures_market`, `options_market` | `wss://fstream.binance.com/market/ws` |
| `coin_futures` | `wss://dstream.binance.com/ws` |

Futures 深度／bookTicker 使用 public；其他市場資料使用 market，需分開連線。Options 每連線上限 200 個訂閱。可用 `subscribe([...])` 傳入官方串流名稱。Rust 對應 `BinancePublicWebSocket::with_profile(profile, timeout)`。

`PrivateClient(profile=...)` 支援 `futures`（預設）、`coin_futures`、`options`、`portfolio_margin`、`margin_risk`。Rust 用 `BinancePrivateWebSocket::with_profile(http_client, profile, timeout, base_url)`。會建立／延長／刪除 listen key，但呼叫端須排程 `keep_alive()`。`margin_risk` 僅涵蓋跨槓桿風險事件；一般交易事件用 `SpotApiClient.subscribe_user_data_listen_token(token)`。建立 Margin token 的 REST 認證規格仍待確認；token 到期前須由呼叫端取得新 token 並重新訂閱。

[USD-M stream docs](https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Connect) · [Margin token docs](https://developers.binance.com/en/docs/products/margin-trading/listen-token-data-stream)

## 限制與驗證

<!-- VERIFICATION -->
Rust `cargo test --workspace --all-features`：**656 項通過**，**53 項需真實交易所存取的測試維持忽略**。原生套件已重新建置並安裝至專案虛擬環境。

Python 全量收集 **12,818 項不重複測試**，分為八組，已確認分組聯集等於完整收集清單。首次執行 12,810 項通過，8 項因測試預期錯誤失敗（Kraken 公開端點認證、Binance 例外型別）。修正後，相關 **315 項 Kraken／Binance 測試全部通過**。最後調整原生綁定以維持空憑證的 `ValueError`，重新建置後 **38 項 Binance WS 測試全部通過**。上述執行結果已無尚未解決的失敗。

修改的 73 個 Python 檔案通過 Ruff 與格式檢查；`pyright dcex` 為 0 錯誤、0 警告。Rust 格式、Git 空白檢查、3,180 列總數與本機文件索引均驗證通過。
<!-- /VERIFICATION -->

未對真實交易所送出下單或帳戶管理操作。離線測試驗證路由、HTTP 動詞、參數、簽章、WS 訊息及回應處理；不代表真實帳戶權限或目前服務可用性。

- OKX SBE 回傳原始位元組，未內建解碼器。
- Lighter explorer 可用 `explorer_base_url` 指定；歷史匯出需要授權，不會自動支付費用。
- 要求錢包授權的操作保留呼叫端簽章；Arcus userPreferences DELETE 需呼叫端提供認證標頭。
- 外部提領／控制與 MM／合作夥伴限定操作排除，唯讀歷史未整類排除。

Source report SHA-256: `6479d7c578f35b2bd9b6a243c37b239dbea399f17054dbecd1edfe98ffd92e07`.
