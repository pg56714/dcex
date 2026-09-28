//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_spot_historical_kline" => Endpoint {
            path: "/openApi/market/his/v1/kline",
            verb: "GET",
            public: true,
            fields: &[
                "product_symbol",
                "interval",
                "startTime",
                "endTime",
                "limit",
                "recvWindow",
            ],
            required: &["product_symbol", "interval"],
            integers: &["startTime", "endTime", "limit", "recvWindow"],
        },
        "get_swap_server_time" => Endpoint {
            path: "/openApi/swap/v2/server/time",
            verb: "GET",
            public: true,
            fields: &[],
            required: &[],
            integers: &[],
        },
        "get_swap_price_ticker" => Endpoint {
            path: "/openApi/swap/v1/ticker/price",
            verb: "GET",
            public: true,
            fields: &["product_symbol", "recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        "get_spot_historical_trades" => Endpoint {
            path: "/openApi/market/his/v1/trade",
            verb: "GET",
            public: true,
            fields: &["product_symbol", "limit", "fromId", "recvWindow"],
            required: &["product_symbol"],
            integers: &["limit", "recvWindow"],
        },
        "get_swap_historical_trades" => Endpoint {
            path: "/openApi/swap/v1/market/historicalTrades",
            verb: "GET",
            public: true,
            fields: &["product_symbol", "fromId", "limit", "recvWindow"],
            required: &["product_symbol"],
            integers: &["fromId", "limit", "recvWindow"],
        },
        _ => return None,
    })
}
