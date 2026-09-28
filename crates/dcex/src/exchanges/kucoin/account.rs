pub(in crate::exchanges::kucoin) use serde_json::{Map, Value};

pub(in crate::exchanges::kucoin) use crate::Result;
pub(in crate::exchanges::kucoin) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::kucoin) use super::client::{KucoinClient, KucoinMarket};
pub(in crate::exchanges::kucoin) use super::endpoints::*;
pub(in crate::exchanges::kucoin) use super::params::{
    KucoinParams, insert_required_string, validate_enum, validate_positive_number,
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
            "get_transfer_quotas" => self.dispatch_get_transfer_quotas(method_name, params).await,
            "flex_transfer" => self.dispatch_flex_transfer(method_name, params).await,
            "get_subaccounts" | "get_spot_subaccount_balances" | "get_uta_subaccounts" => {
                params.ensure_allowed(&["currentPage", "pageSize"])?;
                let path = match method_name {
                    "get_subaccounts" => SUBACCOUNT_LIST,
                    "get_spot_subaccount_balances" => SPOT_SUBACCOUNT_BALANCES,
                    "get_uta_subaccounts" => UTA_SUBACCOUNT_LIST,
                    _ => unreachable!(),
                };
                self.private_get(
                    KucoinMarket::Spot,
                    path,
                    params.only(&["currentPage", "pageSize"]),
                )
                .await
            }
            "get_subaccount_balance" => {
                params.ensure_allowed(&[
                    "subUserId",
                    "includeBaseAmount",
                    "baseCurrency",
                    "baseAmount",
                ])?;
                let path = SUBACCOUNT_BALANCE.replace("{subUserId}", params.required("subUserId")?);
                self.private_get(
                    KucoinMarket::Spot,
                    path,
                    params.only(&["includeBaseAmount", "baseCurrency", "baseAmount"]),
                )
                .await
            }
            "get_futures_subaccount_balances" => {
                params.ensure_allowed(&["currency"])?;
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_SUBACCOUNT_BALANCES,
                    params.only(&["currency"]),
                )
                .await
            }
            "get_uta_subaccount_currency_assets" => {
                params.ensure_allowed(&["uid", "pageSize", "lastId"])?;
                self.private_get(
                    KucoinMarket::Spot,
                    UTA_SUBACCOUNT_CURRENCY_ASSETS,
                    params.only(&["uid", "pageSize", "lastId"]),
                )
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

pub(in crate::exchanges::kucoin) fn validate_comma_list(
    value: &str,
    label: &str,
    maximum: usize,
) -> Result<()> {
    let values = value.split(',').map(str::trim).collect::<Vec<_>>();
    if (1..=maximum).contains(&values.len()) && values.iter().all(|entry| !entry.is_empty()) {
        return Ok(());
    }
    Err(crate::DcexError::InvalidInput(format!(
        "KuCoin {label} list must contain between 1 and {maximum} entries"
    )))
}

pub(in crate::exchanges::kucoin) fn validate_transfer_parties(
    params: &KucoinParams,
    transfer_type: &str,
) -> Result<()> {
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

pub(in crate::exchanges::kucoin) fn validate_transfer_account_versions(
    params: &KucoinParams,
    transfer_type: &str,
) -> Result<()> {
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

pub(in crate::exchanges::kucoin) fn reject_parameter(
    params: &KucoinParams,
    key: &str,
    transfer_type: &str,
) -> Result<()> {
    if params.get(key).is_some() {
        return Err(crate::DcexError::InvalidInput(format!(
            "KuCoin parameter {key} is not supported for {transfer_type} transfers"
        )));
    }
    Ok(())
}

pub(in crate::exchanges::kucoin) fn validate_account_tag(
    params: &KucoinParams,
    account_key: &str,
    tag_key: &str,
) -> Result<()> {
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
