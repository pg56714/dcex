//! Arcus perpetuals REST API and the separate Spot RFQ router.

mod client;
mod endpoints;
mod market;
mod params;
mod signing;
mod trade;
mod wallet;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::{ArcusClient, ArcusSpotClient};
