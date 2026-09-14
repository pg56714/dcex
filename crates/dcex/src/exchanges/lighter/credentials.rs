use std::env;
use std::fmt::{Debug, Formatter};

use crate::{DcexError, Result};

use super::chains::LighterNetwork;

/// Private Lighter credentials scoped to one network deployment.
#[derive(Clone, PartialEq, Eq)]
pub struct LighterCredentials {
    account_index: u64,
    api_key_index: u64,
    api_private_key: String,
}

impl Debug for LighterCredentials {
    fn fmt(&self, formatter: &mut Formatter<'_>) -> std::fmt::Result {
        formatter
            .debug_struct("LighterCredentials")
            .field("account_index", &self.account_index)
            .field("api_key_index", &self.api_key_index)
            .field("api_private_key", &"[REDACTED]")
            .finish()
    }
}

impl LighterCredentials {
    pub fn new(account_index: u64, api_key_index: u64, api_private_key: String) -> Result<Self> {
        if account_index > (1 << 48) - 2 {
            return Err(DcexError::InvalidInput(
                "Lighter account_index is outside the valid range".to_string(),
            ));
        }
        if api_key_index > 254 {
            return Err(DcexError::InvalidInput(
                "Lighter api_key_index must be between 0 and 254".to_string(),
            ));
        }
        if api_private_key.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "Lighter api_private_key cannot be empty".to_string(),
            ));
        }
        Ok(Self {
            account_index,
            api_key_index,
            api_private_key,
        })
    }

    /// Load one complete credential set from network-scoped environment variables.
    pub fn from_env(network: LighterNetwork) -> Result<Self> {
        Self::from_lookup(network, |name| match env::var(name) {
            Ok(value) => Ok(non_empty(value)),
            Err(env::VarError::NotPresent) => Ok(None),
            Err(env::VarError::NotUnicode(_)) => Err(DcexError::InvalidInput(format!(
                "Lighter environment variable {name} is not valid Unicode"
            ))),
        })
    }

    pub const fn account_index(&self) -> u64 {
        self.account_index
    }

    pub const fn api_key_index(&self) -> u64 {
        self.api_key_index
    }

    pub fn api_private_key(&self) -> &str {
        &self.api_private_key
    }

    pub fn into_parts(self) -> (u64, u64, String) {
        (self.account_index, self.api_key_index, self.api_private_key)
    }

    fn from_lookup<F>(network: LighterNetwork, mut lookup: F) -> Result<Self>
    where
        F: FnMut(&str) -> Result<Option<String>>,
    {
        let names = credential_env_names(network);
        let values = read_values(&names, &mut lookup)?;

        let [account_index, api_key_index, api_private_key] = values;
        let account_index = required_value(account_index, names[0])?;
        let api_key_index = required_value(api_key_index, names[1])?;
        let api_private_key = required_value(api_private_key, names[2])?;

        Self::new(
            parse_index(&account_index, names[0])?,
            parse_index(&api_key_index, names[1])?,
            api_private_key,
        )
    }
}

pub const fn credentials_env_prefix(network: LighterNetwork) -> &'static str {
    match network {
        LighterNetwork::Mainnet => "LIGHTER_MAINNET",
        LighterNetwork::Testnet => "LIGHTER_TESTNET",
        LighterNetwork::Robinhood => "LIGHTER_ROBINHOOD",
        LighterNetwork::RobinhoodTestnet => "LIGHTER_ROBINHOOD_TESTNET",
    }
}

pub const fn credential_env_names(network: LighterNetwork) -> [&'static str; 3] {
    match network {
        LighterNetwork::Mainnet => [
            "LIGHTER_MAINNET_ACCOUNT_INDEX",
            "LIGHTER_MAINNET_API_KEY_INDEX",
            "LIGHTER_MAINNET_API_PRIVATE_KEY",
        ],
        LighterNetwork::Testnet => [
            "LIGHTER_TESTNET_ACCOUNT_INDEX",
            "LIGHTER_TESTNET_API_KEY_INDEX",
            "LIGHTER_TESTNET_API_PRIVATE_KEY",
        ],
        LighterNetwork::Robinhood => [
            "LIGHTER_ROBINHOOD_ACCOUNT_INDEX",
            "LIGHTER_ROBINHOOD_API_KEY_INDEX",
            "LIGHTER_ROBINHOOD_API_PRIVATE_KEY",
        ],
        LighterNetwork::RobinhoodTestnet => [
            "LIGHTER_ROBINHOOD_TESTNET_ACCOUNT_INDEX",
            "LIGHTER_ROBINHOOD_TESTNET_API_KEY_INDEX",
            "LIGHTER_ROBINHOOD_TESTNET_API_PRIVATE_KEY",
        ],
    }
}

fn read_values<F>(names: &[&'static str; 3], lookup: &mut F) -> Result<[Option<String>; 3]>
where
    F: FnMut(&str) -> Result<Option<String>>,
{
    Ok([lookup(names[0])?, lookup(names[1])?, lookup(names[2])?])
}

fn required_value(value: Option<String>, name: &str) -> Result<String> {
    value.ok_or_else(|| {
        DcexError::InvalidInput(format!(
            "missing Lighter credential environment variable: {name}"
        ))
    })
}

fn parse_index(value: &str, name: &str) -> Result<u64> {
    value.trim().parse::<u64>().map_err(|error| {
        DcexError::InvalidInput(format!(
            "invalid Lighter environment variable {name}: {error}"
        ))
    })
}

fn non_empty(value: String) -> Option<String> {
    (!value.trim().is_empty()).then_some(value)
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use super::*;

    fn load(network: LighterNetwork, values: &[(&str, &str)]) -> Result<LighterCredentials> {
        let values = values
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect::<BTreeMap<_, _>>();
        LighterCredentials::from_lookup(network, |name| Ok(values.get(name).cloned()))
    }

    #[test]
    fn loads_network_scoped_credentials() {
        let credentials = load(
            LighterNetwork::Robinhood,
            &[
                ("LIGHTER_ROBINHOOD_ACCOUNT_INDEX", "12"),
                ("LIGHTER_ROBINHOOD_API_KEY_INDEX", "3"),
                ("LIGHTER_ROBINHOOD_API_PRIVATE_KEY", "secret"),
            ],
        )
        .expect("Robinhood credentials");

        assert_eq!(credentials.account_index(), 12);
        assert_eq!(credentials.api_key_index(), 3);
        assert_eq!(credentials.api_private_key(), "secret");
        assert!(!format!("{credentials:?}").contains("secret"));
    }

    #[test]
    fn mainnet_rejects_legacy_credentials() {
        let error = load(
            LighterNetwork::Mainnet,
            &[
                ("LIGHTER_ACCOUNT_INDEX", "8"),
                ("LIGHTER_API_KEY_INDEX", "2"),
                ("LIGHTER_API_PRIVATE_KEY", "legacy-secret"),
            ],
        )
        .expect_err("mainnet must require scoped credentials");

        assert!(error.to_string().contains("LIGHTER_MAINNET_ACCOUNT_INDEX"));
    }

    #[test]
    fn robinhood_never_falls_back_to_legacy_credentials() {
        let error = load(
            LighterNetwork::Robinhood,
            &[
                ("LIGHTER_ACCOUNT_INDEX", "8"),
                ("LIGHTER_API_KEY_INDEX", "2"),
                ("LIGHTER_API_PRIVATE_KEY", "legacy-secret"),
            ],
        )
        .expect_err("Robinhood must require scoped credentials");

        assert!(error
            .to_string()
            .contains("LIGHTER_ROBINHOOD_ACCOUNT_INDEX"));
    }

    #[test]
    fn partial_scoped_mainnet_credentials_are_rejected() {
        let error = load(
            LighterNetwork::Mainnet,
            &[
                ("LIGHTER_MAINNET_ACCOUNT_INDEX", "9"),
                ("LIGHTER_API_KEY_INDEX", "2"),
                ("LIGHTER_API_PRIVATE_KEY", "legacy-secret"),
            ],
        )
        .expect_err("partial scoped credentials must fail");

        assert!(error.to_string().contains("LIGHTER_MAINNET_API_KEY_INDEX"));
    }
}
