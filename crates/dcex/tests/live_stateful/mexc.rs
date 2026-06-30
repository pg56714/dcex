use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::mexc::MexcClient;
use tokio::time::sleep;

use super::common::{
    account_restriction, assert_success, asset_amount, contains_non_empty_array,
    fetch_trading_details, find_f64, first_bid_price, format_transfer_amount,
    format_transfer_amount_floor, insufficient_funds_error, leveraged_margin_required,
    live_test_error, margin_target, minimum_order_quantity, params, post_only_buy_price_from_bid,
    price_below_market, require_env, require_live_trading, require_order_id,
    sum_abs_values_for_symbols, unique_client_id, wait_for_flat_position,
    wait_for_positive_position, BTC_USDT_SPOT, BTC_USDT_SWAP,
};

const MEXC_CONTRACT_LEVERAGE: &str = "50";
const MEXC_CONTRACT_LEVERAGE_VALUE: f64 = 50.0;
const MEXC_CONTRACT_OPEN_TYPE: &str = "2";

#[tokio::test]
#[ignore = "requires live exchange API access"]
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
    cleanup_mexc_spot_orders(&client).await?;

    let orderbook = super::common::exchange_method_request(
        &client,
        "get_spot_orderbook",
        params(&[("product_symbol", BTC_USDT_SPOT), ("limit", "5")]),
    )
    .await?;
    let details = fetch_trading_details(Exchange::Mexc, "mexc", BTC_USDT_SPOT).await?;
    let price = price_below_market(first_bid_price(&orderbook.data)?, &details, 0.95)?;
    let quantity = minimum_order_quantity(&price, &details)?;

    let order = super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SPOT),
            ("quantity", quantity.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await?;
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
    match cancel_result {
        Ok(cancel) => assert_success(&cancel),
        Err(error)
            if account_restriction(&error, &["-2011", "order cancelled", "order canceled"]) =>
        {
            if mexc_spot_open_orders(&client).await? {
                return Err(error);
            }
            eprintln!("MEXC spot post-only order was already canceled before cancel response");
        }
        Err(error) => return Err(error),
    }
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
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

    cleanup_mexc_contract_state(&client).await?;

    let ticker = super::common::exchange_method_request(
        &client,
        "get_contract_ticker",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    let bid = find_f64(&ticker.data, &["bid1", "bid", "bidPrice"]).ok_or_else(|| {
        dcex::DcexError::Decode(format!("MEXC contract ticker has no bid: {ticker:?}"))
    })?;
    let details = fetch_trading_details(Exchange::Mexc, "mexc", BTC_USDT_SWAP).await?;
    let price = post_only_buy_price_from_bid(bid, &details)?;
    let quantity = minimum_order_quantity(&price, &details)?;
    let required_usdt =
        leveraged_margin_required(bid, &quantity, &details, MEXC_CONTRACT_LEVERAGE_VALUE)?;
    let transferred = match ensure_mexc_contract_usdt(&client, margin_target(required_usdt)).await?
    {
        Some(amount) => amount,
        None => {
            return Err(live_test_error(
                "MEXC contract has insufficient transferable USDT for live stateful order",
            ));
        }
    };

    let order_result = super::common::exchange_method_request(
        &client,
        "place_contract_post_only_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("price", price.as_str()),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let order = match order_result {
        Ok(order) => order,
        Err(error) if insufficient_funds_error(&error) => {
            return_mexc_contract_transfer(&client, transferred).await?;
            return Err(live_test_error(format!(
                "MEXC contract insufficient margin for post-only order: {error}"
            )));
        }
        Err(error) => {
            return_mexc_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["orderId", "order_id"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_contract_order",
        params(&[("orderId", order_id.as_str())]),
    )
    .await?;
    assert_success(&cancel);

    let open_result = super::common::exchange_method_request(
        &client,
        "place_contract_market_buy_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) if insufficient_funds_error(&error) => {
            return_mexc_contract_transfer(&client, transferred).await?;
            return Err(live_test_error(format!(
                "MEXC contract insufficient margin for market open: {error}"
            )));
        }
        Err(error) => {
            return_mexc_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&opened);
    assert!(wait_for_positive_position(|| mexc_contract_position_abs(&client)).await? > 0.0);

    let closed = super::common::exchange_method_request(
        &client,
        "place_contract_market_order",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("side", "4"),
            ("vol", quantity.as_str()),
            ("leverage", MEXC_CONTRACT_LEVERAGE),
            ("openType", MEXC_CONTRACT_OPEN_TYPE),
            ("externalOid", unique_client_id("dcexrs").as_str()),
        ]),
    )
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
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_open_orders",
        params(&[
            ("product_symbol", BTC_USDT_SWAP),
            ("page_num", "1"),
            ("page_size", "20"),
        ]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn cleanup_mexc_spot_orders(client: &MexcClient) -> dcex::Result<()> {
    if mexc_spot_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_spot_open_orders",
            params(&[("product_symbol", BTC_USDT_SPOT)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    if mexc_spot_open_orders(client).await? {
        return Err(live_test_error(
            "MEXC spot still has open BTC-USDT orders after cleanup",
        ));
    }
    Ok(())
}

async fn cleanup_mexc_contract_state(client: &MexcClient) -> dcex::Result<()> {
    if mexc_contract_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_all_contract_orders",
            params(&[("product_symbol", BTC_USDT_SWAP)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    let volume = mexc_contract_position_abs(client).await?;
    if volume > 0.0 {
        let side = if mexc_contract_position_type(client).await? == 1.0 {
            "4"
        } else {
            "2"
        };
        let open_type = mexc_contract_open_type(client).await?.unwrap_or(2.0);
        let volume = format!("{volume:.0}");
        let close = super::common::exchange_method_request(
            client,
            "place_contract_market_order",
            params(&[
                ("product_symbol", BTC_USDT_SWAP),
                ("side", side),
                ("vol", volume.as_str()),
                ("leverage", MEXC_CONTRACT_LEVERAGE),
                ("openType", format!("{open_type:.0}").as_str()),
                ("externalOid", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await?;
        assert_success(&close);
        sleep(Duration::from_secs(3)).await;
    }
    if mexc_contract_open_orders(client).await? {
        return Err(live_test_error(
            "MEXC contract still has open BTC-USDT swap orders after cleanup",
        ));
    }
    if wait_for_flat_position(|| mexc_contract_position_abs(client)).await? != 0.0 {
        return Err(live_test_error(
            "MEXC BTC-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn mexc_spot_open_orders(client: &MexcClient) -> dcex::Result<bool> {
    let response = super::common::exchange_method_request(
        &client,
        "get_spot_open_orders",
        params(&[("product_symbol", BTC_USDT_SPOT)]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn mexc_contract_position_type(client: &MexcClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_open_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(find_f64(&response.data, &["positionType"]).unwrap_or(1.0))
}

async fn mexc_contract_open_type(client: &MexcClient) -> dcex::Result<Option<f64>> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_open_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
    .await?;
    Ok(find_f64(&response.data, &["openType"]))
}

async fn mexc_contract_position_abs(client: &MexcClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_open_positions",
        params(&[("product_symbol", BTC_USDT_SWAP)]),
    )
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
    let needed = required - futures;
    let spot = mexc_spot_usdt(client).await?;
    if spot < needed {
        return Ok(None);
    }
    mexc_transfer(client, "SPOT", "FUTURES", needed).await?;
    sleep(Duration::from_secs(3)).await;
    if mexc_contract_usdt(client).await? < required {
        return_mexc_contract_transfer(client, needed).await?;
        return Ok(None);
    }
    Ok(Some(needed))
}

async fn return_mexc_contract_transfer(client: &MexcClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = amount.min(mexc_contract_usdt(client).await?);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_floor(amount, 6);
    if amount == "0" {
        return Ok(());
    }
    mexc_transfer_formatted(client, "FUTURES", "SPOT", amount.as_str()).await
}

async fn mexc_transfer(
    client: &MexcClient,
    from_account: &str,
    to_account: &str,
    amount: f64,
) -> dcex::Result<()> {
    let amount = format_transfer_amount(amount);
    mexc_transfer_formatted(client, from_account, to_account, amount.as_str()).await
}

async fn mexc_transfer_formatted(
    client: &MexcClient,
    from_account: &str,
    to_account: &str,
    amount: &str,
) -> dcex::Result<()> {
    let response = super::common::exchange_method_request(
        &client,
        "user_universal_transfer",
        params(&[
            ("fromAccountType", from_account),
            ("toAccountType", to_account),
            ("asset", "USDT"),
            ("amount", amount),
        ]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

async fn mexc_spot_usdt(client: &MexcClient) -> dcex::Result<f64> {
    let response = client.get_spot_account().await?;
    Ok(asset_amount(&response.data, "USDT", &["free", "available"]))
}

async fn mexc_contract_usdt(client: &MexcClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_asset",
        params(&[("currency", "USDT")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["availableBalance", "available"],
    ))
}
