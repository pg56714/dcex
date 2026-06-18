mod account;
mod client;
mod endpoints;
mod market;
mod params;
mod private;
mod signing;
mod trade;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::BitgetClient;
