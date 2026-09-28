//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod api_keys;
mod deposits;
mod market;
mod portfolio_margin;
mod subaccount;
mod trading;
mod transfers;
mod wallet;
mod withdrawals;
pub(super) static ENDPOINTS: std::sync::LazyLock<Vec<&'static Endpoint>> =
    std::sync::LazyLock::new(|| {
        [
            account::ENDPOINTS,
            api_keys::ENDPOINTS,
            deposits::ENDPOINTS,
            market::ENDPOINTS,
            portfolio_margin::ENDPOINTS,
            subaccount::ENDPOINTS,
            trading::ENDPOINTS,
            transfers::ENDPOINTS,
            wallet::ENDPOINTS,
            withdrawals::ENDPOINTS,
        ]
        .into_iter()
        .flatten()
        .collect()
    });
