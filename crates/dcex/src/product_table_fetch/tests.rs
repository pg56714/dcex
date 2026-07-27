use super::exchanges::{hyperliquid_perpetual_market_info, mexc_contract_pair};
use super::*;
use crate::product_table::MarketInfo;

#[test]
fn normalizes_exchange_specific_currency_aliases() {
    assert_eq!(normalize_kucoin_currency("XBT"), "BTC");
    assert_eq!(normalize_kraken_currency("XXBT"), "BTC");
    assert_eq!(normalize_kraken_currency("ZUSD"), "USD");
    assert_eq!(normalize_kraken_spot_currency("XOMx", true), "XOMx");
}

#[test]
fn preserves_python_precision_formatting() {
    assert_eq!(decimal_precision(3), "0.001");
    assert_eq!(decimal_precision(5), "1e-05");
    assert_eq!(decimal_precision(8), "1e-08");
    assert_eq!(python_float_string("10.00000000"), "10.0");
}

#[test]
fn builds_kraken_dated_inverse_product_symbol() {
    let market = serde_json::json!({"lastTradingTime": "2026-06-01"});
    assert_eq!(
        kraken_futures_product("FI_XBTUSD_260601", "BTC", "USD", "futures_inverse", &market,),
        (
            "BTC-USD-260601-INVERSE-SWAP".to_string(),
            "futures".to_string(),
        )
    );
}

#[test]
fn canonical_symbols_cover_exchange_specific_formats() {
    assert_eq!(
        binance_product_symbol("BTC", "USDT", "BTCUSDT", false),
        "BTC-USDT-SWAP"
    );
    assert_eq!(
        binance_product_symbol("BTC", "USDT", "BTCUSDT_260626", false),
        "BTC-USDT-260626-SWAP"
    );
    assert_eq!(binance_product_type("PERPETUAL"), "swap");
    assert_eq!(binance_product_type("CURRENT_QUARTER"), "futures");
    let mut inverse_base = "BTC".to_string();
    assert_eq!(
        bybit_product_symbol(
            "inverse",
            &mut inverse_base,
            "USD",
            "BTC-27MAR26",
            &["BTC", "27MAR26"],
        ),
        "BTC-USD-27MAR26-SWAP"
    );

    let mut inverse_base = "BTC".to_string();
    assert_eq!(
        bybit_product_symbol("inverse", &mut inverse_base, "USD", "BTCUSDH23", &[]),
        "BTC-USD-H23-SWAP"
    );
    assert_eq!(bybit_product_type("inverse", "InverseFutures"), "futures");
    assert_eq!(normalize_kucoin_currency("XBT"), "BTC");
    assert_eq!(normalize_kraken_currency("XXBT"), "BTC");
}

#[test]
fn product_table_indexes_non_text_exchange_symbols() {
    let table = crate::product_table::ProductTable::new(vec![
        MarketInfo {
            exchange: "hyperliquid".to_string(),
            exchange_symbol: "[\"BTC\", 0]".to_string(),
            product_symbol: "BTC-USD-SWAP".to_string(),
            product_type: "swap".to_string(),
            exchange_type: "perpetual".to_string(),
            price_precision: "0.001".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0.001".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USD".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        },
        MarketInfo {
            exchange: "lighter".to_string(),
            exchange_symbol: "42".to_string(),
            product_symbol: "BTC-USDC-SWAP".to_string(),
            product_type: "swap".to_string(),
            exchange_type: "swap".to_string(),
            price_precision: "0.01".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USDC".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        },
    ]);

    assert_eq!(
        table
            .get_exchange_symbol("hyperliquid", "BTC-USD-SWAP")
            .expect("Hyperliquid asset mapping"),
        "[\"BTC\", 0]"
    );
    assert_eq!(
        table
            .get_exchange_symbol("lighter", "BTC-USDC-SWAP")
            .expect("Lighter market id"),
        "42"
    );
}

#[test]
fn canonicalizes_exchange_display_symbols() {
    let bingx = serde_json::json!({"displayName": "AAPL-USDT"});
    assert_eq!(
        canonical_market_pair(&bingx, "displayName", "NCSKAAPL2USD-USDT")
            .expect("BingX display symbol"),
        ("AAPL".to_string(), "USDT".to_string())
    );

    let extended = serde_json::json!({"uiName": "AAPL-USD"});
    assert_eq!(
        canonical_market_pair(&extended, "uiName", "AAPL_24_5-USD").expect("Extended UI symbol"),
        ("AAPL".to_string(), "USD".to_string())
    );
}

#[test]
fn canonicalizes_mexc_contract_currency_names() {
    let market = serde_json::json!({
        "baseCoin": "AAPLSTOCK",
        "baseCoinName": "AAPL",
        "quoteCoin": "USDT",
        "quoteCoinName": "USDT"
    });
    assert_eq!(
        mexc_contract_pair(&market).expect("MEXC currency names"),
        ("AAPL".to_string(), "USDT".to_string())
    );
}

#[test]
fn builds_hyperliquid_builder_perpetual_asset_mapping() {
    let market = serde_json::json!({"name": "xyz:AAPL", "szDecimals": 3});
    let row =
        hyperliquid_perpetual_market_info(&market, 110_007).expect("Hyperliquid builder perpetual");

    assert_eq!(row.exchange_symbol, "[\"xyz:AAPL\", 110007]");
    assert_eq!(row.product_symbol, "xyz:AAPL-USD-SWAP");
    assert_eq!(row.base_currency, "AAPL");
    assert_eq!(row.quote_currency, "USD");
}
