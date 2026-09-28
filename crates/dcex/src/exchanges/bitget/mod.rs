mod account;
mod client;

mod earn;
mod endpoints;

mod generated;
mod loan;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod trading_controls;
pub mod websocket;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::BitgetClient;

mod batch_controls;
mod schema_requests;

mod withdrawals;

mod subaccount;
