pub mod lighter;

use std::fmt::{Display, Formatter};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DcexError {
    InvalidInput(String),
}

impl Display for DcexError {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidInput(message) => f.write_str(message),
        }
    }
}

impl std::error::Error for DcexError {}

pub type Result<T> = std::result::Result<T, DcexError>;
