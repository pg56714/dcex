//! Every convenience method maps to a WebSocket API method its market accepts.

use std::time::Duration;

use serde_json::{Value, json};

use super::api::{BinanceWebSocketApi, BinanceWebSocketApiMarket};
use crate::Result;
use crate::ws::test_peer::TestPeer;

/// Generated from `api_methods.rs`; `list_matches_source` keeps it complete.
const METHODS: &[&str] = &[
    "subscribe_user_data_listen_token",
    "ping",
    "time",
    "exchange_info",
    "execution_rules",
    "get_orderbook",
    "trades_recent",
    "trades_historical",
    "block_trades_historical",
    "trades_aggregate",
    "klines",
    "ui_klines",
    "avg_price",
    "ticker_24hr",
    "ticker_trading_day",
    "ticker",
    "get_price",
    "get_book_ticker",
    "reference_price",
    "reference_price_calculation",
    "logon",
    "get_session",
    "logout",
    "place_order",
    "test_order",
    "cancel_order",
    "cancel_replace_order",
    "amend_order_keep_priority",
    "cancel_all_orders",
    "order_list_place_oco",
    "order_list_place_oto",
    "order_list_place_otoco",
    "order_list_place_opo",
    "order_list_place_opoco",
    "order_list_cancel",
    "sor_order_place",
    "sor_order_test",
    "get_account",
    "get_order",
    "open_orders_status",
    "all_orders",
    "order_list_status",
    "open_order_lists_status",
    "all_order_lists",
    "my_trades",
    "account_rate_limits_orders",
    "my_prevented_matches",
    "my_allocations",
    "account_commission",
    "order_amendments",
    "my_filters",
    "subscribe_session_user_data",
    "unsubscribe_user_data",
    "get_subscriptions",
    "subscribe_user_data",
    "amend_order",
    "place_algo_order",
    "cancel_algo_order",
    "get_balance",
    "get_positions",
    "create_listen_key",
    "keep_alive_listen_key",
    "close_listen_key",
];

async fn call(api: &BinanceWebSocketApi, name: &str, params: Value) -> Result<u64> {
    match name {
        "subscribe_user_data_listen_token" => api.subscribe_user_data_listen_token(params).await,
        "ping" => api.ping(params).await,
        "time" => api.time(params).await,
        "exchange_info" => api.exchange_info(params).await,
        "execution_rules" => api.execution_rules(params).await,
        "get_orderbook" => api.get_orderbook(params).await,
        "trades_recent" => api.trades_recent(params).await,
        "trades_historical" => api.trades_historical(params).await,
        "block_trades_historical" => api.block_trades_historical(params).await,
        "trades_aggregate" => api.trades_aggregate(params).await,
        "klines" => api.klines(params).await,
        "ui_klines" => api.ui_klines(params).await,
        "avg_price" => api.avg_price(params).await,
        "ticker_24hr" => api.ticker_24hr(params).await,
        "ticker_trading_day" => api.ticker_trading_day(params).await,
        "ticker" => api.ticker(params).await,
        "get_price" => api.get_price(params).await,
        "get_book_ticker" => api.get_book_ticker(params).await,
        "reference_price" => api.reference_price(params).await,
        "reference_price_calculation" => api.reference_price_calculation(params).await,
        "logon" => api.logon(params).await,
        "get_session" => api.get_session(params).await,
        "logout" => api.logout(params).await,
        "place_order" => api.place_order(params).await,
        "test_order" => api.test_order(params).await,
        "cancel_order" => api.cancel_order(params).await,
        "cancel_replace_order" => api.cancel_replace_order(params).await,
        "amend_order_keep_priority" => api.amend_order_keep_priority(params).await,
        "cancel_all_orders" => api.cancel_all_orders(params).await,
        "order_list_place_oco" => api.order_list_place_oco(params).await,
        "order_list_place_oto" => api.order_list_place_oto(params).await,
        "order_list_place_otoco" => api.order_list_place_otoco(params).await,
        "order_list_place_opo" => api.order_list_place_opo(params).await,
        "order_list_place_opoco" => api.order_list_place_opoco(params).await,
        "order_list_cancel" => api.order_list_cancel(params).await,
        "sor_order_place" => api.sor_order_place(params).await,
        "sor_order_test" => api.sor_order_test(params).await,
        "get_account" => api.get_account(params).await,
        "get_order" => api.get_order(params).await,
        "open_orders_status" => api.open_orders_status(params).await,
        "all_orders" => api.all_orders(params).await,
        "order_list_status" => api.order_list_status(params).await,
        "open_order_lists_status" => api.open_order_lists_status(params).await,
        "all_order_lists" => api.all_order_lists(params).await,
        "my_trades" => api.my_trades(params).await,
        "account_rate_limits_orders" => api.account_rate_limits_orders(params).await,
        "my_prevented_matches" => api.my_prevented_matches(params).await,
        "my_allocations" => api.my_allocations(params).await,
        "account_commission" => api.account_commission(params).await,
        "order_amendments" => api.order_amendments(params).await,
        "my_filters" => api.my_filters(params).await,
        "subscribe_session_user_data" => api.subscribe_session_user_data(params).await,
        "unsubscribe_user_data" => api.unsubscribe_user_data(params).await,
        "get_subscriptions" => api.get_subscriptions(params).await,
        "subscribe_user_data" => api.subscribe_user_data(params).await,
        "amend_order" => api.amend_order(params).await,
        "place_algo_order" => api.place_algo_order(params).await,
        "cancel_algo_order" => api.cancel_algo_order(params).await,
        "get_balance" => api.get_balance(params).await,
        "get_positions" => api.get_positions(params).await,
        "create_listen_key" => api.create_listen_key(params).await,
        "keep_alive_listen_key" => api.keep_alive_listen_key(params).await,
        "close_listen_key" => api.close_listen_key(params).await,
        other => panic!("no convenience method {other}"),
    }
}

#[test]
fn list_matches_source() {
    let source = include_str!("api_methods.rs");
    let declared: Vec<&str> = source
        .split("pub async fn ")
        .skip(1)
        .map(|rest| &rest[..rest.find('(').expect("signature")])
        .collect();
    assert_eq!(declared, METHODS);
}

#[tokio::test]
async fn every_convenience_method_reaches_a_market_that_accepts_it() {
    let markets = [
        BinanceWebSocketApiMarket::Spot,
        BinanceWebSocketApiMarket::Futures,
        BinanceWebSocketApiMarket::CoinFutures,
    ];
    let mut clients = Vec::new();
    for market in markets {
        let mut peer = TestPeer::start().await;
        let api = BinanceWebSocketApi::with_url(
            market,
            Some("api-key".into()),
            Some("secret".into()),
            None,
            Duration::from_secs(5),
            peer.url.clone(),
        )
        .expect("client");
        api.connect().await.expect("connect");
        peer.wait_connections(1).await;
        clients.push((market, api, peer));
    }
    let mut unsupported = Vec::new();
    for name in METHODS {
        let mut accepted = false;
        for (_, api, peer) in &mut clients {
            match call(api, name, json!({})).await {
                Ok(id) => {
                    let frame = peer.next_json().await;
                    assert_eq!(frame["id"], json!(id), "{name}");
                    assert!(frame["method"].as_str().is_some_and(|m| !m.is_empty()));
                    accepted = true;
                }
                Err(error) if error.to_string().contains("unsupported method") => {}
                // The method exists for this market; the empty placeholder params are
                // rejected by its own schema (e.g. a required field).
                Err(_) => accepted = true,
            }
        }
        if !accepted {
            unsupported.push(*name);
        }
    }
    assert!(unsupported.is_empty(), "no market accepts: {unsupported:?}");
}

#[tokio::test]
async fn market_specific_account_methods_pick_the_documented_name() {
    for (market, expected) in [
        (BinanceWebSocketApiMarket::Spot, "account.status"),
        (BinanceWebSocketApiMarket::Futures, "v2/account.status"),
        (BinanceWebSocketApiMarket::CoinFutures, "account.status"),
    ] {
        let mut peer = TestPeer::start().await;
        let api = BinanceWebSocketApi::with_url(
            market,
            Some("api-key".into()),
            Some("secret".into()),
            None,
            Duration::from_secs(5),
            peer.url.clone(),
        )
        .expect("client");
        api.connect().await.expect("connect");
        api.get_account(json!({})).await.expect("send");
        let frame = peer.next_json().await;
        assert_eq!(frame["method"], expected);
        assert_eq!(frame["params"]["apiKey"], "api-key");
        assert!(frame["params"]["signature"].is_string());
    }
}
