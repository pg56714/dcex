use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::hyperliquid::HyperliquidClient;

use super::common::{
    assert_success, fetch_trading_details, find_f64, find_string, first_bid_price, live_test_error,
    minimum_order_quantity, require_env, require_live_trading, require_order_id, BTC_USD_SWAP,
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

    cleanup_hyperliquid_state(&client, &keys[0]).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_l2book",
        vec![("product_symbol".to_string(), BTC_USD_SWAP.to_string())],
    )
    .await?;
    let details = fetch_trading_details(Exchange::Hyperliquid, "hyperliquid", BTC_USD_SWAP).await?;
    let bid = first_bid_price(&orderbook.data)?;
    let price = hyperliquid_post_only_buy_price(bid)?;
    let size = hyperliquid_order_size(&price, &minimum_order_quantity(&price, &details)?)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_future_limit_buy_order",
        vec![
            ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
            ("price".to_string(), price),
            ("size".to_string(), size),
            ("reduceOnly".to_string(), "false".to_string()),
            ("tif".to_string(), "Alo".to_string()),
        ],
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["oid"])?;
    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_order",
        vec![
            ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
            ("oid".to_string(), order_id),
        ],
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}

async fn cleanup_hyperliquid_state(client: &HyperliquidClient, user: &str) -> dcex::Result<()> {
    let existing = super::common::exchange_method_request(
        client,
        "open_orders",
        vec![("user".to_string(), user.to_string())],
    )
    .await?;
    for order in existing
        .data
        .as_array()
        .into_iter()
        .flatten()
        .filter(|order| order.get("coin").and_then(|coin| coin.as_str()) == Some("BTC"))
    {
        let Some(oid) = find_string(order, &["oid"]) else {
            return Err(live_test_error(format!(
                "Hyperliquid open BTC order has no oid: {order}"
            )));
        };
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_order",
            vec![
                ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
                ("oid".to_string(), oid),
            ],
        )
        .await?;
        assert_success(&cancel);
    }

    let size = hyperliquid_btc_position_size(client, user).await?;
    if size != 0.0 {
        let orderbook = super::common::exchange_method_request(
            client,
            "get_l2book",
            vec![("product_symbol".to_string(), BTC_USD_SWAP.to_string())],
        )
        .await?;
        let (bid, ask) = hyperliquid_bid_ask(&orderbook.data)?;
        let is_buy = size < 0.0;
        let price = if is_buy {
            (ask * 1.005).ceil().to_string()
        } else {
            (bid * 0.995).floor().max(1.0).to_string()
        };
        let close = super::common::exchange_method_request(
            client,
            "place_order",
            vec![
                ("product_symbol".to_string(), BTC_USD_SWAP.to_string()),
                ("isBuy".to_string(), is_buy.to_string()),
                ("price".to_string(), price),
                ("size".to_string(), format_hyperliquid_size(size.abs())),
                ("reduceOnly".to_string(), "true".to_string()),
                ("tif".to_string(), "Ioc".to_string()),
            ],
        )
        .await?;
        assert_success(&close);
    }

    let remaining = super::common::exchange_method_request(
        client,
        "open_orders",
        vec![("user".to_string(), user.to_string())],
    )
    .await?;
    if remaining
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        return Err(live_test_error(
            "Hyperliquid still has open orders after cleanup",
        ));
    }
    if hyperliquid_btc_position_size(client, user).await? != 0.0 {
        return Err(live_test_error(
            "Hyperliquid BTC position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn hyperliquid_btc_position_size(
    client: &HyperliquidClient,
    user: &str,
) -> dcex::Result<f64> {
    let state = super::common::exchange_method_request(
        client,
        "clearinghouse_state",
        vec![("user".to_string(), user.to_string())],
    )
    .await?;
    let Some(positions) = state
        .data
        .get("assetPositions")
        .and_then(|value| value.as_array())
    else {
        return Ok(0.0);
    };
    for item in positions {
        let Some(position) = item.get("position") else {
            continue;
        };
        if position.get("coin").and_then(|coin| coin.as_str()) == Some("BTC") {
            return Ok(find_f64(position, &["szi"]).unwrap_or(0.0));
        }
    }
    Ok(0.0)
}

fn hyperliquid_bid_ask(data: &serde_json::Value) -> dcex::Result<(f64, f64)> {
    let bid = first_bid_price(data)?;
    let ask = data
        .get("levels")
        .and_then(|levels| levels.as_array())
        .and_then(|levels| levels.get(1))
        .and_then(|asks| asks.as_array())
        .and_then(|asks| asks.first())
        .and_then(|level| level.get("px").or_else(|| level.get("price")))
        .and_then(|value| match value {
            serde_json::Value::Number(number) => number.as_f64(),
            serde_json::Value::String(value) => value.parse().ok(),
            _ => None,
        })
        .ok_or_else(|| dcex::DcexError::Decode(format!("Hyperliquid l2book has no ask: {data}")))?;
    Ok((bid, ask))
}

fn format_hyperliquid_size(size: f64) -> String {
    format!("{size:.5}")
        .trim_end_matches('0')
        .trim_end_matches('.')
        .to_string()
}

fn hyperliquid_post_only_buy_price(bid: f64) -> dcex::Result<String> {
    if !bid.is_finite() || bid <= 0.0 {
        return Err(dcex::DcexError::Decode(format!(
            "invalid Hyperliquid bid price: {bid}"
        )));
    }
    Ok(((bid.floor() - 1.0).max(1.0) as i64).to_string())
}

fn hyperliquid_order_size(price: &str, minimum_size: &str) -> dcex::Result<String> {
    let price = price
        .parse::<f64>()
        .map_err(|error| dcex::DcexError::Decode(format!("invalid Hyperliquid price: {error}")))?;
    if !price.is_finite() || price <= 0.0 {
        return Err(dcex::DcexError::Decode(format!(
            "invalid Hyperliquid price: {price}"
        )));
    }
    let minimum_size = minimum_size.parse::<f64>().map_err(|error| {
        dcex::DcexError::Decode(format!("invalid Hyperliquid minimum size: {error}"))
    })?;
    let size = minimum_size.max(0.0002).max(10.5 / price);
    let rounded = (size * 100_000.0).ceil() / 100_000.0;
    Ok(format!("{rounded:.5}")
        .trim_end_matches('0')
        .trim_end_matches('.')
        .to_string())
}
