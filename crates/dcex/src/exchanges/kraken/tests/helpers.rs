pub(super) use super::super::KrakenClient;
pub(super) use super::super::signing::{encode_params, futures_signature, spot_signature};
pub(super) use crate::product_table::{MarketInfo, ProductTable};
pub(super) use std::time::Duration;

pub(super) const SECRET: &str = "c2VjcmV0";
pub(super) const NONCE: &str = "1700000000000000000";
