//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) const ENDPOINTS: &[Endpoint] = &[
    Endpoint {
        name: "get_futures_lead_trader_status",
        market: BinanceMarket::Spot,
        symbol_market: BinanceMarket::Spot,
        method: HttpMethod::Get,
        path: "/sapi/v1/copyTrading/futures/userStatus",
        public: false,
        api_key: false,
        allowed: &["recvWindow"],
        fields: &[Field {
            key: "recvWindow",
            kind: 'i',
            required: false,
            choices: &[],
        }],
    },
    Endpoint {
        name: "get_futures_lead_trading_symbol_whitelist",
        market: BinanceMarket::Spot,
        symbol_market: BinanceMarket::Spot,
        method: HttpMethod::Get,
        path: "/sapi/v1/copyTrading/futures/leadSymbol",
        public: false,
        api_key: false,
        allowed: &["recvWindow"],
        fields: &[Field {
            key: "recvWindow",
            kind: 'i',
            required: false,
            choices: &[],
        }],
    },
];
