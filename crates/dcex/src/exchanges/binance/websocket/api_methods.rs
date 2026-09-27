// Convenience methods for the official Binance WebSocket API method names.
use super::api::{BinanceWebSocketApi, BinanceWebSocketApiMarket};
use crate::Result;
use serde_json::Value;
impl BinanceWebSocketApi {
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn ping(&self, params: Value) -> Result<u64> {
        self.request("ping", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn time(&self, params: Value) -> Result<u64> {
        self.request("time", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn exchange_info(&self, params: Value) -> Result<u64> {
        self.request("exchangeInfo", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn execution_rules(&self, params: Value) -> Result<u64> {
        self.request("executionRules", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_orderbook(&self, params: Value) -> Result<u64> {
        self.request("depth", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn trades_recent(&self, params: Value) -> Result<u64> {
        self.request("trades.recent", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn trades_historical(&self, params: Value) -> Result<u64> {
        self.request("trades.historical", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn block_trades_historical(&self, params: Value) -> Result<u64> {
        self.request("blockTrades.historical", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn trades_aggregate(&self, params: Value) -> Result<u64> {
        self.request("trades.aggregate", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn klines(&self, params: Value) -> Result<u64> {
        self.request("klines", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn ui_klines(&self, params: Value) -> Result<u64> {
        self.request("uiKlines", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn avg_price(&self, params: Value) -> Result<u64> {
        self.request("avgPrice", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn ticker_24hr(&self, params: Value) -> Result<u64> {
        self.request("ticker.24hr", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn ticker_trading_day(&self, params: Value) -> Result<u64> {
        self.request("ticker.tradingDay", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn ticker(&self, params: Value) -> Result<u64> {
        self.request("ticker", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_price(&self, params: Value) -> Result<u64> {
        self.request("ticker.price", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_book_ticker(&self, params: Value) -> Result<u64> {
        self.request("ticker.book", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn reference_price(&self, params: Value) -> Result<u64> {
        self.request("referencePrice", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn reference_price_calculation(&self, params: Value) -> Result<u64> {
        self.request("referencePrice.calculation", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn logon(&self, params: Value) -> Result<u64> {
        self.request("session.logon", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_session(&self, params: Value) -> Result<u64> {
        self.request("session.status", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn logout(&self, params: Value) -> Result<u64> {
        self.request("session.logout", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn place_order(&self, params: Value) -> Result<u64> {
        self.request("order.place", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn test_order(&self, params: Value) -> Result<u64> {
        self.request("order.test", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn cancel_order(&self, params: Value) -> Result<u64> {
        self.request("order.cancel", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn cancel_replace_order(&self, params: Value) -> Result<u64> {
        self.request("order.cancelReplace", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn amend_order_keep_priority(&self, params: Value) -> Result<u64> {
        self.request("order.amend.keepPriority", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn cancel_all_orders(&self, params: Value) -> Result<u64> {
        self.request("openOrders.cancelAll", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_place_oco(&self, params: Value) -> Result<u64> {
        self.request("orderList.place.oco", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_place_oto(&self, params: Value) -> Result<u64> {
        self.request("orderList.place.oto", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_place_otoco(&self, params: Value) -> Result<u64> {
        self.request("orderList.place.otoco", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_place_opo(&self, params: Value) -> Result<u64> {
        self.request("orderList.place.opo", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_place_opoco(&self, params: Value) -> Result<u64> {
        self.request("orderList.place.opoco", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_cancel(&self, params: Value) -> Result<u64> {
        self.request("orderList.cancel", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn sor_order_place(&self, params: Value) -> Result<u64> {
        self.request("sor.order.place", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn sor_order_test(&self, params: Value) -> Result<u64> {
        self.request("sor.order.test", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_account(&self, params: Value) -> Result<u64> {
        let method = match self.market_kind() {
            BinanceWebSocketApiMarket::Spot | BinanceWebSocketApiMarket::CoinFutures => {
                "account.status"
            }
            BinanceWebSocketApiMarket::Futures => "v2/account.status",
        };
        self.request(method, params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_order(&self, params: Value) -> Result<u64> {
        self.request("order.status", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn open_orders_status(&self, params: Value) -> Result<u64> {
        self.request("openOrders.status", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn all_orders(&self, params: Value) -> Result<u64> {
        self.request("allOrders", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_list_status(&self, params: Value) -> Result<u64> {
        self.request("orderList.status", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn open_order_lists_status(&self, params: Value) -> Result<u64> {
        self.request("openOrderLists.status", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn all_order_lists(&self, params: Value) -> Result<u64> {
        self.request("allOrderLists", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn my_trades(&self, params: Value) -> Result<u64> {
        self.request("myTrades", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn account_rate_limits_orders(&self, params: Value) -> Result<u64> {
        self.request("account.rateLimits.orders", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn my_prevented_matches(&self, params: Value) -> Result<u64> {
        self.request("myPreventedMatches", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn my_allocations(&self, params: Value) -> Result<u64> {
        self.request("myAllocations", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn account_commission(&self, params: Value) -> Result<u64> {
        self.request("account.commission", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn order_amendments(&self, params: Value) -> Result<u64> {
        self.request("order.amendments", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn my_filters(&self, params: Value) -> Result<u64> {
        self.request("myFilters", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn subscribe_session_user_data(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.subscribe", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn unsubscribe_user_data(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.unsubscribe", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_subscriptions(&self, params: Value) -> Result<u64> {
        self.request("session.subscriptions", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn subscribe_user_data(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.subscribe.signature", params)
            .await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn amend_order(&self, params: Value) -> Result<u64> {
        self.request("order.modify", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn place_algo_order(&self, params: Value) -> Result<u64> {
        self.request("algoOrder.place", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn cancel_algo_order(&self, params: Value) -> Result<u64> {
        self.request("algoOrder.cancel", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_balance(&self, params: Value) -> Result<u64> {
        self.request(
            if self.market_kind() == BinanceWebSocketApiMarket::CoinFutures {
                "account.balance"
            } else {
                "v2/account.balance"
            },
            params,
        )
        .await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn get_positions(&self, params: Value) -> Result<u64> {
        self.request(
            if self.market_kind() == BinanceWebSocketApiMarket::CoinFutures {
                "account.position"
            } else {
                "v2/account.position"
            },
            params,
        )
        .await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn create_listen_key(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.start", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn keep_alive_listen_key(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.ping", params).await
    }
    /// Send the corresponding WebSocket API method; receive its outcome with `recv`.
    pub async fn close_listen_key(&self, params: Value) -> Result<u64> {
        self.request("userDataStream.stop", params).await
    }
}
