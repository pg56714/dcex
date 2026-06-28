use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::kraken::KrakenClient;
use serde_json::Value;
use tokio::time::sleep;

use super::common::{
    assert_success, contains_non_empty_array, fetch_trading_details, find_f64, first_bid_price,
    format_transfer_amount_ceil, leveraged_margin_required, minimum_order_quantity, optional_env,
    params, parse_positive, post_only_buy_price, require_env, require_live_trading,
    require_order_id, sum_abs_values_for_symbols, wait_for_flat_position,
    wait_for_non_empty_records, wait_for_positive_position, BTC_USDT_SPOT, BTC_USD_SWAP,
};

const KRAKEN_FUTURES_MARGIN_LEVERAGE_VALUE: f64 = 50.0;

struct KrakenSpotTransferBack {
    amount: f64,
    futures_wallet: &'static str,
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kraken_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["KRAKEN_SPOT_API_KEY", "KRAKEN_SPOT_API_SECRET"]) else {
        return Ok(());
    };
    let futures_key = optional_env("KRAKEN_FUTURES_API_KEY");
    let futures_secret = optional_env("KRAKEN_FUTURES_API_SECRET");
    let client = KrakenClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        futures_key,
        futures_secret,
        Duration::from_secs(20),
    )?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("count", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Kraken, "kraken", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt =
        parse_positive(&price, "price")? * parse_positive(&quantity, "quantity")? * 1.01;
    let transfer = match ensure_kraken_spot_usdt(&client, required_usdt).await? {
        Some(transfer) => transfer,
        None => return Ok(()),
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("volume", quantity.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_kraken_spot_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["txid"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_spot_order",
        params(&[("txid", order_id.as_str())]),
    )
    .await;
    return_kraken_spot_transfer(&client, &transfer).await?;
    let cancel = cancel_result?;
    assert_success(&cancel);
    Ok(())
}

async fn ensure_kraken_spot_usdt(
    client: &KrakenClient,
    required: f64,
) -> dcex::Result<Option<KrakenSpotTransferBack>> {
    let spot = kraken_spot_balance(client, "USDT").await?;
    if spot >= required {
        return Ok(Some(KrakenSpotTransferBack {
            amount: 0.0,
            futures_wallet: "cash",
        }));
    }
    let needed = required - spot;
    let accounts = match client.get_futures_accounts().await {
        Ok(accounts) => accounts,
        Err(error) => {
            eprintln!(
                "skipping Kraken spot live stateful order; insufficient spot USDT and futures balance unavailable, required={required:.8}, spot={spot:.8}: {error}"
            );
            return Ok(None);
        }
    };
    let cash = kraken_cash_available(&accounts.data, "usdt");
    let flex = kraken_flex_available(&accounts.data);
    let futures_wallet = if cash >= needed {
        "cash"
    } else if flex >= needed {
        "flex"
    } else {
        eprintln!(
            "skipping Kraken spot live stateful order; insufficient transferable USDT, required={required:.8}, spot={spot:.8}, cash={cash:.8}, flex={flex:.8}"
        );
        return Ok(None);
    };

    withdraw_kraken_futures_to_spot(client, needed, futures_wallet).await?;
    sleep(Duration::from_secs(5)).await;
    let transfer = KrakenSpotTransferBack {
        amount: needed,
        futures_wallet,
    };
    if kraken_spot_balance(client, "USDT").await? < required {
        return_kraken_spot_transfer(client, &transfer).await?;
        eprintln!(
            "skipping Kraken spot live stateful order; spot USDT remains insufficient, required={required:.8}"
        );
        return Ok(None);
    }
    Ok(Some(transfer))
}

async fn return_kraken_spot_transfer(
    client: &KrakenClient,
    transfer: &KrakenSpotTransferBack,
) -> dcex::Result<()> {
    if transfer.amount <= 0.0 {
        return Ok(());
    }
    let amount = transfer
        .amount
        .min(kraken_spot_balance(client, "USDT").await?);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_ceil(amount, 8);
    let response = super::common::exchange_method_request(
        &client,
        "wallet_transfer_to_futures",
        params(&[
            ("asset", "USDT"),
            ("amount", amount.as_str()),
            ("from", "Spot Wallet"),
            ("to", "Futures Wallet"),
        ]),
    )
    .await?;
    assert_success(&response);
    sleep(Duration::from_secs(5)).await;
    if transfer.futures_wallet == "flex" {
        let accounts = client.get_futures_accounts().await?;
        let available = kraken_cash_available(&accounts.data, "usdt");
        let amount = format_transfer_amount_ceil(
            transfer
                .amount
                .min(available)
                .min(amount.parse::<f64>().unwrap_or_default()),
            8,
        );
        if amount != "0" {
            let response = super::common::exchange_method_request(
                &client,
                "futures_wallet_transfer",
                params(&[
                    ("amount", amount.as_str()),
                    ("fromAccount", "cash"),
                    ("toAccount", "flex"),
                    ("unit", "USDT"),
                ]),
            )
            .await?;
            assert_success(&response);
        }
    }
    Ok(())
}

async fn withdraw_kraken_futures_to_spot(
    client: &KrakenClient,
    amount: f64,
    source_wallet: &str,
) -> dcex::Result<()> {
    let amount = format_transfer_amount_ceil(amount, 8);
    let response = super::common::exchange_method_request(
        &client,
        "withdraw_futures_to_spot_wallet",
        params(&[
            ("amount", amount.as_str()),
            ("currency", "USDT"),
            ("sourceWallet", source_wallet),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn kraken_futures_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["KRAKEN_FUTURES_API_KEY", "KRAKEN_FUTURES_API_SECRET"]) else {
        return Ok(());
    };
    let client = KrakenClient::new(
        None,
        None,
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if kraken_futures_open_orders(&client).await? {
        eprintln!("skipping Kraken futures live stateful order; open BTC-USD swap orders exist");
        return Ok(());
    }
    if kraken_futures_position_abs(&client).await? > 0.0 {
        eprintln!("skipping Kraken futures live stateful order; BTC-USD swap position exists");
        return Ok(());
    }

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_futures_orderbook",
        params(&[("product_symbol", BTC_USD_SWAP)]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Kraken, "kraken", BTC_USD_SWAP).await?;
    let bid = first_bid_price(&orderbook.data)?;
    let price = kraken_futures_post_only_buy_price(&orderbook.data)?;
    let quantity = kraken_futures_quantity(&details);
    let required_usdt = leveraged_margin_required(
        bid,
        &quantity,
        &details,
        KRAKEN_FUTURES_MARGIN_LEVERAGE_VALUE,
    )?;
    let transferred = match ensure_kraken_futures_margin(&client, required_usdt).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order = super::common::exchange_method_request(
        &client,
        "place_futures_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USD_SWAP),
            ("size", quantity.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_futures_order",
        params(&[("order_id", order_id.as_str())]),
    )
    .await?;
    assert_success(&cancel);

    let opened = super::common::exchange_method_request(
        &client,
        "place_futures_market_buy_order",
        params(&[
            ("product_symbol", BTC_USD_SWAP),
            ("size", quantity.as_str()),
        ]),
    )
    .await?;
    assert_success(&opened);
    let opened_id = require_order_id(&opened.data, &["order_id"])?;
    eprintln!("Kraken futures market open order_id={opened_id}");
    assert!(wait_for_positive_position(|| kraken_futures_position_abs(&client)).await? > 0.0);

    let closed = super::common::exchange_method_request(
        &client,
        "place_futures_market_sell_order",
        params(&[
            ("product_symbol", BTC_USD_SWAP),
            ("size", quantity.as_str()),
            ("reduceOnly", "true"),
        ]),
    )
    .await?;
    assert_success(&closed);
    let closed_id = require_order_id(&closed.data, &["order_id"])?;
    eprintln!("Kraken futures market close order_id={closed_id}");
    assert_eq!(
        wait_for_flat_position(|| kraken_futures_position_abs(&client)).await?,
        0.0
    );
    assert_kraken_futures_records(&client, &opened_id, &closed_id).await?;
    return_kraken_futures_margin(&client, transferred).await?;
    Ok(())
}

async fn kraken_spot_balance(client: &KrakenClient, asset: &str) -> dcex::Result<f64> {
    let response = client.get_spot_account_balance().await?;
    Ok(kraken_balance_amount(&response.data, asset))
}

fn kraken_balance_amount(data: &Value, asset: &str) -> f64 {
    match data {
        Value::Object(object) => object
            .get(asset)
            .and_then(kraken_value_as_f64)
            .or_else(|| {
                object
                    .values()
                    .map(|value| kraken_balance_amount(value, asset))
                    .find(|value| *value > 0.0)
            })
            .unwrap_or(0.0),
        Value::Array(values) => values
            .iter()
            .map(|value| kraken_balance_amount(value, asset))
            .find(|value| *value > 0.0)
            .unwrap_or(0.0),
        _ => 0.0,
    }
}

fn kraken_value_as_f64(value: &Value) -> Option<f64> {
    match value {
        Value::Number(value) => value.as_f64(),
        Value::String(value) => value.parse().ok(),
        _ => None,
    }
}

async fn kraken_futures_open_orders(client: &KrakenClient) -> dcex::Result<bool> {
    let response = client.get_futures_open_orders().await?;
    Ok(contains_non_empty_array(&response.data, &["openOrders"]))
}

async fn kraken_futures_position_abs(client: &KrakenClient) -> dcex::Result<f64> {
    let response = client.get_futures_open_positions().await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["PF_XBTUSD"],
        &["size", "qty", "quantity"],
    ))
}

async fn ensure_kraken_futures_margin(
    client: &KrakenClient,
    required: f64,
) -> dcex::Result<Option<f64>> {
    let accounts = client.get_futures_accounts().await?;
    let flex = kraken_flex_available(&accounts.data);
    if flex >= required {
        return Ok(Some(0.0));
    }
    let needed = required - flex;
    let cash = kraken_cash_available(&accounts.data, "usdt");
    if cash < needed {
        eprintln!(
            "skipping Kraken futures live stateful order; insufficient cash USDT, required={required:.8}, flex={flex:.8}, cash={cash:.8}"
        );
        return Ok(None);
    }
    let amount = format_transfer_amount_ceil(needed, 8);
    let response = super::common::exchange_method_request(
        &client,
        "futures_wallet_transfer",
        params(&[
            ("amount", amount.as_str()),
            ("fromAccount", "cash"),
            ("toAccount", "flex"),
            ("unit", "USDT"),
        ]),
    )
    .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_kraken_futures_margin(client: &KrakenClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let accounts = client.get_futures_accounts().await?;
    let amount = amount.min(kraken_flex_available(&accounts.data));
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_ceil(amount, 8);
    let response = super::common::exchange_method_request(
        &client,
        "futures_wallet_transfer",
        params(&[
            ("amount", amount.as_str()),
            ("fromAccount", "flex"),
            ("toAccount", "cash"),
            ("unit", "USDT"),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

async fn assert_kraken_futures_records(
    client: &KrakenClient,
    opened_id: &str,
    closed_id: &str,
) -> dcex::Result<()> {
    let opened_status = super::common::exchange_method_request(
        &client,
        "get_futures_order_status",
        params(&[("orderIds", opened_id)]),
    )
    .await?;
    assert_success(&opened_status);
    let closed_status = super::common::exchange_method_request(
        &client,
        "get_futures_order_status",
        params(&[("orderIds", closed_id)]),
    )
    .await?;
    assert_success(&closed_status);

    let has_fills = wait_for_non_empty_records(|| client.get_futures_fills(), &["fills"]).await?;
    assert!(
        has_fills,
        "Kraken futures fills endpoint did not return fills"
    );
    Ok(())
}

fn kraken_flex_available(data: &Value) -> f64 {
    data.get("accounts")
        .and_then(|accounts| accounts.get("flex"))
        .and_then(|flex| find_f64(flex, &["availableMargin"]))
        .unwrap_or(0.0)
}

fn kraken_cash_available(data: &Value, unit: &str) -> f64 {
    data.get("accounts")
        .and_then(|accounts| accounts.get("cash"))
        .and_then(|cash| cash.get("balances"))
        .and_then(|balances| balances.get(unit))
        .and_then(|balance| find_f64(balance, &["available", "balance", "amount"]))
        .unwrap_or(0.0)
}

fn kraken_futures_post_only_buy_price(data: &Value) -> dcex::Result<String> {
    let bid = first_bid_price(data)?;
    let tick = 0.5;
    let price = ((bid * 0.5) / tick).floor() * tick;
    if price <= 0.0 {
        return Err(dcex::DcexError::Decode(format!(
            "Kraken futures orderbook produced invalid bid price: {data}"
        )));
    }
    Ok(format!("{price:.1}"))
}

fn kraken_futures_quantity(details: &dcex::product_table::TradingDetails) -> String {
    let min_size = details
        .min_size
        .parse::<f64>()
        .unwrap_or(0.0001)
        .max(0.0001);
    format!("{min_size:.4}")
}
