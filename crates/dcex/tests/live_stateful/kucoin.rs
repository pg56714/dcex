use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::kucoin::KucoinClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, fetch_trading_details, first_bid_price, format_step_decimal,
    live_test_error, minimum_order_quantity, params, parse_positive, post_only_buy_price,
    require_env, require_live_trading, require_order_id, round_down_to_step, unique_client_id,
    BTC_USDT_SPOT,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kucoin_spot_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "KUCOIN_API_KEY",
        "KUCOIN_API_SECRET",
        "KUCOIN_API_PASSPHRASE",
    ]) else {
        return Ok(());
    };
    let client = KucoinClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    cleanup_kucoin_spot_state(&client, 0.0).await?;
    let initial_btc = kucoin_spot_btc(&client).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::KuCoin, "kucoin", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let size = minimum_order_quantity(&price, &details)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("size", size.as_str()),
            ("price", price.as_str()),
            ("clientOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_spot_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await;
    let cleanup_result = cleanup_kucoin_spot_state(&client, initial_btc).await;
    let cancel = cancel_result?;
    assert_success(&cancel);
    cleanup_result?;
    Ok(())
}

async fn cleanup_kucoin_spot_orders(client: &KucoinClient) -> dcex::Result<()> {
    let open_orders = super::common::exchange_method_request(
        client,
        "get_spot_open_orders",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    if open_orders
        .data
        .get("items")
        .and_then(|v| v.as_array())
        .is_some_and(|items| !items.is_empty())
    {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_spot_all_orders_by_symbol",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        assert_success(&cancel);
        let remaining = super::common::exchange_method_request(
            client,
            "get_spot_open_orders",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        if remaining
            .data
            .get("items")
            .and_then(|v| v.as_array())
            .is_some_and(|items| !items.is_empty())
        {
            return Err(live_test_error(
                "KuCoin spot still has open BTC-USDT orders after cleanup",
            ));
        }
    }
    Ok(())
}

async fn cleanup_kucoin_spot_state(client: &KucoinClient, initial_btc: f64) -> dcex::Result<()> {
    cleanup_kucoin_spot_orders(client).await?;
    let current = kucoin_spot_btc(client).await?;
    if current <= initial_btc {
        return Ok(());
    }

    let orderbook = super::common::exchange_method_request(
        client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::KuCoin, "kucoin", BTC_USDT_SPOT).await?;
    let bid = first_bid_price(&orderbook.data)?;
    let step = parse_positive(&details.size_precision, "size_precision")?;
    let size = round_down_to_step(current - initial_btc, step);
    if size <= 0.0 {
        return Ok(());
    }
    let min_size = details.min_size.parse::<f64>().unwrap_or(0.0);
    let min_notional = details.min_notional.parse::<f64>().unwrap_or(0.0);
    if size < min_size || size * bid < min_notional {
        if current - initial_btc > step {
            return Err(live_test_error(format!(
                "KuCoin BTC spot excess is below minimum sell size after cleanup: size={size}, min_size={min_size}, notional={}",
                size * bid
            )));
        }
        return Ok(());
    }

    let size = format_step_decimal(size, step)?;
    let sell = super::common::exchange_method_request(
        client,
        "place_spot_market_sell_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("size", size.as_str()),
            ("clientOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await?;
    assert_success(&sell);
    sleep(Duration::from_secs(2)).await;

    let remaining = kucoin_spot_btc(client).await?;
    if remaining > initial_btc + step {
        return Err(live_test_error(format!(
            "KuCoin BTC spot excess remains after cleanup: current={remaining}, initial={initial_btc}",
        )));
    }
    Ok(())
}

async fn kucoin_spot_btc(client: &KucoinClient) -> dcex::Result<f64> {
    let response = client.get_account_balance().await?;
    Ok(asset_amount(
        &response.data,
        "BTC",
        &["available", "balance", "free"],
    ))
}
