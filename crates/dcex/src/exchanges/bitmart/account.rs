use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::{BitmartClient, BitmartMarket};
use super::endpoints::*;
use super::params::{boolean_or_string, BitmartParams};

impl BitmartClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BitmartParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_spot_fee_rates" | "get_futures_fee_rates" => {
                let (market, path, spot) = match method_name {
                    "get_spot_fee_rates" => (BitmartMarket::Spot, SPOT_TRADE_FEE, true),
                    "get_futures_fee_rates" => {
                        (BitmartMarket::Futures, FUTURES_TRADE_FEE_RATE, false)
                    }
                    _ => unreachable!(),
                };
                let product_symbol = params.required("product_symbol")?;
                self.get_private(
                    market,
                    path,
                    vec![(
                        "symbol".to_string(),
                        self.exchange_symbol(product_symbol, spot)?,
                    )],
                )
                .await
            }
            "get_account_balance" => {
                let mut query = Vec::new();
                query.push((
                    "needUsdValuation".to_string(),
                    params
                        .get("needUsdValuation")
                        .map(|value| match boolean_or_string(value) {
                            serde_json::Value::Bool(value) => value.to_string(),
                            _ => value.to_string(),
                        })
                        .unwrap_or_else(|| "false".to_string()),
                ));
                if let Some(currency) = params.get("currency") {
                    query.push(("currency".to_string(), currency.to_string()));
                }
                self.get_private(BitmartMarket::Spot, ACCOUNT_BALANCE, query)
                    .await
            }
            "get_account_currencies" => {
                self.get_private(
                    BitmartMarket::Spot,
                    ACCOUNT_CURRENCIES,
                    params.only(&["currencies"]),
                )
                .await
            }
            "get_spot_wallet" => {
                self.get_private(BitmartMarket::Spot, SPOT_WALLET, Vec::new())
                    .await
            }
            "get_deposit_address" => {
                self.get_private(
                    BitmartMarket::Spot,
                    DEPOSIT_ADDRESS,
                    vec![(
                        "currency".to_string(),
                        params.required("currency")?.to_string(),
                    )],
                )
                .await
            }
            "get_contract_assets" => {
                self.get_private(BitmartMarket::Futures, FUTURES_CONTRACT_ASSETS, Vec::new())
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
