mod account;
mod client;
mod schema_requests;

mod endpoints;

mod generated;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod trading_controls;
mod wallet;
mod websocket;
mod wrappers;

pub use client::BingxClient;
pub use websocket::{BingxPrivateWebSocket, BingxPublicWebSocket};

#[cfg(test)]
mod tests;
