mod private;
mod public;

pub use private::{OkxPrivateWebSocket, OkxPrivateWebSocketArg};
pub use public::{OkxPublicWebSocket, OkxWebSocketArg};

fn is_business_channel(channel: &str) -> bool {
    channel.starts_with("candle")
        || channel.starts_with("mark-price-candle")
        || channel.starts_with("index-candle")
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
                | "grid-orders-moon"
                | "grid-positions"
                | "grid-sub-orders"
                | "algo-recurring-buy"
        )
}
