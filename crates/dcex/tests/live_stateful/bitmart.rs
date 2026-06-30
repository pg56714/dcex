use std::time::Duration;

use dcex::exchange::Exchange;
use dcex::exchanges::bitmart::BitmartClient;
use tokio::time::sleep;

use super::common::{
    account_restriction, assert_success, asset_amount, contains_non_empty_array,
    fetch_trading_details, find_f64, first_bid_price, format_transfer_amount_ceil,
    format_transfer_amount_floor, leveraged_margin_required, live_test_error, margin_target,
    minimum_order_quantity_with_step, params, post_only_buy_price, post_only_buy_price_from_bid,
    require_env, require_live_trading, require_order_id, sum_abs_values_for_symbols,
    unique_client_id, wait_for_flat_position, wait_for_non_empty_records,
    wait_for_positive_position, DOGE_USDT_SPOT, DOGE_USDT_SWAP,
};

const BITMART_CONTRACT_LEVERAGE: &str = "50";
const BITMART_CONTRACT_LEVERAGE_VALUE: f64 = 50.0;

#[tokio::test]
#[ignore = "requires live exchange API access"]
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
    cleanup_bitmart_spot_orders(&client).await?;

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
    let price = post_only_buy_price_from_bid(bid, &details)?;
    let size = minimum_order_quantity_with_step(&price, &details, Some(&details.min_size))?;

    let order = match super::common::exchange_method_request(
        &client,
        "place_spot_post_only_limit_buy_order",
        params(&[
            ("product_symbol", DOGE_USDT_SPOT),
            ("size", size.as_str()),
            ("price", price.as_str()),
        ]),
    )
    .await
    {
        Ok(response) => response,
        Err(error)
            if account_restriction(&error, &["33136", "60052", "personal verification", "kyc"]) =>
        {
            return Err(live_test_error(format!(
                "BitMart stateful order blocked by account restriction: {error}"
            )));
        }
        Err(error) => return Err(error),
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id", "orderId"])?;

    let cancel = super::common::exchange_method_request(
        &client,
        "cancel_spot_order",
        params(&[
            ("product_symbol", DOGE_USDT_SPOT),
            ("order_id", order_id.as_str()),
        ]),
    )
    .await?;
    assert_success(&cancel);
    Ok(())
}

#[tokio::test]
#[ignore = "requires live exchange API access"]
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

    cleanup_bitmart_contract_state(&client).await?;

    let orderbook = client.get_depth(DOGE_USDT_SWAP).await?;
    let details = fetch_trading_details(Exchange::BitMart, "bitmart", DOGE_USDT_SWAP).await?;
    let price = post_only_buy_price(&orderbook.data, &details)?;
    let size = minimum_order_quantity_with_step(&price, &details, Some(&details.min_size))?;
    let market_price_estimate = first_bid_price(&orderbook.data)?;
    let required_usdt = leveraged_margin_required(
        market_price_estimate,
        &size,
        &details,
        BITMART_CONTRACT_LEVERAGE_VALUE,
    )?;
    let transferred =
        match ensure_bitmart_contract_usdt(&client, margin_target(required_usdt)).await? {
            Some(amount) => amount,
            None => {
                return Err(live_test_error(
                    "BitMart contract has insufficient transferable USDT for live stateful order",
                ));
            }
        };

    let leverage_result = super::common::exchange_method_request(
        &client,
        "submit_leverage",
        params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
        ]),
    )
    .await;
    let leverage = match leverage_result {
        Ok(leverage) => leverage,
        Err(error) => {
            return_bitmart_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&leverage);

    let order = match super::common::exchange_method_request(
        &client,
        "place_contract_post_only_buy_order",
        params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("price", price.as_str()),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await
    {
        Ok(response) => response,
        Err(error)
            if account_restriction(&error, &["33136", "60052", "personal verification", "kyc"]) =>
        {
            return_bitmart_contract_transfer(&client, transferred).await?;
            return Err(live_test_error(format!(
                "BitMart contract stateful order blocked by account restriction: {error}"
            )));
        }
        Err(error) => {
            return_bitmart_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&order);
    let order_id = require_order_id(&order.data, &["order_id", "orderId"])?;

    let cancel_result = super::common::exchange_method_request(
        &client,
        "cancel_contract_order",
        params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("order_id", order_id.as_str()),
        ]),
    )
    .await;
    let cancel = match cancel_result {
        Ok(cancel) => cancel,
        Err(error) => {
            return_bitmart_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&cancel);

    let open_result = super::common::exchange_method_request(
        &client,
        "place_contract_market_buy_order",
        params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]),
    )
    .await;
    let opened = match open_result {
        Ok(opened) => opened,
        Err(error) => {
            return_bitmart_contract_transfer(&client, transferred).await?;
            return Err(error);
        }
    };
    assert_success(&opened);
    let opened_id = require_order_id(&opened.data, &["order_id", "orderId"])?;
    eprintln!("BitMart contract market open order_id={opened_id}");
    assert!(wait_for_positive_position(|| bitmart_contract_position_abs(&client)).await? > 0.0);

    let closed = super::common::exchange_method_request(
        &client,
        "place_contract_market_sell_order",
        params(&[
            ("product_symbol", DOGE_USDT_SWAP),
            ("size", size.as_str()),
            ("leverage", BITMART_CONTRACT_LEVERAGE),
            ("open_type", "cross"),
            ("client_order_id", unique_client_id("dcexrs").as_str()),
        ]),
    )
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
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_open_order",
        params(&[("product_symbol", DOGE_USDT_SWAP), ("limit", "20")]),
    )
    .await?;
    Ok(contains_non_empty_array(&response.data, &["data"]))
}

async fn cleanup_bitmart_spot_orders(client: &BitmartClient) -> dcex::Result<()> {
    let cancel =
        super::common::exchange_method_request(client, "cancel_spot_all_order", params(&[]))
            .await?;
    assert_success(&cancel);
    sleep(Duration::from_secs(1)).await;
    Ok(())
}

async fn cleanup_bitmart_contract_state(client: &BitmartClient) -> dcex::Result<()> {
    if bitmart_contract_open_orders(client).await? {
        let cancel = super::common::exchange_method_request(
            client,
            "cancel_all_contract_order",
            params(&[("product_symbol", DOGE_USDT_SWAP)]),
        )
        .await?;
        assert_success(&cancel);
        sleep(Duration::from_secs(1)).await;
    }
    let position = bitmart_contract_position_abs(client).await?;
    if position > 0.0 {
        let size = format_transfer_amount_floor(position, 0);
        let close = super::common::exchange_method_request(
            client,
            "place_contract_market_sell_order",
            params(&[
                ("product_symbol", DOGE_USDT_SWAP),
                ("size", size.as_str()),
                ("leverage", BITMART_CONTRACT_LEVERAGE),
                ("open_type", "cross"),
                ("client_order_id", unique_client_id("dcexrs").as_str()),
            ]),
        )
        .await?;
        assert_success(&close);
        sleep(Duration::from_secs(2)).await;
    }
    if bitmart_contract_open_orders(client).await? {
        return Err(live_test_error(
            "BitMart contract still has open DOGE-USDT swap orders after cleanup",
        ));
    }
    if wait_for_flat_position(|| bitmart_contract_position_abs(client)).await? != 0.0 {
        return Err(live_test_error(
            "BitMart DOGE-USDT swap position still exists after cleanup",
        ));
    }
    Ok(())
}

async fn bitmart_contract_position_abs(client: &BitmartClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_contract_position",
        params(&[("product_symbol", DOGE_USDT_SWAP)]),
    )
    .await?;
    Ok(sum_abs_values_for_symbols(
        &response.data,
        &["symbol"],
        &["DOGEUSDT", DOGE_USDT_SWAP],
        &["current_amount", "position_amount"],
    ))
}

async fn ensure_bitmart_contract_usdt(
    client: &BitmartClient,
    required: f64,
) -> dcex::Result<Option<f64>> {
    let contract = bitmart_contract_usdt(client).await?;
    if contract >= required {
        return Ok(Some(0.0));
    }
    let needed = required - contract;
    let spot = bitmart_spot_usdt(client).await?;
    if spot < needed {
        return Ok(None);
    }
    let amount = bitmart_transfer_amount(needed);
    let response = super::common::exchange_method_request(
        &client,
        "transfer_contract",
        params(&[("amount", amount.as_str()), ("type", "spot_to_contract")]),
    )
    .await?;
    assert_success(&response);
    sleep(Duration::from_secs(2)).await;
    Ok(Some(needed))
}

async fn return_bitmart_contract_transfer(client: &BitmartClient, amount: f64) -> dcex::Result<()> {
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = amount.min(bitmart_contract_usdt(client).await?);
    if amount <= 0.0 {
        return Ok(());
    }
    let amount = format_transfer_amount_floor(amount, 2);
    let response = super::common::exchange_method_request(
        &client,
        "transfer_contract",
        params(&[("amount", amount.as_str()), ("type", "contract_to_spot")]),
    )
    .await?;
    assert_success(&response);
    Ok(())
}

async fn assert_bitmart_contract_records(
    client: &BitmartClient,
    opened_id: &str,
    closed_id: &str,
) -> dcex::Result<()> {
    let opened_detail = super::common::exchange_method_request(
        &client,
        "get_contract_order_detail",
        params(&[("product_symbol", DOGE_USDT_SWAP), ("order_id", opened_id)]),
    )
    .await?;
    assert_success(&opened_detail);

    let closed_detail = super::common::exchange_method_request(
        &client,
        "get_contract_order_detail",
        params(&[("product_symbol", DOGE_USDT_SWAP), ("order_id", closed_id)]),
    )
    .await?;
    assert_success(&closed_detail);

    let has_history = wait_for_non_empty_records(
        || {
            super::common::exchange_method_request(
                &client,
                "get_contract_order_history",
                params(&[("product_symbol", DOGE_USDT_SWAP)]),
            )
        },
        &["data"],
    )
    .await?;
    assert!(
        has_history,
        "BitMart contract order history did not return records"
    );

    let has_trades = wait_for_non_empty_records(
        || {
            super::common::exchange_method_request(
                &client,
                "get_contract_trade",
                params(&[("product_symbol", DOGE_USDT_SWAP)]),
            )
        },
        &["data"],
    )
    .await?;
    assert!(
        has_trades,
        "BitMart contract trade endpoint did not return fills"
    );

    let transaction_history = super::common::exchange_method_request(
        &client,
        "get_contract_transaction_history",
        params(&[("product_symbol", DOGE_USDT_SWAP), ("page_size", "20")]),
    )
    .await?;
    assert_success(&transaction_history);
    Ok(())
}

async fn bitmart_spot_usdt(client: &BitmartClient) -> dcex::Result<f64> {
    let response = super::common::exchange_method_request(
        &client,
        "get_account_balance",
        params(&[("currency", "USDT")]),
    )
    .await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available", "available_balance"],
    ))
}

async fn bitmart_contract_usdt(client: &BitmartClient) -> dcex::Result<f64> {
    let response = client.get_contract_assets().await?;
    Ok(asset_amount(
        &response.data,
        "USDT",
        &["available_balance", "availableBalance", "available"],
    ))
}

fn bitmart_transfer_amount(value: f64) -> String {
    format_transfer_amount_ceil(value, 2)
}
