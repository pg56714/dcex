mod private;
mod public;

pub use private::{OkxPrivateWebSocket, OkxPrivateWebSocketArg};
pub use public::{OkxPublicWebSocket, OkxWebSocketArg};

/// Channels served on `/ws/v5/business` per the OKX v5 WebSocket docs.
///
/// Spread trading channels (`sprd-orders`, `sprd-trades`, `sprd-books5`,
/// `sprd-books-l2-tbt`, `sprd-bbo-tbt`, `sprd-public-trades`, `sprd-tickers`,
/// `sprd-candle*`) are all business-only, hence the `sprd-` prefix match.
fn is_business_channel(channel: &str) -> bool {
    channel.starts_with("candle")
        || channel.starts_with("mark-price-candle")
        || channel.starts_with("index-candle")
        || channel.starts_with("sprd-")
        || matches!(
            channel,
            "trades-all"
                | "rfqs"
                | "quotes"
                | "struc-block-trades"
                | "public-struc-block-trades"
                | "public-block-trades"
                | "block-tickers"
                | "orders-algo"
                | "algo-advance"
                | "grid-orders-spot"
                | "grid-orders-contract"
                // Deprecated: OKX took moon grid offline (changelog 2024-04-18) and the
                // channel is no longer documented; kept for backward compatibility.
                | "grid-orders-moon"
                | "grid-positions"
                | "grid-sub-orders"
                | "algo-recurring-buy"
                | "copytrading-lead-notification"
                | "economic-calendar"
                | "deposit-info"
                | "withdrawal-info"
        )
}

#[cfg(test)]
mod tests {
    use super::is_business_channel;

    #[test]
    fn routes_documented_business_channels() {
        for channel in [
            "candle1m",
            "mark-price-candle1m",
            "index-candle1m",
            "trades-all",
            "sprd-orders",
            "sprd-trades",
            "sprd-books5",
            "sprd-books-l2-tbt",
            "sprd-bbo-tbt",
            "sprd-public-trades",
            "sprd-tickers",
            "sprd-candle1m",
            "sprd-candle1Dutc",
            "deposit-info",
            "withdrawal-info",
            "economic-calendar",
            "copytrading-lead-notification",
            "orders-algo",
            "grid-orders-moon",
        ] {
            assert!(is_business_channel(channel), "{channel} should be business");
        }
    }

    #[test]
    fn keeps_documented_public_and_private_channels_off_business() {
        for channel in [
            "trades",
            "tickers",
            "books5",
            "instruments",
            "liquidation-orders",
            "adl-warning",
            "opt-summary",
            "estimated-price",
            "option-trades",
            "orders",
            "positions",
            "account",
            "fills",
        ] {
            assert!(
                !is_business_channel(channel),
                "{channel} should not be business"
            );
        }
    }
}
