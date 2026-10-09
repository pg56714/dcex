mod private;
#[cfg(test)]
mod private_tests;
mod public;
#[cfg(test)]
mod routing_tests;

pub use private::{OkxPrivateWebSocket, OkxPrivateWebSocketArg};
pub use public::{OkxPublicWebSocket, OkxWebSocketArg};

fn validate_raw_subscriptions(op: &str, args: &[serde_json::Value]) -> crate::Result<()> {
    use crate::DcexError;
    if !matches!(op, "subscribe" | "unsubscribe") || args.is_empty() {
        return Err(DcexError::InvalidInput(
            "subscribe/unsubscribe requires at least one argument".into(),
        ));
    }
    for arg in args {
        let object = arg.as_object().ok_or_else(|| {
            DcexError::InvalidInput("subscription argument must be an object".into())
        })?;
        if !object
            .get("channel")
            .is_some_and(serde_json::Value::is_string)
            || object.iter().any(|(key, value)| {
                ![
                    "channel",
                    "instType",
                    "instFamily",
                    "instId",
                    "ccy",
                    "sprdId",
                    "algoId",
                    "extraParams",
                ]
                .contains(&key.as_str())
                    || !value.is_string()
            })
        {
            return Err(DcexError::InvalidInput(
                "unsupported subscription field or value type".into(),
            ));
        }
    }
    Ok(())
}

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
