mod account;
mod additional;
mod client;
mod completion_wrappers;
mod endpoints;
mod inventory_completion;
mod inventory_wrappers;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod trading_controls;
mod wallet_completion;
mod websocket;
mod wrappers;

pub use client::BingxClient;
pub use websocket::{BingxPrivateWebSocket, BingxPublicWebSocket};

#[cfg(test)]
mod tests;
