use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BackpackClient;
use super::endpoints::*;
use super::params::BackpackParams;

impl BackpackClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_account" => self.private_get(ACCOUNT, Vec::new(), "accountQuery").await,
            "get_max_borrow_quantity" => {
                self.private_get(
                    MAX_BORROW_QUANTITY,
                    params.only(&["symbol"]),
                    "maxBorrowQuantity",
                )
                .await
            }
            "get_max_order_quantity" => {
                self.private_get(
                    MAX_ORDER_QUANTITY,
                    params.only(&[
                        "symbol",
                        "side",
                        "price",
                        "reduceOnly",
                        "autoBorrow",
                        "autoBorrowRepay",
                        "autoLendRedeem",
                    ]),
                    "maxOrderQuantity",
                )
                .await
            }
            "get_max_withdrawal_quantity" => {
                self.private_get(
                    MAX_WITHDRAWAL_QUANTITY,
                    params.only(&["symbol", "autoBorrow", "autoLendRedeem"]),
                    "maxWithdrawalQuantity",
                )
                .await
            }
            "get_borrow_lend_positions" => {
                self.private_get(BORROW_LEND_POSITIONS, Vec::new(), "borrowLendPositionQuery")
                    .await
            }
            "get_borrow_history" => {
                self.private_get(
                    BORROW_HISTORY,
                    params.only(&["symbol", "side", "limit", "offset", "sortDirection"]),
                    "borrowHistoryQueryAll",
                )
                .await
            }
            "get_interest_history" => {
                self.private_get(
                    INTEREST_HISTORY,
                    params.only(&["symbol", "limit", "offset", "sortDirection"]),
                    "interestHistoryQueryAll",
                )
                .await
            }
            "get_borrow_position_history" => {
                self.private_get(
                    BORROW_POSITION_HISTORY,
                    params.only(&[
                        "symbol",
                        "side",
                        "state",
                        "limit",
                        "offset",
                        "sortDirection",
                    ]),
                    "borrowPositionHistoryQueryAll",
                )
                .await
            }
            "get_balances" => self.private_get(BALANCES, Vec::new(), "balanceQuery").await,
            "convert_dust" => {
                self.private_post_value(
                    CONVERT_DUST,
                    Value::Object(params.body(&["symbol"], &[], &[])),
                    "convertDust",
                )
                .await
            }
            "get_private_collateral" => {
                self.private_get(PRIVATE_COLLATERAL, Vec::new(), "collateralQuery")
                    .await
            }
            "get_deposits" => {
                self.private_get(
                    DEPOSITS,
                    params.only(&["from", "to", "limit", "offset", "excludePlatform"]),
                    "depositQueryAll",
                )
                .await
            }
            "get_deposit_address" => {
                self.private_get(
                    DEPOSIT_ADDRESS,
                    params.only(&["blockchain"]),
                    "depositAddressQuery",
                )
                .await
            }
            "get_withdrawals" => {
                self.private_get(
                    WITHDRAWALS,
                    params.only(&["id", "clientId", "from", "to", "limit", "offset"]),
                    "withdrawalQueryAll",
                )
                .await
            }
            "get_dust_conversion_history" => {
                self.private_get(
                    DUST_CONVERSION_HISTORY,
                    params.only(&["id", "symbol", "limit", "offset", "sortDirection"]),
                    "dustHistoryQueryAll",
                )
                .await
            }
            "get_settlement_history" => {
                self.private_get(
                    SETTLEMENT_HISTORY,
                    params.only(&["limit", "offset", "source", "sortDirection"]),
                    "settlementHistoryQueryAll",
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }
}
