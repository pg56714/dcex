//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod announcements;
mod api_keys;
mod convert;
mod leveraged_tokens;
mod loan;
mod margin;
mod market;
mod options;
mod portfolio_margin;
mod subaccount;
mod trading;
mod travel_rule;
mod wallet;
mod withdrawals;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    None.or_else(|| account::endpoint(name))
        .or_else(|| announcements::endpoint(name))
        .or_else(|| api_keys::endpoint(name))
        .or_else(|| convert::endpoint(name))
        .or_else(|| leveraged_tokens::endpoint(name))
        .or_else(|| loan::endpoint(name))
        .or_else(|| margin::endpoint(name))
        .or_else(|| market::endpoint(name))
        .or_else(|| options::endpoint(name))
        .or_else(|| portfolio_margin::endpoint(name))
        .or_else(|| subaccount::endpoint(name))
        .or_else(|| trading::endpoint(name))
        .or_else(|| travel_rule::endpoint(name))
        .or_else(|| wallet::endpoint(name))
        .or_else(|| withdrawals::endpoint(name))
}
