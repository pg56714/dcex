use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::ExtendedClient;
use super::endpoints::*;
use super::params::{path_with_id, ExtendedParams};
use super::signing::{
    build_signed_order, extract_market_from_param, extract_market_from_response,
    signed_order_response,
};

impl ExtendedClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = ExtendedParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Extended private method: {method_name}"
        )))
    }

    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &ExtendedParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_open_orders" => {
                self.private_get(ORDERS, params.only(&["market", "type", "side"]))
                    .await
            }
            "get_orders_history" | "get_order_history" => {
                self.private_get(
                    ORDERS_HISTORY,
                    params.only(&[
                        "id",
                        "externalId",
                        "market",
                        "type",
                        "side",
                        "cursor",
                        "limit",
                        "sort",
                    ]),
                )
                .await
            }
            "get_order" => {
                let path = path_with_id(ORDERS, params.required("id")?);
                self.private_get(&path, Vec::new()).await
            }
            "get_orders_by_external_id" | "get_order_by_external_id" => {
                let path = format!(
                    "{ORDERS}/external/{}",
                    params
                        .required("externalId")
                        .or_else(|_| params.required("external_id"))?
                );
                self.private_get(&path, Vec::new()).await
            }
            "place_order" | "create_order" => match params.body_optional()? {
                Some(body) => self.private_post_value(ORDER, body, Vec::new()).await,
                None => self.place_signed_limit_order(params).await,
            },
            "place_limit_order" | "create_limit_order" => {
                self.place_signed_limit_order(params).await
            }
            "sign_create_order" | "sign_order" => {
                let signed = self.signed_order_from_params(params).await?;
                return Ok(Some(signed_order_response(signed.body, signed.order_hash)));
            }
            "cancel_order" => {
                let path = path_with_id(ORDER, params.required("id")?);
                self.private_delete(&path, Vec::new()).await
            }
            "cancel_order_by_external_id" => {
                self.private_delete(
                    ORDER,
                    vec![(
                        "externalId".to_string(),
                        params.required("externalId")?.to_string(),
                    )],
                )
                .await
            }
            "mass_cancel" => {
                self.private_post_value(MASS_CANCEL, params.body_required()?, Vec::new())
                    .await
            }
            "set_deadmanswitch" | "set_deadman_switch" => {
                self.request(
                    crate::http::HttpMethod::Post,
                    DEADMAN_SWITCH,
                    params.only(&["countdownTime"]),
                    None,
                    true,
                    std::collections::BTreeMap::new(),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    async fn place_signed_limit_order(&self, params: &ExtendedParams) -> Result<ValidatedResponse> {
        let signed = self.signed_order_from_params(params).await?;
        self.private_post_value(ORDER, signed.body, Vec::new())
            .await
    }

    async fn signed_order_from_params(
        &self,
        params: &ExtendedParams,
    ) -> Result<super::signing::ExtendedSignedOrder> {
        let market_name = self.signed_order_market(params)?;
        let market = match extract_market_from_param(params, &market_name)? {
            Some(market) => market,
            None => {
                let response = self
                    .public_get(MARKETS, vec![("market".to_string(), market_name.clone())])
                    .await?;
                extract_market_from_response(&response.data, &market_name)?
            }
        };
        build_signed_order(params, market, self.signing_credentials()?)
    }

    fn signed_order_market(&self, params: &ExtendedParams) -> Result<String> {
        if let Some(product_symbol) = params.get("product_symbol") {
            return self.exchange_symbol(product_symbol);
        }
        if let Some(market) = params.get("market") {
            return self.exchange_symbol(market);
        }
        Err(DcexError::InvalidInput(
            "missing required parameter: market or product_symbol".to_string(),
        ))
    }
}
