# 端點複核：剩餘項目

[English](endpoint-recheck.md) | **繁體中文**

核對日期：2026-09-27。原始 HTML 的 **3,180 列均已分類**，但**尚未全部實作**。有 **10 列受規格阻礙、2 列部分完成**；合併列可能含多個操作，因此這不是「只剩 12 個端點」。另有 9 列停用／維護中／缺乏有效介面，以及 111 列依範圍排除。

[完整可搜尋表](endpoint-coverage.html) · [逐列 JSON 與證據](endpoint-coverage-ledger.json) · [覆蓋與驗證](endpoint-audit.zh_tw.md)

## 仍需確認規格

| 原始列號 | 交易所 | 端點／操作 | 狀態及原因 |
| ---: | --- | --- | --- |
| 8 | binance | Margin user data (margin-stream.binance.com, /sapi/v1/margin/listen-key) | **partial** — 已支援跨槓桿風險串流生命週期，以及呼叫端提供 token 的交易／帳戶訂閱。POST /sapi/v1/userListenToken 的官方頁面未明列認證與簽章規格，官方 SDK 也沒有對應實作；REST 建立 token 尚未封裝。 [Docs](https://developers.binance.com/en/docs/products/margin-trading/listen-token-data-stream) |
| 1906 | bingx | GET /openApi/spot/v1/server/time | **blocked** — 舊版 Spot server/time 路徑未出現在目前官方文件，是否仍可用或被哪個路徑取代不知道；目前有封裝官方已文件化的時間查詢。 [Docs](https://github.com/BingX-API/api-ai-skills) |
| 2037 | kraken | GET/POST/PUT/DELETE /funding/v1/* , /funding/v2/deposit/addresses (15 endpoints) | **blocked** — Funding Beta 合併列有 15 個操作，其中 11 個一般查詢／入金操作缺乏可確認的 API-Nonce 與 GET 簽章前置字串規格；另 4 個外部提領／地址寫入操作依範圍排除。已補舊版唯讀查詢，但不代表 Beta 遷移完成。 [Docs](https://docs.kraken.com/api-reference/) |
| 2472 | kucoin | DELETE /api/v3/hf/margin/stop-order/cancel-by-id | **blocked** — 官方停損撤單頁面的請求參數表缺漏或誤植；缺少可確認的訂單識別與其他必要參數，不能猜測。 [Docs](https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-orderld) |
| 2767 | lighter | L2CreateStakingPool (33) / L2StakeAssets (35) / L2UnstakeAssets (36) | **partial** — 已補交易類型 35／36 的質押與解鎖；類型 33 CreateStakingPool 缺乏公開簽章結構。 [Docs](https://apidocs.lighter.xyz/) |
| 2769 | lighter | L2StrategyTransfer (43) / L2UpdateMarketConfig (44) / L2ApproveIntegrator (45) | **blocked** — 交易類型 43 StrategyTransfer 與 44 UpdateMarketConfig 的公開簽章結構／適用資格未確認；45 ApproveIntegrator 屬合作夥伴範圍，排除。 [Docs](https://apidocs.lighter.xyz/) |
| 2846 | backpack | GET /wapi/v1/capital/withdrawals/delay | **blocked** — 提領延遲唯讀查詢仍在範圍內，但官方 OpenAPI 未提供可確認的認證／簽章 instruction，未認證請求回傳 401。 [Docs](https://docs.backpack.exchange/#tag/Withdrawal-Delays) |
| 2876 | aster | GET /api/v3/ticker/opt/24hr | **blocked** — 選擇權 24 小時行情的官方請求規格不完整。 [Docs](https://github.com/asterdex/api-docs) |
| 2886 | aster | POST /api/v3/batchOrders | **blocked** — 現貨 V3 批次下單的官方參數與格式不完整。 [Docs](https://github.com/asterdex/api-docs) |
| 2887 | aster | DELETE /api/v3/batchOrders | **blocked** — 現貨 V3 批次撤單的官方參數與格式不完整。 [Docs](https://github.com/asterdex/api-docs) |
| 2910 | aster | GET /fapi/v3/marketKlines | **blocked** — 官方提及 marketKlines 路徑，但完整參數規格尚未確認。 [Docs](https://github.com/asterdex/api-docs) |
| 2969 | aster | POST /fapi/v3/asset/migrateUser | **blocked** — 資產遷移需要來源錢包簽章；所有權驗證與是否限同帳戶體系未確認。 [Docs](https://github.com/asterdex/api-docs) |

## 停用、維護中或缺乏有效介面

| 原始列號 | 交易所 | 端點／操作 | 原因 |
| ---: | --- | --- | --- |
| 1367 | okx | POST /api/v5/finance/stable-rewards/quote | 官方 Stable Rewards 文件已公告停止 quote、trade 與 subscribe-redeem-history 服務。 [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1368 | okx | POST /api/v5/finance/stable-rewards/trade | 官方 Stable Rewards 文件已公告停止 quote、trade 與 subscribe-redeem-history 服務。 [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1369 | okx | GET /api/v5/finance/stable-rewards/subscribe-redeem-history | 官方 Stable Rewards 文件已公告停止 quote、trade 與 subscribe-redeem-history 服務。 [Docs](https://www.okx.com/docs-v5/en/#financial-product-stable-rewards) |
| 1986 | bingx | - | 原始報告未提供有效官方串流名稱或協定；目前不知道可實作的介面規格。 [Docs](https://github.com/BingX-API/api-ai-skills) |
| 2065 | kraken | GET /derivatives/api/v3/feeschedules | 官方已於 2026-06-22 棄用，數值不再反映實際費率。 [Docs](https://docs.kraken.com/api-reference/) |
| 2066 | kraken | GET /derivatives/api/v3/feeschedules/volumes | 官方已於 2026-06-22 棄用，數值不再反映實際費率。 [Docs](https://docs.kraken.com/api-reference/) |
| 2218 | mexc | POST /api/v1/private/account/change_risk_level | 官方標示此風險等級介面停用，回傳錯誤碼 8817。 [Docs](https://www.mexc.com/api-docs/spot-v3/introduction) |
| 2221 | mexc | POST /api/v1/private/order/submit_batch | 官方標示批次下單介面維護中，恢復時間與目前可用性不知道。 [Docs](https://www.mexc.com/api-docs/spot-v3/introduction) |
| 3162 | arcus | POST /v1/settleLoan | Arcus 現貨借貸尚未開放；供應上限為零，settleLoanResults 串流不代表 REST settleLoan 可用。 [Docs](https://docs.arcus.xyz/api-reference) |

## 範圍及完成條件

外部提領／控制、跨帳戶體系轉帳、做市商／合作夥伴限定操作仍排除。唯讀提領歷史、一般借貸、投資與資金池未整類排除。每筆排除原因見 JSON。

受阻項目需要官方參數、簽章規格或權限範圍確認後才能實作；未知事項不以猜測補入。WebSocket 的 `protocol` 表示共用訂閱／傳輸支援，未宣稱每個主題都有專用型別與測試。
