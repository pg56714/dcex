# 升級至 Python 0.34.0／Rust rust-v0.12.0

此文件記錄從 0.33.0／rust-v0.11.0 升級的呼叫契約差異，並涵蓋同次發佈新增的安全要求。同步與非同步 Python 介面適用相同規則；非同步呼叫請加 await。表中的 `...`、`args` 代表原本其他必填參數，範例不會自動執行。錯誤欄列出實際訊息或穩定片段，Python 綁定、native 與交易所回應的完整前綴可能不同。

`CHANGELOG.md` 由 CI 產生；此指南獨立維護。部署中間 commit 前請先讀[部署限制](intermediate-commit-deployment.zh_tw.md)。

## 明確確認與操作範圍

不可逆／敏感操作須明確傳入布林 `confirm=True`；不要把字串 `"true"` 當成 Python 布林。全帳戶操作須提供非空商品／訂單範圍，或傳 `all_symbols=True`，兩者互斥。Backpack vault 贖回使用 `all=True` 與 `vault_token_quantity` 互斥。這些旗標只供本地檢查，驗證後移除，不送給交易所。

| 規則 | 舊呼叫 | 新呼叫 | 錯誤 |
|---|---|---|---|
| confirm | `client.delete_api_key(**args)` | `client.delete_api_key(**args, confirm=True)` | `confirm=True is required for this account operation` |
| scope | `client.cancel_spot_all_orders()` | `client.cancel_spot_all_orders(product_symbol="BTC-USDT-SPOT")` or `client.cancel_spot_all_orders(all_symbols=True)` | `provide a nonempty scope or all_symbols=True, exclusively` |
| vault | `client.vault_redeem(vault_id=1)` | `client.vault_redeem(vault_id=1, vault_token_quantity="1")` or `client.vault_redeem(vault_id=1, all=True)` | `provide a nonempty scope or all=True, exclusively` |

下表完整列出 REST 公開入口；每列的舊形式為 `client.method(**args)`，新形式為加上所列旗標（或明確範圍）。除了表後列出的 native 特例，Python 錯誤使用上方 confirm／scope 訊息。

| 方法 | 新要求 |
|---|---|
| `aster.trigger_futures_asset_exchange` | `confirm=True` |
| `backpack.cancel_open_strategies` | `all_symbols=True` 或明確範圍 |
| `bingx.cancel_coin_swap_all_orders` | `all_symbols=True` 或明確範圍 |
| `bingx.close_coin_swap_all_positions` | `all_symbols=True` 或明確範圍 |
| `bingx.delete_cswap_v1_trade_all_open_orders` | `all_symbols=True` 或明確範圍 |
| `bingx.reverse_swap_position` | `confirm=True` |
| `bingx.set_swap_asset_mode` | `confirm=True` |
| `bitget.broker_delete_subaccount_apikey` | `confirm=True` |
| `bitget.cancel_futures_plan_orders` | `all_symbols=True` 或明確範圍 |
| `bitget.cancel_spot_plan_orders` | `all_symbols=True` 或明確範圍 |
| `bitget.cfd_trade_cancel_all_orders` | `confirm=True` |
| `bitget.cfd_trade_close_all_positions` | `confirm=True` |
| `bitget.classic_broker_apikey_delete_subaccount_api_key` | `confirm=True` |
| `bitget.classic_copytrading_future_copytrade_follower_close_positions` | `all_symbols=True` 或明確範圍 |
| `bitget.classic_copytrading_future_copytrade_trader_trader_order_close_positions` | `all_symbols=True` 或明確範圍 |
| `bitget.close_futures_positions` | `all_symbols=True` 或明確範圍 |
| `bitget.close_uta_positions` | `all_symbols=True` 或明確範圍 |
| `bitget.copy_trading_follower_close_all` | `confirm=True` |
| `bitget.delete_uta_subaccount` | `confirm=True` |
| `bitget.move_uta_positions` | `confirm=True` |
| `bitget.p2p_order_management_confirm_payment` | `confirm=True` |
| `bitget.p2p_order_management_release_asset` | `confirm=True` |
| `bitget.reverse_futures_position` | `confirm=True` |
| `bitget.set_futures_asset_mode` | `confirm=True` |
| `bitget.set_uta_account_mode` | `confirm=True` |
| `bitget.upgrade_classic_account` | `confirm=True` |
| `bitget.upgrade_to_uta` | `confirm=True` |
| `bybit.delete_api_key` | `confirm=True` |
| `bybit.modify_api_key` | `confirm=True` |
| `hyperliquid.convert_to_multi_sig_user_signed` | `confirm=True` |
| `hyperliquid.perp_deploy_disable_dex` | `confirm=True` |
| `kucoin.cancel_futures_stop_orders` | `all_symbols=True` 或明確範圍 |
| `kucoin.cancel_margin_oco_orders` | `all_symbols=True` 或明確範圍 |
| `kucoin.cancel_spot_oco_orders` | `all_symbols=True` 或明確範圍 |
| `kucoin.cancel_spot_stop_orders` | `all_symbols=True` 或明確範圍 |
| `kucoin.delete_v1_broker_nd_account_apikey` | `confirm=True` |
| `kucoin.set_uta_account_mode` | `confirm=True` |
| `mexc.cancel_spot_all_orders` | `all_symbols=True` 或明確範圍 |
| `ondo.delete_api_key` | `confirm=True` |

Rust/native 的 `params` 使用 `("confirm", "true")` 或 `("all_symbols", "true")`；錯誤為 `<method>: confirm=true is required` 或 `<method>: provide a symbol, order IDs, or all_symbols=true, exclusively`。KuCoin `delete_v1_broker_nd_account_apikey` 的拒絕片段是 `API key deletion requires confirm=true`。Bybit `modify_api_key(confirm=True)` 仍須至少提供一項實際變更，否則回報 `at least one API key change is required`。

### WebSocket 範圍

- Kraken V1：`send_message({"event":"cancelAll"})` → `send_message({"event":"cancelAll"}, all_symbols=True)`；`cancelAllOrdersAfter` 同樣要求全帳戶旗標。拒絕片段：`Only account-wide cancellations require all_symbols=true.`。
- OKX：mass cancel 沒有 instrument family／spread 時，須在 `send_operation(..., all_symbols=True)` 明確選擇全範圍；拒絕片段：`provide an instrument family/spread or all_symbols=true exclusively`。一般下單不可傳此旗標。

## 其他呼叫、輸入與回傳差異

### 精確數值輸入

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `client.place_order(..., quantity=0.1)` | `client.place_order(..., quantity="0.1") / Decimal("0.1")` | `requires an exact decimal string or Decimal, not float/bool` |

所有已宣告 decimal 欄位（含巢狀訂單、TP/SL、批次）拒絕 float／bool；使用一般十進位字串、有限 Decimal 或合法整數。Rust／native 傳入一般十進位字串。

### 科學記號與界限

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `price="1e-7" / quantity="-1" / price="0"` | `price="0.0000001"; positive quantities/prices` | `requires a plain decimal string / must be a positive plain decimal string` |

正負號、正值界限與特殊值由明確 input catalog 決定；一般數量與限價不接受零，除非端點有宣告。integer／boolean metadata 宣告不代表全面執行期型別檢查。

### 結構化陣列與物件

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `rfq_cancel_batch_rfqs(rfq_ids="a,b")` | `rfq_cancel_batch_rfqs(rfq_ids=["a", "b"]) / rfq_ids='["a","b"]'` | `must be a JSON array / must be a JSON object` |

陣列接受 list 與 JSON array 字串；只有 11 個宣告欄位接受 CSV，物件陣列不可攤平成 CSV。67 個欄位、wire alias 與重複 query 規則見 array-input-formats。

### Kraken 保證金模式

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `set_futures_leverage_preference("PF_XBTUSD")` | `set_futures_leverage_preference("PF_XBTUSD", margin_mode="cross") / margin_mode="isolated", max_leverage="5"` | `missing required parameter: margin_mode / margin_mode must be cross without maxLeverage, or isolated with maxLeverage` |

cross 不帶槓桿上限；isolated 必須帶正值上限。省略參數不再代表推斷帳戶設定。

### BingX 倉位方向

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `place_swap_market_buy_order("BTC-USDT-SWAP", "1")` | `place_swap_market_buy_order("BTC-USDT-SWAP", "1", position_side="LONG")` | `missing a required argument: 'position_side' / missing required parameter: positionSide` |

六個 market／limit／post-only 的 buy／sell helper 必填 position_side；雙向倉位選 LONG／SHORT，單向模式依帳戶設定選 BOTH。低階訂單也須符合各自方向／平倉規則。

### MEXC 開倉槓桿

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `place_contract_market_buy_order("BTC-USDT-SWAP", vol=1)` | `place_contract_market_buy_order("BTC-USDT-SWAP", vol=1, leverage=5)` | `missing required parameter: leverage (required for MEXC Contract opening orders, side 1 or 3)` |

九個合約 market／limit／post-only wrapper 不再預設 50 倍槓桿。開倉 side 1／3 必須指定，平倉 side 2／4 沒有新增此要求。

### KuCoin 斷線保護

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `set_dcp(0); set_dcp(..., product_symbol="BTC-USDT")` | `set_dcp(-1) to disable; set_dcp(30, symbols=["BTC-USDT"]) to arm` | `KuCoin DCP timeout must be -1 or between 5 and 86400 / unexpected keyword argument` |

DCP 使用現貨 /api/v1/hf/orders/dead-cancel-all，get_dcp 使用 /query。symbols 為最多 50 對的 list 或 CSV；省略／空值代表全部交易對，不代表支援永續 DCP。

### Binance 批次回傳格式

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `for item in client.place_futures_batch_orders(orders): ...` | `result = client.place_futures_batch_orders(orders); inspect result["ok"] and result["errors"]` | `No exception is guaranteed for partial failure; inspect errors even after HTTP 200.` |

USD-M／COIN-M 的新增／修改／撤單，以及 options 新增／撤單，回傳兩個陣列，每筆保留 index 與 response。請依原始 index 對帳，先判讀逐筆錯誤再決定是否重試。

### Binance 條件式批次單

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `place_futures_batch_orders([{"type":"STOP_MARKET", ...}])` | `place_futures_algo_order(...) / place_coin_futures_algo_order(...)` | `USD-M conditional orders cannot be batched; use place_futures_algo_order` |

改用對應市場 REST algo 介面；COIN-M 回報自身遷移錯誤並使用 /dapi/v1/algoOrder。LIMIT／MARKET 批次會在本地拒絕 closePosition、混用識別碼清單、超長清單與非法型別。

### OKX 附加訂單欄位修正

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `amend_order(..., attachAlgoOrds=[{"newSz":"1"}])` | `amend_order(..., attachAlgoOrds=[{"sz":"1"}])` | `contains unsupported fields: newSz` |

修改附加單的數量是正值 sz；algo-order 附加項不接受 sz／newSz。下單比例大於 -1 且非零；修改用 new* 比例可用零刪除，也保留負值賣單比例。-1 只限宣告的 TP/SL 市價特殊值；closeFraction 不帶 algo sz，而非 sz=0。

### BingX 選填 TP/SL

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `takeProfit="{}" / stopLoss={} / takeProfit="   "` | `omit unused fields or pass None; supply a nonempty JSON object when used` | `must be a nonempty JSON object` |

單筆 swap、幣本位與批次一致省略 null、空字串、純空白 TP/SL；空物件會被拒絕。巢狀 decimal 保留精度，client order ID 保留字串與前導零。

### 文件允許的零值與相對值

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `send qty=0 without closing flags; use absolute triggerQuantity="0"` | `Bybit qty="0" only with reduceOnly=True and closeOnTrigger=True; Backpack triggerQuantity="10%" or a positive absolute value` | `must be a positive plain decimal string / requires a decimal percentage greater than 0% and at most 100%` |

Kraken 零數量平倉保留 reduce_only=True；一般下單／修改 helper 要正值數量。Kraken 相對價格 +5、-5、#5 與百分比仍支援，保留有號保證金差額及宣告的 TP/SL 刪除零值。

### Backpack funding 帳戶篩選

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `get_funding_payments(subaccountId=1)` | `get_funding_payments() on the intended authenticated client` | `unexpected keyword argument 'subaccountId'` |

此端點移除不支援的 subaccountId 參數；不要以未接受的 query 欄位假定已切換子帳戶。

### BingX 聚合委託簿深度

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `get_spot_orderbook_v2("BTC-USDT-SPOT", limit=5)` | `get_spot_orderbook_v2("BTC-USDT-SPOT", depth=5)` | `unexpected keyword argument 'limit' / missing a required argument: 'depth'` |

V2 聚合委託簿 depth 明確必填；另一個 get_spot_orderbook 保留其 limit 參數。

### KuCoin 市場界限

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `batch_cancel_uta_orders(trade_type="SPOT", cancel_order_list=[{"symbol":"XBTUSDTM", ...}])` | `use matching trade_type and symbols for SPOT/MARGIN/FUTURES` | `tradeType` |

商品符號與 SPOT／MARGIN／FUTURES 類型不符會拒絕，不會靜默選用其他市場；錯誤含 tradeType，完整文字依錯誤 symbol 而異。

### Ondo product table 擴充

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `iterate get_product_symbols(exchange="ondo") and trade every row` | `get_product_symbols(exchange="ondo", product_type="swap") for perpetual trading` | `Ondo -SPOT symbols are only valid for get_spot_* endpoints` |

現貨列僅供公開行情，私有現貨訂單／餘額規格仍未提供。本次後續 WS 修正可接受 SPY-USDC-SPOT 與 SPY-USDC；原先發佈的 0.34.0 WS helper 需用交易所形式 SPY-USDC。

### 空交易所套件與內部 import

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `import dcex.bitmart / bitmex / decibel / gateio; import private domain modules` | `use an implemented exchange Client and its documented public methods` | `ModuleNotFoundError / ImportError` |

移除空的交易所套件；底線開頭的內部模組已依領域整理，不是穩定 import 路徑。使用 dcex.<exchange>.client.Client 或 async_support 對應介面。

### 新舊關鍵字衝突

| 舊呼叫／假設 | 新呼叫／處理 | 錯誤或結果 |
|---|---|---|
| `place_spot_order(..., orderType="limit", order_type="limit")` | `provide only order_type="limit"` | `Provide only order_type; orderType is its legacy alias.` |

已宣告的 Bitget／BingX camelCase alias 仍相容，snake_case 改名本身不等於移除；同時給兩種拼法會報錯，不會靜默擇一。native 通用呼叫仍使用文件 wire 欄位名稱。

## 核對依據

- [Array 輸入規則](array-input-formats.zh_tw.md)
- [Schema 與數值宣告](schema-conventions.zh_tw.md)
- [Ondo 現貨範圍](ondo-spot.zh_tw.md)
- [Python operation guards](../dcex/_operation_guards.py)
- [Rust operation guards](../crates/dcex/src/exchanges/operation_guards.rs)
- [Complete explicit input catalog](../dcex/_input_contracts.json)
- [Endpoint coverage and replacements](endpoint-audit.md)
