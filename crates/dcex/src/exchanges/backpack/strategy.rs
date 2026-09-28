//! Scheduled strategies, signed with the dedicated Strategy instructions.
use super::{BackpackClient, params::BackpackParams};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};
use serde_json::Value;

const CREATE: &[&str] = &[
    "product_symbol",
    "symbol",
    "strategyType",
    "side",
    "quantity",
    "price",
    "clientStrategyId",
    "duration",
    "interval",
    "randomizedIntervalQuantity",
    "timeInForce",
    "postOnly",
    "reduceOnly",
    "selfTradePrevention",
    "slippageTolerance",
    "slippageToleranceType",
    "autoLend",
    "autoLendRedeem",
    "autoBorrow",
    "autoBorrowRepay",
];
const BOOLS: &[&str] = &[
    "randomizedIntervalQuantity",
    "postOnly",
    "reduceOnly",
    "autoLend",
    "autoLendRedeem",
    "autoBorrow",
    "autoBorrowRepay",
];
const INTEGERS: &[&str] = &["clientStrategyId", "duration", "interval"];
const MARKET_TYPES: &[&str] = &["SPOT", "PERP", "IPERP", "DATED", "PREDICTION", "RFQ"];

impl BackpackClient {
    pub(super) async fn strategy_private_request(
        &self,
        method: &str,
        params: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, instruction, verb, fields): (&str, &str, &str, &[&str]) = match method {
            "create_strategy" => ("/api/v1/strategy", "strategyCreate", "POST", CREATE),
            "get_open_strategy" => (
                "/api/v1/strategy",
                "strategyQuery",
                "GET",
                &["product_symbol", "symbol", "strategyId", "clientStrategyId"],
            ),
            "cancel_strategy" => (
                "/api/v1/strategy",
                "strategyCancel",
                "DELETE",
                &["product_symbol", "symbol", "strategyId", "clientStrategyId"],
            ),
            "get_open_strategies" => (
                "/api/v1/strategies",
                "strategyQueryAll",
                "GET",
                &["product_symbol", "symbol", "marketType", "strategyType"],
            ),
            "cancel_open_strategies" => (
                "/api/v1/strategies",
                "strategyCancelAll",
                "DELETE",
                &["product_symbol", "symbol", "strategyType"],
            ),
            "get_strategy_history" => (
                "/wapi/v1/history/strategies",
                "strategyHistoryQueryAll",
                "GET",
                &[
                    "product_symbol",
                    "symbol",
                    "strategyId",
                    "limit",
                    "offset",
                    "marketType",
                    "sortDirection",
                ],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(
            fields,
            if method == "get_strategy_history" {
                &["marketType"]
            } else {
                &[]
            },
        )?;
        params.optional_u64_range("clientStrategyId", 0, u32::MAX as u64)?;
        params.optional_u64_range("duration", 1, u64::MAX)?;
        params.optional_u64_range("interval", 1, u64::MAX)?;
        params.optional_u64_range("limit", 1, 1000)?;
        params.optional_u64_range("offset", 0, u64::MAX)?;
        params.values_one_of("marketType", MARKET_TYPES)?;
        params.optional_one_of("sortDirection", &["Asc", "Desc"])?;
        params.optional_one_of("strategyType", &["Scheduled"])?;
        params.optional_one_of("side", &["Bid", "Ask"])?;
        params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK"])?;
        params.optional_one_of(
            "selfTradePrevention",
            &["RejectTaker", "RejectMaker", "RejectBoth"],
        )?;
        params.optional_one_of("slippageToleranceType", &["TickSize", "Percent"])?;
        for key in BOOLS {
            params.optional_bool(key)?;
        }
        for key in ["quantity", "price", "slippageTolerance"] {
            if let Some(v) = params.get(key)
                && !crate::common::is_positive_plain_decimal(v)
            {
                return Err(invalid(
                    "quantity, price and slippageTolerance must be positive decimals",
                ));
            }
        }
        if method == "create_strategy" {
            params.required("strategyType")?;
            params.required("side")?;
            if let (Some(duration), Some(interval)) =
                (params.get("duration"), params.get("interval"))
            {
                let duration = duration.parse::<u64>().expect("validated duration");
                let interval = interval.parse::<u64>().expect("validated interval");
                if duration % interval != 0 {
                    return Err(invalid("duration must be a multiple of interval"));
                }
            }
            if params.bool("postOnly") == Some(true)
                && params.get("timeInForce").is_some_and(|v| v != "GTC")
            {
                return Err(invalid("postOnly requires GTC"));
            }
        }
        if matches!(method, "get_open_strategy" | "cancel_strategy") {
            params.ensure_exactly_one(&["strategyId", "clientStrategyId"])?;
        }
        let symbol = if matches!(
            method,
            "create_strategy" | "get_open_strategy" | "cancel_strategy"
        ) {
            Some(self.exchange_symbol(params.required_any(&["product_symbol", "symbol"])?)?)
        } else {
            params
                .get_any(&["product_symbol", "symbol"])
                .map(|s| self.exchange_symbol(s))
                .transpose()?
        };
        let result = if verb == "GET" {
            let mut query = params.only(
                &fields
                    .iter()
                    .copied()
                    .filter(|k| !matches!(*k, "product_symbol" | "symbol"))
                    .collect::<Vec<_>>(),
            );
            if let Some(symbol) = symbol {
                query.push(("symbol".into(), symbol));
            }
            self.private_get(path, query, instruction).await
        } else {
            let strings: Vec<_> = fields
                .iter()
                .copied()
                .filter(|k| {
                    !BOOLS.contains(k)
                        && !INTEGERS.contains(k)
                        && !matches!(*k, "product_symbol" | "symbol")
                })
                .collect();
            let mut body = params.body(&strings, &[], BOOLS);
            for key in INTEGERS {
                if let Some(v) = params.get(key) {
                    body.insert(
                        (*key).into(),
                        Value::from(v.parse::<u64>().expect("validated integer")),
                    );
                }
            }
            if let Some(symbol) = symbol {
                body.insert("symbol".into(), symbol.into());
            }
            if verb == "POST" {
                self.private_post_value(path, Value::Object(body), instruction)
                    .await
            } else {
                self.private_delete_value(path, Value::Object(body), instruction)
                    .await
            }
        };
        result.map(Some)
    }
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Backpack strategy: {message}"))
}
