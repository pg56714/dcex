//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) const ENDPOINTS: &[Endpoint] = &[Endpoint {
    name: "get_cloud_mining_payment_and_refund_history",
    market: BinanceMarket::Spot,
    symbol_market: BinanceMarket::Spot,
    method: HttpMethod::Get,
    path: "/sapi/v1/asset/ledger-transfer/cloud-mining/queryByPage",
    public: false,
    api_key: false,
    allowed: &[
        "startTime",
        "endTime",
        "tranId",
        "clientTranId",
        "asset",
        "current",
        "size",
    ],
    fields: &[
        Field {
            key: "startTime",
            kind: 'i',
            required: true,
            choices: &[],
        },
        Field {
            key: "endTime",
            kind: 'i',
            required: true,
            choices: &[],
        },
        Field {
            key: "tranId",
            kind: 'i',
            required: false,
            choices: &[],
        },
        Field {
            key: "clientTranId",
            kind: 's',
            required: false,
            choices: &[],
        },
        Field {
            key: "asset",
            kind: 's',
            required: false,
            choices: &[],
        },
        Field {
            key: "current",
            kind: 'i',
            required: false,
            choices: &[],
        },
        Field {
            key: "size",
            kind: 'i',
            required: false,
            choices: &[],
        },
    ],
}];
