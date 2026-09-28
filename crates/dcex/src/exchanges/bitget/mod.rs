mod account;
mod client;
mod completion;
mod completion_wrappers;
mod earn;
mod endpoints;
mod inventory_completion;
mod inventory_wrappers;
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
mod risk;
