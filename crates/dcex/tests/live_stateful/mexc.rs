use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::mexc::MexcClient;
use tokio::time::sleep;

use super::common::{
    assert_success, asset_amount, contains_non_empty_array, fetch_trading_details, find_f64,
    format_transfer_amount, minimum_order_quantity, params, post_only_buy_price,
    price_below_market, require_env, require_live_trading, require_order_id,
    sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const MEXC_CONTRACT_LEVERAGE: &str = "50";
const MEXC_CONTRACT_OPEN_TYPE: &str = "2";

#[tokio::test]
async fn mexc_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["MEXC_API_KEY", "MEXC_API_SECRET"]) else {
        return Ok(());
    };
    let client = MexcClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    let orderbook = client
        .get_spot_orderbook(params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]))
        .await?;
    let details = fetch_trading_details(Exchange::Mexc, "mexc", BTC_USDT_SPOT).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = client
        .place_spot_post_only_limit_buy_order(params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
        ]))
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId"])?;

    let cancel = client
        .cancel_spot_order(params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("orderId", order_id.as_str()),
        ]))
        .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
async fn mexc_contract_direct_live_stateful_order() -> dcex::Result<()> {
    if !require_live_trading() {
        return Ok(());
    }
    let Some(keys) = require_env(&["MEXC_API_KEY", "MEXC_API_SECRET"]) else {
        return Ok(());
    };
    let client = MexcClient::new(
        Some(keys[0].clone()),
        Some(keys[1].clone()),
        Duration::from_secs(20),
    )?;

    if mexc_contract_open_orders(&client).await? {
        eprintln!("skipping MEXC contract live stateful order; open BTC-USDT swap orders exist");
        return Ok(());
    }
    if mexc_contract_position_abs(&client).await? > 0.0 {
        eprintln!("skipping MEXC contract live stateful order; BTC-USDT swap position exists");
        return Ok(());
    }

    let ticker = client
        .get_contract_ticker(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    let bid = find_f64(&ticker.data, &["bid1", "bid", "bidPrice"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!("MEXC contract ticker has no bid: {ticker:?}"))
    })?;
    let details = fetch_trading_details(Exchange::Mexc, "mexc", BTC_USDT_SWAP).await?;
    let price = price_below_market(bid, &details, 0.50)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let transferred = match ensure_mexc_contract_usdt(&client, 0.5).await? {
        Some(amount) => amount,
        None => return Ok(()),
    };

    let order = client
        .place_contract_post_only_buy_order(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("price", price.as_str()),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId", "order_id"])?;

    let cancel = client
        .cancel_contract_order(params(&[("orderId", order_id.as_str())]))
        .await?;
    assert_success(&cancel);

    let opened = client
        .place_contract_market_buy_order(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&opened);
    assert!(wait_for_positive_position(|| mexc_contract_position_abs(&client)).await? > 0.0);

    let closed = client
        .place_contract_market_order(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("side", "4"),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]))
        .await?;
    assert_success(&closed);
    assert_eq!(
        wait_for_flat_position(|| mexc_contract_position_abs(&client)).await?,
        0.0
    );
    return_mexc_contract_transfer(&client, transferred).await?;
    Ok(())
}

async fn mexc_contract_open_orders(client: &MexcClient) -> dcex::Result<bool> {
    let response = client
        .get_contract_open_orders(params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("page_num", "1"),
            ("page_size", "20"),
        ]))
        .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn mexc_contract_position_abs(client: &MexcClient) -> dcex::Result<f64> {
    let response = client
        .get_contract_open_positions(params(&[("product_symbol", BTC_USDT_SWAP)]))
        .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["BTC_USDT"],
        &["holdVol"],
    ))
}

async fn ensure_mexc_contract_usdt(
    client: &MexcClient,
    required: f64,
) -> dcex::Result<Option<f64>> {
    let futures = mexc_contract_usdt(client).await?;
    if futures >= required {
        return Ok(Some(0.0));
    }
    let amount = 1.0;
    if mexc_spot_usdt(client).await? < amount {
        eprintln!("skipping MEXC contract live stateful order; insufficient transferable USDT");
        return Ok(None);
    }
    mexc_transfer(client, "SPOT", "FUTURES", amount).await?;
    sleep(Duration::from_secs(3)).await;
    if mexc_contract_usdt(client).await? < required {
        eprintln!("skipping MEXC contract live stateful order; futures USDT remains insufficient");
        return Ok(None);
    }
    Ok(Some(amount))
}

async fn return_mexc_contract_transfer(client: &MexcClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = amount.min(mexc_contract_usdt(client).await?);
    if amount <= 0.0 {
        return Ok(());
    }
    mexc_transfer(client, "FUTURES", "SPOT", amount).await
}

async fn mexc_transfer(
    client: &MexcClient,
    from_account: &str,
    to_account: &str,
    amount: f64,
) -> dcex::Result<()> {
    let amount = format_transfer_amount(amount);
    let response = client
        .user_universal_transfer(params(&[
            ("fromAccountType", from_account),
            ("toAccountType", to_account),
            ("asset", "USDT"),
            ("amount", amount.as_str()),
        ]))
        .await?;
    assert_success(&response);
    Ok(())
}

async fn mexc_spot_usdt(client: &MexcClient) -> dcex::Result<f64> {
    let response = client.get_spot_account(Vec::new()).await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn mexc_contract_usdt(client: &MexcClient) -> dcex::Result<f64> {
    let response = client
        .get_contract_asset(params(&[("currency", "USDT")]))
        .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableBalance", "available", "balance"],
    ))
}
