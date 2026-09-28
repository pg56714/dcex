//! Business-specific endpoint schema tables.
use super::*;
mod account;
mod api_keys;
mod coin_futures;
mod convert;
mod copy_trading;
mod deposits;
mod earn;
mod loan;
mod margin;
mod market;
mod mining;
mod options;
mod order_lists;
mod portfolio_margin;
mod subaccount;
mod trading;
mod transfers;
mod travel_rule;
mod wallet;
mod withdrawals;
pub(super) static ENDPOINTS: std::sync::LazyLock<Vec<&'static Endpoint>> =
    std::sync::LazyLock::new(|| {
        [
            account::ENDPOINTS,
            api_keys::ENDPOINTS,
            coin_futures::ENDPOINTS,
            convert::ENDPOINTS,
            copy_trading::ENDPOINTS,
            deposits::ENDPOINTS,
            earn::ENDPOINTS,
            loan::ENDPOINTS,
            margin::ENDPOINTS,
            market::ENDPOINTS,
            mining::ENDPOINTS,
            options::ENDPOINTS,
            order_lists::ENDPOINTS,
            portfolio_margin::ENDPOINTS,
            subaccount::ENDPOINTS,
            trading::ENDPOINTS,
            transfers::ENDPOINTS,
            travel_rule::ENDPOINTS,
            wallet::ENDPOINTS,
            withdrawals::ENDPOINTS,
        ]
        .into_iter()
        .flatten()
        .collect()
    });
