use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmart::BitmartClient;
use tokio::time::sleep;

use super::common::{
    account_restriction, assert_success, asset_amount, contains_non_empty_array,
    fetch_trading_details, find_f64, format_transfer_amount, minimum_order_quantity_with_step,
    params, post_only_buy_price, price_below_market, require_env, require_live_trading,
    require_order_id, sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_non_empty_records, wait_for_positive_position, DOGE_USDT_SPOT, DOGE_USDT_SWAP,
};

const BITMART_CONTRACT_LEVERAGE: &str = "50";

#[tokio::test]
async fn bitmart_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"]) else {
        return Ok(());
    };
    let client = BitmartClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    let ticker = client.get_ticker_of_a_pair(DOGE_USDT_SPOT).await?;
    let bid = find_f64(
        &ticker.data,
        &["bid_px", "bidPrice", "last", "last_price", "lastPrice"],
    )
    .ok_or_else(|| {
        dcex::DcexError::Decode(format!(
            "BitMart ticker response has no usable bid/last price: {ticker:?}"
        ))
    })?;
    let details = fetch_trading_details(Exchange::BitMart, "bitmart", DOGE_USDT_SPOT).await?;
    let price = price_below_market(bid, &details, 0.95)?;
    let size = minimum_order_quantity_with_step(&price, &details, Some(&details.min_size))?;

    let order = match client
        .place_spot_post_only_limit_buy_order(params(&[
            ("product_symbol", DOGE_USDT_SPOT),
            ("size", size.as_str()),
            ("price", price.as_str()),
        ]))
        .await
    {
        Ok(response) => response,
        Err(error)
            if account_restriction(&error, &["33136", "60052", "personal verification", "kyc"]) =>
        {
            eprintln!("skipping BitMart stateful order due account restriction: {error}");
            return Ok(());
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id", "orderId"])?;

    let cancel = client
        .cancel_spot_order(params(&[
            ("product_symbol", DOGE_USDT_SPOT),
            ("order_id", order_id.as_str()),
        ]))
        .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
async fn bitmart_contract_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["BITMART_API_KEY", "BITMART_API_SECRET", "BITMART_MEMO"]) else {
        return Ok(());
    };
    let client = BitmartClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Some(keys[2].clone()),
        Duration::from_secs(20),
    )?;

    if bitmart_contract_open_orders(&client).await? {
        eprintln!(
            "skipping BitMart contract live stateful order; open DOGE-USDT swap orders exist"
        );
        return Ok(());
    }
    if bitmart_contract_position_abs(&client).await? > 0.0 {
        eprintln!("skipping BitMart contract live stateful order; DOGE-USDT swap position exists");
        return Ok(());
    }

    let orderbook = client.get_depth(DOGE_USDT_SWAP).await?;
    let details = fetch_trading_details(Exchange::BitMart, "bitmart", DOGE_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let size = minimum_order_quantity_with_step(&price, &details, Some(&details.min_size))?;
    let transferred = match ensure_bitmart_contract_usdt(&client).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let leverage = client
        .submit_leverage(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
        ]))
        .await?;
    assert_success(&leverage);

    let order = match client
        .place_contract_post_only_buy_order(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("price", price.as_str()),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]))
        .await
    {
        Ok(response) => response,
        Err(error)
            if account_restriction(&error, &["33136", "60052", "personal verification", "kyc"]) =>
        {
            eprintln!("skipping BitMart contract stateful order due account restriction: {error}");
            return Ok(());
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id", "orderId"])?;

    let cancel = client
        .cancel_contract_order(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("order_id", order_id.as_str()),
        ]))
        .await?;
    assert_success(&cancel);

    let opened = client
        .place_contract_market_buy_order(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&opened);
    let opened_id = require_order_id(&opened.data, &["order_id", "orderId"])?;
    eprintln!("BitMart contract market open order_id={opened_id}");
    assert!(wait_for_positive_position(|| bitmart_contract_position_abs(&client)).await? > 0.0);

    let closed = client
        .place_contract_market_sell_order(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&closed);
    let closed_id = require_order_id(&closed.data, &["order_id", "orderId"])?;
    eprintln!("BitMart contract market close order_id={closed_id}");
    assert_eq!(
        wait_for_flat_position(|| bitmart_contract_position_abs(&client)).await?,
        0.0
    );
    assert_bitmart_contract_records(&client, &opened_id, &closed_id).await?;
    return_bitmart_contract_transfer(&client, transferred).await?;
    Ok(())
}

async fn bitmart_contract_open_orders(client: &BitmartClient) -> dcex::Result<bool> {
    let response = client
        .get_contract_open_order(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("limit", "20"),
        ]))
        .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn bitmart_contract_position_abs(client: &BitmartClient) -> dcex::Result<f64> {
    let response = client
        .get_contract_position(params(&[("product_symbol", DOGE_USDT_SWAP)]))
        .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["DOGEUSDT", DOGE_USDT_SWAP],
        &["current_amount", "position_amount"],
    ))
}

async fn ensure_bitmart_contract_usdt(client: &BitmartClient) -> dcex::Result<Option<f64>> {
    if bitmart_contract_usdt(client).await? >= 1.0 {
        return Ok(Some(0.0));
    }
    if bitmart_spot_usdt(client).await? < 2.0 {
        eprintln!("skipping BitMart contract live stateful order; insufficient transferable USDT");
        return Ok(None);
    }
    let response = client
        .transfer_contract(params(&[("amount", "2"), ("type", "spot_to_contract")]))
        .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(2.0))
}

async fn return_bitmart_contract_transfer(client: &BitmartClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = amount.min(bitmart_contract_usdt(client).await?);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount(amount);
    let response = client
        .transfer_contract(params(&[
            ("amount", amount.as_str()),
            ("type", "contract_to_spot"),
        ]))
        .await?;
    assert_success(&response);
    Ok(())
}

async fn assert_bitmart_contract_records(
    client: &BitmartClient,
    opened_id: &str,
    closed_id: &str,
) -> dcex::Result<()> {
    let opened_detail = client
        .get_contract_order_detail(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("order_id", opened_id),
        ]))
        .await?;
    assert_success(&opened_detail);

    let closed_detail = client
        .get_contract_order_detail(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("order_id", closed_id),
        ]))
        .await?;
    assert_success(&closed_detail);

    let has_history = wait_for_non_empty_records(
        || client.get_contract_order_history(params(&[("product_symbol", DOGE_USDT_SWAP)])),
        &["data"],
    )
    .await?;
    assert!(
        has_history,
        "BitMart contract order history did not return records"
    );

    let has_trades = wait_for_non_empty_records(
        || client.get_contract_trade(params(&[("product_symbol", DOGE_USDT_SWAP)])),
        &["data"],
    )
    .await?;
    assert!(
        has_trades,
        "BitMart contract trade endpoint did not return fills"
    );

    let transaction_history = client
        .get_contract_transaction_history(params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("page_size", "20"),
        ]))
        .await?;
    assert_success(&transaction_history);
    Ok(())
}

async fn bitmart_spot_usdt(client: &BitmartClient) -> dcex::Result<f64> {
    let response = client
        .get_account_balance(params(&[("currency", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available", "available_balance"],
    ))
}

async fn bitmart_contract_usdt(client: &BitmartClient) -> dcex::Result<f64> {
    let response = client.get_contract_assets(Vec::new()).await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available_balance", "availableBalance", "available"],
    ))
}
