use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::gateio::GateioClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    leveraged_margin_required, minimum_order_quantity, params, post_only_buy_price, require_env,
    require_live_trading, require_order_id, wait_for_flat_position, wait_for_positive_position,
    BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const GATEIO_CONTRACT_LEVERAGE_VALUE: f64 = 2.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn gateio_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["GATEIO_API_KEY", "GATEIO_API_SECRET"]) else {
        return Ok(());
    };
    let client = GateioClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if gateio_spot_open_orders(&client).await? {
        eprintln!("skipping Gate.io spot live stateful order; open BTC-USDT spot orders exist");
        return Ok(());
    }

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_order_book",
        params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::GateIo, "gateio", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let amount = minimum_order_quantity(&price, &details)?;
    let required_usdt =
        super::common::order_notional(price.parse::<f64>().unwrap_or_default(), &amount, &details)?;
    if gateio_spot_usdt(&client).await? < required_usdt {
        eprintln!(
            "skipping Gate.io spot live stateful order; insufficient spot USDT, required={required_usdt:.8}"
        );
        return Ok(());
    }

    let order = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("amount", amount.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["id", "order_id", "orderId"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_spot_single_order",
        params(&[
            ("order_id", order_id.as_str()),
            ("product_symbol", BTC_USDT_SPOT),
        ]),
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
async fn gateio_contract_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["GATEIO_API_KEY", "GATEIO_API_SECRET"]) else {
        return Ok(());
    };
    let client = GateioClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if gateio_contract_open_orders(&client).await? {
        eprintln!("skipping Gate.io contract live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }
    if gateio_contract_position_abs(&client).await? > 0.0 {
        eprintln!("skipping Gate.io contract live stateful order; BTC-USDT swap position exists");
        return Ok(());
    }

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_contract_order_book",
        params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::GateIo, "gateio", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let size = minimum_order_quantity(&price, &details)?;
    let market_price = gateio_contract_market_price(&client).await?;
    let required_usdt = leveraged_margin_required(
        market_price,
        &size,
        &details,
        GATEIO_CONTRACT_LEVERAGE_VALUE,
    )?;
    if gateio_futures_usdt(&client).await? < required_usdt {
        eprintln!(
            "skipping Gate.io contract live stateful order; insufficient futures USDT, required={required_usdt:.8}"
        );
        return Ok(());
    }

    let order = super::common::exchange_method_request(
        &client,
        "place_contract_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("size", size.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["id", "order_id", "orderId"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_contract_single_order",
        params(&[("order_id", order_id.as_str())]),
    )
    .await?;
    assert_success(&cancel);

    let opened = super::common::exchange_method_request(
        &client,
        "place_contract_market_buy_order",
        params(&[("product_symbol", BTC_USDT_SWAP), ("size", size.as_str())]),
    )
    .await?;
    assert_success(&opened);
    let opened_id = require_order_id(&opened.data, &["id", "order_id", "orderId"])?;
    eprintln!("Gate.io contract market open order_id={opened_id}");
    assert!(wait_for_positive_position(|| gateio_contract_position_abs(&client)).await? > 0.0);

    let close_size = format!("-{}", size.trim_start_matches('-'));
    let closed = super::common::exchange_method_request(
        &client,
        "place_contract_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("size", close_size.as_str()),
            ("price", "0"),
            ("tif", "ioc"),
            ("reduce_only", "true"),
        ]),
    )
    .await?;
    assert_success(&closed);
    let closed_id = require_order_id(&closed.data, &["id", "order_id", "orderId"])?;
    eprintln!("Gate.io contract market close order_id={closed_id}");
    assert_eq!(
        wait_for_flat_position(|| gateio_contract_position_abs(&client)).await?,
        0.0
    );
    assert_gateio_contract_records(&client).await?;
    Ok(())
}

async fn gateio_spot_open_orders(client: &GateioClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_spot_open_orders",
        params(&[("limit", "20")]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &[]))
}

async fn gateio_contract_open_orders(client: &GateioClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_order_list",
        params(&[
            ("status", "open"),
            ("product_symbol", BTC_USDT_SWAP),
            ("limit", "20"),
        ]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &[]))
}

async fn gateio_contract_position_abs(client: &GateioClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_single_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(find_f64(&response.data, &["size", "value"])
        .unwrap_or_default()
        .abs())
}

async fn gateio_spot_usdt(client: &GateioClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_spot_account",
        params(&[("ccy", "USDT")]),
    )
    .await?;
    Ok(asset_amount(&response.data, "USDT", &["available"]))
}

async fn gateio_futures_usdt(client: &GateioClient) -> dcex::Result<f64> {
    let response = client.get_futures_account().await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &[
            "available",
            "available_margin",
            "availableBalance",
            "available_balance",
        ],
    ))
}

async fn gateio_contract_market_price(client: &GateioClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_list_tickers",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    find_f64(&response.data, &["last", "last_price", "mark_price"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!(
            "Gate.io contract ticker has no usable market price: {response:?}"
        ))
    })
}

async fn assert_gateio_contract_records(client: &GateioClient) -> dcex::Result<()> {
    sleep(Duration::from_secs(2)).await;
    let orders = super::common::exchange_method_request(
        &client,
        "get_contract_order_list",
        params(&[
            ("status", "finished"),
            ("product_symbol", BTC_USDT_SWAP),
            ("limit", "20"),
        ]),
    )
    .await?;
    assert_success(&orders);
    let trades = super::common::exchange_method_request(
        &client,
        "get_trading_history",
        params(&[("product_symbol", BTC_USDT_SWAP), ("limit", "20")]),
    )
    .await?;
    assert_success(&trades);
    Ok(())
}
