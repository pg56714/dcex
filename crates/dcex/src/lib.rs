pub mod common;
pub mod crypto;
pub mod ethereum;
pub mod exchange;
pub mod exchanges;
pub mod http;
pub mod lighter;
pub mod product_table;

use std::fmt::{Display, Formatter};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DcexError {
    Decode(String),
    HttpStatus {
        status: u16,
        message: String,
        headers: Vec<(String, String)>,
    },
    InvalidInput(String),
    Runtime(String),
    Transport(String),
}

impl Display for DcexError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Decode(message) => write!(f, "failed to decode response: {message}"),
            Self::HttpStatus {
                status, message, ..
            } => write!(f, "HTTP request failed with status {status}: {message}"),
            Self::InvalidInput(message) => f.write_str(message),
            Self::Runtime(message) => write!(f, "runtime error: {message}"),
            Self::Transport(message) => write!(f, "request transport failed: {message}"),
        }
    }
}

impl std::error::Error for DcexError {}

pub type Result<T> = std::result::Result<T, DcexError>;
