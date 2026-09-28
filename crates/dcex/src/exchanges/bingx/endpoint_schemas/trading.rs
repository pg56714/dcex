//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "reverse_swap_position" => Endpoint {
            path: "/openApi/swap/v1/trade/reverse",
            verb: "POST",
            public: false,
            fields: &[
                "type_",
                "product_symbol",
                "triggerPrice",
                "workingType",
                "recvWindow",
            ],
            required: &["type_", "product_symbol"],
            integers: &["recvWindow"],
        },
        "adjust_simulated_trading_balance" => Endpoint {
            path: "/openApi/swap/v2/trade/getVst",
            verb: "POST",
            public: false,
            fields: &["adjustType", "amount", "recvWindow"],
            required: &[],
            integers: &["amount", "recvWindow"],
        },
        _ => return None,
    })
}
