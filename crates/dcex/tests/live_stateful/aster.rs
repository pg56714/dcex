use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::aster::AsterClient;

use super::common::{
    assert_success, fetch_trading_details, find_f64, first_bid_price, live_test_error,
    minimum_order_quantity, params, post_only_buy_price, require_env, require_live_fill,
    require_live_trading, require_order_id, wait_for_flat_position, wait_for_positive_position,
    BTC_USDT_SWAP,
};

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn aster_futures_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "ASTER_USER_ADDRESS",
        "ASTER_SIGNER_ADDRESS",
        "ASTER_PRIVATE_KEY",
    ]) else {
        return Ok(());
    };
    let client = AsterClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let open_orders = super::common::exchange_method_request(
        &client,
        "get_futures_open_orders",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    if open_orders
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
    {
        let cancel = super::common::exchange_method_request(
            &client,
            "cancel_all_futures_open_orders",
            params(&[("product_symbol", BTC_USDT_SWAP)]),
        )
        .await?;
        assert_success(&cancel);
        let remaining = super::common::exchange_method_request(
            &client,
            "get_futures_open_orders",
            params(&[("product_symbol", BTC_USDT_SWAP)]),
        )
        .await?;
        if remaining
            .data
            .as_array()
            .is_some_and(|orders| !orders.is_empty())
        {
            return Err(live_test_error(
                "Aster futures still has open BTC-USDT swap orders after cleanup",
            ));
        }
    }

    let orderbook = client.get_futures_orderbook(BTC_USDT_SWAP).limit(5).await?;
    let details = fetch_trading_details(Exchange::Aster, "aster", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let order = super::common::exchange_method_request(
        &client,
        "place_futures_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("timeInForce", "GTC"),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;
    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_futures_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access and real fills"]
async fn aster_futures_direct_live_fill_and_close() -> dcex::Result<()> {
    if !require_live_fill() {
        return Ok(());
    }
    let Some(keys) = require_env(&[
        "ASTER_USER_ADDRESS",
        "ASTER_SIGNER_ADDRESS",
        "ASTER_PRIVATE_KEY",
    ]) else {
        return Ok(());
    };
    let client = AsterClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;
    let open_orders = super::common::exchange_method_request(
        &client,
        "get_futures_open_orders",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    if open_orders
        .data
        .as_array()
        .is_some_and(|orders| !orders.is_empty())
        || aster_futures_position(&client).await? != 0.0
    {
        return Err(live_test_error(
            "Aster fill test requires no BTC-USDT orders or position",
        ));
    }

    let book = client.get_futures_orderbook(BTC_USDT_SWAP).limit(5).await?;
    let details = fetch_trading_details(Exchange::Aster, "aster", BTC_USDT_SWAP).await?;
    let bid = first_bid_price(&book.data)?;
    let minimum_price = post_only_buy_price(&book.data, &details)?;
    let quantity = minimum_order_quantity(&minimum_price, &details)?;
    let notional = bid * quantity.parse::<f64>().unwrap_or(0.0);
    if notional > 25.0 {
        return Err(live_test_error(format!(
            "Aster minimum fill order exceeds 25 USDT: {notional}"
        )));
    }

    let lifecycle_result = async {
        let buy = super::common::exchange_method_request(
            &client,
            "place_futures_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("side", "BUY"),
                ("type", "MARKET"),
                ("quantity", quantity.as_str()),
                ("newOrderRespType", "RESULT"),
            ]),
        )
        .await?;
        assert_success(&buy);
        let filled = wait_for_positive_position(|| aster_futures_position(&client)).await?;
        if filled <= 0.0 {
            return Err(live_test_error(
                "Aster market buy did not create a long position",
            ));
        }
        let close = super::common::exchange_method_request(
            &client,
            "place_futures_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("side", "SELL"),
                ("type", "MARKET"),
                ("quantity", filled.to_string().as_str()),
                ("reduceOnly", "true"),
                ("newOrderRespType", "RESULT"),
            ]),
        )
        .await?;
        assert_success(&close);
        Ok::<(), dcex::DcexError>(())
    }
    .await;
    let cleanup_result = close_aster_futures_position(&client).await;
    cleanup_result?;
    lifecycle_result
}

async fn aster_futures_position(client: &AsterClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        client,
        "get_futures_position_risk",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(response
        .data
        .as_array()
        .into_iter()
        .flatten()
        .map(|position| find_f64(position, &["positionAmt"]).unwrap_or(0.0))
        .sum())
}

async fn close_aster_futures_position(client: &AsterClient) -> dcex::Result<()> {
    let position = aster_futures_position(client).await?;
    if position != 0.0 {
        let side = if position > 0.0 { "SELL" } else { "BUY" };
        let quantity = position.abs().to_string();
        let close = super::common::exchange_method_request(
            client,
            "place_futures_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("side", side),
                ("type", "MARKET"),
                ("quantity", quantity.as_str()),
                ("reduceOnly", "true"),
                ("newOrderRespType", "RESULT"),
            ]),
        )
        .await?;
        assert_success(&close);
    }
    if wait_for_flat_position(|| aster_futures_position(client)).await? != 0.0 {
        return Err(live_test_error(
            "Aster position remains after reduce-only close",
        ));
    }
    Ok(())
}
