# 端點覆蓋與驗證紀錄

[English](endpoint-audit.md) | **繁體中文**

對照日期：2026-09-27。基準為使用者提供的端點覆蓋表與本次查閱的官方 API 文件。範圍涵蓋一般行情、交易、帳戶、內部轉帳與風控；外部提領提交、做市商／合作夥伴專用流程不納入。

## 驗證狀態

**離線驗證已通過。** `cargo test --workspace --all-features`：639 項通過（636 項核心測試、3 項介面／安全檢查），53 項線上測試依設定略過。以本次原始碼重新建立並安裝 native extension 後，`pytest tests/unit` 全部 10,993 項通過，0 失敗、0 略過。Ruff lint／格式、Rust 格式及 Pyright 均通過（0 型別錯誤）。沒有對正式帳戶下單或執行管理操作。離線測試可確認請求路徑、動詞、型別、簽章及回應處理，無法證明帳戶權限或交易所即時可用性。

**覆蓋完整性更正：尚未全部補完。** 重新核對發現唯讀帳務查詢、Arcus api-meta、KuCoin 槓桿止損撤單及其他功能仍未封裝。測試通過不代表原表每列已完成。詳見[尚未完成項目](endpoint-recheck.zh_tw.md)。

## 各交易所

下列數字是公開 REST／簽名便利方法數量，包含別名與不同操作，不是官方端點覆蓋率。Rust 提供相同 named dispatch 與 typed request builder；二進位下載及離線簽名有獨立方法。新增方法詳見[索引](endpoint-methods.zh_tw.md)。

| 交易所／官方文件 | Python 同步 | Python 非同步 | 本次新增方法 | 本次補強 |
| --- | ---: | ---: | ---: | --- |
| [Binance](https://developers.binance.com/) | 566 | 566 | 257 | 現貨訂單清單與撤改單；USD-M／COIN-M 與 PM 風控；SAPI 帳戶、內部轉帳、兌換；TWAP／VP；WS 交易 |
| [Bybit](https://bybit-exchange.github.io/docs/v5/intro) | 249 | 249 | 79 | 帳戶風控、抵押品、持倉移轉、批次交易、歷史資料與 PRO 配額 |
| [OKX](https://www.okx.com/docs-v5/en/) | 266 | 266 | 90 | 策略單、價差交易、保證金／投資組合模擬、持倉移轉、兌換、子帳戶與 RFQ taker 操作 |
| [Bitget](https://www.bitget.com/api-doc/common/intro) | 352 | 352 | 214 | Classic／UTA 帳戶風控、批次操作、計畫單、內部轉帳、配額、子帳戶管理與 WS 交易 |
| [Kraken](https://docs.kraken.com/api-reference/) | 117 | 117 | 51 | 現貨批次單與匯出；期貨風控、歷史、分析及子帳戶；現貨 WS 交易及期貨串流 |
| [MEXC](https://www.mexc.com/api-docs/) | 141 | 141 | 21 | 現貨與合約行情／帳戶控制、兌換及合約 WS 訂閱 |
| [BingX](https://bingx-api.github.io/docs/) | 165 | 165 | 76 | USD-M／COIN-M 控制；現貨 OCO／撤改單；二進位報表；COIN-M WS |
| [KuCoin](https://www.kucoin.com/docs-new) | 295 | 295 | 179 | Classic 現貨／槓桿／期貨及 UTA 交易風控、批次單、兌換及子帳戶 |
| [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api) | 65 | 65 | 19 | 行情與帳戶查詢、交易控制及呼叫端預簽 WS 操作 |
| [Lighter](https://github.com/elliottech/lighter-python) | 89 | 89 | 18 | 組合單、帳戶／資產模式、子帳戶、金鑰變更、唯讀 token、入金及已簽名 WS 提交 |
| [Backpack](https://docs.backpack.exchange/) | 70 | 70 | 6 | 策略單生命週期與自成交防護 |
| [Aster](https://github.com/asterdex/api-docs) | 102 | 102 | 14 | V3 帳戶／行情查詢、受限撤單、內部轉帳、資產兌換及呼叫端預簽錢包管理 |
| [Extended](https://api.docs.extended.exchange/) | 59 | 59 | 18 | 投資組合資金費率、利息／回撤分析及 RFQ 訂單簿串流 |
| [Ondo](https://docs.ondoperps.xyz/api-reference) | 74 | 74 | 5 | 永續行情／帳戶／交易端點、SIWE 登入及 JWT 撤銷 |
| [Arcus](https://docs.arcus.xyz/api-reference) | 46 | 46 | 22 | 永續查詢、TP／SL 組合、簽名 WS 請求建立及錢包授權 API key |

## 限制與未封裝項目

| 項目 | 狀態與原因 |
| --- | --- |
| 外部提領提交、轉出至非帳戶家族、broker／affiliate、MM 專用操作 | 依指定範圍排除；提領紀錄等唯讀查詢仍有漏項，詳見重新核對清單。 |
| Kraken 舊 Futures fee schedules | 官方標示 2026-06-22 起數值不再反映實際費率；使用 Spot GetTradeVolume。 |
| Kraken 投資組合模擬 | 已提供封裝；官方限定 pre-production，須設定對應 base URL。 |
| Kraken assignment program／off-book RFQ 管理 | 尚未封裝；不列為一般訂單端點已支援。 |
| OKX SBE 二進位訂單簿 | 已以 get_sbe_orderbook 封裝 REST snapshot bytes；使用官方版本化 XML schema 解碼 template 1006。未內建 SBE 解碼器。 |
| Lighter historicalTrades 匯出 | 不知道目前有效的官方請求規格；現行查閱的 SDK 未提供該方法，因此不猜測路徑與欄位。 |
| Binance COIN-M algo、BingX 舊 spot/time、報告中的過時路徑 | 無法從目前官方文件確認的項目不以猜測新增；既有明確記載的行情與交易路徑另行支援。 |
| 理財／質押／公共池、借出投資產品、推薦／租賃、預測市場與鏈瀏覽器資料 | 本次尚未完成。須逐項依約定的排除範圍判斷；使用者並未同意整類排除，詳見重新核對清單。 |

以上不宣稱涵蓋交易所所有業務或協定。原報表中的合併列、動態路徑及別名必須逐項解讀，不能由字串出現次數推導覆蓋率。

## 使用注意

- Arcus API key 的建立／撤銷、Aster 錢包管理與 Lighter API key 變更保留呼叫端錢包授權。不可用交易 API key 取代錢包簽章。
- Lighter `change_api_key_signed` 必須提供明確 nonce；簽署官方 `Register Lighter Account` 訊息，金鑰更新確認後以新 key 重建 client。
- Binance PM／PM Pro、Bybit PRO 配額、Kraken 機構子帳戶等仍受交易所帳戶資格限制。
- Bitget 持倉移轉會影響兩帳戶的待成交訂單；API key 管理與 JWT 撤銷會改變帳戶存取狀態。
- Kraken 匯出回傳 ZIP bytes；BingX 收益匯出回傳 Excel bytes。不要當作 JSON 解碼。
- KuCoin convert 使用十進位字串輸入，以 JSON number 原樣編碼；不可先轉為浮點數。 期貨批次撤單會保留 DELETE 的 JSON 本文，並將完全相同的位元組納入簽章。

## 測試位置

Rust：`crates/dcex/src/exchanges/*/tests*`；Python：`tests/unit/test_*_endpoint_coverage.py`、`test_*risk*`、`test_ws_*` 與二進位匯出測試。簽章測試使用本機假憑證與本機 HTTP／WS 伺服器。

## 相關官方說明

- [Kraken Futures fee schedules](https://docs.kraken.com/api-reference/fee-schedules/get-fee-schedules)
- [Kraken portfolio simulation](https://docs.kraken.com/api-reference/account-information/calculate-portfolio-margin-pnl-and-greeks)
- [Lighter transaction definitions](https://github.com/elliottech/lighter-go/tree/main/types/txtypes)
- [Arcus API key onboarding](https://docs.arcus.xyz/api-reference/onboarding/create-api-key)
