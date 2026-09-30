# 中間版本 commit 部署限制

請勿部署 `610eafb0` 至 `93da40ff`（包含兩端）的 commit。這段版本的 Ondo `batch_cancel_orders` 將 `orderIDs` 序列化為 JSON 陣列，而非要求的逗號分隔 query 值。第一個完成修正的 commit 是 `2b36ecce`；`dbdd3a8b` 發佈的 Python `0.34.0`／Rust `rust-v0.12.0` 已包含修正。

| Commit／問題 | 修正 | 影響 |
|---|---|---|
| `610eafb0`、`6018ae33`、`41b76a7d`、`900692fb`：`fund_nondispatch_arms.json` 的 hash 過期 | `93da40ff` 更新 Binance dust 驗證敘述的精確 pin | 單獨執行 ownership 測試會失敗。 |
| `610eafb0` 至 `93da40ff`（包含兩端）：Ondo 批次撤單的 CSV 變成 JSON | `2b36ecce` 在 endpoint 正規化後保留 CSV | 批次撤單不可用，請勿部署這段版本。 |

只確認可編譯無法發現這些問題。相關 commit 已公開，保留原本 tree 與分界，不改寫歷史。之後每個 commit 都須在提交前通過其受影響測試；修改序列化時，須包含 ownership pin 與實際封包斷言。分支最終版本通過，不代表每個中間 commit 均通過。

限制適用於上述中間 commit；已修正的公開 `0.34.0` 版本不在此限制內。
