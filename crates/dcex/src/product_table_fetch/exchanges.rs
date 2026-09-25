use std::collections::{HashMap, HashSet};
use std::time::Duration;

use serde_json::Value;

use crate::exchanges::arcus::ArcusClient;
use crate::exchanges::aster::AsterClient;
use crate::exchanges::backpack::BackpackClient;
use crate::exchanges::binance::BinanceClient;
use crate::exchanges::bingx::BingxClient;
use crate::exchanges::bitget::BitgetClient;
use crate::exchanges::bybit::BybitClient;
use crate::exchanges::extended::ExtendedClient;
use crate::exchanges::hyperliquid::HyperliquidClient;
use crate::exchanges::kraken::KrakenClient;
use crate::exchanges::kucoin::KucoinClient;
use crate::exchanges::lighter::{LighterClient, LighterNetwork};
use crate::exchanges::mexc::MexcClient;
use crate::exchanges::okx::OkxClient;
use crate::exchanges::ondo::OndoClient;
use crate::product_table::MarketInfo;
use crate::{DcexError, Result};

use super::*;
pub(super) async fn fetch_arcus(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = ArcusClient::public(timeout)?;
    let response = client.public_request("get_markets", vec![]).await?;
    response_array(&response, &["markets"])
        .iter()
        .filter(|market| value_string(market, "status", "") == "ONLINE")
        .map(arcus_market_info)
        .collect()
}

pub(super) fn arcus_market_info(market: &Value) -> Result<MarketInfo> {
    let base = required_string(market, "baseAsset")?;
    let quote = required_string(market, "quoteAsset")?;
    Ok(MarketInfo {
        exchange: "arcus".into(),
        exchange_symbol: required_string(market, "marketId")?,
        product_symbol: format!("{base}-{quote}-SWAP"),
        product_type: "swap".into(),
        exchange_type: value_string(market, "type", "PERPETUAL"),
        price_precision: value_string(market, "tickSize", "0"),
        size_precision: value_string(market, "stepSize", "0"),
        min_size: value_string(market, "minOrderSize", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: value_string(market, "minOrderNotional", "0"),
        size_per_contract: "1".into(),
    })
}

pub(super) async fn fetch_aster(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = AsterClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_exchange_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        if value_string(market, "status", "") == "TRADING" {
            rows.push(aster_market_info(market, "spot")?);
        }
    }
    for market in response_array(&futures, &["symbols"]) {
        if value_string(market, "status", "") != "TRADING" {
            continue;
        }
        let product_type = if value_string(market, "contractType", "") == "PERPETUAL" {
            "swap"
        } else {
            "futures"
        };
        rows.push(aster_market_info(market, product_type)?);
    }
    Ok(rows)
}

fn aster_market_info(market: &Value, product_type: &str) -> Result<MarketInfo> {
    let symbol = required_string(market, "symbol")?;
    let base = required_string(market, "baseAsset")?;
    let quote = required_string(market, "quoteAsset")?;
    let filters = value_array(market.get("filters"));
    let price = find_filter(filters, &["PRICE_FILTER"]);
    let lot = find_filter(filters, &["LOT_SIZE"]);
    let notional = find_filter(filters, &["MIN_NOTIONAL", "NOTIONAL"]);
    Ok(MarketInfo {
        exchange: "aster".to_string(),
        exchange_symbol: symbol,
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: if product_type == "spot" {
            "spot".to_string()
        } else {
            value_string(market, "contractType", "PERPETUAL")
        },
        price_precision: value_string(price, "tickSize", "0"),
        size_precision: value_string(lot, "stepSize", "0"),
        min_size: value_string(lot, "minQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: first_non_empty(
            value_string(notional, "minNotional", ""),
            value_string(notional, "notional", "0"),
        ),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_backpack(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BackpackClient::public(5_000, timeout)?;
    let response = client.public_request("get_markets", vec![]).await?;
    let securities = client.public_request("get_securities", vec![]).await?;
    let mut rows = Vec::new();
    for market in value_array(Some(&response.data)) {
        if market.get("visible").and_then(Value::as_bool) == Some(false)
            || !value_string(market, "orderBookState", "").eq_ignore_ascii_case("open")
        {
            continue;
        }
        let market_type = value_string(market, "marketType", "").to_ascii_uppercase();
        if !matches!(market_type.as_str(), "SPOT" | "PERP" | "IPERP" | "DATED") {
            continue;
        }
        let symbol = required_string(market, "symbol")?;
        let base = non_empty_string(market, "baseSymbol")
            .unwrap_or_else(|| symbol.split('_').next().unwrap_or(&symbol).to_string());
        let quote = non_empty_string(market, "quoteSymbol").unwrap_or_else(|| "USDC".to_string());
        let product_type = match market_type.as_str() {
            "SPOT" => "spot",
            "PERP" | "IPERP" => "swap",
            "DATED" => "futures",
            _ => unreachable!(),
        };
        let filters = market.get("filters").and_then(Value::as_object);
        let price = filters
            .and_then(|filters| filters.get("price"))
            .unwrap_or(&Value::Null);
        let quantity = filters
            .and_then(|filters| filters.get("quantity"))
            .unwrap_or(&Value::Null);
        rows.push(MarketInfo {
            exchange: "backpack".to_string(),
            exchange_symbol: symbol,
            product_symbol: if product_type == "swap" {
                format!("{base}-{quote}-SWAP")
            } else {
                format!("{base}-{quote}-{}", product_type.to_ascii_uppercase())
            },
            product_type: product_type.to_string(),
            exchange_type: market_type,
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(quantity, "stepSize", "0"),
            min_size: value_string(quantity, "minQuantity", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    for security in value_array(Some(&securities.data)) {
        rows.push(backpack_rfq_market_info(security)?);
    }
    Ok(rows)
}

pub(super) fn backpack_rfq_market_info(security: &Value) -> Result<MarketInfo> {
    let asset = required_string(security, "asset")?;
    let sessions = value_array(security.get("sessions"));
    Ok(MarketInfo {
        exchange: "backpack".to_string(),
        exchange_symbol: format!("{asset}_USDC_RFQ"),
        product_symbol: format!("{asset}-USDC-RFQ"),
        product_type: "rfq".to_string(),
        exchange_type: "RFQ".to_string(),
        price_precision: "0".to_string(),
        size_precision: backpack_largest_session_limit(sessions, "stepSize"),
        min_size: backpack_largest_session_limit(sessions, "minQuantity"),
        base_currency: asset,
        quote_currency: "USDC".to_string(),
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    })
}

fn backpack_largest_session_limit(sessions: &[Value], key: &str) -> String {
    sessions
        .iter()
        .filter_map(|session| {
            let value = non_empty_string(session, key)?;
            let number = value.parse::<f64>().ok()?;
            (number.is_finite() && number >= 0.0).then_some((number, value))
        })
        .max_by(|(left, _), (right, _)| left.total_cmp(right))
        .map_or_else(|| "0".to_string(), |(_, value)| value)
}

pub(super) async fn fetch_binance(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BinanceClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_exchange_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        let base = required_string(market, "baseAsset")?;
        let quote = required_string(market, "quoteAsset")?;
        let filters = value_array(market.get("filters"));
        let price = find_filter(filters, &["PRICE_FILTER"]);
        let lot = find_filter(filters, &["LOT_SIZE"]);
        let notional = find_filter(filters, &["NOTIONAL"]);
        rows.push(MarketInfo {
            exchange: "binance".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(lot, "stepSize", "0"),
            min_size: value_string(lot, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: python_float_string(&value_string(notional, "minNotional", "0")),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["symbols"]) {
        let base = required_string(market, "baseAsset")?;
        let quote = required_string(market, "quoteAsset")?;
        let symbol = required_string(market, "symbol")?;
        let product_symbol = binance_product_symbol(&base, &quote, &symbol, false);
        let contract_type = value_string(market, "contractType", "");
        let filters = value_array(market.get("filters"));
        let price = find_filter(filters, &["PRICE_FILTER"]);
        let lot = find_filter(filters, &["LOT_SIZE"]);
        let notional = find_filter(filters, &["MIN_NOTIONAL"]);
        rows.push(MarketInfo {
            exchange: "binance".to_string(),
            exchange_symbol: symbol,
            product_symbol,
            product_type: binance_product_type(&contract_type).to_string(),
            exchange_type: contract_type,
            price_precision: value_string(price, "tickSize", "0"),
            size_precision: value_string(lot, "stepSize", "0"),
            min_size: value_string(lot, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(notional, "notional", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    let coin_futures = client
        .public_request("get_coin_futures_exchange_info", vec![])
        .await?;
    for market in response_array(&coin_futures, &["symbols"]) {
        if value_string(market, "contractStatus", "") == "TRADING" {
            rows.push(binance_coin_futures_market_info(market)?);
        }
    }
    let options = client
        .public_request("get_options_exchange_info", vec![])
        .await?;
    for market in response_array(&options, &["optionSymbols"]) {
        if value_string(market, "status", "") == "TRADING" {
            if let Some(row) = binance_option_market_info(market) {
                rows.push(row);
            }
        }
    }
    // The Equity metadata endpoint requires an API key even though it is unsigned.
    if let Ok(api_key) = std::env::var("BINANCE_API_KEY") {
        if !api_key.is_empty() {
            let equity_client = BinanceClient::new(Some(api_key), None, timeout)?;
            if let Ok(equity) = equity_client
                .public_request("get_equity_exchange_info", vec![])
                .await
            {
                for market in response_array(&equity, &["symbols"]) {
                    rows.push(binance_equity_market_info(market)?);
                }
            }
        }
    }
    Ok(rows)
}

pub(super) fn binance_coin_futures_market_info(market: &Value) -> Result<MarketInfo> {
    let base = required_string(market, "baseAsset")?;
    let quote = required_string(market, "quoteAsset")?;
    let symbol = required_string(market, "symbol")?;
    let contract_type = required_string(market, "contractType")?;
    let product_type = binance_product_type(&contract_type);
    let product_symbol = if product_type == "swap" {
        format!("{base}-{quote}-SWAP")
    } else {
        let expiry = symbol.rsplit_once('_').map_or("", |(_, expiry)| expiry);
        if expiry.is_empty() {
            return Err(DcexError::Decode(format!(
                "Binance COIN-M delivery symbol lacks expiry: {symbol}"
            )));
        }
        format!("{base}-{quote}-{expiry}-FUTURES")
    };
    let filters = value_array(market.get("filters"));
    let price = find_filter(filters, &["PRICE_FILTER"]);
    let lot = find_filter(filters, &["LOT_SIZE"]);
    Ok(MarketInfo {
        // COIN-M must not share the USD-M namespace: generic Binance order
        // routing interprets binance swaps/futures as USD-M products.
        exchange: "binance_coinm".to_string(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: product_type.to_string(),
        exchange_type: contract_type,
        price_precision: value_string(price, "tickSize", "0"),
        size_precision: value_string(lot, "stepSize", "0"),
        min_size: value_string(lot, "minQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: value_string(market, "contractSize", "1"),
    })
}

pub(super) fn binance_equity_market_info(market: &Value) -> Result<MarketInfo> {
    let symbol = required_string(market, "symbol")?;
    Ok(MarketInfo {
        exchange: "binance".to_string(),
        exchange_symbol: symbol.clone(),
        product_symbol: format!("{symbol}-USDC-EQUITY"),
        product_type: "equity".to_string(),
        exchange_type: "equity".to_string(),
        price_precision: "0".to_string(),
        size_precision: value_string(market, "stepSize", "0"),
        min_size: value_string(market, "minQty", "0"),
        base_currency: symbol,
        quote_currency: "USDC".to_string(),
        min_notional: value_string(market, "minNotional", "0"),
        size_per_contract: "1".to_string(),
    })
}

pub(super) fn option_product_symbol(
    base: &str,
    quote: &str,
    expiry: &str,
    strike: &str,
    side: &str,
) -> Option<String> {
    if base.is_empty()
        || quote.is_empty()
        || expiry.len() != 6
        || !expiry.bytes().all(|byte| byte.is_ascii_digit())
        || !matches!(side, "C" | "P")
        || strike
            .parse::<f64>()
            .ok()
            .filter(|value| value.is_finite() && *value > 0.0)
            .is_none()
    {
        return None;
    }
    let strike = if strike.contains('.') {
        strike.trim_end_matches('0').trim_end_matches('.')
    } else {
        strike
    };
    Some(format!("{base}-{quote}-{expiry}-{strike}-{side}-OPTION"))
}

pub(super) fn bybit_option_expiry(expiry: &str) -> Option<String> {
    if expiry.len() != 7 {
        return None;
    }
    let day = &expiry[0..2];
    let month = match &expiry[2..5].to_ascii_uppercase()[..] {
        "JAN" => "01",
        "FEB" => "02",
        "MAR" => "03",
        "APR" => "04",
        "MAY" => "05",
        "JUN" => "06",
        "JUL" => "07",
        "AUG" => "08",
        "SEP" => "09",
        "OCT" => "10",
        "NOV" => "11",
        "DEC" => "12",
        _ => return None,
    };
    let year = &expiry[5..7];
    if !day.bytes().all(|byte| byte.is_ascii_digit())
        || !year.bytes().all(|byte| byte.is_ascii_digit())
        || !(1..=31).contains(&day.parse::<u8>().ok()?)
    {
        return None;
    }
    Some(format!("{year}{month}{day}"))
}

pub(super) fn binance_option_market_info(market: &Value) -> Option<MarketInfo> {
    let symbol = non_empty_string(market, "symbol")?;
    let parts = symbol.split('-').collect::<Vec<_>>();
    if parts.len() != 4 {
        return None;
    }
    let quote = non_empty_string(market, "quoteAsset")?;
    let product_symbol = option_product_symbol(parts[0], &quote, parts[1], parts[2], parts[3])?;
    let filters = value_array(market.get("filters"));
    let price = find_filter(filters, &["PRICE_FILTER"]);
    let lot = find_filter(filters, &["LOT_SIZE"]);
    let base = parts[0].to_string();
    Some(MarketInfo {
        exchange: "binance".into(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: "option".into(),
        exchange_type: "option".into(),
        price_precision: value_string(price, "tickSize", "0"),
        size_precision: value_string(lot, "stepSize", "0"),
        min_size: value_string(lot, "minQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".into(),
        size_per_contract: value_string(market, "unit", "1"),
    })
}

pub(super) fn bybit_option_market_info(market: &Value) -> Option<MarketInfo> {
    let symbol = non_empty_string(market, "symbol")?;
    let parts = symbol.split('-').collect::<Vec<_>>();
    if parts.len() != 5 {
        return None;
    }
    let base = non_empty_string(market, "baseCoin")?;
    let quote = non_empty_string(market, "quoteCoin")?;
    let expiry = bybit_option_expiry(parts[1])?;
    let product_symbol = option_product_symbol(&base, &quote, &expiry, parts[2], parts[3])?;
    let price = market.get("priceFilter").unwrap_or(&Value::Null);
    let lot = market.get("lotSizeFilter").unwrap_or(&Value::Null);
    Some(MarketInfo {
        exchange: "bybit".into(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: "option".into(),
        exchange_type: "option".into(),
        price_precision: value_string(price, "tickSize", "0"),
        size_precision: value_string(lot, "qtyStep", "0"),
        min_size: value_string(lot, "minOrderQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".into(),
        size_per_contract: "1".into(),
    })
}

pub(super) fn okx_option_market_info(market: &Value) -> Option<MarketInfo> {
    let symbol = non_empty_string(market, "instId")?;
    let parts = symbol.split('-').collect::<Vec<_>>();
    if parts.len() != 5 {
        return None;
    }
    let product_symbol = option_product_symbol(parts[0], parts[1], parts[2], parts[3], parts[4])?;
    let base = parts[0].to_string();
    let quote = parts[1].to_string();
    Some(MarketInfo {
        exchange: "okx".into(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: "option".into(),
        exchange_type: "OPTION".into(),
        price_precision: value_string(market, "tickSz", "0"),
        size_precision: value_string(market, "lotSz", "0"),
        min_size: value_string(market, "minSz", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".into(),
        size_per_contract: value_string(market, "ctVal", "1"),
    })
}

pub(super) fn okx_unlisted_option_family(error: &DcexError) -> bool {
    matches!(
        error,
        DcexError::HttpStatus { status: 400, message, .. }
            if message.contains("[51000] Parameter instFamily error")
    )
}

pub(super) async fn fetch_bingx(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BingxClient::public(timeout)?;
    let swap = client
        .public_request("get_swap_instrument_info", vec![])
        .await?;
    let spot = client
        .public_request("get_spot_instrument_info", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&swap, &["data"]) {
        let symbol = required_string(market, "symbol")?;
        let (base, quote) = canonical_market_pair(market, "displayName", &symbol)?;
        let price_places = value_i32(market, "pricePrecision", 0);
        let quantity_places = value_i32(market, "quantityPrecision", 0);
        rows.push(MarketInfo {
            exchange: "bingx".to_string(),
            exchange_symbol: symbol,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: decimal_precision_or_zero(price_places),
            size_precision: decimal_precision_or_zero(quantity_places),
            min_size: decimal_precision_or_zero(quantity_places),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "tradeMinUSDT", "0"),
            size_per_contract: value_string(market, "size", "1"),
        });
    }
    let spot_data = spot.data.get("data").unwrap_or(&Value::Null);
    let spot_symbols = spot_data.get("symbols").unwrap_or(spot_data);
    for market in value_array(Some(spot_symbols)) {
        let symbol = required_string(market, "symbol")?;
        let (base, quote) = split_last(&symbol, '-')?;
        rows.push(MarketInfo {
            exchange: "bingx".to_string(),
            exchange_symbol: symbol,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: value_string(market, "stepSize", "0"),
            min_size: value_string(market, "minQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minNotional", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    disambiguate_bingx_products(&mut rows);
    Ok(rows)
}

pub(super) fn disambiguate_bingx_products(rows: &mut [MarketInfo]) {
    let mut counts = HashMap::new();
    for row in rows.iter() {
        *counts.entry(row.product_symbol.clone()).or_insert(0usize) += 1;
    }
    for row in rows.iter_mut() {
        if counts.get(&row.product_symbol).copied().unwrap_or(0) < 2 {
            continue;
        }
        // Preserve display aliases for unique products (including equities).
        // Only colliding aliases fall back to the exchange's unique symbol.
        if let Ok((base, quote)) = split_last(&row.exchange_symbol, '-') {
            let native_product =
                format!("{base}-{quote}-{}", row.product_type.to_ascii_uppercase());
            if native_product != row.product_symbol {
                row.base_currency = base;
                row.quote_currency = quote;
                row.product_symbol = native_product;
            }
        }
    }
}

pub(super) async fn fetch_bitget(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BitgetClient::public(timeout)?;
    let spot = client
        .public_request(
            "get_uta_instruments",
            vec![("category".to_string(), "SPOT".to_string())],
        )
        .await?;
    let futures = client
        .public_request(
            "get_futures_contracts",
            vec![("productType".to_string(), "USDT-FUTURES".to_string())],
        )
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["data"]) {
        let status = value_string(market, "status", "").to_ascii_lowercase();
        if !status.is_empty() && status != "online" {
            continue;
        }
        let base = required_string(market, "baseCoin")?;
        let quote = required_string(market, "quoteCoin")?;
        rows.push(MarketInfo {
            exchange: "bitget".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: decimal_precision(value_i32(market, "pricePrecision", 0)),
            size_precision: decimal_precision(value_i32(market, "quantityPrecision", 0)),
            min_size: value_string(market, "minOrderQty", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minOrderAmount", "0"),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["data"]) {
        let status = first_non_empty(
            value_string(market, "symbolStatus", ""),
            value_string(market, "status", ""),
        )
        .to_ascii_lowercase();
        if !status.is_empty() && !matches!(status.as_str(), "normal" | "online") {
            continue;
        }
        let base = required_string(market, "baseCoin")?;
        let quote = required_string(market, "quoteCoin")?;
        rows.push(MarketInfo {
            exchange: "bitget".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: value_string(market, "symbolType", "USDT-FUTURES"),
            price_precision: decimal_precision(value_i32(market, "pricePlace", 0)),
            size_precision: decimal_precision(value_i32(market, "volumePlace", 0)),
            min_size: value_string(market, "minTradeNum", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: value_string(market, "minTradeUSDT", "0"),
            size_per_contract: value_string(market, "sizeMultiplier", "1"),
        });
    }
    for category in ["COIN-FUTURES", "USDC-FUTURES"] {
        let response = client
            .public_request(
                "get_uta_instruments",
                vec![("category".to_string(), category.to_string())],
            )
            .await?;
        for market in response_array(&response, &["data"]) {
            if value_string(market, "status", "").eq_ignore_ascii_case("online") {
                rows.push(bitget_uta_futures_market_info(market, category)?);
            }
        }
    }
    Ok(rows)
}

pub(super) fn bitget_uta_futures_market_info(market: &Value, category: &str) -> Result<MarketInfo> {
    let base = required_string(market, "baseCoin")?;
    let quote = required_string(market, "quoteCoin")?;
    let symbol = required_string(market, "symbol")?;
    let contract_type = value_string(market, "type", "perpetual");
    let product_type = if contract_type.eq_ignore_ascii_case("perpetual") {
        "swap"
    } else {
        "futures"
    };
    let product_symbol = if product_type == "swap" {
        format!("{base}-{quote}-SWAP")
    } else {
        format!("{base}-{quote}-{symbol}-FUTURES")
    };
    Ok(MarketInfo {
        exchange: "bitget".to_string(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: product_type.to_string(),
        exchange_type: category.to_string(),
        price_precision: decimal_precision(value_i32(market, "pricePrecision", 0)),
        size_precision: decimal_precision(value_i32(market, "quantityPrecision", 0)),
        min_size: value_string(market, "minOrderQty", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: value_string(market, "minOrderAmount", "0"),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_bybit(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = BybitClient::public(5_000, false, timeout)?;
    let mut rows = Vec::new();
    for category in ["linear", "inverse", "spot", "option"] {
        let markets = bybit_instruments(&client, category).await?;
        for market in markets {
            if category == "option" {
                if value_string(&market, "status", "") == "Trading" {
                    if let Some(row) = bybit_option_market_info(&market) {
                        rows.push(row);
                    }
                }
                continue;
            }
            let mut base = required_string(&market, "baseCoin")?;
            let quote = required_string(&market, "quoteCoin")?;
            let symbol = required_string(&market, "symbol")?;
            let parts = symbol.split('-').collect::<Vec<_>>();
            let product_symbol = bybit_product_symbol(category, &mut base, &quote, &symbol, &parts);
            let contract_type = value_string(&market, "contractType", "");
            let product_type = bybit_product_type(category, &contract_type);
            let price = market.get("priceFilter").unwrap_or(&Value::Null);
            let lot = market.get("lotSizeFilter").unwrap_or(&Value::Null);
            rows.push(MarketInfo {
                exchange: "bybit".to_string(),
                exchange_symbol: symbol,
                product_symbol,
                product_type: product_type.to_string(),
                exchange_type: category.to_string(),
                price_precision: value_string(price, "tickSize", "0"),
                size_precision: value_string(
                    lot,
                    if category == "spot" {
                        "basePrecision"
                    } else {
                        "qtyStep"
                    },
                    "0",
                ),
                min_size: value_string(lot, "minOrderQty", "0"),
                base_currency: base,
                quote_currency: quote,
                min_notional: if category == "spot" {
                    value_string(lot, "minOrderAmt", "0")
                } else if category == "inverse" {
                    "0".to_string()
                } else {
                    value_string(lot, "minNotionalValue", "0")
                },
                size_per_contract: "1".to_string(),
            });
        }
    }
    Ok(rows)
}

async fn bybit_instruments(client: &BybitClient, category: &str) -> Result<Vec<Value>> {
    let mut rows = Vec::new();
    let mut cursor: Option<String> = None;
    loop {
        let mut params = vec![("category".to_string(), category.to_string())];
        if category == "option" {
            params.push(("baseCoin".to_string(), "All".to_string()));
        }
        if let Some(cursor) = cursor.as_ref() {
            params.push(("cursor".to_string(), cursor.clone()));
        }
        let response = client
            .public_request("get_instruments_info", params)
            .await?;
        let result = response.data.get("result").unwrap_or(&Value::Null);
        rows.extend(value_array(result.get("list")).iter().cloned());
        let next = value_string(result, "nextPageCursor", "");
        if next.is_empty() {
            break;
        }
        cursor = Some(next);
    }
    Ok(rows)
}

pub(super) async fn fetch_extended(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = ExtendedClient::public(timeout)?;
    let response = client.public_request("get_markets", vec![]).await?;
    let mut rows = Vec::new();
    for market in response_array(&response, &["data"]) {
        if market.get("active").and_then(Value::as_bool) == Some(false) {
            continue;
        }
        let status = value_string(market, "status", "");
        if status != "ACTIVE" {
            continue;
        }
        rows.push(extended_market_info(market)?);
    }
    Ok(rows)
}

fn extended_market_info(market: &Value) -> Result<MarketInfo> {
    let symbol = required_string(market, "name")?;
    let market_type = value_string(market, "type", "PERPETUAL");
    let (base, quote) = canonical_market_pair(market, "uiName", &symbol)?;
    let config = market.get("tradingConfig").unwrap_or(&Value::Null);
    let product_type = if market_type == "SPOT" {
        "spot"
    } else {
        "swap"
    };
    Ok(MarketInfo {
        exchange: "extended".to_string(),
        exchange_symbol: symbol,
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: market_type,
        price_precision: value_string(config, "minPriceChange", "0"),
        size_precision: value_string(config, "minOrderSizeChange", "0"),
        min_size: value_string(config, "minOrderSize", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_hyperliquid(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = HyperliquidClient::public(false, timeout)?;
    let perpetual = client.public_request("get_meta", Vec::new()).await?;
    let perpetual_dexs = client.public_request("get_perp_dexs", Vec::new()).await?;
    let spot = client.public_request("get_spot_meta", Vec::new()).await?;
    let mut rows = Vec::new();
    append_hyperliquid_perpetual_rows(&mut rows, &perpetual, 0)?;
    for (dex_index, dex) in value_array(Some(&perpetual_dexs.data))
        .iter()
        .enumerate()
        .skip(1)
    {
        let Some(dex_name) = non_empty_string(dex, "name") else {
            continue;
        };
        let metadata = client
            .public_request("get_meta", vec![("dex".to_string(), dex_name)])
            .await?;
        let asset_offset = 100_000 + dex_index as u64 * 10_000;
        append_hyperliquid_perpetual_rows(&mut rows, &metadata, asset_offset)?;
    }
    append_hyperliquid_spot_rows(&mut rows, &spot)?;
    Ok(rows)
}

fn append_hyperliquid_perpetual_rows(
    rows: &mut Vec<MarketInfo>,
    metadata: &crate::exchange::ValidatedResponse,
    asset_offset: u64,
) -> Result<()> {
    for (index, market) in response_array(metadata, &["universe"]).iter().enumerate() {
        rows.push(hyperliquid_perpetual_market_info(
            market,
            asset_offset + index as u64,
        )?);
    }
    Ok(())
}

pub(super) fn hyperliquid_perpetual_market_info(
    market: &Value,
    asset_id: u64,
) -> Result<MarketInfo> {
    let coin = required_string(market, "name")?;
    let base = coin
        .rsplit_once(':')
        .map_or_else(|| coin.clone(), |(_, base)| base.to_string());
    let precision = decimal_precision(value_i32(market, "szDecimals", 0));
    Ok(MarketInfo {
        exchange: "hyperliquid".to_string(),
        exchange_symbol: format!("[\"{coin}\", {asset_id}]"),
        product_symbol: format!("{coin}-USD-SWAP"),
        product_type: "swap".to_string(),
        exchange_type: "perpetual".to_string(),
        price_precision: precision.clone(),
        size_precision: precision.clone(),
        min_size: precision,
        base_currency: base,
        quote_currency: "USD".to_string(),
        min_notional: "10".to_string(),
        size_per_contract: "1".to_string(),
    })
}

fn append_hyperliquid_spot_rows(
    rows: &mut Vec<MarketInfo>,
    spot: &crate::exchange::ValidatedResponse,
) -> Result<()> {
    let mut tokens = HashMap::new();
    for token in response_array(spot, &["tokens"]) {
        if let Some(index) = token.get("index").and_then(Value::as_i64) {
            tokens.insert(index, token);
        }
    }
    for (index, market) in response_array(spot, &["universe"]).iter().enumerate() {
        let token_indexes = value_array(market.get("tokens"));
        if token_indexes.len() < 2 {
            continue;
        }
        let Some(base_token) = token_indexes[0]
            .as_i64()
            .and_then(|value| tokens.get(&value))
        else {
            continue;
        };
        let Some(quote_token) = token_indexes[1]
            .as_i64()
            .and_then(|value| tokens.get(&value))
        else {
            continue;
        };
        let base = required_string(base_token, "name")?;
        let quote = required_string(quote_token, "name")?;
        let precision = decimal_precision(value_i32(base_token, "szDecimals", 0));
        let asset_index = market
            .get("index")
            .and_then(Value::as_u64)
            .unwrap_or(index as u64);
        rows.push(MarketInfo {
            exchange: "hyperliquid".to_string(),
            exchange_symbol: format!(
                "[\"{}\", {}]",
                required_string(market, "name")?,
                10_000 + asset_index
            ),
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: precision.clone(),
            size_precision: precision.clone(),
            min_size: precision,
            base_currency: base,
            quote_currency: quote,
            min_notional: "10".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(())
}

pub(super) async fn fetch_kucoin(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = KucoinClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_instrument_info", vec![])
        .await?;
    let futures = client
        .public_request("get_futures_contracts", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["data"]) {
        let base = required_string(market, "baseCurrency")?;
        let quote = required_string(market, "quoteCurrency")?;
        rows.push(MarketInfo {
            exchange: "kucoin".to_string(),
            exchange_symbol: required_string(market, "symbol")?,
            product_symbol: format!("{base}-{quote}-SPOT"),
            product_type: "spot".to_string(),
            exchange_type: "spot".to_string(),
            price_precision: value_string(market, "priceIncrement", "0"),
            size_precision: value_string(market, "baseIncrement", "0"),
            min_size: value_string(market, "baseMinSize", "0"),
            base_currency: base,
            quote_currency: quote,
            min_notional: non_empty_string(market, "minFunds").unwrap_or_else(|| "0".to_string()),
            size_per_contract: "1".to_string(),
        });
    }
    for market in response_array(&futures, &["data"]) {
        rows.push(kucoin_futures_market_info(market)?);
    }
    Ok(rows)
}

pub(super) fn kucoin_futures_market_info(market: &Value) -> Result<MarketInfo> {
    let base = normalize_kucoin_currency(&required_string(market, "baseCurrency")?);
    let quote = required_string(market, "quoteCurrency")?;
    let symbol = required_string(market, "symbol")?;
    let is_dated = market
        .get("expireDate")
        .is_some_and(|expiry| !expiry.is_null());
    let product_type = if is_dated { "futures" } else { "swap" };
    let product_symbol = if is_dated {
        // KuCoin embeds the standard delivery month/year code in the
        // contract symbol (for example XBTMU26 versus XBTMZ26).
        let expiry = symbol.chars().rev().take(3).collect::<String>();
        let expiry = expiry.chars().rev().collect::<String>();
        format!("{base}-{quote}-{expiry}-FUTURES")
    } else {
        format!("{base}-{quote}-SWAP")
    };
    Ok(MarketInfo {
        exchange: "kucoin".to_string(),
        exchange_symbol: symbol,
        product_symbol,
        product_type: product_type.to_string(),
        exchange_type: value_string(market, "type", ""),
        price_precision: value_string(market, "tickSize", "0"),
        size_precision: value_string(market, "lotSize", "0"),
        min_size: value_string(market, "lotSize", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: value_string(market, "multiplier", "1"),
    })
}

pub(super) async fn fetch_kraken(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = KrakenClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_asset_pairs", vec![])
        .await?;
    let tokenized = client
        .public_request(
            "get_spot_asset_pairs",
            vec![("aclass_base".to_string(), "tokenized_asset".to_string())],
        )
        .await?;
    let futures = client
        .public_request(
            "get_futures_instruments",
            vec![
                ("contractType".to_string(), "futures_inverse".to_string()),
                ("contractType".to_string(), "futures_vanilla".to_string()),
                ("contractType".to_string(), "flexible_futures".to_string()),
            ],
        )
        .await?;
    let mut rows = Vec::new();
    let mut seen_tokenized_symbols = HashSet::new();
    for (response, requested_asset_class) in [(&spot, None), (&tokenized, Some("tokenized_asset"))]
    {
        if let Some(result) = response.data.get("result").and_then(Value::as_object) {
            for (symbol, market) in result {
                let asset_class = non_empty_string(market, "aclass_base")
                    .or_else(|| requested_asset_class.map(str::to_string))
                    .unwrap_or_else(|| "spot".to_string());
                let is_tokenized = asset_class == "tokenized_asset";
                let status = value_string(market, "status", "");
                if !status.is_empty()
                    && status != "online"
                    && !(is_tokenized && status == "post_only")
                {
                    continue;
                }
                let wsname = value_string(market, "wsname", "");
                let (base, quote) = if let Some((base, quote)) = wsname.split_once('/') {
                    (
                        normalize_kraken_spot_currency(base, is_tokenized),
                        normalize_kraken_currency(quote),
                    )
                } else {
                    (
                        normalize_kraken_spot_currency(
                            &value_string(market, "base", ""),
                            is_tokenized,
                        ),
                        normalize_kraken_currency(&value_string(market, "quote", "")),
                    )
                };
                let exchange_symbol = if is_tokenized {
                    non_empty_string(market, "altname").unwrap_or_else(|| symbol.clone())
                } else {
                    symbol.clone()
                };
                if is_tokenized && !seen_tokenized_symbols.insert(exchange_symbol.clone()) {
                    continue;
                }
                rows.push(MarketInfo {
                    exchange: "kraken".to_string(),
                    exchange_symbol,
                    product_symbol: format!("{base}-{quote}-SPOT"),
                    product_type: "spot".to_string(),
                    exchange_type: if is_tokenized {
                        asset_class
                    } else {
                        "spot".to_string()
                    },
                    price_precision: market.get("tick_size").map_or_else(
                        || decimal_precision(value_i32(market, "pair_decimals", 0)),
                        json_string,
                    ),
                    size_precision: decimal_precision(value_i32(market, "lot_decimals", 0)),
                    min_size: value_string(market, "ordermin", "0"),
                    base_currency: base,
                    quote_currency: quote,
                    min_notional: value_string(market, "costmin", "0"),
                    size_per_contract: "1".to_string(),
                });
            }
        }
    }
    for market in response_array(&futures, &["instruments"]) {
        let instrument_type = value_string(market, "type", "");
        if instrument_type == "options"
            || market.get("tradeable").and_then(Value::as_bool) != Some(true)
            || market
                .get("isExpired")
                .and_then(Value::as_bool)
                .unwrap_or(false)
        {
            continue;
        }
        let symbol = required_string(market, "symbol")?;
        let base = normalize_kraken_currency(&value_string(market, "base", ""));
        let quote = normalize_kraken_currency(&value_string(market, "quote", ""));
        let (product_symbol, product_type) =
            kraken_futures_product(&symbol, &base, &quote, &instrument_type, market);
        let precision = kraken_size_precision(market);
        rows.push(MarketInfo {
            exchange: "kraken".to_string(),
            exchange_symbol: symbol,
            product_symbol,
            product_type,
            exchange_type: instrument_type,
            price_precision: value_string(market, "tickSize", "0"),
            size_precision: precision.clone(),
            min_size: precision,
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: value_string(market, "contractSize", "1"),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_ondo(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = OndoClient::public(timeout)?;
    let response = client.public_request("get_markets", Vec::new()).await?;
    let mut rows = Vec::new();
    for market in response_array(&response, &["result", "perps", "tradingPairs"]) {
        if market.get("disabled").and_then(Value::as_bool) == Some(true) {
            continue;
        }
        let pair = market.get("pair").unwrap_or(&Value::Null);
        let base = required_string(pair, "base")?;
        let quote = required_string(pair, "quote")?;
        let symbol = required_string(market, "market")?;
        let base_increment = required_string(market, "baseIncrement")?;
        rows.push(MarketInfo {
            exchange: "ondo".to_string(),
            exchange_symbol: symbol,
            product_symbol: format!("{base}-{quote}-SWAP"),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: required_string(market, "quoteIncrement")?,
            size_precision: base_increment.clone(),
            min_size: base_increment,
            base_currency: base,
            quote_currency: quote,
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        });
    }
    Ok(rows)
}

pub(super) async fn fetch_lighter(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let mut rows = fetch_lighter_network(timeout, LighterNetwork::Mainnet).await?;
    if let Ok(mut robinhood_rows) = fetch_lighter_network(timeout, LighterNetwork::Robinhood).await
    {
        rows.append(&mut robinhood_rows);
    }
    Ok(rows)
}

async fn fetch_lighter_network(
    timeout: Duration,
    network: LighterNetwork,
) -> Result<Vec<MarketInfo>> {
    let client = LighterClient::with_network(timeout, network)?;
    let response = client
        .public_request("get_order_book_details", Vec::new())
        .await?;
    let mut rows = Vec::new();
    for (key, product_type) in [
        ("order_book_details", "swap"),
        ("spot_order_book_details", "spot"),
    ] {
        for market in response_array(&response, &[key]) {
            if !value_string(market, "status", "").eq_ignore_ascii_case("active") {
                continue;
            }
            let mut row = lighter_market_info(market, product_type)?;
            if network == LighterNetwork::Robinhood {
                row.exchange = "lighter_robinhood".to_string();
            }
            rows.push(row);
        }
    }
    Ok(rows)
}

fn lighter_market_info(market: &Value, product_type: &str) -> Result<MarketInfo> {
    let symbol = required_string(market, "symbol")?;
    let (base, quote) = if product_type == "spot" {
        symbol.split_once('/').map_or_else(
            || (symbol.clone(), "USDC".to_string()),
            |(base, quote)| (base.to_string(), quote.to_string()),
        )
    } else {
        (symbol, "USDC".to_string())
    };
    Ok(MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: value_string(market, "market_id", ""),
        product_symbol: if product_type == "spot" {
            format!("{base}-{quote}-SPOT")
        } else {
            format!("{base}-{quote}-SWAP")
        },
        product_type: product_type.to_string(),
        exchange_type: non_empty_string(market, "market_type")
            .unwrap_or_else(|| product_type.to_string()),
        price_precision: lighter_precision(market, "price_decimals", "supported_price_decimals"),
        size_precision: lighter_precision(market, "size_decimals", "supported_size_decimals"),
        min_size: value_string(market, "min_base_amount", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: value_string(market, "min_quote_amount", "0"),
        size_per_contract: "1".to_string(),
    })
}

pub(super) async fn fetch_mexc(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = MexcClient::public(timeout)?;
    let spot = client
        .public_request("get_spot_exchange_info", vec![])
        .await?;
    let contracts = client
        .public_request("get_contract_details", vec![])
        .await?;
    let mut rows = Vec::new();
    for market in response_array(&spot, &["symbols"]) {
        let status = value_string(market, "status", "");
        if (!status.is_empty() && !matches!(status.as_str(), "1" | "TRADING"))
            || market.get("isSpotTradingAllowed").and_then(Value::as_bool) == Some(false)
        {
            continue;
        }
        rows.push(mexc_spot_market_info(market)?);
    }
    let contract_data = contracts.data.get("data").unwrap_or(&Value::Null);
    let contract_rows = if contract_data.is_object() {
        vec![contract_data]
    } else {
        value_array(Some(contract_data)).iter().collect()
    };
    for market in contract_rows {
        let state = market.get("state");
        if state.is_some_and(|value| {
            !value.is_null() && value.as_i64() != Some(0) && value.as_str() != Some("0")
        }) || market.get("apiAllowed").and_then(Value::as_bool) == Some(false)
        {
            continue;
        }
        rows.push(mexc_contract_market_info(market)?);
    }
    Ok(rows)
}

pub(super) fn mexc_spot_market_info(market: &Value) -> Result<MarketInfo> {
    let base = required_string(market, "baseAsset")?;
    let quote = required_string(market, "quoteAsset")?;
    Ok(MarketInfo {
        exchange: "mexc".to_string(),
        exchange_symbol: required_string(market, "symbol")?,
        product_symbol: format!("{base}-{quote}-SPOT"),
        product_type: "spot".to_string(),
        exchange_type: if mexc_market_has_category(market, "conceptPlates", "Tokenized Stocks") {
            "tokenized_stock"
        } else {
            "spot"
        }
        .to_string(),
        price_precision: decimal_precision(value_i32(market, "quotePrecision", 0)),
        size_precision: market.get("baseAssetPrecision").map_or_else(
            || value_string(market, "baseSizePrecision", "0"),
            |_| decimal_precision(value_i32(market, "baseAssetPrecision", 0)),
        ),
        min_size: value_string(market, "baseSizePrecision", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: value_string(market, "quoteAmountPrecision", "0"),
        size_per_contract: "1".to_string(),
    })
}

pub(super) fn mexc_contract_market_info(market: &Value) -> Result<MarketInfo> {
    let (base, quote) = mexc_contract_pair(market)?;
    Ok(MarketInfo {
        exchange: "mexc".to_string(),
        exchange_symbol: required_string(market, "symbol")?,
        product_symbol: format!("{base}-{quote}-SWAP"),
        product_type: "swap".to_string(),
        exchange_type: if mexc_market_has_category(market, "conceptPlate", "mc-trade-zone-Stock") {
            "stock_perpetual"
        } else {
            "perpetual"
        }
        .to_string(),
        price_precision: value_string(market, "priceUnit", "0"),
        size_precision: value_string(market, "volUnit", "0"),
        min_size: value_string(market, "minVol", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: value_string(market, "contractSize", "1"),
    })
}

fn mexc_market_has_category(market: &Value, key: &str, category: &str) -> bool {
    market
        .get(key)
        .and_then(Value::as_array)
        .is_some_and(|categories| {
            categories
                .iter()
                .any(|value| value.as_str() == Some(category))
        })
}

pub(super) fn mexc_contract_pair(market: &Value) -> Result<(String, String)> {
    let base = non_empty_string(market, "baseCoinName")
        .map_or_else(|| required_string(market, "baseCoin"), Ok)?;
    let quote = non_empty_string(market, "quoteCoinName")
        .map_or_else(|| required_string(market, "quoteCoin"), Ok)?;
    Ok((base, quote))
}

pub(super) async fn fetch_okx(timeout: Duration) -> Result<Vec<MarketInfo>> {
    let client = OkxClient::public(timeout)?;
    let mut rows = Vec::new();
    for (instrument_type, product_type) in
        [("SWAP", "swap"), ("SPOT", "spot"), ("FUTURES", "futures")]
    {
        let response = client
            .public_request(
                "get_public_instruments",
                vec![("instType".to_string(), instrument_type.to_string())],
            )
            .await?;
        for market in response_array(&response, &["data"]) {
            let exchange_symbol = required_string(market, "instId")?;
            let parts = exchange_symbol.split('-').collect::<Vec<_>>();
            if parts.len() < 2 {
                continue;
            }
            rows.push(okx_market_info(market, product_type)?);
        }
    }
    let families = client
        .public_request(
            "get_public_underlying",
            vec![("instType".to_string(), "OPTION".to_string())],
        )
        .await?;
    for group in response_array(&families, &["data"]) {
        for family in value_array(Some(group)).iter().filter_map(Value::as_str) {
            let options = match client
                .public_request(
                    "get_public_instruments",
                    vec![
                        ("instType".to_string(), "OPTION".to_string()),
                        ("instFamily".to_string(), family.to_string()),
                    ],
                )
                .await
            {
                Ok(response) => response,
                // OKX can list an underlying before it has queryable option contracts.
                Err(error) if okx_unlisted_option_family(&error) => continue,
                Err(error) => return Err(error),
            };
            for market in response_array(&options, &["data"]) {
                if value_string(market, "state", "") == "live" {
                    if let Some(row) = okx_option_market_info(market) {
                        rows.push(row);
                    }
                }
            }
        }
    }
    Ok(rows)
}

pub(super) fn okx_market_info(market: &Value, product_type: &str) -> Result<MarketInfo> {
    let exchange_symbol = required_string(market, "instId")?;
    let parts = exchange_symbol.split('-').collect::<Vec<_>>();
    let base = if product_type == "spot" {
        required_string(market, "baseCcy")?
    } else {
        parts[0].to_string()
    };
    let quote = if product_type == "spot" {
        required_string(market, "quoteCcy")?
    } else {
        parts[1].to_string()
    };
    Ok(MarketInfo {
        exchange: "okx".to_string(),
        product_symbol: if product_type == "spot" {
            format!("{exchange_symbol}-SPOT")
        } else {
            exchange_symbol.clone()
        },
        exchange_symbol,
        product_type: product_type.to_string(),
        exchange_type: value_string(market, "instType", ""),
        price_precision: value_string(market, "tickSz", "0"),
        size_precision: value_string(market, "lotSz", "0"),
        min_size: value_string(market, "minSz", "0"),
        base_currency: base,
        quote_currency: quote,
        min_notional: "0".to_string(),
        size_per_contract: if matches!(product_type, "swap" | "futures") {
            value_string(market, "ctVal", "1")
        } else {
            "1".to_string()
        },
    })
}
