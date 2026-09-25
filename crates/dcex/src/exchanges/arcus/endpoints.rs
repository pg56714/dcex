use crate::{DcexError, Result};

pub(super) const MAINNET_URL: &str = "https://api.arcus.xyz";
pub(super) const TESTNET_URL: &str = "https://api.testnet.arcus.xyz";

pub(super) fn public_path(method_name: &str) -> Result<&'static str> {
    Ok(match method_name {
        "get_service_info" => "/",
        "health" => "/health",
        "get_time" => "/v1/time",
        "get_markets" => "/v1/markets",
        "get_fee_tiers" => "/v1/feetiers",
        "get_commission_rates" => "/v1/commissionrates",
        "get_spot_assets" => "/v1/spotAssets",
        "get_compliance" => "/v1/compliance",
        "get_bbo" => "/v1/bbo",
        "get_l2_orderbook" => "/v1/l2OrderBook",
        "get_mid_prices" => "/v1/mids",
        "get_live_prices" => "/v1/prices",
        "get_trades" => "/v1/trades",
        "get_trade" => "/v1/trade",
        "get_candles" => "/v1/candles",
        "get_account" => "/v1/account",
        "get_account_stats" => "/v1/account/stats",
        "get_positions" => "/v1/positions",
        "get_leverages" => "/v1/leverages",
        "get_open_orders" => "/v1/openOrders",
        "get_order_history" => "/v1/orders",
        "get_order_status" => "/v1/order",
        "get_fills" => "/v1/fills",
        "get_fill" => "/v1/fill",
        "get_transfer_updates" => "/v1/accountTransferUpdates",
        "get_funding" => "/v1/funding",
        "get_interest" => "/v1/interest",
        "get_funding_rates" => "/v1/fundingRates",
        "get_portfolio_history" => "/v1/portfolio",
        "get_rate_limit" => "/v1/rateLimit",
        "get_spot_positions" => "/v1/spotPositions",
        "get_spot_fills" => "/v1/spotFills",
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unknown Arcus public method: {method_name}"
            )));
        }
    })
}
