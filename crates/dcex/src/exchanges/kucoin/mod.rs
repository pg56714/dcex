mod account;
mod classic_trading;
mod client;
mod completion_wrappers;
mod earn;
mod endpoints;
mod inventory_completion;
mod inventory_wrappers;
mod margin;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod uta;
mod websocket;
mod withdrawals;
mod wrappers;

pub use client::{KucoinClient, KucoinMarket};
pub use websocket::{KucoinPrivateWebSocket, KucoinProWebSocket, KucoinPublicWebSocket};

#[cfg(test)]
mod tests;

mod risk;
