pub mod common;
pub mod crypto;
pub mod ethereum;
pub mod exchange;
pub mod exchanges;
pub mod http;
pub mod lighter;
pub mod lighter_crypto;
pub mod product_table;
pub mod ws;

use std::fmt::{Display, Formatter};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DcexError {
    Decode(String),
    HttpStatus {
        status: u16,
        message: String,
        headers: Vec<(String, String)>,
    },
    /// Exchange failure with structured outcomes, including partial execution.
    ExchangeResponse {
        status: u16,
        message: String,
        headers: Vec<(String, String)>,
        data: serde_json::Value,
    },
    InvalidInput(String),
    Runtime(String),
    Transport(String),
}

impl Display for DcexError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Decode(message) => write!(f, "failed to decode response: {message}"),
            // Built by `http::api_error_message`: exchange, code, message and HTTP status.
            Self::HttpStatus { message, .. } | Self::ExchangeResponse { message, .. } => {
                f.write_str(message)
            }
            Self::InvalidInput(message) => f.write_str(message),
            Self::Runtime(message) => write!(f, "runtime error: {message}"),
            Self::Transport(message) => write!(f, "request transport failed: {message}"),
        }
    }
}

impl std::error::Error for DcexError {}

pub type Result<T> = std::result::Result<T, DcexError>;

pub mod address;
pub mod decimal;
pub mod order_side;
pub mod sanitization;
#[cfg(test)]
#[path = "exchanges/symbol_resolution_tests.rs"]
mod symbol_resolution_tests;
pub mod time;
pub mod timeframe;
