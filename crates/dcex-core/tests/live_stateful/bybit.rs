use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bybit::BybitClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, fetch_trading_details, format_transfer_amount_ceil,
    minimum_order_quantity, params, parse_positive, post_only_buy_price, require_env,
    require_live_trading, require_order_id, BTC_USDT_SPOT,
};

#[tokio::test]
async fn bybit_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BYBIT_API_KEY", "BYBIT_API_SECRET"]) else {
        return Ok(());
    };
    let client = BybitClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        5_000,
        true,
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Bybit, "bybit", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")?;
    let transferred = match ensure_unified_usdt(&client, required_usdt * 1.01).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order_result = client
        .private_request(
            "place_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("qty", quantity.as_str()),
                ("price", price.as_str()),
            ]),
        )
        .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_bybit_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_result = client
        .private_request(
            "cancel_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("orderId", order_id.as_str()),
            ]),
        )
        .await;
    return_bybit_transfer(&client, transferred).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

async fn ensure_unified_usdt(client: &BybitClient, required: f64) -> dcex::Result<Option<f64>> {
    let unified = account_usdt(client, "UNIFIED").await?;
    if unified >= required {
        return Ok(Some(0.0));
    }
    let needed = required - unified;
    if account_usdt(client, "FUND").await? < needed {
        eprintln!("skipping Bybit live stateful order; insufficient transferable USDT");
        return Ok(None);
    }
    let amount = format_transfer_amount_ceil(needed, 4);
    let response = client
        .private_request(
            "create_internal_transfer",
            params(&[
                ("coin", "USDT"),
                ("amount", amount.as_str()),
                ("fromAccountType", "FUND"),
                ("toAccountType", "UNIFIED"),
            ]),
        )
        .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_bybit_transfer(client: &BybitClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let available = account_usdt(client, "UNIFIED").await?;
    let amount = format_transfer_amount_ceil(amount.min(available), 4);
    if amount == "0" {
        return Ok(());
    }
    let response = client
        .private_request(
            "create_internal_transfer",
            params(&[
                ("coin", "USDT"),
                ("amount", amount.as_str()),
                ("fromAccountType", "UNIFIED"),
                ("toAccountType", "FUND"),
            ]),
        )
        .await?;
    assert_success(&response);
    Ok(())
}

async fn account_usdt(client: &BybitClient, account_type: &str) -> dcex::Result<f64> {
    let response = client
        .private_request(
            "get_coin_balance",
            params(&[("accountType", account_type), ("coin", "USDT")]),
        )
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &[
            "transferBalance",
            "walletBalance",
            "availableToWithdraw",
            "availableBalance",
        ],
    ))
}
