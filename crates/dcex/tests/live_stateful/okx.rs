use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::okx::OkxClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, first_bid_price,
    format_step_decimal, format_transfer_amount, format_transfer_amount_floor,
    insufficient_funds_error, leveraged_margin_required, live_test_error, margin_target,
    minimum_order_quantity, params, parse_positive, post_only_buy_price, require_env,
    require_live_trading, require_order_id, round_down_to_step, sum_abs_values_for_symbols,
    wait_for_flat_position, wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const OKX_SWAP_LEVERAGE: &str = "50";
const OKX_SWAP_LEVERAGE_VALUE: f64 = 50.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
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
    cleanup_okx_spot_state(&client, 0.0).await?;
    let initial_btc = okx_spot_btc(&client).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
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
        None => {
            return Err(live_test_error(
                "OKX trading account has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
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

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("ordId", order_id.as_str()),
        ]),
    )
    .await;
    let cleanup_result = cleanup_okx_spot_state(&client, initial_btc).await;
    let transfer_result = return_okx_transfer(&client, transferred).await;
    cleanup_result?;
    transfer_result?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn okx_swap_direct_live_stateful_order() -> dcex::Result<()> {
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

    cleanup_okx_swap_state(&client).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_orderbook",
        params(&[("product_symbol", BTC_USDT_SWAP), ("sz", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Okx, "okx", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let leverage = super::common::exchange_method_request(
        &client,
        "set_leverage",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("lever", OKX_SWAP_LEVERAGE),
            ("mgnMode", "cross"),
        ]),
    )
    .await?;
    assert_success(&leverage);
    let market_price_estimate = first_bid_price(&orderbook.data)?;
    let required_usdt = leveraged_margin_required(
        market_price_estimate,
        &quantity,
        &details,
        OKX_SWAP_LEVERAGE_VALUE,
    )?;
    let transferred = match ensure_trading_usdt(&client, margin_target(required_usdt)).await? {
        Some(amount) => amount,
        None => {
            return Err(live_test_error(
                "OKX swap has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("tdMode", "cross"),
            ("sz", quantity.as_str()),
            ("px", price.as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) if insufficient_funds_error(&error) => {
            return_okx_transfer(&client, transferred).await?;
            return Err(live_test_error(format!(
                "OKX swap insufficient margin for post-only order: {error}"
            )));
        }
        Err(error) => {
            return_okx_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["ordId"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("ordId", order_id.as_str()),
        ]),
    )
    .await?;
    assert_success(&cancel);

    let open_result = super::common::exchange_method_request(
        &client,
        "place_market_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("tdMode", "cross"),
            ("sz", quantity.as_str()),
        ]),
    )
    .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) if insufficient_funds_error(&error) => {
            return_okx_transfer(&client, transferred).await?;
            return Err(live_test_error(format!(
                "OKX swap insufficient margin for market open: {error}"
            )));
        }
        Err(error) => {
            return_okx_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&opened);
    assert!(wait_for_positive_position(|| okx_swap_position_abs(&client)).await? > 0.0);

    let closed = super::common::exchange_method_request(
        &client,
        "close_positions",
        params(&[("product_symbol", BTC_USDT_SWAP), ("mgnMode", "cross")]),
    )
    .await?;
    assert_success(&closed);
    assert_eq!(
        wait_for_flat_position(|| okx_swap_position_abs(&client)).await?,
        0.0
    );

    return_okx_transfer(&client, transferred).await?;
    Ok(())
}

async fn ensure_trading_usdt(client: &OkxClient, required: f64) -> dcex::Result<Option<f64>> {
    let trading = trading_usdt(client).await?;
    if trading >= required {
        return Ok(Some(0.0));
    }
    let needed = required - trading;
    let funding = funding_usdt(client).await?;
    if funding < needed {
        return Ok(None);
    }
    let amount = format_transfer_amount(needed);
    let response = super::common::exchange_method_request(
        &client,
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
    let amount = format_transfer_amount_floor(amount.min(available), 6);
    if amount == "0" {
        return Ok(());
    }
    let response = super::common::exchange_method_request(
        &client,
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
    let response = super::common::exchange_method_request(
        &client,
        "get_account_balance",
        params(&[("ccy", "USDT")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availBal", "availEq", "cashBal"],
    ))
}

async fn funding_usdt(client: &OkxClient) -> dcex::Result<f64> {
    let response =
        super::common::exchange_method_request(&client, "get_balances", params(&[("ccy", "USDT")]))
            .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availBal", "availEq", "bal"],
    ))
}

async fn cleanup_okx_orders(client: &OkxClient, product_symbol: &str) -> dcex::Result<()> {
    let response = super::common::exchange_method_request(
        client,
        "get_order_list",
        params(&[("product_symbol", product_symbol), ("limit", "20")]),
    )
    .await?;
    if contains_non_empty_array(&response.data, &["data"]) {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_all_orders",
            params(&[("product_symbol", product_symbol)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    let remaining = super::common::exchange_method_request(
        client,
        "get_order_list",
        params(&[("product_symbol", product_symbol), ("limit", "20")]),
    )
    .await?;
    if contains_non_empty_array(&remaining.data, &["data"]) {
        return Err(live_test_error(format!(
            "OKX {product_symbol} still has open orders after cleanup"
        )));
    }
    Ok(())
}

async fn cleanup_okx_spot_state(client: &OkxClient, initial_btc: f64) -> dcex::Result<()> {
    cleanup_okx_orders(client, BTC_USDT_SPOT).await?;
    let current = okx_spot_btc(client).await?;
    if current <= initial_btc {
        return Ok(());
    }

    let orderbook = super::common::exchange_method_request(
        client,
        "get_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("sz", "5")]),
    )
    .await?;
    let bid = first_bid_price(&orderbook.data)?;
    let details = fetch_trading_details(Exchange::Okx, "okx", BTC_USDT_SPOT).await?;
    let step = parse_positive(&details.size_precision, "size_precision")?;
    let quantity = round_down_to_step(current - initial_btc, step);
    if quantity <= 0.0 {
        return Ok(());
    }
    let min_size = details.min_size.parse::<f64>().unwrap_or(0.0);
    let min_notional = details.min_notional.parse::<f64>().unwrap_or(0.0);
    if quantity < min_size || quantity * bid < min_notional {
        if current - initial_btc > step {
            return Err(live_test_error(format!(
                "OKX BTC spot excess is below minimum sell size after cleanup: quantity={quantity}, min_size={min_size}, notional={}",
                quantity * bid
            )));
        }
        return Ok(());
    }

    let quantity = format_step_decimal(quantity, step)?;
    let sell = super::common::exchange_method_request(
        client,
        "place_market_sell_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("tdMode", "cash"),
            ("sz", quantity.as_str()),
        ]),
    )
    .await?;
    assert_success(&sell);
    sleep(Duration::from_secs(2)).await;

    let remaining = okx_spot_btc(client).await?;
    if remaining > initial_btc + step {
        return Err(live_test_error(format!(
            "OKX BTC spot excess remains after cleanup: current={remaining}, initial={initial_btc}",
        )));
    }
    Ok(())
}

async fn cleanup_okx_swap_state(client: &OkxClient) -> dcex::Result<()> {
    cleanup_okx_orders(client, BTC_USDT_SWAP).await?;
    if okx_swap_position_abs(client).await? != 0.0 {
        let close = super::common::exchange_method_request(
            client,
            "close_positions",
            params(&[("product_symbol", BTC_USDT_SWAP), ("mgnMode", "cross")]),
        )
        .await?;
        assert_success(&close);
        sleep(Duration::from_secs(2)).await;
    }
    if wait_for_flat_position(|| okx_swap_position_abs(client)).await? != 0.0 {
        return Err(live_test_error(
            "OKX BTC-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn okx_swap_position_abs(client: &OkxClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["instId"],
        &[BTC_USDT_SWAP],
        &["pos"],
    ))
}

async fn okx_spot_btc(client: &OkxClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        client,
        "get_account_balance",
        params(&[("ccy", "BTC")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "BTC",
        &["availBal", "availEq", "cashBal"],
    ))
}
