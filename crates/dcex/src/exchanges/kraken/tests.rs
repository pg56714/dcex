use super::signing::{encode_params, futures_signature, spot_signature};
use super::KrakenClient;
use crate::product_table::{MarketInfo, ProductTable};
use std::time::Duration;

const SECRET: &str = "c2VjcmV0";
const NONCE: &str = "1700000000000000000";

#[test]
fn spot_signature_matches_python_vector() {
    assert_eq!(
        spot_signature(
            "/0/private/Balance",
            NONCE,
            "nonce=1700000000000000000&asset=BTC+USD",
            SECRET,
        )
        .expect("signature"),
        "WEQePGAjbQaKqtYh0z8ylm5D/0D60D6FAQXlHzu7dDclIHTnRqYoAijaRpRtwLIoj4hnPnEPFO2nXwS+c+BhPQ=="
    );
}

#[test]
fn futures_signature_matches_python_vector() {
    assert_eq!(
        futures_signature(
            "/derivatives/api/v3/sendorder",
            "symbol=PI_XBTUSD&side=buy",
            NONCE,
            SECRET,
        )
        .expect("signature"),
        "W2YL8mj+KExVX/X6fTAPvwlPPo6EP14ISry2Bv5BfJsBu4tDy6PUc1nVNu3OKXcJXrliaG19axFphls37F14zQ=="
    );
}

#[test]
fn query_encoding_uses_uri_percent_encoding() {
    assert_eq!(
        encode_params(&[("greeting".to_string(), "hello world".to_string())]),
        "greeting=hello%20world"
    );
}

#[test]
fn xstock_symbol_infers_tokenized_asset_class() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    assert_eq!(
        client
            .spot_asset_class("AAPLx-USD-SPOT")
            .expect("asset class"),
        Some("tokenized_asset".to_string())
    );
    assert_eq!(
        client
            .spot_asset_class("BTC-USD-SPOT")
            .expect("asset class"),
        None
    );
}

#[test]
fn product_table_asset_class_drives_xstock_orders() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "kraken".to_string(),
        exchange_symbol: "AAPLxUSD".to_string(),
        product_symbol: "APPLE-USD-SPOT".to_string(),
        product_type: "spot".to_string(),
        exchange_type: "tokenized_asset".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.00000001".to_string(),
        min_size: "0.00000001".to_string(),
        base_currency: "AAPLx".to_string(),
        quote_currency: "USD".to_string(),
        min_notional: "0.5".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = KrakenClient::public(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client
            .spot_asset_class("APPLE-USD-SPOT")
            .expect("asset class"),
        Some("tokenized_asset".to_string())
    );
}
