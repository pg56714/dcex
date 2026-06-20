use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::hyperliquid::HyperliquidClient;

use super::common::{
    assert_success, fetch_trading_details, first_bid_price, minimum_order_quantity,
    price_below_market, require_env, require_live_trading, require_order_id, BTC_USD_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn hyperliquid_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["HYPERLIQUID_WALLET_ADDRESS", "HYPERLIQUID_PRIVATE_KEY"]) else {
        return Ok(());
    };
    let client = HyperliquidClient::new(
        false,
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    let existing = client
        .open_orders(vec![("user".to_string(), keys[0].clone())])
        .await?;
    if existing
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        eprintln!("skipping Hyperliquid live stateful order; open orders exist");
        return Ok(());
    }

    let orderbook = client
        .get_l2book(vec![(
            "product_symbol".to_string(),
            BTC_USD_SWAP.to_string(),
        )])
        .await?;
    let details = fetch_trading_details(Exchange::Hyperliquid, "hyperliquid", BTC_USD_SWAP).await?;
    let bid = first_bid_price(&orderbook.data)?;
    let price = price_below_market(bid, &details, 0.95)?;
    let size = minimum_order_quantity(&price, &details)?;
    let order = client
        .place_future_limit_buy_order(vec![
            ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
            ("price".to_string(), price),
            ("size".to_string(), size),
            ("reduceOnly".to_string(), "false".to_string()),
            ("tif".to_string(), "Alo".to_string()),
        ])
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["oid"])?;
    let cancel = client
        .cancel_order(vec![
            ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
            ("oid".to_string(), order_id),
        ])
        .await?;
    assert_success(&cancel);
    Ok(())
}
