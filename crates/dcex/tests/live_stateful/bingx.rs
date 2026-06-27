use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bingx::BingxClient;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    format_transfer_amount, leveraged_margin_required, minimum_order_quantity, params,
    post_only_buy_price, require_env, require_live_trading, require_order_id,
    sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};
use tokio::time::sleep;

const BINGX_SYMBOL: &str = "BTC-USDT";
const BINGX_FUND_ACCOUNT: &str = "fund";
const BINGX_SPOT_ACCOUNT: &str = "spot";
const BINGX_SWAP_ACCOUNT: &str = "USDTMPerp";
const BINGX_LEVERAGE_VALUE: f64 = 10.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bingx_spot_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BINGX_API_KEY", "BINGX_API_SECRET"]) else {
        return Ok(());
    };
    let client = BingxClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if bingx_spot_open_orders(&client).await? {
        eprintln!("skipping BingX spot live stateful order; open BTC-USDT spot orders exist");
        return Ok(());
    }

    let orderbook = client
        .get_spot_orderbook_with(params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]))
        .await?;
    let details = fetch_trading_details(Exchange::BingX, "bingx", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = super::common::order_notional(
        price.parse::<f64>().unwrap_or_default(),
        &quantity,
        &details,
    )?;
    if !ensure_bingx_usdt(&client, BINGX_SPOT_ACCOUNT, required_usdt).await? {
        eprintln!(
            "skipping BingX spot live stateful order; insufficient transferable USDT, required={required_usdt:.8}"
        );
        return Ok(());
    }

    let order = client
        .place_spot_post_only_buy_order_with(params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel = client
        .cancel_spot_order_with(params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("orderId", order_id.as_str()),
        ]))
        .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn bingx_swap_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BINGX_API_KEY", "BINGX_API_SECRET"]) else {
        return Ok(());
    };
    let client = BingxClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if bingx_swap_open_orders(&client).await? {
        eprintln!("skipping BingX swap live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }
    if bingx_swap_position_abs(&client).await? > 0.0 {
        eprintln!("skipping BingX swap live stateful order; BTC-USDT swap position exists");
        return Ok(());
    }

    let orderbook = client
        .get_orderbook_with(params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "5")]))
        .await?;
    let details = fetch_trading_details(Exchange::BingX, "bingx", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let market_price = bingx_swap_market_price(&client).await?;
    let required_usdt =
        leveraged_margin_required(market_price, &quantity, &details, BINGX_LEVERAGE_VALUE)?;
    if !ensure_bingx_usdt(&client, BINGX_SWAP_ACCOUNT, required_usdt).await? {
        eprintln!(
            "skipping BingX swap live stateful order; insufficient transferable USDT, required={required_usdt:.8}"
        );
        return Ok(());
    }

    let order = client
        .place_swap_post_only_buy_order_with(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("positionSide", "LONG"),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel = client
        .cancel_swap_order_with(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("orderId", order_id.as_str()),
        ]))
        .await?;
    assert_success(&cancel);

    let market_order = client
        .place_swap_market_buy_order_with(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("quantity", quantity.as_str()),
            ("positionSide", "LONG"),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&market_order);
    assert!(wait_for_positive_position(|| bingx_swap_position_abs(&client)).await? > 0.0);

    let close = client
        .close_swap_all_positions_with(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    assert_success(&close);
    assert_eq!(
        wait_for_flat_position(|| bingx_swap_position_abs(&client)).await?,
        0.0
    );
    Ok(())
}

async fn bingx_spot_open_orders(client: &BingxClient) -> dcex::Result<bool> {
    let response = client
        .get_spot_open_orders_with(params(&[("product_symbol", BTC_USDT_SPOT)]))
        .await?;
    Ok(contains_non_empty_array(&response.data, &["orders"]))
}

async fn bingx_swap_open_orders(client: &BingxClient) -> dcex::Result<bool> {
    let response = client
        .get_open_orders_with(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    Ok(contains_non_empty_array(&response.data, &["orders"]))
}

async fn bingx_swap_position_abs(client: &BingxClient) -> dcex::Result<f64> {
    let response = client
        .get_open_positions_with(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &[BINGX_SYMBOL],
        &["positionAmt", "positionAmount"],
    ))
}

async fn bingx_spot_usdt(client: &BingxClient) -> dcex::Result<f64> {
    let response = client.get_spot_account_balance().await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn bingx_fund_usdt(client: &BingxClient) -> dcex::Result<f64> {
    let response = client
        .get_fund_account_balance_with(params(&[("asset", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["free", "available", "availableBalance", "balance"],
    ))
}

async fn bingx_swap_usdt(client: &BingxClient) -> dcex::Result<f64> {
    let response = client.get_swap_account_balance().await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableMargin", "availableBalance", "available"],
    ))
}

async fn ensure_bingx_usdt(
    client: &BingxClient,
    target_account: &str,
    required: f64,
) -> dcex::Result<bool> {
    if bingx_account_usdt(client, target_account).await? >= required {
        return Ok(true);
    }

    for source_account in transfer_sources_for(target_account) {
        let current = bingx_account_usdt(client, target_account).await?;
        if current >= required {
            return Ok(true);
        }
        let needed = required - current;
        let source_available = match bingx_account_usdt(client, source_account).await {
            Ok(value) => value,
            Err(error) => {
                eprintln!(
                    "skipping BingX transfer source {source_account}; balance unavailable: {error}"
                );
                continue;
            }
        };
        let transferable = match bingx_transferable_usdt(client, source_account, target_account)
            .await
        {
            Ok(value) => value,
            Err(error) => {
                eprintln!(
                    "skipping BingX transfer route {source_account}->{target_account}; transferable amount unavailable: {error}"
                );
                continue;
            }
        };
        let available = source_available.min(transferable);
        if available <= 0.0 {
            continue;
        }

        let amount = available.min((needed + 0.5).max(1.0));
        if amount <= 0.0 {
            continue;
        }
        let amount = format_transfer_amount(amount);
        let transfer = client
            .asset_transfer_with(params(&[
                ("fromAccount", source_account),
                ("toAccount", target_account),
                ("asset", "USDT"),
                ("amount", amount.as_str()),
            ]))
            .await;
        let transfer = match transfer {
            Ok(response) => response,
            Err(error) => {
                eprintln!(
                    "skipping BingX transfer route {source_account}->{target_account}; transfer failed: {error}"
                );
                continue;
            }
        };
        assert_success(&transfer);
        sleep(Duration::from_secs(2)).await;
    }

    Ok(bingx_account_usdt(client, target_account).await? >= required)
}

fn transfer_sources_for(target_account: &str) -> &'static [&'static str] {
    match target_account {
        BINGX_SPOT_ACCOUNT => &[BINGX_FUND_ACCOUNT, BINGX_SWAP_ACCOUNT],
        BINGX_SWAP_ACCOUNT => &[BINGX_FUND_ACCOUNT, BINGX_SPOT_ACCOUNT],
        _ => &[BINGX_FUND_ACCOUNT, BINGX_SPOT_ACCOUNT, BINGX_SWAP_ACCOUNT],
    }
}

async fn bingx_account_usdt(client: &BingxClient, account: &str) -> dcex::Result<f64> {
    match account {
        BINGX_FUND_ACCOUNT => bingx_fund_usdt(client).await,
        BINGX_SPOT_ACCOUNT => bingx_spot_usdt(client).await,
        BINGX_SWAP_ACCOUNT => bingx_swap_usdt(client).await,
        _ => Ok(0.0),
    }
}

async fn bingx_transferable_usdt(
    client: &BingxClient,
    from_account: &str,
    to_account: &str,
) -> dcex::Result<f64> {
    let response = client
        .get_transferable_coins_with(params(&[
            ("fromAccount", from_account),
            ("toAccount", to_account),
        ]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableTransferAmount", "amount", "available", "free"],
    ))
}

async fn bingx_swap_market_price(client: &BingxClient) -> dcex::Result<f64> {
    let response = client
        .get_ticker_with(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    find_f64(&response.data, &["lastPrice", "last", "price"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!(
            "BingX swap ticker has no usable market price: {response:?}"
        ))
    })
}
