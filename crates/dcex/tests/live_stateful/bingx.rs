use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bingx::BingxClient;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    first_bid_price, format_transfer_amount_floor, insufficient_funds_error,
    leveraged_margin_required, margin_target, minimum_order_quantity, params, post_only_buy_price,
    price_below_market, require_env, require_live_trading, require_order_id,
    sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};
use tokio::time::sleep;

const BINGX_SYMBOL: &str = "BTC-USDT";
const BINGX_FUND_ACCOUNT: &str = "fund";
const BINGX_SPOT_ACCOUNT: &str = "spot";
const BINGX_SWAP_ACCOUNT: &str = "USDTMPerp";
const BINGX_LEVERAGE_VALUE: f64 = 10.0;

struct BingxTransferBack {
    from_account: &'static str,
    to_account: &'static str,
    amount: f64,
}

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

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::BingX, "bingx", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt = super::common::order_notional(
        price.parse::<f64>().unwrap_or_default(),
        &quantity,
        &details,
    )?;
    let transfers = match ensure_bingx_usdt(&client, BINGX_SPOT_ACCOUNT, required_usdt).await? {
        Some(transfers) => transfers,
        None => {
            eprintln!(
                "skipping BingX spot live stateful order; insufficient transferable USDT, required={required_usdt:.8}"
            );
            return Ok(());
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_bingx_transfers(&client, &transfers).await?;
            return Err(error);
        }
    };
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
    return_bingx_transfers(&client, &transfers).await?;
    let cancel = cancel_result?;
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

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_orderbook",
        params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::BingX, "bingx", BTC_USDT_SWAP).await?;
    let price = price_below_market(first_bid_price(&orderbook.data)?, &details, 0.95)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let market_price = bingx_swap_market_price(&client).await?;
    let required_usdt =
        leveraged_margin_required(market_price, &quantity, &details, BINGX_LEVERAGE_VALUE)?;
    let transfers = match ensure_bingx_usdt(
        &client,
        BINGX_SWAP_ACCOUNT,
        margin_target(required_usdt),
    )
    .await?
    {
        Some(transfers) => transfers,
        None => {
            eprintln!(
                    "skipping BingX swap live stateful order; insufficient transferable USDT, required={required_usdt:.8}"
                );
            return Ok(());
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_swap_post_only_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
            ("positionSide", "LONG"),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) if insufficient_funds_error(&error) => {
            return_bingx_transfers(&client, &transfers).await?;
            eprintln!(
                "skipping BingX swap live stateful order; insufficient margin for post-only order: {error}"
            );
            return Ok(());
        }
        Err(error) => {
            return_bingx_transfers(&client, &transfers).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_swap_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("orderId", order_id.as_str()),
        ]),
    )
    .await;
    let cancel = match cancel_result {
        Ok(cancel) => cancel,
        Err(error) => {
            return_bingx_transfers(&client, &transfers).await?;
            return Err(error);
        }
    };
    assert_success(&cancel);

    let market_order_result = super::common::exchange_method_request(
        &client,
        "place_swap_market_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("quantity", quantity.as_str()),
            ("positionSide", "LONG"),
            ("clientOrderId", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let market_order = match market_order_result {
        Ok(market_order) => market_order,
        Err(error) if insufficient_funds_error(&error) => {
            return_bingx_transfers(&client, &transfers).await?;
            eprintln!(
                "skipping BingX swap live stateful order; insufficient margin for market open: {error}"
            );
            return Ok(());
        }
        Err(error) => {
            return_bingx_transfers(&client, &transfers).await?;
            return Err(error);
        }
    };
    assert_success(&market_order);
    assert!(wait_for_positive_position(|| bingx_swap_position_abs(&client)).await? > 0.0);

    let close = super::common::exchange_method_request(
        &client,
        "close_swap_all_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    assert_success(&close);
    assert_eq!(
        wait_for_flat_position(|| bingx_swap_position_abs(&client)).await?,
        0.0
    );
    return_bingx_transfers(&client, &transfers).await?;
    Ok(())
}

async fn bingx_spot_open_orders(client: &BingxClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_spot_open_orders",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["orders"]))
}

async fn bingx_swap_open_orders(client: &BingxClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_open_orders",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["orders"]))
}

async fn bingx_swap_position_abs(client: &BingxClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_open_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
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
    let response = super::common::exchange_method_request(
        &client,
        "get_fund_account_balance",
        params(&[("asset", "USDT")]),
    )
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
    target_account: &'static str,
    required: f64,
) -> dcex::Result<Option<Vec<BingxTransferBack>>> {
    let mut transfers = Vec::new();
    if bingx_account_usdt(client, target_account).await? >= required {
        return Ok(Some(transfers));
    }

    for source_account in transfer_sources_for(target_account) {
        let current = bingx_account_usdt(client, target_account).await?;
        if current >= required {
            return Ok(Some(transfers));
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
        match bingx_transfer(client, source_account, target_account, amount).await {
            Ok(()) => {
                transfers.push(BingxTransferBack {
                    from_account: target_account,
                    to_account: source_account,
                    amount,
                });
                sleep(Duration::from_secs(2)).await;
            }
            Err(error) => {
                eprintln!(
                    "skipping BingX transfer route {source_account}->{target_account}; transfer failed: {error}"
                );
            }
        }
    }

    if bingx_account_usdt(client, target_account).await? >= required {
        return Ok(Some(transfers));
    }
    return_bingx_transfers(client, &transfers).await?;
    Ok(None)
}

async fn return_bingx_transfers(
    client: &BingxClient,
    transfers: &[BingxTransferBack],
) -> dcex::Result<()> {
    for transfer in transfers.iter().rev() {
        if transfer.amount <= 0.0 {
            continue;
        }
        let available = bingx_account_usdt(client, transfer.from_account).await?;
        let amount = transfer.amount.min(available);
        if amount <= 0.0 {
            continue;
        }
        bingx_transfer(client, transfer.from_account, transfer.to_account, amount).await?;
    }
    Ok(())
}

async fn bingx_transfer(
    client: &BingxClient,
    from_account: &str,
    to_account: &str,
    amount: f64,
) -> dcex::Result<()> {
    let amount = format_transfer_amount_floor(amount, 6);
    let response = super::common::exchange_method_request(
        &client,
        "asset_transfer",
        params(&[
            ("fromAccount", from_account),
            ("toAccount", to_account),
            ("asset", "USDT"),
            ("amount", amount.as_str()),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
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
    let response = super::common::exchange_method_request(
        &client,
        "get_transferable_coins",
        params(&[("fromAccount", from_account), ("toAccount", to_account)]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableTransferAmount", "amount", "available", "free"],
    ))
}

async fn bingx_swap_market_price(client: &BingxClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_ticker",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    find_f64(&response.data, &["lastPrice", "last", "price"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!(
            "BingX swap ticker has no usable market price: {response:?}"
        ))
    })
}
