use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::BitgetParams;

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
                self.get_private(
                    SPOT_ACCOUNT_TRANSFER_COIN_INFO,
                    params.only(&["fromType", "toType"]),
                )
                .await
            }
            "get_deposit_records" => {
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
            "set_uta_leverage" => {
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
                self.post_private(UTA_SET_HOLD_MODE, Value::Object(params.body(&["holdMode"])))
                    .await
            }
            "get_futures_account" => {
                let mut query = params.only(&["productType", "marginCoin"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_ACCOUNT, query).await
            }
            "get_futures_accounts" => {
                self.get_private(FUTURES_ACCOUNTS, params.only(&["productType"]))
                    .await
            }
            "get_futures_account_bills" => {
                self.get_private(
                    FUTURES_ACCOUNT_BILLS,
                    params.only(&[
                        "productType",
                        "symbol",
                        "marginCoin",
                        "startTime",
                        "endTime",
                        "lastEndId",
                        "limit",
                    ]),
                )
                .await
            }
            "set_futures_leverage" => {
                let mut body = params.body(&["productType", "marginCoin", "leverage", "holdSide"]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(FUTURES_SET_LEVERAGE, Value::Object(body))
                    .await
            }
            "set_futures_margin_mode" => {
                let mut body = params.body(&["productType", "marginCoin", "marginMode"]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(FUTURES_SET_MARGIN_MODE, Value::Object(body))
                    .await
            }
            "set_futures_position_mode" => {
                self.post_private(
                    FUTURES_SET_POSITION_MODE,
                    Value::Object(params.body(&["productType", "posMode"])),
                )
                .await
            }
            "get_futures_positions" => {
                self.get_private(
                    FUTURES_ALL_POSITIONS,
                    params.only(&["productType", "marginCoin"]),
                )
                .await
            }
            "get_futures_position" => {
                let mut query = params.only(&["productType", "marginCoin"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_SINGLE_POSITION, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
