use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::{insert_optional_value, require_one_identifier, BitgetParams};

const HISTORY_FIELDS: &[&str] = &[
    "orderId",
    "loanCoin",
    "pledgeCoin",
    "startTime",
    "endTime",
    "pageNum",
    "pageSize",
];

impl BitgetClient {
    pub(super) async fn loan_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_crypto_loan_coins" => {
                self.get_private(CRYPTO_LOAN_COINS, params.only(&["coin"]))
                    .await
            }
            "get_crypto_loan_interest" => {
                for key in ["loanCoin", "pledgeCoin", "daily", "pledgeAmount"] {
                    params.required(key)?;
                }
                self.get_private(
                    CRYPTO_LOAN_INTEREST,
                    params.only(&["loanCoin", "pledgeCoin", "daily", "pledgeAmount"]),
                )
                .await
            }
            "borrow_crypto_loan" => {
                for key in ["loanCoin", "pledgeCoin", "daily"] {
                    params.required(key)?;
                }
                require_one_identifier(params, &["pledgeAmount", "loanAmount"])?;
                if params.get("pledgeAmount").is_some() && params.get("loanAmount").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Specify only pledgeAmount or loanAmount.".to_string(),
                    ));
                }
                self.post_private(
                    CRYPTO_LOAN_BORROW,
                    Value::Object(params.body(&[
                        "loanCoin",
                        "pledgeCoin",
                        "daily",
                        "pledgeAmount",
                        "loanAmount",
                    ])),
                )
                .await
            }
            "get_crypto_loan_ongoing" => {
                self.get_private(
                    CRYPTO_LOAN_BORROW_ONGOING,
                    params.only(&["orderId", "loanCoin", "pledgeCoin"]),
                )
                .await
            }
            "get_crypto_loan_borrow_history" => {
                params.required("startTime")?;
                params.required("endTime")?;
                let mut fields = HISTORY_FIELDS.to_vec();
                fields.push("status");
                self.get_private(CRYPTO_LOAN_BORROW_HISTORY, params.only(&fields))
                    .await
            }
            "repay_crypto_loan" => {
                params.required("orderId")?;
                let repay_all = params.required("repayAll")?;
                if !["yes", "no"].contains(&repay_all) {
                    return Err(DcexError::InvalidInput(
                        "repayAll must be yes or no.".to_string(),
                    ));
                }
                if repay_all == "no" {
                    params.required("amount")?;
                }
                self.post_private(
                    CRYPTO_LOAN_REPAY,
                    Value::Object(params.body(&["orderId", "repayAll", "amount", "repayUnlock"])),
                )
                .await
            }
            "get_crypto_loan_repay_history" => {
                params.required("startTime")?;
                params.required("endTime")?;
                self.get_private(CRYPTO_LOAN_REPAY_HISTORY, params.only(HISTORY_FIELDS))
                    .await
            }
            "revise_crypto_loan_pledge" => {
                for key in ["orderId", "amount", "pledgeCoin", "reviseType"] {
                    params.required(key)?;
                }
                self.post_private(
                    CRYPTO_LOAN_REVISE_PLEDGE,
                    Value::Object(params.body(&["orderId", "amount", "pledgeCoin", "reviseType"])),
                )
                .await
            }
            "get_crypto_loan_pledge_history" => {
                params.required("startTime")?;
                params.required("endTime")?;
                self.get_private(
                    CRYPTO_LOAN_PLEDGE_RATE_HISTORY,
                    params.only(&[
                        "orderId",
                        "reviseSide",
                        "pledgeCoin",
                        "startTime",
                        "endTime",
                        "pageNum",
                        "pageSize",
                    ]),
                )
                .await
            }
            "get_crypto_loan_liquidations" => {
                params.required("startTime")?;
                params.required("endTime")?;
                let mut fields = HISTORY_FIELDS.to_vec();
                fields.push("status");
                self.get_private(CRYPTO_LOAN_REDUCES, params.only(&fields))
                    .await
            }
            "get_crypto_loan_debts" => self.get_private(CRYPTO_LOAN_DEBTS, Vec::new()).await,
            "repay_uta_liability" => {
                let mut body = serde_json::Map::new();
                insert_optional_value(
                    &mut body,
                    "repayableCoinList",
                    Some(params.json_required("repayableCoinList")?),
                );
                insert_optional_value(
                    &mut body,
                    "paymentCoinList",
                    Some(params.json_required("paymentCoinList")?),
                );
                self.post_private(UTA_REPAY, Value::Object(body)).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
