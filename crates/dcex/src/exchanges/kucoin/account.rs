use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{
    generate_client_oid, insert_optional_string, insert_required_string, validate_enum,
    validate_positive_number, validate_text_length, KucoinParams,
};

impl KucoinClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_fee_rates" | "get_futures_fee_rates" => {
                params.ensure_allowed(&["product_symbol"])?;
                let product_symbol = params.required("product_symbol")?;
                let (market, path, query_key, futures) = match method_name {
                    "get_spot_fee_rates" => (KucoinMarket::Spot, SPOT_TRADE_FEES, "symbols", false),
                    "get_futures_fee_rates" => {
                        (KucoinMarket::Futures, FUTURES_TRADE_FEES, "symbol", true)
                    }
                    _ => unreachable!(),
                };
                self.private_get(
                    market,
                    path,
                    vec![(
                        query_key.to_string(),
                        self.exchange_symbol(product_symbol, futures)?,
                    )],
                )
                .await
            }
            "get_uta_fee_rates" => {
                params.ensure_allowed(&["tradeType", "symbol"])?;
                params.required("tradeType")?;
                let symbols = params.required("symbol")?;
                validate_enum(params, "tradeType", &["SPOT", "FUTURES"])?;
                validate_comma_list(symbols, "symbol", 10)?;
                self.private_get(
                    KucoinMarket::Spot,
                    UTA_FEE_RATES,
                    params.only(&["tradeType", "symbol"]),
                )
                .await
            }

            "get_account_balance" => {
                params.ensure_allowed(&["currency", "type"])?;
                validate_enum(params, "type", &["main", "trade"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    SPOT_ACCOUNT_BALANCE,
                    params.only(&["currency", "type"]),
                )
                .await
            }
            "get_transfer_quotas" => {
                params.ensure_allowed(&["currency", "account_type", "type", "tag"])?;
                let account_type = params.required_any(&["account_type", "type"])?;
                if !matches!(
                    account_type,
                    "MAIN" | "TRADE" | "MARGIN" | "ISOLATED" | "MARGIN_V2" | "ISOLATED_V2"
                ) {
                    return Err(crate::DcexError::InvalidInput(format!(
                        "unsupported KuCoin account type: {account_type}"
                    )));
                }
                let mut query = Vec::new();
                query.push((
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                ));
                query.push(("type".to_string(), account_type.to_string()));
                if let Some(tag) = params.get("tag") {
                    query.push(("tag".to_string(), tag.to_string()));
                }
                self.private_get(KucoinMarket::Spot, SPOT_TRANSFER_QUOTAS, query)
                    .await
            }
            "flex_transfer" => {
                params.ensure_allowed(&[
                    "clientOid",
                    "currency",
                    "amount",
                    "fromUserId",
                    "fromAccountType",
                    "fromAccountTag",
                    "transfer_type",
                    "type",
                    "toUserId",
                    "toAccountType",
                    "toAccountTag",
                ])?;
                validate_positive_number(params, "amount")?;
                validate_text_length(params, "clientOid", 128, true)?;
                let transfer_type = params
                    .get_any(&["transfer_type", "type"])
                    .unwrap_or("INTERNAL");
                if !matches!(
                    transfer_type,
                    "INTERNAL" | "PARENT_TO_SUB" | "SUB_TO_PARENT" | "SUB_TO_SUB"
                ) {
                    return Err(crate::DcexError::InvalidInput(format!(
                        "unsupported KuCoin transfer type: {transfer_type}"
                    )));
                }
                validate_transfer_parties(params, transfer_type)?;
                validate_transfer_account_versions(params, transfer_type)?;
                validate_account_tag(params, "fromAccountType", "fromAccountTag")?;
                validate_account_tag(params, "toAccountType", "toAccountTag")?;
                let mut body = Map::new();
                let client_oid = params
                    .get("clientOid")
                    .map(str::to_string)
                    .unwrap_or_else(generate_client_oid);
                insert_required_string(&mut body, "clientOid", &client_oid);
                insert_required_string(&mut body, "type", transfer_type);
                insert_required_string(&mut body, "currency", params.required("currency")?);
                insert_required_string(&mut body, "amount", params.required("amount")?);
                insert_required_string(
                    &mut body,
                    "fromAccountType",
                    params.required("fromAccountType")?,
                );
                insert_required_string(
                    &mut body,
                    "toAccountType",
                    params.required("toAccountType")?,
                );
                insert_optional_string(&mut body, "fromUserId", params.get("fromUserId"));
                insert_optional_string(&mut body, "fromAccountTag", params.get("fromAccountTag"));
                insert_optional_string(&mut body, "toUserId", params.get("toUserId"));
                insert_optional_string(&mut body, "toAccountTag", params.get("toAccountTag"));
                self.private_post(KucoinMarket::Spot, SPOT_FLEX_TRANSFER, Value::Object(body))
                    .await
            }
            "get_futures_account" => {
                params.ensure_allowed(&["currency"])?;
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_ACCOUNT_OVERVIEW,
                    params.only(&["currency"]),
                )
                .await
            }
            "get_futures_positions" => {
                params.ensure_allowed(&["currency"])?;
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_POSITIONS,
                    params.only(&["currency"]),
                )
                .await
            }
            "get_futures_position" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_POSITION, query)
                    .await
            }
            "get_futures_position_mode" => {
                params.ensure_allowed(&[])?;
                self.private_get(KucoinMarket::Futures, FUTURES_POSITION_MODE, Vec::new())
                    .await
            }
            "get_futures_cross_margin_leverage" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_CROSS_MARGIN_LEVERAGE, query)
                    .await
            }
            "modify_futures_cross_margin_leverage" => {
                params.ensure_allowed(&["product_symbol", "symbol", "leverage"])?;
                validate_positive_number(params, "leverage")?;
                let mut body = Map::new();
                body.insert(
                    "symbol".to_string(),
                    Value::String(self.exchange_symbol(
                        params.required_any(&["product_symbol", "symbol"])?,
                        true,
                    )?),
                );
                insert_required_string(&mut body, "leverage", params.required("leverage")?);
                self.private_post(
                    KucoinMarket::Futures,
                    FUTURES_MODIFY_CROSS_MARGIN_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_comma_list(value: &str, label: &str, maximum: usize) -> Result<()> {
    let values = value.split(',').map(str::trim).collect::<Vec<_>>();
    if (1..=maximum).contains(&values.len()) && values.iter().all(|entry| !entry.is_empty()) {
        return Ok(());
    }
    Err(crate::DcexError::InvalidInput(format!(
        "KuCoin {label} list must contain between 1 and {maximum} entries"
    )))
}

fn validate_transfer_parties(params: &KucoinParams, transfer_type: &str) -> Result<()> {
    match transfer_type {
        "PARENT_TO_SUB" => {
            params.required("toUserId")?;
            reject_parameter(params, "fromUserId", transfer_type)?;
        }
        "SUB_TO_PARENT" => {
            params.required("fromUserId")?;
            reject_parameter(params, "toUserId", transfer_type)?;
        }
        "SUB_TO_SUB" => {
            params.required("fromUserId")?;
            params.required("toUserId")?;
        }
        "INTERNAL" => {
            reject_parameter(params, "fromUserId", transfer_type)?;
            reject_parameter(params, "toUserId", transfer_type)?;
        }
        _ => unreachable!(),
    }
    Ok(())
}

fn validate_transfer_account_versions(params: &KucoinParams, transfer_type: &str) -> Result<()> {
    if transfer_type == "INTERNAL" {
        return Ok(());
    }
    for key in ["fromAccountType", "toAccountType"] {
        if matches!(params.get(key), Some("MARGIN_V2" | "ISOLATED_V2")) {
            return Err(crate::DcexError::InvalidInput(format!(
                "KuCoin {key} cannot use a V2 margin account type for {transfer_type} transfers"
            )));
        }
    }
    Ok(())
}

fn reject_parameter(params: &KucoinParams, key: &str, transfer_type: &str) -> Result<()> {
    if params.get(key).is_some() {
        return Err(crate::DcexError::InvalidInput(format!(
            "KuCoin parameter {key} is not supported for {transfer_type} transfers"
        )));
    }
    Ok(())
}

fn validate_account_tag(params: &KucoinParams, account_key: &str, tag_key: &str) -> Result<()> {
    let account_type = params.required(account_key)?;
    if !matches!(
        account_type,
        "MAIN"
            | "TRADE"
            | "CONTRACT"
            | "MARGIN"
            | "ISOLATED"
            | "MARGIN_V2"
            | "ISOLATED_V2"
            | "UNIFIED"
    ) {
        return Err(crate::DcexError::InvalidInput(format!(
            "unsupported KuCoin {account_key}: {account_type}"
        )));
    }
    if matches!(account_type, "ISOLATED" | "ISOLATED_V2") {
        params.required(tag_key)?;
    }
    Ok(())
}
