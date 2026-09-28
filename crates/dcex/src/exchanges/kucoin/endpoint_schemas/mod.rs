//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod announcements;
mod api_keys;
mod convert;
mod deposits;
mod fiat;
mod loan;
mod margin;
mod market;
mod subaccount;
mod transfers;
mod withdrawals;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    None.or_else(|| account::endpoint(name))
        .or_else(|| announcements::endpoint(name))
        .or_else(|| api_keys::endpoint(name))
        .or_else(|| convert::endpoint(name))
        .or_else(|| deposits::endpoint(name))
        .or_else(|| fiat::endpoint(name))
        .or_else(|| loan::endpoint(name))
        .or_else(|| margin::endpoint(name))
        .or_else(|| market::endpoint(name))
        .or_else(|| subaccount::endpoint(name))
        .or_else(|| transfers::endpoint(name))
        .or_else(|| withdrawals::endpoint(name))
}
