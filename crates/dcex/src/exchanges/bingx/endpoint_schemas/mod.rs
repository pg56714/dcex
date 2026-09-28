//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod coin_futures;
mod deposits;
mod market;
mod order_lists;
mod standard_futures;
mod subaccount;
mod trading;
mod transfers;
mod wallet;
mod withdrawals;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    None.or_else(|| account::endpoint(name))
        .or_else(|| coin_futures::endpoint(name))
        .or_else(|| deposits::endpoint(name))
        .or_else(|| market::endpoint(name))
        .or_else(|| order_lists::endpoint(name))
        .or_else(|| standard_futures::endpoint(name))
        .or_else(|| subaccount::endpoint(name))
        .or_else(|| trading::endpoint(name))
        .or_else(|| transfers::endpoint(name))
        .or_else(|| wallet::endpoint(name))
        .or_else(|| withdrawals::endpoint(name))
}
