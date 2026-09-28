//! Arcus perpetuals REST API and the separate Spot RFQ router.

mod client;

mod api_keys;
mod endpoints;
mod market;
mod metadata;
mod params;
mod private;
mod signing;
mod trade;
mod wallet;
mod wrappers;

#[cfg(test)]
mod tests;

pub use client::{ArcusClient, ArcusSpotClient};

mod query_validation;

mod schema_requests;

mod batch;

mod withdrawals;

mod transfers;
