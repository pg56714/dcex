use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{validate_enum, validate_positive_number, KucoinParams};

impl KucoinClient {
    pub(super) async fn earn_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_dual_investment_products" => {
                let fields = ["category", "strikeCurrency", "investCurrency", "side"];
                params.ensure_allowed(&fields)?;
                for key in fields {
                    params.required(key)?;
                }
                validate_enum(params, "side", &["CALL", "PUT"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    DUAL_INVESTMENT_PRODUCTS,
                    params.only(&fields),
                )
                .await
            }
            "purchase_earn" => {
                params.ensure_allowed(&["productId", "amount", "accountType"])?;
                for key in ["productId", "amount", "accountType"] {
                    params.required(key)?;
                }
                validate_positive_number(params, "amount")?;
                validate_enum(params, "accountType", &["MAIN", "TRADE"])?;
                self.private_post(
                    KucoinMarket::Spot,
                    EARN_ORDERS,
                    Value::Object(params.body(
                        &["productId", "amount", "accountType"],
                        &[],
                        &[],
                    )?),
                )
                .await
            }
            "get_earn_redeem_preview" => {
                params.ensure_allowed(&["orderId", "fromAccountType"])?;
                params.required("orderId")?;
                params.required("fromAccountType")?;
                validate_enum(params, "fromAccountType", &["MAIN", "TRADE"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    EARN_REDEEM_PREVIEW,
                    params.only(&["orderId", "fromAccountType"]),
                )
                .await
            }
            "redeem_earn" => {
                params.ensure_allowed(&[
                    "orderId",
                    "amount",
                    "fromAccountType",
                    "confirmPunishRedeem",
                ])?;
                params.required("orderId")?;
                if params.get("amount").is_some() {
                    validate_positive_number(params, "amount")?;
                }
                validate_enum(params, "fromAccountType", &["MAIN", "TRADE"])?;
                self.private_delete(
                    KucoinMarket::Spot,
                    EARN_ORDERS,
                    params.only(&[
                        "orderId",
                        "amount",
                        "fromAccountType",
                        "confirmPunishRedeem",
                    ]),
                )
                .await
            }
            "get_earn_savings_products"
            | "get_earn_promotion_products"
            | "get_earn_staking_products"
            | "get_earn_kcs_staking_products"
            | "get_earn_eth_staking_products" => {
                params.ensure_allowed(&["currency"])?;
                let path = match method_name {
                    "get_earn_savings_products" => EARN_SAVINGS_PRODUCTS,
                    "get_earn_promotion_products" => EARN_PROMOTION_PRODUCTS,
                    "get_earn_staking_products" => EARN_STAKING_PRODUCTS,
                    "get_earn_kcs_staking_products" => EARN_KCS_STAKING_PRODUCTS,
                    "get_earn_eth_staking_products" => EARN_ETH_STAKING_PRODUCTS,
                    _ => unreachable!(),
                };
                self.private_get(KucoinMarket::Spot, path, params.only(&["currency"]))
                    .await
            }
            "get_earn_account_holdings" => {
                let fields = [
                    "currency",
                    "productId",
                    "productCategory",
                    "currentPage",
                    "pageSize",
                ];
                params.ensure_allowed(&fields)?;
                self.private_get(
                    KucoinMarket::Spot,
                    EARN_ACCOUNT_HOLDINGS,
                    params.only(&fields),
                )
                .await
            }
            "purchase_structured_earn" => {
                let fields = ["productId", "investCurrency", "investAmount", "accountType"];
                params.ensure_allowed(&fields)?;
                for key in fields {
                    params.required(key)?;
                }
                validate_positive_number(params, "investAmount")?;
                validate_enum(params, "accountType", &["MAIN", "TRADE"])?;
                self.private_post(
                    KucoinMarket::Spot,
                    STRUCTURED_EARN_ORDERS,
                    Value::Object(params.body(&fields, &[], &[])?),
                )
                .await
            }
            "get_structured_earn_orders" => {
                let fields = [
                    "categories",
                    "orderId",
                    "investCurrency",
                    "currentPage",
                    "pageSize",
                ];
                params.ensure_allowed(&fields)?;
                params.required("categories")?;
                self.private_get(
                    KucoinMarket::Spot,
                    STRUCTURED_EARN_ORDERS,
                    params.only(&fields),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
