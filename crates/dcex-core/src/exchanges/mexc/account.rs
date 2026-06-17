use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::endpoints::*;
use super::params::{insert_number, MexcParams};

impl MexcClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &MexcParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_kyc_status" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_KYC_STATUS,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "get_spot_self_symbols" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_SELF_SYMBOLS,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "get_spot_account" => {
                self.spot_private(HttpMethod::Get, SPOT_ACCOUNT, params.only(&["recvWindow"]))
                    .await
            }
            "get_spot_mx_deduct_status" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_MX_DEDUCT_ENABLE,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "set_spot_mx_deduct" => {
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_MX_DEDUCT_ENABLE,
                    params.only(&["mxDeductEnable", "recvWindow"]),
                )
                .await
            }
            "get_spot_symbol_commission" => {
                let mut query = params.only(&["recvWindow"]);
                self.push_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_SYMBOL_COMMISSION, query)
                    .await
            }
            "get_currency_info" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_CURRENCY_INFO,
                    params.only(&["coin", "network", "recvWindow"]),
                )
                .await
            }
            "get_deposit_history" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_DEPOSIT_HISTORY,
                    params.only(&[
                        "coin",
                        "status",
                        "startTime",
                        "endTime",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_withdraw_history" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_WITHDRAW_HISTORY,
                    params.only(&[
                        "coin",
                        "status",
                        "startTime",
                        "endTime",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_deposit_address" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_DEPOSIT_ADDRESS,
                    params.only(&["coin", "network", "recvWindow"]),
                )
                .await
            }
            "user_universal_transfer" => {
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "asset",
                        "amount",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_user_universal_transfer_history" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "startTime",
                        "endTime",
                        "page",
                        "size",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_user_universal_transfer_by_id" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER_BY_ID,
                    params.only(&["tranId", "recvWindow"]),
                )
                .await
            }
            "get_internal_transfer_history" => {
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_INTERNAL_TRANSFER_HISTORY,
                    params.only(&[
                        "tranId",
                        "clientTranId",
                        "startTime",
                        "endTime",
                        "page",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_contract_assets" => self.contract_get(CONTRACT_ASSETS, Vec::new()).await,
            "get_contract_asset" => {
                let path = CONTRACT_ASSET.replace("{currency}", params.required("currency")?);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_transfer_records" => {
                self.contract_get(
                    CONTRACT_TRANSFER_RECORDS,
                    params.only(&["currency", "state", "page_num", "page_size"]),
                )
                .await
            }
            "get_contract_history_positions" => {
                let mut query = params.only(&["type", "page_num", "page_size"]);
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_HISTORY_POSITIONS, query).await
            }
            "get_contract_open_positions" => {
                let mut query = Vec::new();
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_OPEN_POSITIONS, query).await
            }
            "get_contract_funding_records" => {
                let mut query = params.only(&["position_id", "page_num", "page_size"]);
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_FUNDING_RECORDS, query).await
            }
            "get_contract_risk_limits" => {
                let mut query = Vec::new();
                self.push_required_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_RISK_LIMITS, query).await
            }
            "get_contract_trading_fee_rate" => {
                let mut query = Vec::new();
                self.push_required_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_TRADING_FEE_RATE, query).await
            }
            "get_contract_leverage" => {
                let mut query = Vec::new();
                self.push_required_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_LEVERAGE, query).await
            }
            "change_contract_margin" => {
                let body = params.body(&["positionId", "amount", "type"], &["positionId"], &[]);
                self.contract_post_json(CONTRACT_CHANGE_MARGIN, Value::Object(body))
                    .await
            }
            "change_contract_leverage" => {
                let mut body = params.body(
                    &["positionId", "leverage", "openType", "positionType"],
                    &["positionId", "leverage", "openType", "positionType"],
                    &[],
                );
                self.insert_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CHANGE_LEVERAGE, Value::Object(body))
                    .await
            }
            "get_contract_position_mode" => {
                self.contract_get(CONTRACT_POSITION_MODE, Vec::new()).await
            }
            "change_contract_position_mode" => {
                let mut body = serde_json::Map::new();
                let position_mode = params.required("positionMode")?.parse().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid positionMode: {error}"))
                })?;
                insert_number(&mut body, "positionMode", position_mode);
                self.contract_post_json(CONTRACT_CHANGE_POSITION_MODE, Value::Object(body))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
