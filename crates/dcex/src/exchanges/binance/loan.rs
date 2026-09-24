use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    fn loan_request(
        &self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, method_name, params)
    }

    pub fn check_flexible_loan_collateral_repay_rate(
        &self,
        loan_coin: &str,
        collateral_coin: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request(
            "check_flexible_loan_collateral_repay_rate",
            vec![
                ("loanCoin".to_string(), loan_coin.to_string()),
                ("collateralCoin".to_string(), collateral_coin.to_string()),
            ],
        )
    }

    pub fn adjust_flexible_loan_ltv(
        &self,
        loan_coin: &str,
        collateral_coin: &str,
        adjustment_amount: &str,
        direction: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request(
            "adjust_flexible_loan_ltv",
            vec![
                ("loanCoin".to_string(), loan_coin.to_string()),
                ("collateralCoin".to_string(), collateral_coin.to_string()),
                (
                    "adjustmentAmount".to_string(),
                    adjustment_amount.to_string(),
                ),
                ("direction".to_string(), direction.to_string()),
            ],
        )
    }

    pub fn borrow_flexible_loan(
        &self,
        loan_coin: &str,
        collateral_coin: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request(
            "borrow_flexible_loan",
            vec![
                ("loanCoin".to_string(), loan_coin.to_string()),
                ("collateralCoin".to_string(), collateral_coin.to_string()),
            ],
        )
    }

    pub fn repay_flexible_loan(
        &self,
        loan_coin: &str,
        collateral_coin: &str,
        repay_amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request(
            "repay_flexible_loan",
            vec![
                ("loanCoin".to_string(), loan_coin.to_string()),
                ("collateralCoin".to_string(), collateral_coin.to_string()),
                ("repayAmount".to_string(), repay_amount.to_string()),
            ],
        )
    }

    pub fn get_flexible_loan_assets(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_assets", Vec::new())
    }

    pub fn get_flexible_loan_borrow_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_borrow_history", Vec::new())
    }

    pub fn get_flexible_loan_collateral_assets(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_collateral_assets", Vec::new())
    }

    pub fn get_flexible_loan_interest_rate_history(
        &self,
        coin: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request(
            "get_flexible_loan_interest_rate_history",
            vec![("coin".to_string(), coin.to_string())],
        )
    }

    pub fn get_flexible_loan_liquidation_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_liquidation_history", Vec::new())
    }

    pub fn get_flexible_loan_ltv_adjustment_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_ltv_adjustment_history", Vec::new())
    }

    pub fn get_flexible_loan_ongoing_orders(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_ongoing_orders", Vec::new())
    }

    pub fn get_flexible_loan_repayment_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_flexible_loan_repayment_history", Vec::new())
    }

    pub fn get_crypto_loan_income_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_crypto_loan_income_history", Vec::new())
    }

    pub fn get_stable_loan_borrow_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_stable_loan_borrow_history", Vec::new())
    }

    pub fn get_stable_loan_ltv_adjustment_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_stable_loan_ltv_adjustment_history", Vec::new())
    }

    pub fn get_stable_loan_repayment_history(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.loan_request("get_stable_loan_repayment_history", Vec::new())
    }

    pub(super) async fn loan_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path) = match method_name {
            "check_flexible_loan_collateral_repay_rate" => {
                params.required("loanCoin")?;
                params.required("collateralCoin")?;
                (HttpMethod::Get, FLEXIBLE_LOAN_COLLATERAL_REPAY_RATE)
            }
            "adjust_flexible_loan_ltv" => {
                params.required("loanCoin")?;
                params.required("collateralCoin")?;
                params.required("adjustmentAmount")?;
                let direction = params.required("direction")?.to_ascii_uppercase();
                if !matches!(direction.as_str(), "ADDITIONAL" | "REDUCED") {
                    return Err(DcexError::InvalidInput(
                        "Binance flexible loan direction must be ADDITIONAL or REDUCED."
                            .to_string(),
                    ));
                }
                (HttpMethod::Post, FLEXIBLE_LOAN_ADJUST_LTV)
            }
            "borrow_flexible_loan" => {
                params.required("loanCoin")?;
                params.required("collateralCoin")?;
                if params.get("loanAmount").is_none() && params.get("collateralAmount").is_none() {
                    return Err(DcexError::InvalidInput(
                        "Binance flexible loan borrowing requires loanAmount or collateralAmount."
                            .to_string(),
                    ));
                }
                (HttpMethod::Post, FLEXIBLE_LOAN_BORROW)
            }
            "repay_flexible_loan" => {
                params.required("loanCoin")?;
                params.required("collateralCoin")?;
                params.required("repayAmount")?;
                (HttpMethod::Post, FLEXIBLE_LOAN_REPAY)
            }
            "get_flexible_loan_assets" => (HttpMethod::Get, FLEXIBLE_LOAN_ASSETS),
            "get_flexible_loan_borrow_history" => (HttpMethod::Get, FLEXIBLE_LOAN_BORROW_HISTORY),
            "get_flexible_loan_collateral_assets" => {
                (HttpMethod::Get, FLEXIBLE_LOAN_COLLATERAL_ASSETS)
            }
            "get_flexible_loan_interest_rate_history" => {
                params.required("coin")?;
                (HttpMethod::Get, FLEXIBLE_LOAN_INTEREST_RATE_HISTORY)
            }
            "get_flexible_loan_liquidation_history" => {
                (HttpMethod::Get, FLEXIBLE_LOAN_LIQUIDATION_HISTORY)
            }
            "get_flexible_loan_ltv_adjustment_history" => {
                (HttpMethod::Get, FLEXIBLE_LOAN_LTV_ADJUSTMENT_HISTORY)
            }
            "get_flexible_loan_ongoing_orders" => (HttpMethod::Get, FLEXIBLE_LOAN_ONGOING_ORDERS),
            "get_flexible_loan_repayment_history" => {
                (HttpMethod::Get, FLEXIBLE_LOAN_REPAYMENT_HISTORY)
            }
            "get_crypto_loan_income_history" => (HttpMethod::Get, CRYPTO_LOAN_INCOME_HISTORY),
            "get_stable_loan_borrow_history" => (HttpMethod::Get, STABLE_LOAN_BORROW_HISTORY),
            "get_stable_loan_ltv_adjustment_history" => {
                (HttpMethod::Get, STABLE_LOAN_LTV_ADJUSTMENT_HISTORY)
            }
            "get_stable_loan_repayment_history" => (HttpMethod::Get, STABLE_LOAN_REPAYMENT_HISTORY),
            _ => return Ok(None),
        };

        Ok(Some(
            self.request(method, BinanceMarket::Spot, path, params.without(&[]), true)
                .await?,
        ))
    }
}
