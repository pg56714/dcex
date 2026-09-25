use serde_json::Value;

use crate::Result;
use crate::exchange::ValidatedResponse;

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{KucoinParams, validate_positive_number};

const HISTORY_FIELDS: &[&str] = &[
    "currency",
    "isIsolated",
    "product_symbol",
    "symbol",
    "orderNo",
    "startTime",
    "endTime",
    "currentPage",
    "pageSize",
];

impl KucoinClient {
    pub(super) async fn margin_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_cross_margin_account" => {
                params.ensure_allowed(&["quoteCurrency", "queryType"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    CROSS_MARGIN_ACCOUNT,
                    params.only(&["quoteCurrency", "queryType"]),
                )
                .await
            }
            "get_isolated_margin_account" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "quoteCurrency",
                    "queryType",
                ])?;
                let mut query = params.only(&["quoteCurrency", "queryType"]);
                if let Some(symbol) = params.get_any(&["product_symbol", "symbol"]) {
                    query.push(("symbol".to_string(), self.exchange_symbol(symbol, false)?));
                }
                self.private_get(KucoinMarket::Spot, ISOLATED_MARGIN_ACCOUNT, query)
                    .await
            }
            "get_margin_borrow_interest_rate" => {
                params.ensure_allowed(&["vipLevel", "currency"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_BORROW_RATE,
                    params.only(&["vipLevel", "currency"]),
                )
                .await
            }
            "borrow_margin" => {
                params.ensure_allowed(&[
                    "currency",
                    "size",
                    "timeInForce",
                    "isIsolated",
                    "isHf",
                    "product_symbol",
                    "symbol",
                ])?;
                params.required("currency")?;
                validate_positive_number(params, "size")?;
                let mut body = params.body(
                    &["currency", "size", "timeInForce"],
                    &[],
                    &["isIsolated", "isHf"],
                )?;
                insert_optional_margin_symbol(self, params, &mut body)?;
                self.private_post(KucoinMarket::Spot, MARGIN_BORROW, Value::Object(body))
                    .await
            }
            "get_margin_borrow_history" => {
                params.ensure_allowed(HISTORY_FIELDS)?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_BORROW,
                    margin_history_query(self, params)?,
                )
                .await
            }
            "repay_margin" => {
                params.ensure_allowed(&[
                    "currency",
                    "size",
                    "isIsolated",
                    "product_symbol",
                    "symbol",
                ])?;
                params.required("currency")?;
                validate_positive_number(params, "size")?;
                let mut body = params.body(&["currency", "size"], &[], &["isIsolated"])?;
                insert_optional_margin_symbol(self, params, &mut body)?;
                self.private_post(KucoinMarket::Spot, MARGIN_REPAY, Value::Object(body))
                    .await
            }
            "get_margin_repay_history" => {
                params.ensure_allowed(HISTORY_FIELDS)?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_REPAY,
                    margin_history_query(self, params)?,
                )
                .await
            }
            "get_margin_interest_history" => {
                let fields = [
                    "currency",
                    "isIsolated",
                    "symbol",
                    "startTime",
                    "endTime",
                    "currentPage",
                    "pageSize",
                ];
                params.ensure_allowed(&fields)?;
                params.required("status")?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_INTEREST,
                    margin_history_query(self, params)?,
                )
                .await
            }
            "modify_margin_leverage" => {
                params.ensure_allowed(&["leverage", "isIsolated", "product_symbol", "symbol"])?;
                validate_positive_number(params, "leverage")?;
                let mut body = params.body(&["leverage"], &[], &["isIsolated"])?;
                insert_optional_margin_symbol(self, params, &mut body)?;
                self.private_post(
                    KucoinMarket::Spot,
                    MARGIN_MODIFY_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            "get_margin_loan_market" => {
                params.ensure_allowed(&["currency"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_LOAN_MARKET,
                    params.only(&["currency"]),
                )
                .await
            }
            "purchase_margin_lending" => {
                params.ensure_allowed(&["currency", "size", "interestRate"])?;
                params.required("currency")?;
                validate_positive_number(params, "size")?;
                validate_positive_number(params, "interestRate")?;
                self.private_post(
                    KucoinMarket::Spot,
                    MARGIN_LENDING_PURCHASE,
                    Value::Object(params.body(&["currency", "size", "interestRate"], &[], &[])?),
                )
                .await
            }
            "modify_margin_lending_purchase" => {
                params.ensure_allowed(&["currency", "purchaseOrderNo", "interestRate"])?;
                validate_positive_number(params, "interestRate")?;
                for key in ["currency", "purchaseOrderNo"] {
                    params.required(key)?;
                }
                self.private_post(
                    KucoinMarket::Spot,
                    MARGIN_LENDING_MODIFY_PURCHASE,
                    Value::Object(params.body(
                        &["currency", "purchaseOrderNo", "interestRate"],
                        &[],
                        &[],
                    )?),
                )
                .await
            }
            "get_margin_lending_purchase_orders" => {
                let fields = [
                    "status",
                    "currency",
                    "purchaseOrderNo",
                    "currentPage",
                    "pageSize",
                ];
                params.ensure_allowed(&fields)?;
                params.required("status")?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_LENDING_PURCHASE_ORDERS,
                    params.only(&fields),
                )
                .await
            }
            "redeem_margin_lending" => {
                params.ensure_allowed(&["currency", "size", "purchaseOrderNo"])?;
                validate_positive_number(params, "size")?;
                for key in ["currency", "purchaseOrderNo"] {
                    params.required(key)?;
                }
                self.private_post(
                    KucoinMarket::Spot,
                    MARGIN_LENDING_REDEEM,
                    Value::Object(params.body(
                        &["currency", "size", "purchaseOrderNo"],
                        &[],
                        &[],
                    )?),
                )
                .await
            }
            "get_margin_lending_redeem_orders" => {
                let fields = [
                    "status",
                    "currency",
                    "redeemOrderNo",
                    "currentPage",
                    "pageSize",
                ];
                params.ensure_allowed(&fields)?;
                self.private_get(
                    KucoinMarket::Spot,
                    MARGIN_LENDING_REDEEM_ORDERS,
                    params.only(&fields),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn insert_optional_margin_symbol(
    client: &KucoinClient,
    params: &KucoinParams,
    body: &mut serde_json::Map<String, Value>,
) -> Result<()> {
    if let Some(symbol) = params.get_any(&["product_symbol", "symbol"]) {
        body.insert(
            "symbol".to_string(),
            Value::String(client.exchange_symbol(symbol, false)?),
        );
    }
    Ok(())
}

fn margin_history_query(
    client: &KucoinClient,
    params: &KucoinParams,
) -> Result<Vec<(String, String)>> {
    let mut query = params.only(HISTORY_FIELDS);
    if let Some((key, _)) = query.iter_mut().find(|(key, _)| key == "product_symbol") {
        *key = "symbol".to_string();
    }
    if let Some((_, symbol)) = query.iter_mut().find(|(key, _)| key == "symbol") {
        *symbol = client.exchange_symbol(symbol, false)?;
    }
    Ok(query)
}
