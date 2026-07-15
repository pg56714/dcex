use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{push_optional, BingxParams};

impl BingxClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BingxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_account_balance" | "get_swap_account_balance" => {
                self.private_get(SWAP_ACCOUNT_BALANCE, Vec::new()).await
            }
            "get_spot_account_balance" => {
                self.private_get(SPOT_ACCOUNT_BALANCE, params.only(&["recvWindow"]))
                    .await
            }
            "get_fund_account_balance" => {
                self.private_get(FUND_ACCOUNT_BALANCE, params.only(&["asset", "recvWindow"]))
                    .await
            }
            "get_all_account_balance" => {
                self.private_get(
                    FUND_ALL_ACCOUNT_BALANCE,
                    params.only(&["accountType", "recvWindow"]),
                )
                .await
            }
            "get_account_uid" => {
                self.private_get(FUND_ACCOUNT_UID, params.only(&["recvWindow"]))
                    .await
            }
            "get_api_key_info" => {
                self.private_get(
                    FUND_API_KEY_INFO,
                    params.only(&["uid", "apiKey", "recvWindow"]),
                )
                .await
            }
            "get_transferable_coins" => {
                self.private_get(
                    TRANSFERABLE_COINS,
                    params.only(&["fromAccount", "toAccount", "recvWindow"]),
                )
                .await
            }
            "asset_transfer" => {
                self.private_post(
                    ASSET_TRANSFER,
                    params.only(&["fromAccount", "toAccount", "asset", "amount", "recvWindow"]),
                )
                .await
            }
            "get_asset_transfer_records" => {
                self.private_get(
                    TRANSFER_RECORDS,
                    params.only(&[
                        "fromAccount",
                        "toAccount",
                        "tranId",
                        "startTime",
                        "endTime",
                        "pageIndex",
                        "pageSize",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_open_positions" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_OPEN_POSITIONS, query).await
            }
            "get_fund_flow" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                push_optional(&mut query, "incomeType", params.get("income_type"));
                push_optional(&mut query, "startTime", params.get("start_time"));
                push_optional(&mut query, "endTime", params.get("end_time"));
                push_optional(&mut query, "limit", params.get("limit"));
                self.private_get(SWAP_FUND_FLOW, query).await
            }
            "get_listen_key" => {
                self.unsigned_post_with_api_key(SWAP_LISTEN_KEY, Vec::new())
                    .await
            }
            "keep_alive_listen_key" => {
                self.private_put(
                    SWAP_LISTEN_KEY,
                    vec![(
                        "listenKey".to_string(),
                        params.required("listen_key")?.to_string(),
                    )],
                )
                .await
            }
            "close_listen_key" => {
                self.private_delete(
                    SWAP_LISTEN_KEY,
                    vec![(
                        "listenKey".to_string(),
                        params.required("listen_key")?.to_string(),
                    )],
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
