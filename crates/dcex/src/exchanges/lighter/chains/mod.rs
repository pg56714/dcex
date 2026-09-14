mod lighter;
mod robinhood;

use std::fmt::{Display, Formatter};
use std::str::FromStr;

use crate::{DcexError, Result};

pub use lighter::{MAINNET, TESTNET};
pub use robinhood::{ROBINHOOD, ROBINHOOD_TESTNET};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LighterEndpointProfile {
    pub name: &'static str,
    pub api_url: &'static str,
    pub ws_url: &'static str,
    pub chain_id: u64,
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum LighterNetwork {
    #[default]
    Mainnet,
    Testnet,
    Robinhood,
    RobinhoodTestnet,
}

impl LighterNetwork {
    pub const ALL: [Self; 4] = [
        Self::Mainnet,
        Self::Testnet,
        Self::Robinhood,
        Self::RobinhoodTestnet,
    ];

    pub const fn profile(self) -> LighterEndpointProfile {
        match self {
            Self::Mainnet => MAINNET,
            Self::Testnet => TESTNET,
            Self::Robinhood => ROBINHOOD,
            Self::RobinhoodTestnet => ROBINHOOD_TESTNET,
        }
    }

    pub const fn as_str(self) -> &'static str {
        self.profile().name
    }

    pub fn from_api_url(api_url: &str) -> Option<Self> {
        let api_url = api_url.trim_end_matches('/');
        Self::ALL
            .into_iter()
            .find(|network| network.profile().api_url == api_url)
    }
}

impl Display for LighterNetwork {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        formatter.write_str(self.as_str())
    }
}

impl FromStr for LighterNetwork {
    type Err = DcexError;

    fn from_str(value: &str) -> Result<Self> {
        match value.trim().to_ascii_lowercase().replace('-', "_").as_str() {
            "mainnet" => Ok(Self::Mainnet),
            "testnet" => Ok(Self::Testnet),
            "robinhood" => Ok(Self::Robinhood),
            "robinhood_testnet" => Ok(Self::RobinhoodTestnet),
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Lighter network: {value}"
            ))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exposes_official_endpoint_profiles() {
        assert_eq!(MAINNET.chain_id, 304);
        assert_eq!(TESTNET.chain_id, 300);
        assert_eq!(ROBINHOOD.api_url, "https://api.rh.lighter.xyz");
        assert_eq!(ROBINHOOD.ws_url, "wss://api.rh.lighter.xyz/stream");
        assert_eq!(ROBINHOOD.chain_id, 466_324);
        assert_eq!(ROBINHOOD_TESTNET.chain_id, 300);
    }

    #[test]
    fn parses_network_names_and_known_urls() {
        assert_eq!(
            "robinhood-testnet".parse::<LighterNetwork>(),
            Ok(LighterNetwork::RobinhoodTestnet)
        );
        assert_eq!(
            LighterNetwork::from_api_url("https://api.rh.lighter.xyz/"),
            Some(LighterNetwork::Robinhood)
        );
        assert_eq!(LighterNetwork::from_api_url("http://localhost:8000"), None);
        assert!("unknown".parse::<LighterNetwork>().is_err());
    }
}
