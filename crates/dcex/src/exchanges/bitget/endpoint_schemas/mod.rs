//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod bots;
mod convert;
mod deposits;
mod earn;
mod funding;
mod loan;
mod margin;
mod market;
mod subaccount;
mod trading;
mod transfers;
mod withdrawals;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    None.or_else(|| account::endpoint(name))
        .or_else(|| bots::endpoint(name))
        .or_else(|| convert::endpoint(name))
        .or_else(|| deposits::endpoint(name))
        .or_else(|| earn::endpoint(name))
        .or_else(|| funding::endpoint(name))
        .or_else(|| loan::endpoint(name))
        .or_else(|| margin::endpoint(name))
        .or_else(|| market::endpoint(name))
        .or_else(|| subaccount::endpoint(name))
        .or_else(|| trading::endpoint(name))
        .or_else(|| transfers::endpoint(name))
        .or_else(|| withdrawals::endpoint(name))
}
