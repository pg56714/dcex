# 端點重新核對：尚未完成項目

[English](endpoint-recheck.md) | **繁體中文**

核對日期：2026-09-27。結論：**尚未全部補完**。先前 10,993 項 Python 測試及 639 項 Rust 測試通過，只能驗證已實作功能，不能證明原表每一列已完成。本次只重新核對並修正文檔，沒有修改端點實作。

基準為使用者提供的 3,180 列 HTML 表、目前原始碼、官方文件及先前取得的官方文件快取。重新篩查原表 1,551 列 missing 與 92 列 rust-only：1,027 列找到路由文字，423 列沒有直接命中，193 列需要按複合項目／WS／交易型別解讀。這些是搜尋分類，不是支援率或未完成端點數；路由文字存在也不足以確認動詞、參數與 Python 封裝。

**以下 25 列是具體尚無封裝的介面，並非剩餘總數。** 其中 KuCoin 取消止損單的參數仍待官方澄清；Arcus 7 列使用先前官方文件快取作為證據。其他未封裝功能族群與未知項目列在後面。

## 具體未封裝介面

| 交易所 | 路由 | 狀態／官方來源 |
| --- | --- | --- |
| Binance | `GET /sapi/v1/capital/withdraw/history` | 唯讀帳務對帳。 [Docs](https://developers.binance.com/docs/wallet/capital/withdraw-history) |
| Binance | `GET /sapi/v1/capital/deposit/subAddress` | 子帳戶入金地址／紀錄。 [Docs](https://github.com/binance/binance-connector-java/blob/master/clients/sub-account/example_rest.md) |
| Binance | `GET /sapi/v1/capital/deposit/subHisrec` | 子帳戶入金地址／紀錄。 [Docs](https://github.com/binance/binance-connector-java/blob/master/clients/sub-account/example_rest.md) |
| Binance | `GET /sapi/v1/sub-account/futures/move-position` | 持倉移轉／紀錄；移轉有 VIP 7–9、主帳戶等資格限制。 [Docs](https://binance.github.io/binance-connector-js/classes/_binance_sub-account.SubAccountRestAPI.AssetManagementApi.html) |
| Binance | `POST /sapi/v1/sub-account/futures/move-position` | 持倉移轉／紀錄；移轉有 VIP 7–9、主帳戶等資格限制。 [Docs](https://binance.github.io/binance-connector-js/classes/_binance_sub-account.SubAccountRestAPI.AssetManagementApi.html) |
| Bybit | `GET /v5/asset/withdraw/query-record` | 唯讀提領紀錄。 [Docs](https://bybit-exchange.github.io/docs/v5/asset/withdraw/withdraw-record) |
| OKX | `GET /api/v5/asset/withdrawal-history` | 唯讀提領紀錄；已核對先前官方文件快取。 [Docs](https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history) |
| OKX | `GET /api/v5/public/interest-rate-loan-quota` | 公開借款利率／額度；已核對先前官方文件快取。 [Docs](https://www.okx.com/docs-v5/en/#public-data-rest-api-get-interest-rate-and-loan-quota) |
| Bitget | `GET /api/v2/spot/wallet/withdrawal-records` | Classic 唯讀提領紀錄。 [Docs](https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-withdrawal-records) |
| Bitget | `GET /api/v3/account/withdrawal-records` | UTA 唯讀提領紀錄。 [Docs](https://www.bitget.com/zh-CN/api-doc/uta/account/withdrawal/Get-Withdrawal-Records) |
| BingX | `GET /openApi/api/v3/capital/withdraw/history` | 唯讀提領紀錄；已核對官方參考文件快取。 [Docs](https://github.com/BingX-API/api-ai-skills) |
| BingX | `GET /openApi/wallets/v1/capital/innerTransfer/records` | 主／子帳戶 P2P 轉帳紀錄唯讀查詢；轉出至其他帳戶的提交操作仍排除。 [Docs](https://github.com/BingX-API/api-ai-skills) |
| BingX | `GET /openApi/wallets/v1/capital/subAccount/innerTransfer/records` | 主／子帳戶 P2P 轉帳紀錄唯讀查詢；轉出至其他帳戶的提交操作仍排除。 [Docs](https://github.com/BingX-API/api-ai-skills) |
| KuCoin | `GET /api/v1/withdrawals` | Classic 唯讀提領紀錄。 [Docs](https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-history) |
| KuCoin | `GET /api/v1/withdrawals/{withdrawalId}` | 唯讀單筆提領明細。 [Docs](https://www.kucoin.com/docs-new/rest/account-info/withdrawals/get-withdrawal-by-id) |
| KuCoin | `GET /api/ua/v2/asset/withdrawal/history` | UTA 唯讀提領紀錄。 [Docs](https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history) |
| KuCoin | `DELETE /api/v3/hf/margin/stop-order/cancel-by-id` | 路由確認存在，但官方頁面列為無請求參數；正確必填參數目前不知道，實作前需確認。 [Docs](https://www.kucoin.com/docs-new/rest/margin-trading/orders/cancel-stop-order-by-orderld) |
| Kraken | `GET /funding/v1/withdrawals` | 新版 Funding（Beta）唯讀查詢；目前實作沒有 /funding/ 路由，其他 Funding 查詢亦待遷移盤點。 [Docs](https://docs.kraken.com/api-reference/funding-beta/list-funding-withdrawals) |
| Arcus | `GET /v1/api-meta/markets` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-market-metadata) |
| Arcus | `GET /v1/api-meta/overview` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-market-overview) |
| Arcus | `GET /v1/api-meta/spot/overview` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-spot-market-overview) |
| Arcus | `GET /v1/api-meta/candles` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/marketmetadata/get-spot-candles) |
| Arcus | `GET /v1/api-meta/userPreferences` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/userpreferences/get-user-preferences) |
| Arcus | `PATCH /v1/api-meta/userPreferences` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/userpreferences/upsert-user-preferences) |
| Arcus | `DELETE /v1/api-meta/userPreferences` | 先前取得的官方 llms-full 有列出；本次無法重新取得線上文件。Rust／Python 都沒有封裝。 [Docs](https://docs.arcus.xyz/api-reference/userpreferences/delete-a-user-preference) |

## 其他尚未封裝的功能族群

下列功能仍未完成；不能只因其優先級較低，就當作已完成或使用者已同意排除。

| 交易所 | 尚未封裝／待逐項核對 |
| --- | --- |
| Binance | 部分子帳戶 API 金鑰／IP 管理、虛擬子帳戶、期貨／選擇權啟用、Travel Rule 入金問卷及紀錄、託管子帳戶查詢；依實際資格區分一般帳戶與合作夥伴專用。 |
| Bybit | 新版 crypto-loan 固定／彈性借貸及抵押品管理；舊版 crypto-loan 路由需先核對棄用狀態。另有部分提領地址／唯讀資訊。 |
| OKX | Grid、DCA、Signal Bot、Recurring Buy、Copy Trading、部分法幣／借貸查詢。SBE 目前只回傳二進位快照，沒有內建解碼器。 |
| Bitget | 14 個 UTA grid 端點、部分 reality 股票基本面資料、借貸與唯讀提領額度／地址。 |
| MEXC | 原表的 5 個 STP strategy/group 操作、3 個子帳戶 API key 操作沒有封裝；本次未找到足以確認現行路由與資格的官方資料，狀態為待確認。 |
| KuCoin | OES 幣種／託管額度、唯讀提領額度、VIP／OTC loan 查詢等。 |
| Hyperliquid | 部分借貸、vault、staking、部署與帳戶抽象化查詢／操作未納入；逐項資格與用途仍須判斷。 |
| Lighter | historicalTrades 匯出、type 43／44／45 等原表列出的進階操作仍待官方 schema／資格核對；池、staking、leasing 等產品未封裝。 |
| Backpack | Vault／prediction 功能及提領延遲控制未納入；RFQ maker quote 依 MM 範圍排除。 |
| Extended | 部分 vault 公開資料、rewards；affiliate／referral 依合作夥伴範圍另列。 |
| Aster | Spot 批次單與替代 24h ticker 的文件不完整，見下一節；錢包資產遷移需先判斷是否屬外部轉出。 |
| Kraken | Funding（Beta）查詢遷移未完成；舊 EditOrder 與建議使用的 AmendOrder 應分開記錄。 |

[Bitget 官方更新紀錄](https://www.bitget.com/docs/uta/changelog/2026-08)列出 14 個 grid API。[OKX 官方 Grid 文件](https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-place-grid-algo-order)列出尚未封裝的策略系列。

## 文件不足、已停用及明確排除

- Aster 官方 Spot 文件只提及 `POST/DELETE /api/v3/batchOrders` 與 `GET /api/v3/ticker/opt/24hr` 存在，未提供完整定義；正確請求 schema 目前不知道，不能猜填。來源：[官方 Spot V3 文件](https://github.com/asterdex/api-docs/blob/master/V3%28Recommended%29/EN/aster-finance-spot-api-v3.md)。
- MEXC `POST /api/v1/private/account/change_risk_level` 已由官方標示停用，會回傳 8817，應列為停用而非待新增。來源：[官方合約文件](https://mexcdevelop.github.io/apidocs/contract_v1_en/#switch-the-risk-level)。
- Kraken `POST /0/private/WithdrawStatus` 已標為 deprecated；官方建議遷移 Funding（Beta）。[官方說明](https://docs.kraken.com/api-reference/funding/get-status-of-recent-withdrawals)。Futures fee schedules 的既有棄用註記保留。
- Lighter `historicalTrades` 匯出，以及先前列出的未確認 Binance COIN-M algo／舊 BingX spot-time 路由，現行官方 schema 仍不知道。
- 外部提領提交、轉出至非帳戶家族、MM／合作夥伴專用端點，維持使用者已指定的排除範圍。唯讀提領／轉帳紀錄不應因此一併排除。

## 已排除的誤判

- Arcus `get_trade`、`get_fill` 的路徑含動態 ID，Python 同步／非同步已提供；`settleLoanResults` 頻道已支援。
- Arcus `get_commission_rates` 仍只有 Rust 命名 dispatch 與 Python 通用入口；官方用途是 referral 佣金，不是一般交易費率。
- KuCoin 同步撤單的 `{orderId}`／`{clientOid}` 使用動態路徑，已有實作。
- Kraken 歷史查詢及 Extended funding／interest 的複合列不能按整串文字比對判定缺少。
- BingX 子帳戶 API key 查詢已有 `get_api_key_info(uid, apiKey)`，實際路由為 `/openApi/account/v1/apiKey/query`，不是原表的舊路由。

本輪沒有確認 Ondo 新增的一般交易端點缺口；這不等於保證所有官方 API 已覆蓋。精確剩餘總數目前不知道，尚有複合列、產品範圍及官方定義需要逐項閉合。
