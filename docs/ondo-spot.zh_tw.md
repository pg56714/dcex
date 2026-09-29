# Ondo 現貨支援範圍

Rust 與 Python 同步／非同步介面提供現貨公開深度、成交、symbol 資訊及 TradingView 歷史資料，方法分別為 `get_spot_depth`、`get_spot_trades`、`get_spot_symbol_info`、`get_spot_price_history`。深度與成交接受 `SPY-USDC` 或 `SPY-USDC-SPOT`；歷史資料使用 symbol 資訊回傳的 TradingView 名稱，例如 `SPYUSDC`，時間範圍 `from_time`／`to_time` 使用 Unix 秒。

Product table 從 `/v1/markets` 同時讀取 `result.perps.tradingPairs` 與 `result.spot.tradingPairs`。啟用的現貨交易對使用 `BASE-QUOTE-SPOT`，停用交易對會略過。數量與價格精度直接採 `baseIncrement`、`quoteIncrement`，不經浮點轉換；行情回應及 token 設定保留原值。新增公開請求沒有價格或數量輸入；symbol、resolution 與時間控制欄位已於 input catalog 明確宣告。

[官方現貨說明](https://docs.ondoperps.xyz/spot-trading) 描述以足額資金購買代幣，並以股票等值數量顯示。實際持有的是 GM token，符合條件的代幣可分配為永續合約擔保品。不要僅由顯示 symbol 推算代幣單位換算；應查看回傳的原始 `tokenConfig`，包括存在時的 `ledgerUnit`、`sharesMultiplier`、`custodiedAs`、`collateralEligible`。

截至 2026-09-30，[官方文件索引](https://docs.ondoperps.xyz/llms.txt) 尚未公布現貨私有 REST 契約或現貨 WebSocket 頻道規格。下單、撤單、查單、批次、成交紀錄及 K 線在 ledger 維持 **blocked**。預定私有操作的 method／path 只是待確認項目，不代表官方規格。沒有實作現貨私有簽章或下單方法，也沒有發送實盤帳戶請求或訂單。

已公布的 `get_account()` 提供帳戶資訊；`get_balance()` 對應 `/v1/perps/balance` 永續保證金摘要。這兩份官方 schema 都未確認現貨 GM token 餘額的查詢方式。因此現貨持倉查詢及現貨 WebSocket 訂閱維持 unverified；API 表示方式公布前，請透過官方介面查看相關餘額。既有永續方法不得搭配 `-SPOT` symbol 使用。

公開路徑依據工作單提供的 2026-09-29 唯讀觀察，並具備離線 wire 覆蓋。2026-09-30 的新公開查詢因 TLS 憑證驗證回報過期而未完成。TLS 驗證保持啟用；離線實作不代表目前已獲線上認證。
