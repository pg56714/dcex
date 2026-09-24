use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub fn get_simple_earn_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_simple_earn_account",
            Vec::new(),
        )
    }

    pub fn get_flexible_earn_products(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_flexible_earn_products",
            Vec::new(),
        )
    }

    pub fn get_locked_earn_products(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_locked_earn_products",
            Vec::new(),
        )
    }

    pub fn get_flexible_earn_positions(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_flexible_earn_positions",
            Vec::new(),
        )
    }

    pub fn get_locked_earn_positions(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_locked_earn_positions",
            Vec::new(),
        )
    }

    pub fn subscribe_flexible_earn(
        &self,
        product_id: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "subscribe_flexible_earn",
            vec![
                ("productId".to_string(), product_id.to_string()),
                ("amount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn subscribe_locked_earn(
        &self,
        project_id: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "subscribe_locked_earn",
            vec![
                ("projectId".to_string(), project_id.to_string()),
                ("amount".to_string(), amount.to_string()),
            ],
        )
    }

    pub fn redeem_flexible_earn(
        &self,
        product_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "redeem_flexible_earn",
            vec![("productId".to_string(), product_id.to_string())],
        )
    }

    pub fn redeem_locked_earn(
        &self,
        position_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "redeem_locked_earn",
            vec![("positionId".to_string(), position_id.to_string())],
        )
    }

    pub fn get_flexible_earn_subscription_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_flexible_earn_subscription_history",
            Vec::new(),
        )
    }

    pub fn get_locked_earn_subscription_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_locked_earn_subscription_history",
            Vec::new(),
        )
    }

    pub fn get_flexible_earn_redemption_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_flexible_earn_redemption_history",
            Vec::new(),
        )
    }

    pub fn get_locked_earn_redemption_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_locked_earn_redemption_history",
            Vec::new(),
        )
    }

    pub fn get_flexible_earn_rewards_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_flexible_earn_rewards_history",
            Vec::new(),
        )
    }

    pub fn get_locked_earn_rewards_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_locked_earn_rewards_history",
            Vec::new(),
        )
    }

    pub(super) async fn simple_earn_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path) = match method_name {
            "get_simple_earn_account" => (HttpMethod::Get, SIMPLE_EARN_ACCOUNT),
            "get_flexible_earn_products" => (HttpMethod::Get, SIMPLE_EARN_FLEXIBLE_LIST),
            "get_locked_earn_products" => (HttpMethod::Get, SIMPLE_EARN_LOCKED_LIST),
            "get_flexible_earn_positions" => (HttpMethod::Get, SIMPLE_EARN_FLEXIBLE_POSITION),
            "get_locked_earn_positions" => (HttpMethod::Get, SIMPLE_EARN_LOCKED_POSITION),
            "subscribe_flexible_earn" => {
                params.required("productId")?;
                params.required("amount")?;
                (HttpMethod::Post, SIMPLE_EARN_FLEXIBLE_SUBSCRIBE)
            }
            "subscribe_locked_earn" => {
                params.required("projectId")?;
                params.required("amount")?;
                (HttpMethod::Post, SIMPLE_EARN_LOCKED_SUBSCRIBE)
            }
            "redeem_flexible_earn" => {
                params.required("productId")?;
                let redeem_all = params
                    .get("redeemAll")
                    .is_some_and(|value| value.eq_ignore_ascii_case("true"));
                if !redeem_all && params.get("amount").is_none() {
                    return Err(DcexError::InvalidInput(
                        "Binance flexible earn redemption requires amount unless redeemAll is true."
                            .to_string(),
                    ));
                }
                (HttpMethod::Post, SIMPLE_EARN_FLEXIBLE_REDEEM)
            }
            "redeem_locked_earn" => {
                params.required("positionId")?;
                (HttpMethod::Post, SIMPLE_EARN_LOCKED_REDEEM)
            }
            "get_flexible_earn_subscription_history" => {
                (HttpMethod::Get, SIMPLE_EARN_FLEXIBLE_SUBSCRIPTIONS)
            }
            "get_locked_earn_subscription_history" => {
                (HttpMethod::Get, SIMPLE_EARN_LOCKED_SUBSCRIPTIONS)
            }
            "get_flexible_earn_redemption_history" => {
                (HttpMethod::Get, SIMPLE_EARN_FLEXIBLE_REDEMPTIONS)
            }
            "get_locked_earn_redemption_history" => {
                (HttpMethod::Get, SIMPLE_EARN_LOCKED_REDEMPTIONS)
            }
            "get_flexible_earn_rewards_history" => (HttpMethod::Get, SIMPLE_EARN_FLEXIBLE_REWARDS),
            "get_locked_earn_rewards_history" => (HttpMethod::Get, SIMPLE_EARN_LOCKED_REWARDS),
            _ => return Ok(None),
        };
        Ok(Some(
            self.request(method, BinanceMarket::Spot, path, params.without(&[]), true)
                .await?,
        ))
    }
}
