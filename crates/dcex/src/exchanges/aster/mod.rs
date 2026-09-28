mod account;

mod client;

mod endpoints;
mod market;
mod params;
mod private;
mod signing;
#[cfg(test)]
mod tests;
mod trade;
pub mod websocket;
mod wrappers;

pub use client::{AsterClient, AsterMarket};
pub use params::{
    AsterAggTradesParams, AsterFundingRateParams, AsterHistoricalTradesParams,
    AsterIndexPriceKlinesParams, AsterKlinesParams, AsterLimitParams, AsterOptionalSymbolParams,
};
pub use signing::sign_message;

mod prediction;

mod asset;

mod subaccount;

mod agents;

mod builder;

mod withdrawals;

mod transfers;

mod batch;
