use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::gateio::GateioClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    format_transfer_amount, format_transfer_amount_floor, insufficient_funds_error,
    leveraged_margin_required, live_test_error, margin_target, minimum_order_quantity, params,
    post_only_buy_price, require_env, require_live_trading, require_order_id,
    wait_for_flat_position, wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const GATEIO_CONTRACT_LEVERAGE_VALUE: f64 = 2.0;
const GATEIO_SPOT_ACCOUNT: &str = "spot";
const GATEIO_FUTURES_ACCOUNT: &str = "futures";

struct GateioTransferBack {
    from_account: &'static str,
    to_account: &'static str,
    amount: f64,
}

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

    cleanup_gateio_spot_orders(&client).await?;

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
    let transfer = match ensure_gateio_spot_usdt(&client, required_usdt).await? {
        Some(transfer) => transfer,
        None => {
            return Err(live_test_error(
                "Gate.io spot has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("amount", amount.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["id", "order_id", "orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_spot_single_order",
        params(&[
            ("order_id", order_id.as_str()),
            ("product_symbol", BTC_USDT_SPOT),
        ]),
    )
    .await;
    return_gateio_transfer(&client, &transfer).await?;
    let cancel = cancel_result?;
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

    cleanup_gateio_contract_state(&client).await?;

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
    let transfer = match ensure_gateio_futures_usdt(&client, margin_target(required_usdt)).await? {
        Some(transfer) => transfer,
        None => {
            return Err(live_test_error(
                "Gate.io futures has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_contract_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("size", size.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) if insufficient_funds_error(&error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(live_test_error(format!(
                "Gate.io contract insufficient margin for post-only order: {error}"
            )));
        }
        Err(error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["id", "order_id", "orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_contract_single_order",
        params(&[("order_id", order_id.as_str())]),
    )
    .await;
    let cancel = match cancel_result {
        Ok(cancel) => cancel,
        Err(error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
    assert_success(&cancel);

    let open_result = super::common::exchange_method_request(
        &client,
        "place_contract_market_buy_order",
        params(&[("product_symbol", BTC_USDT_SWAP), ("size", size.as_str())]),
    )
    .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) if insufficient_funds_error(&error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(live_test_error(format!(
                "Gate.io contract insufficient margin for market open: {error}"
            )));
        }
        Err(error) => {
            return_gateio_transfer(&client, &transfer).await?;
            return Err(error);
        }
    };
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
    return_gateio_transfer(&client, &transfer).await?;
    Ok(())
}

async fn ensure_gateio_spot_usdt(
    client: &GateioClient,
    required: f64,
) -> dcex::Result<Option<GateioTransferBack>> {
    ensure_gateio_usdt(
        client,
        GATEIO_SPOT_ACCOUNT,
        GATEIO_FUTURES_ACCOUNT,
        required,
    )
    .await
}

async fn ensure_gateio_futures_usdt(
    client: &GateioClient,
    required: f64,
) -> dcex::Result<Option<GateioTransferBack>> {
    ensure_gateio_usdt(
        client,
        GATEIO_FUTURES_ACCOUNT,
        GATEIO_SPOT_ACCOUNT,
        required,
    )
    .await
}

async fn ensure_gateio_usdt(
    client: &GateioClient,
    target_account: &'static str,
    source_account: &'static str,
    required: f64,
) -> dcex::Result<Option<GateioTransferBack>> {
    let target = gateio_account_usdt(client, target_account).await?;
    if target >= required {
        return Ok(Some(GateioTransferBack {
            from_account: target_account,
            to_account: source_account,
            amount: 0.0,
        }));
    }
    let needed = required - target;
    let source = gateio_account_usdt(client, source_account).await?;
    if source < needed {
        return Ok(None);
    }
    gateio_transfer(client, source_account, target_account, needed).await?;
    sleep(Duration::from_secs(2)).await;
    let transfer = GateioTransferBack {
        from_account: target_account,
        to_account: source_account,
        amount: needed,
    };
    if gateio_account_usdt(client, target_account).await? < required {
        return_gateio_transfer(client, &transfer).await?;
        return Ok(None);
    }
    Ok(Some(transfer))
}

async fn return_gateio_transfer(
    client: &GateioClient,
    transfer: &GateioTransferBack,
) -> dcex::Result<()> {
    if transfer.amount <= 0.0 {
        return Ok(());
    }
    let available = gateio_account_usdt(client, transfer.from_account).await?;
    let amount = transfer.amount.min(available);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_floor(amount, 6);
    if amount == "0" {
        return Ok(());
    }
    gateio_transfer_formatted(
        client,
        transfer.from_account,
        transfer.to_account,
        amount.as_str(),
    )
    .await
}

async fn gateio_transfer(
    client: &GateioClient,
    from_account: &str,
    to_account: &str,
    amount: f64,
) -> dcex::Result<()> {
    let amount = format_transfer_amount(amount);
    gateio_transfer_formatted(client, from_account, to_account, amount.as_str()).await
}

async fn gateio_transfer_formatted(
    client: &GateioClient,
    from_account: &str,
    to_account: &str,
    amount: &str,
) -> dcex::Result<()> {
    let response = super::common::exchange_method_request(
        &client,
        "wallet_transfer",
        params(&[
            ("currency", "USDT"),
            ("from", from_account),
            ("to", to_account),
            ("amount", amount),
            ("settle", "usdt"),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

async fn gateio_account_usdt(client: &GateioClient, account: &str) -> dcex::Result<f64> {
    match account {
        GATEIO_SPOT_ACCOUNT => gateio_spot_usdt(client).await,
        GATEIO_FUTURES_ACCOUNT => gateio_futures_usdt(client).await,
        _ => Ok(0.0),
    }
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

async fn cleanup_gateio_spot_orders(client: &GateioClient) -> dcex::Result<()> {
    if gateio_spot_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_spot_order",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    if gateio_spot_open_orders(client).await? {
        return Err(live_test_error(
            "Gate.io spot still has open BTC-USDT orders after cleanup",
        ));
    }
    Ok(())
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

async fn cleanup_gateio_contract_state(client: &GateioClient) -> dcex::Result<()> {
    if gateio_contract_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_contract_all_order_matched",
            params(&[("product_symbol", BTC_USDT_SWAP)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    let size = gateio_contract_position_size(client).await?;
    if size != 0.0 {
        let close_size = if size > 0.0 { -size.abs() } else { size.abs() };
        let close_size = format!("{close_size:.0}");
        let close = super::common::exchange_method_request(
            client,
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
        assert_success(&close);
        sleep(Duration::from_secs(2)).await;
    }
    if gateio_contract_open_orders(client).await? {
        return Err(live_test_error(
            "Gate.io contract still has open BTC-USDT swap orders after cleanup",
        ));
    }
    if wait_for_flat_position(|| gateio_contract_position_abs(client)).await? != 0.0 {
        return Err(live_test_error(
            "Gate.io BTC-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn gateio_contract_position_abs(client: &GateioClient) -> dcex::Result<f64> {
    Ok(gateio_contract_position_size(client).await?.abs())
}

async fn gateio_contract_position_size(client: &GateioClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_single_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(find_f64(&response.data, &["size", "value"]).unwrap_or_default())
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
    Ok(find_f64(
        &response.data,
        &[
            "available_margin",
            "available_balance",
            "availableBalance",
            "available",
        ],
    )
    .unwrap_or(0.0))
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
