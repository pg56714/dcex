//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) const ENDPOINTS: &[Endpoint] = &[Endpoint {
    name: "get_spot_wallet_accounts",
    path: "/0/private/ListWalletAccounts",
    method: HttpMethod::Post,
    auth: KrakenAuth::Spot,
    public: false,
    allowed: &[],
    fields: &[],
    symbol_key: None,
}];
