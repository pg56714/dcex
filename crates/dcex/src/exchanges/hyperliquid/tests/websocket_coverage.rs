//! Offline coverage for Hyperliquid WebSocket subscription payloads.

use serde_json::json;

use crate::exchanges::hyperliquid::websocket::{
    all_mids_subscription, candle_subscription, coin_subscription, l2_book_subscription,
    subscription_payload, user_subscription,
};

const USER: &str = "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
const USER_LOWER: &str = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

#[test]
fn helper_subscriptions_match_official_shapes() {
    let cases = vec![
        (all_mids_subscription(None), json!({"type": "allMids"})),
        (
            all_mids_subscription(Some("xyz")),
            json!({"type": "allMids", "dex": "xyz"}),
        ),
        (
            coin_subscription("trades", "BTC".into()),
            json!({"type": "trades", "coin": "BTC"}),
        ),
        (
            coin_subscription("bbo", "@107".into()),
            json!({"type": "bbo", "coin": "@107"}),
        ),
        (
            coin_subscription("activeAssetCtx", "xyz:ABC".into()),
            json!({"type": "activeAssetCtx", "coin": "xyz:ABC"}),
        ),
        (
            candle_subscription("ETH".into(), "1M"),
            json!({"type": "candle", "coin": "ETH", "interval": "1M"}),
        ),
        (
            l2_book_subscription("BTC".into(), None, None),
            json!({"type": "l2Book", "coin": "BTC"}),
        ),
        (
            l2_book_subscription("BTC".into(), Some(5), Some(5)),
            json!({"type": "l2Book", "coin": "BTC", "nSigFigs": 5, "mantissa": 5}),
        ),
    ];
    for (built, expected) in cases {
        assert_eq!(built.expect("subscription"), expected);
    }
    for subscription_type in [
        "notification",
        "webData3",
        "orderUpdates",
        "userEvents",
        "userFills",
        "userFundings",
        "userNonFundingLedgerUpdates",
        "userTwapSliceFills",
        "userTwapHistory",
    ] {
        assert_eq!(
            user_subscription(subscription_type, USER, None).expect(subscription_type),
            json!({"type": subscription_type, "user": USER_LOWER})
        );
    }
    for subscription_type in ["clearinghouseState", "openOrders", "twapStates"] {
        assert_eq!(
            user_subscription(subscription_type, USER, Some("xyz")).expect(subscription_type),
            json!({"type": subscription_type, "user": USER_LOWER, "dex": "xyz"})
        );
    }
}

#[test]
fn raw_subscriptions_cover_types_without_dedicated_helpers() {
    for subscription in [
        json!({"type": "spotState", "user": USER_LOWER}),
        json!({"type": "spotState", "user": USER_LOWER, "isPortfolioMargin": true}),
        json!({"type": "allDexsClearinghouseState", "user": USER_LOWER}),
        json!({"type": "allDexsAssetCtxs"}),
        json!({"type": "fastAssetCtxs"}),
        json!({"type": "outcomeMetaUpdates"}),
        json!({"type": "activeAssetData", "user": USER_LOWER, "coin": "BTC"}),
        json!({"type": "l2Book", "coin": "BTC", "fast": true}),
    ] {
        let payload = subscription_payload("subscribe", subscription.clone()).expect("payload");
        assert_eq!(
            payload,
            json!({"method": "subscribe", "subscription": subscription})
        );
        let payload = subscription_payload("unsubscribe", subscription.clone()).expect("payload");
        assert_eq!(payload["method"], "unsubscribe");
    }
}

#[test]
fn helper_subscriptions_reject_invalid_inputs() {
    assert!(candle_subscription("BTC".into(), "2m").is_err());
    assert!(l2_book_subscription("BTC".into(), Some(6), None).is_err());
    assert!(l2_book_subscription("BTC".into(), None, Some(2)).is_err());
    assert!(user_subscription("userFills", "0x1234", None).is_err());
    assert!(user_subscription("openOrders", USER, Some("bad dex")).is_err());
    assert!(all_mids_subscription(Some("")).is_err());
    assert!(coin_subscription("trades", String::new()).is_err());
    assert!(subscription_payload("post", json!({"type": "trades"})).is_err());
}

#[test]
fn active_asset_data_resolves_canonical_symbols_through_product_table() {
    use crate::exchanges::hyperliquid::websocket::resolve_coin;
    use crate::product_table::{MarketInfo, ProductTable};

    let row = |exchange_symbol: &str, product_symbol: &str, product_type: &str| MarketInfo {
        exchange: "hyperliquid".to_string(),
        exchange_symbol: exchange_symbol.to_string(),
        product_symbol: product_symbol.to_string(),
        product_type: product_type.to_string(),
        exchange_type: product_type.to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.01".to_string(),
        min_size: "0.01".to_string(),
        base_currency: "X".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "10".to_string(),
        size_per_contract: "1".to_string(),
    };
    let table = ProductTable::new(vec![
        row("[\"@107\",10107]", "HYPE-USDC-SPOT", "spot"),
        row("[\"BTC\",0]", "BTC-USDC-SWAP", "swap"),
    ]);
    // Same resolution as the public helpers: spot canonical symbols need the table.
    assert_eq!(
        resolve_coin(Some(&table), "HYPE-USDC-SPOT").expect("spot"),
        "@107"
    );
    assert_eq!(
        resolve_coin(Some(&table), "BTC-USDC-SWAP").expect("swap"),
        "BTC"
    );
    assert_eq!(resolve_coin(Some(&table), "ETH").expect("raw"), "ETH");
    assert!(resolve_coin(Some(&table), "DOGE-USDC-SWAP").is_err());
    let coin = resolve_coin(Some(&table), "HYPE-USDC-SPOT").expect("spot");
    assert_eq!(
        coin_subscription("activeAssetData", coin).expect("subscription"),
        json!({"type": "activeAssetData", "coin": "@107"})
    );
    // Without a table the canonical spot symbol cannot be resolved safely.
    let coin = resolve_coin(None, "HYPE-USDC-SPOT").expect("passthrough");
    assert!(coin_subscription("activeAssetData", coin).is_err());
}
