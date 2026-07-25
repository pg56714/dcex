use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::{require_one_identifier, BitgetParams};

impl BitgetClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_fee_rates" | "get_futures_fee_rates" => {
                let mut query = Vec::new();
                self.push_required_product_symbol(&mut query, params)?;
                let business_type = match method_name {
                    "get_spot_fee_rates" => "spot",
                    "get_futures_fee_rates" => "mix",
                    _ => unreachable!(),
                };
                query.push(("businessType".to_string(), business_type.to_string()));
                self.get_private(COMMON_TRADE_RATE, query).await
            }
            "get_all_account_balance" => {
                self.get_private(COMMON_ALL_ACCOUNT_BALANCE, Vec::new())
                    .await
            }
            "get_funding_assets" => {
                self.get_private(COMMON_FUNDING_ASSETS, params.only(&["coin"]))
                    .await
            }
            "get_spot_account_info" => self.get_private(SPOT_ACCOUNT_INFO, Vec::new()).await,
            "get_spot_account_assets" => {
                self.get_private(SPOT_ACCOUNT_ASSETS, params.only(&["coin", "assetType"]))
                    .await
            }
            "get_spot_account_bills" => {
                self.get_private(
                    SPOT_ACCOUNT_BILLS,
                    params.only(&[
                        "coin",
                        "groupType",
                        "businessType",
                        "startTime",
                        "endTime",
                        "limit",
                        "idLessThan",
                    ]),
                )
                .await
            }
            "transfer" => {
                for key in ["coin", "amount", "fromType", "toType"] {
                    params.required(key)?;
                }
                if matches!(params.get("fromType"), Some("isolated_margin"))
                    || matches!(params.get("toType"), Some("isolated_margin"))
                {
                    params.required("symbol")?;
                }
                self.post_private(
                    SPOT_ACCOUNT_TRANSFER,
                    Value::Object(params.body(&[
                        "coin",
                        "amount",
                        "fromType",
                        "toType",
                        "symbol",
                        "clientOid",
                    ])),
                )
                .await
            }
            "get_transfer_records" => {
                params.required("coin")?;
                self.get_private(
                    SPOT_ACCOUNT_TRANSFER_RECORDS,
                    params.only(&[
                        "coin",
                        "fromType",
                        "startTime",
                        "endTime",
                        "clientOid",
                        "pageNum",
                        "limit",
                        "idLessThan",
                    ]),
                )
                .await
            }
            "get_transferable_coins" => {
                params.required("fromType")?;
                params.required("toType")?;
                self.get_private(
                    SPOT_ACCOUNT_TRANSFER_COIN_INFO,
                    params.only(&["fromType", "toType"]),
                )
                .await
            }
            "get_deposit_records" => {
                params.required("startTime")?;
                params.required("endTime")?;
                self.get_private(
                    SPOT_ACCOUNT_DEPOSIT_RECORDS,
                    params.only(&[
                        "coin",
                        "orderId",
                        "startTime",
                        "endTime",
                        "idLessThan",
                        "limit",
                    ]),
                )
                .await
            }
            "get_uta_account_assets" => self.get_private(UTA_ACCOUNT_ASSETS, Vec::new()).await,
            "get_uta_account_info" => self.get_private(UTA_ACCOUNT_INFO, Vec::new()).await,
            "get_uta_all_fee_rates" => {
                params.required("category")?;
                let mut query = params.only(&["category"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_ALL_FEE_RATES, query).await
            }
            "get_uta_loan_data" => self.get_private(UTA_LOAN_DATA, Vec::new()).await,
            "get_uta_collateral_type" => self.get_private(UTA_COLLATERAL_TYPE, Vec::new()).await,
            "get_uta_custom_collateral_coins" => {
                self.get_private(UTA_CUSTOM_COLLATERAL_COINS, Vec::new())
                    .await
            }
            "get_uta_pre_set_leverage" => {
                params.required("category")?;
                params.required("marginMode")?;
                let mut query = params.only(&[
                    "category",
                    "coin",
                    "marginMode",
                    "leverage",
                    "longLeverage",
                    "shortLeverage",
                ]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_PRE_SET_LEVERAGE, query).await
            }
            "set_uta_leverage" => {
                params.required("category")?;
                params.required("leverage")?;
                let mut body = params.body(&[
                    "category",
                    "leverage",
                    "coin",
                    "posSide",
                    "marginMode",
                    "longLeverage",
                    "shortLeverage",
                ]);
                self.insert_uta_symbol(&mut body, params)?;
                self.post_private(UTA_SET_LEVERAGE, Value::Object(body))
                    .await
            }
            "set_uta_hold_mode" => {
                params.required("holdMode")?;
                self.post_private(UTA_SET_HOLD_MODE, Value::Object(params.body(&["holdMode"])))
                    .await
            }
            "get_futures_account" => {
                params.required("productType")?;
                params.required("marginCoin")?;
                let mut query = params.only(&["productType", "marginCoin"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_ACCOUNT, query).await
            }
            "get_futures_accounts" => {
                params.required("productType")?;
                self.get_private(FUTURES_ACCOUNTS, params.only(&["productType"]))
                    .await
            }
            "get_futures_account_bills" => {
                params.required("productType")?;
                self.get_private(
                    FUTURES_ACCOUNT_BILLS,
                    params.only(&[
                        "productType",
                        "coin",
                        "businessType",
                        "onlyFunding",
                        "idLessThan",
                        "startTime",
                        "endTime",
                        "limit",
                    ]),
                )
                .await
            }
            "set_futures_leverage" => {
                params.required("productType")?;
                params.required("marginCoin")?;
                require_one_identifier(params, &["leverage", "longLeverage", "shortLeverage"])?;
                let mut body = params.body(&[
                    "productType",
                    "marginCoin",
                    "leverage",
                    "longLeverage",
                    "shortLeverage",
                    "holdSide",
                ]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(FUTURES_SET_LEVERAGE, Value::Object(body))
                    .await
            }
            "set_futures_margin_mode" => {
                params.required("productType")?;
                params.required("marginCoin")?;
                params.required("marginMode")?;
                let mut body = params.body(&["productType", "marginCoin", "marginMode"]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(FUTURES_SET_MARGIN_MODE, Value::Object(body))
                    .await
            }
            "set_futures_position_mode" => {
                params.required("productType")?;
                params.required("posMode")?;
                self.post_private(
                    FUTURES_SET_POSITION_MODE,
                    Value::Object(params.body(&["productType", "posMode"])),
                )
                .await
            }
            "get_futures_positions" => {
                params.required("productType")?;
                self.get_private(
                    FUTURES_ALL_POSITIONS,
                    params.only(&["productType", "marginCoin"]),
                )
                .await
            }
            "get_futures_position" => {
                params.required("productType")?;
                params.required("marginCoin")?;
                let mut query = params.only(&["productType", "marginCoin"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_SINGLE_POSITION, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
