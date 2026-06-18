use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::okx::OkxClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, fetch_trading_details, format_transfer_amount,
    minimum_order_quantity, params, parse_positive, post_only_buy_price, require_env,
    require_live_trading, require_order_id, BTC_USDT_SPOT,
};

#[tokio::test]
async fn okx_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["OKX_API_KEY", "OKX_API_SECRET", "OKX_PASSPHRASE"]) else {
        return Ok(());
    };
    let client = OkxClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        "0".to_string(),
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .public_request(
            "get_orderbook",
            params(&[("product_symbol", BTC_USDT_SPOT), ("sz", "5")]),
        )
        .await?;
    let details = fetch_trading_details(Exchange::Okx, "okx", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")?;
    let transferred = match ensure_trading_usdt(&client, required_usdt * 1.01).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order_result = client
        .private_request(
            "place_post_only_limit_buy_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("tdMode", "cash"),
                ("sz", quantity.as_str()),
                ("px", price.as_str()),
            ]),
        )
        .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_okx_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["ordId"])?;

    let cancel_result = client
        .private_request(
            "cancel_order",
            params(&[
                ("product_symbol", BTC_USDT_SPOT),
                ("ordId", order_id.as_str()),
            ]),
        )
        .await;
    return_okx_transfer(&client, transferred).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

async fn ensure_trading_usdt(client: &OkxClient, required: f64) -> dcex::Result<Option<f64>> {
    let trading = trading_usdt(client).await?;
    if trading >= required {
        return Ok(Some(0.0));
    }
    let needed = required - trading;
    if funding_usdt(client).await? < needed {
        eprintln!("skipping OKX live stateful order; insufficient transferable USDT");
        return Ok(None);
    }
    let amount = format_transfer_amount(needed);
    let response = client
        .private_request(
            "funds_transfer",
            params(&[
                ("ccy", "USDT"),
                ("amt", amount.as_str()),
                ("from_account", "FUND"),
                ("to_account", "TRADING"),
            ]),
        )
        .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_okx_transfer(client: &OkxClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let available = trading_usdt(client).await?;
    let amount = format_transfer_amount(amount.min(available));
    if amount == "0" {
        return Ok(());
    }
    let response = client
        .private_request(
            "funds_transfer",
            params(&[
                ("ccy", "USDT"),
                ("amt", amount.as_str()),
                ("from_account", "TRADING"),
                ("to_account", "FUND"),
            ]),
        )
        .await?;
    assert_success(&response);
    Ok(())
}

async fn trading_usdt(client: &OkxClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_account_balance", params(&[("ccy", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availBal", "availEq", "cashBal"],
    ))
}

async fn funding_usdt(client: &OkxClient) -> dcex::Result<f64> {
    let response = client
        .private_request("get_balances", params(&[("ccy", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availBal", "availEq", "bal"],
    ))
}
