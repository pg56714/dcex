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
        if !matches!(
            method_name,
            "get_account"
                | "get_max_borrow_quantity"
                | "get_max_order_quantity"
                | "get_max_withdrawal_quantity"
                | "get_borrow_lend_positions"
                | "get_borrow_history"
                | "get_interest_history"
                | "get_borrow_position_history"
                | "get_balances"
                | "convert_dust"
                | "get_private_collateral"
                | "get_deposits"
                | "get_deposit_address"
                | "get_withdrawals"
                | "get_dust_conversion_history"
                | "get_settlement_history"
        ) {
            return Ok(None);
        }
        self.validate_account_params(method_name, params)?;
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
                    params.only(&[
                        "type",
                        "sources",
                        "positionId",
                        "symbol",
                        "limit",
                        "offset",
                        "sortDirection",
                    ]),
                    "borrowHistoryQueryAll",
                )
                .await
            }
            "get_interest_history" => {
                self.private_get(
                    INTEREST_HISTORY,
                    params.only(&[
                        "asset",
                        "symbol",
                        "positionId",
                        "limit",
                        "offset",
                        "source",
                        "sortDirection",
                    ]),
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

    fn validate_account_params(&self, method_name: &str, params: &BackpackParams) -> Result<()> {
        match method_name {
            "get_account"
            | "get_borrow_lend_positions"
            | "get_balances"
            | "get_private_collateral" => params.ensure_allowed(&[], &[]),
            "get_max_borrow_quantity" | "convert_dust" => {
                params.ensure_allowed(&["symbol"], &[])?;
                params.required("symbol")?;
                Ok(())
            }
            "get_max_order_quantity" => {
                params.ensure_allowed(
                    &[
                        "symbol",
                        "side",
                        "price",
                        "reduceOnly",
                        "autoBorrow",
                        "autoBorrowRepay",
                        "autoLendRedeem",
                    ],
                    &[],
                )?;
                params.required("symbol")?;
                params.required("side")?;
                params.optional_one_of("side", &["Bid", "Ask"])?;
                validate_optional_bools(
                    params,
                    &[
                        "reduceOnly",
                        "autoBorrow",
                        "autoBorrowRepay",
                        "autoLendRedeem",
                    ],
                )
            }
            "get_max_withdrawal_quantity" => {
                params.ensure_allowed(&["symbol", "autoBorrow", "autoLendRedeem"], &[])?;
                params.required("symbol")?;
                validate_optional_bools(params, &["autoBorrow", "autoLendRedeem"])
            }
            "get_borrow_history" => {
                params.ensure_allowed(
                    &[
                        "type",
                        "sources",
                        "positionId",
                        "symbol",
                        "limit",
                        "offset",
                        "sortDirection",
                    ],
                    &[],
                )?;
                params.optional_one_of("type", &["Borrow", "BorrowRepay", "Lend", "LendRedeem"])?;
                validate_history_pagination(params)
            }
            "get_interest_history" => {
                params.ensure_allowed(
                    &[
                        "asset",
                        "symbol",
                        "positionId",
                        "limit",
                        "offset",
                        "source",
                        "sortDirection",
                    ],
                    &[],
                )?;
                params.optional_one_of("source", &["UnrealizedPnl", "BorrowLend"])?;
                validate_history_pagination(params)
            }
            "get_borrow_position_history" => {
                params.ensure_allowed(
                    &[
                        "symbol",
                        "side",
                        "state",
                        "limit",
                        "offset",
                        "sortDirection",
                    ],
                    &[],
                )?;
                params.optional_one_of("side", &["Borrow", "Lend"])?;
                params.optional_one_of("state", &["Open", "Closed"])?;
                validate_history_pagination(params)
            }
            "get_deposits" => {
                params
                    .ensure_allowed(&["from", "to", "limit", "offset", "excludePlatform"], &[])?;
                params.ensure_time_order("from", "to")?;
                params.optional_bool("excludePlatform")?;
                validate_history_pagination(params)
            }
            "get_deposit_address" => {
                params.ensure_allowed(&["blockchain"], &[])?;
                params.required("blockchain")?;
                Ok(())
            }
            "get_withdrawals" => {
                params.ensure_allowed(&["id", "clientId", "from", "to", "limit", "offset"], &[])?;
                params.optional_i64_range("id", i32::MIN.into(), i32::MAX.into())?;
                params.ensure_time_order("from", "to")?;
                validate_history_pagination(params)
            }
            "get_dust_conversion_history" => {
                params
                    .ensure_allowed(&["id", "symbol", "limit", "offset", "sortDirection"], &[])?;
                params.optional_i64("id")?;
                validate_history_pagination(params)
            }
            "get_settlement_history" => {
                params.ensure_allowed(&["limit", "offset", "source", "sortDirection"], &[])?;
                params.optional_one_of(
                    "source",
                    &[
                        "BackstopLiquidation",
                        "FundingPayment",
                        "RealizePnl",
                        "TradingFees",
                        "TradingFeesSystem",
                    ],
                )?;
                validate_history_pagination(params)
            }
            _ => Ok(()),
        }
    }
}

fn validate_optional_bools(params: &BackpackParams, keys: &[&str]) -> Result<()> {
    for key in keys {
        params.optional_bool(key)?;
    }
    Ok(())
}

fn validate_history_pagination(params: &BackpackParams) -> Result<()> {
    params.optional_u64_range("limit", 1, 1_000)?;
    params.optional_u64_range("offset", 0, u64::MAX)?;
    params.optional_one_of("sortDirection", &["Asc", "Desc"])
}
