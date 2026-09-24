use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

macro_rules! staking_methods {
    ($($name:ident),+ $(,)?) => {
        $(
            pub fn $name(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
                self.staking_request(stringify!($name), Vec::new())
            }
        )+
    };
}

impl BinanceClient {
    fn staking_request(
        &self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, method_name, params)
    }

    staking_methods!(
        get_eth_staking_account,
        get_eth_staking_quota,
        get_eth_redemption_history,
        get_eth_staking_history,
        get_wbeth_rate_history,
        get_wbeth_rewards_history,
        get_wbeth_unwrap_history,
        get_wbeth_wrap_history,
        get_onchain_yields_products,
        get_onchain_yields_positions,
        get_onchain_yields_redemption_history,
        get_onchain_yields_rewards_history,
        get_onchain_yields_subscription_history,
        get_onchain_yields_account,
        get_soft_staking_products,
        get_soft_staking_rewards_history,
        get_sol_staking_account,
        get_sol_staking_quota,
        get_bnsol_rate_history,
        get_bnsol_rewards_history,
        get_sol_boost_rewards_history,
        get_sol_redemption_history,
        get_sol_staking_history,
        get_sol_unclaimed_rewards,
        claim_sol_boost_rewards,
    );

    pub fn redeem_eth_staking(
        &self,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "redeem_eth_staking",
            vec![("amount".to_string(), amount.to_string())],
        )
    }

    pub fn subscribe_eth_staking(
        &self,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "subscribe_eth_staking",
            vec![("amount".to_string(), amount.to_string())],
        )
    }

    pub fn wrap_beth(&self, amount: &str) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "wrap_beth",
            vec![("amount".to_string(), amount.to_string())],
        )
    }

    pub fn get_onchain_yields_personal_quota(
        &self,
        project_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "get_onchain_yields_personal_quota",
            vec![("projectId".to_string(), project_id.to_string())],
        )
    }

    pub fn preview_onchain_yields_subscription(
        &self,
        project_id: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "preview_onchain_yields_subscription",
            vec![
                ("projectId".to_string(), project_id.to_string()),
                ("amount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn subscribe_onchain_yields(
        &self,
        project_id: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "subscribe_onchain_yields",
            vec![
                ("projectId".to_string(), project_id.to_string()),
                ("amount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn redeem_onchain_yields(
        &self,
        position_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "redeem_onchain_yields",
            vec![("positionId".to_string(), position_id.to_string())],
        )
    }

    pub fn set_onchain_yields_auto_subscribe(
        &self,
        position_id: &str,
        auto_subscribe: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "set_onchain_yields_auto_subscribe",
            vec![
                ("positionId".to_string(), position_id.to_string()),
                ("autoSubscribe".to_string(), auto_subscribe.to_string()),
            ],
        )
    }

    pub fn set_onchain_yields_redeem_option(
        &self,
        position_id: &str,
        redeem_to: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "set_onchain_yields_redeem_option",
            vec![
                ("positionId".to_string(), position_id.to_string()),
                ("redeemTo".to_string(), redeem_to.to_string()),
            ],
        )
    }

    pub fn set_soft_staking(
        &self,
        enabled: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "set_soft_staking",
            vec![("softStaking".to_string(), enabled.to_string())],
        )
    }

    pub fn subscribe_sol_staking(
        &self,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "subscribe_sol_staking",
            vec![("amount".to_string(), amount.to_string())],
        )
    }

    pub fn redeem_sol_staking(
        &self,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.staking_request(
            "redeem_sol_staking",
            vec![("amount".to_string(), amount.to_string())],
        )
    }

    pub(super) async fn staking_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path, required): (HttpMethod, &str, &[&str]) = match method_name {
            "get_eth_staking_account" => (HttpMethod::Get, ETH_STAKING_ACCOUNT, &[]),
            "get_eth_staking_quota" => (HttpMethod::Get, ETH_STAKING_QUOTA, &[]),
            "get_eth_redemption_history" => (HttpMethod::Get, ETH_REDEMPTION_HISTORY, &[]),
            "get_eth_staking_history" => (HttpMethod::Get, ETH_STAKING_HISTORY, &[]),
            "get_wbeth_rate_history" => (HttpMethod::Get, WBETH_RATE_HISTORY, &[]),
            "get_wbeth_rewards_history" => (HttpMethod::Get, WBETH_REWARDS_HISTORY, &[]),
            "get_wbeth_unwrap_history" => (HttpMethod::Get, WBETH_UNWRAP_HISTORY, &[]),
            "get_wbeth_wrap_history" => (HttpMethod::Get, WBETH_WRAP_HISTORY, &[]),
            "redeem_eth_staking" => (HttpMethod::Post, ETH_STAKING_REDEEM, &["amount"]),
            "subscribe_eth_staking" => (HttpMethod::Post, ETH_STAKING_SUBSCRIBE, &["amount"]),
            "wrap_beth" => (HttpMethod::Post, WBETH_WRAP, &["amount"]),
            "get_onchain_yields_personal_quota" => (
                HttpMethod::Get,
                ONCHAIN_YIELDS_PERSONAL_QUOTA,
                &["projectId"],
            ),
            "get_onchain_yields_products" => (HttpMethod::Get, ONCHAIN_YIELDS_PRODUCTS, &[]),
            "get_onchain_yields_positions" => (HttpMethod::Get, ONCHAIN_YIELDS_POSITIONS, &[]),
            "get_onchain_yields_redemption_history" => {
                (HttpMethod::Get, ONCHAIN_YIELDS_REDEMPTION_HISTORY, &[])
            }
            "get_onchain_yields_rewards_history" => {
                (HttpMethod::Get, ONCHAIN_YIELDS_REWARDS_HISTORY, &[])
            }
            "preview_onchain_yields_subscription" => (
                HttpMethod::Get,
                ONCHAIN_YIELDS_SUBSCRIPTION_PREVIEW,
                &["projectId", "amount"],
            ),
            "get_onchain_yields_subscription_history" => {
                (HttpMethod::Get, ONCHAIN_YIELDS_SUBSCRIPTION_HISTORY, &[])
            }
            "get_onchain_yields_account" => (HttpMethod::Get, ONCHAIN_YIELDS_ACCOUNT, &[]),
            "redeem_onchain_yields" => (HttpMethod::Post, ONCHAIN_YIELDS_REDEEM, &["positionId"]),
            "set_onchain_yields_auto_subscribe" => (
                HttpMethod::Post,
                ONCHAIN_YIELDS_SET_AUTO_SUBSCRIBE,
                &["positionId", "autoSubscribe"],
            ),
            "set_onchain_yields_redeem_option" => (
                HttpMethod::Post,
                ONCHAIN_YIELDS_SET_REDEEM_OPTION,
                &["positionId", "redeemTo"],
            ),
            "subscribe_onchain_yields" => (
                HttpMethod::Post,
                ONCHAIN_YIELDS_SUBSCRIBE,
                &["projectId", "amount"],
            ),
            "get_soft_staking_products" => (HttpMethod::Get, SOFT_STAKING_PRODUCTS, &[]),
            "get_soft_staking_rewards_history" => {
                (HttpMethod::Get, SOFT_STAKING_REWARDS_HISTORY, &[])
            }
            "set_soft_staking" => (HttpMethod::Get, SOFT_STAKING_SET, &["softStaking"]),
            "claim_sol_boost_rewards" => (HttpMethod::Post, SOL_STAKING_CLAIM, &[]),
            "get_bnsol_rate_history" => (HttpMethod::Get, BNSOL_RATE_HISTORY, &[]),
            "get_bnsol_rewards_history" => (HttpMethod::Get, BNSOL_REWARDS_HISTORY, &[]),
            "get_sol_boost_rewards_history" => (HttpMethod::Get, SOL_BOOST_REWARDS_HISTORY, &[]),
            "get_sol_redemption_history" => (HttpMethod::Get, SOL_REDEMPTION_HISTORY, &[]),
            "get_sol_staking_history" => (HttpMethod::Get, SOL_STAKING_HISTORY, &[]),
            "get_sol_staking_quota" => (HttpMethod::Get, SOL_STAKING_QUOTA, &[]),
            "get_sol_unclaimed_rewards" => (HttpMethod::Get, SOL_UNCLAIMED_REWARDS, &[]),
            "redeem_sol_staking" => (HttpMethod::Post, SOL_STAKING_REDEEM, &["amount"]),
            "get_sol_staking_account" => (HttpMethod::Get, SOL_STAKING_ACCOUNT, &[]),
            "subscribe_sol_staking" => (HttpMethod::Post, SOL_STAKING_SUBSCRIBE, &["amount"]),
            _ => return Ok(None),
        };

        for field in required {
            params.required(field)?;
        }
        Ok(Some(
            self.request(method, BinanceMarket::Spot, path, params.without(&[]), true)
                .await?,
        ))
    }
}
