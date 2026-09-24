use super::client::{BinanceClient, BinanceMarket};
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

const EXCHANGE_INFO: &str = "/sapi/v1/convert/exchangeInfo";
const ASSET_INFO: &str = "/sapi/v1/convert/assetInfo";
const GET_QUOTE: &str = "/sapi/v1/convert/getQuote";
const ACCEPT_QUOTE: &str = "/sapi/v1/convert/acceptQuote";
const ORDER_STATUS: &str = "/sapi/v1/convert/orderStatus";
const TRADE_FLOW: &str = "/sapi/v1/convert/tradeFlow";
const PLACE_LIMIT: &str = "/sapi/v1/convert/limit/placeOrder";
const CANCEL_LIMIT: &str = "/sapi/v1/convert/limit/cancelOrder";
const OPEN_LIMIT: &str = "/sapi/v1/convert/limit/queryOpenOrders";

fn exactly_one(params: &PublicParams, first: &str, second: &str) -> Result<()> {
    if params.get(first).is_some() == params.get(second).is_some() {
        return Err(DcexError::InvalidInput(format!(
            "exactly one of {first} or {second} is required"
        )));
    }
    Ok(())
}

fn positive_amount(params: &PublicParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !value
            .parse::<f64>()
            .is_ok_and(|amount| amount.is_finite() && amount > 0.0)
        {
            return Err(DcexError::InvalidInput(format!(
                "Binance {key} must be a positive finite amount"
            )));
        }
    }
    Ok(())
}

impl BinanceClient {
    pub fn get_convert_pairs(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_convert_pairs", Vec::new())
    }

    pub fn get_convert_asset_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_convert_asset_info", Vec::new())
    }

    pub fn get_convert_quote(
        &self,
        from_asset: &str,
        to_asset: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_convert_quote",
            vec![
                ("fromAsset".into(), from_asset.into()),
                ("toAsset".into(), to_asset.into()),
            ],
        )
    }

    pub fn accept_convert_quote(
        &self,
        quote_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "accept_convert_quote",
            vec![("quoteId".into(), quote_id.into())],
        )
    }

    pub fn get_convert_order_status(
        &self,
        order_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_convert_order_status",
            vec![("orderId".into(), order_id.into())],
        )
    }

    pub fn get_convert_trade_history(
        &self,
        start_time: u64,
        end_time: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_convert_trade_history",
            vec![
                ("startTime".into(), start_time.to_string()),
                ("endTime".into(), end_time.to_string()),
            ],
        )
    }

    pub fn place_convert_limit_order(
        &self,
        base_asset: &str,
        quote_asset: &str,
        limit_price: &str,
        side: &str,
        expired_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_convert_limit_order",
            vec![
                ("baseAsset".into(), base_asset.into()),
                ("quoteAsset".into(), quote_asset.into()),
                ("limitPrice".into(), limit_price.into()),
                ("side".into(), side.into()),
                ("expiredType".into(), expired_type.into()),
            ],
        )
    }

    pub fn cancel_convert_limit_order(
        &self,
        order_id: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_convert_limit_order",
            vec![("orderId".into(), order_id.to_string())],
        )
    }

    pub fn get_open_convert_limit_orders(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_open_convert_limit_orders",
            Vec::new(),
        )
    }

    pub(super) async fn convert_public_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        if name != "get_convert_pairs" {
            return Ok(None);
        }
        params.ensure_allowed(&["fromAsset", "toAsset"])?;
        if params.get("fromAsset").is_none() && params.get("toAsset").is_none() {
            return Err(DcexError::InvalidInput(
                "Binance Convert requires fromAsset or toAsset".into(),
            ));
        }
        Ok(Some(
            self.request(
                HttpMethod::Get,
                BinanceMarket::Spot,
                EXCHANGE_INFO,
                params.0.clone(),
                false,
            )
            .await?,
        ))
    }

    pub(super) async fn convert_private_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path, allowed): (HttpMethod, &str, &[&str]) = match name {
            "get_convert_asset_info" => (HttpMethod::Get, ASSET_INFO, &["recvWindow"]),
            "get_convert_quote" => (
                HttpMethod::Post,
                GET_QUOTE,
                &[
                    "fromAsset",
                    "toAsset",
                    "fromAmount",
                    "toAmount",
                    "walletType",
                    "validTime",
                    "recvWindow",
                ],
            ),
            "accept_convert_quote" => (HttpMethod::Post, ACCEPT_QUOTE, &["quoteId", "recvWindow"]),
            "get_convert_order_status" => (
                HttpMethod::Get,
                ORDER_STATUS,
                &["orderId", "quoteId", "recvWindow"],
            ),
            "get_convert_trade_history" => (
                HttpMethod::Get,
                TRADE_FLOW,
                &["startTime", "endTime", "limit", "recvWindow"],
            ),
            "place_convert_limit_order" => (
                HttpMethod::Post,
                PLACE_LIMIT,
                &[
                    "baseAsset",
                    "quoteAsset",
                    "limitPrice",
                    "side",
                    "expiredType",
                    "baseAmount",
                    "quoteAmount",
                    "walletType",
                    "recvWindow",
                ],
            ),
            "cancel_convert_limit_order" => {
                (HttpMethod::Post, CANCEL_LIMIT, &["orderId", "recvWindow"])
            }
            "get_open_convert_limit_orders" => (HttpMethod::Get, OPEN_LIMIT, &["recvWindow"]),
            _ => return Ok(None),
        };
        params.ensure_allowed(allowed)?;
        params.optional_u64_range("recvWindow", 1, 60_000)?;
        match name {
            "get_convert_quote" => {
                params.required("fromAsset")?;
                params.required("toAsset")?;
                exactly_one(params, "fromAmount", "toAmount")?;
                positive_amount(params, "fromAmount")?;
                positive_amount(params, "toAmount")?;
                params.optional_one_of(
                    "walletType",
                    &[
                        "SPOT",
                        "FUNDING",
                        "EARN",
                        "SPOT_FUNDING",
                        "FUNDING_EARN",
                        "SPOT_FUNDING_EARN",
                        "SPOT_EARN",
                    ],
                )?;
                params.optional_one_of("validTime", &["10s", "30s", "1m"])?;
            }
            "accept_convert_quote" => {
                params.required("quoteId")?;
            }
            "get_convert_order_status" => {
                if params.get("orderId").is_none() && params.get("quoteId").is_none() {
                    return Err(DcexError::InvalidInput(
                        "orderId or quoteId is required".into(),
                    ));
                }
            }
            "get_convert_trade_history" => {
                let start = params
                    .u64("startTime")?
                    .ok_or_else(|| DcexError::InvalidInput("startTime is required".into()))?;
                let end = params
                    .u64("endTime")?
                    .ok_or_else(|| DcexError::InvalidInput("endTime is required".into()))?;
                if end < start || end - start > 30 * 24 * 60 * 60 * 1000 {
                    return Err(DcexError::InvalidInput(
                        "Binance Convert history range must be at most 30 days".into(),
                    ));
                }
                params.optional_u64_range("limit", 1, 1000)?;
            }
            "place_convert_limit_order" => {
                for key in [
                    "baseAsset",
                    "quoteAsset",
                    "limitPrice",
                    "side",
                    "expiredType",
                ] {
                    params.required(key)?;
                }
                positive_amount(params, "limitPrice")?;
                exactly_one(params, "baseAmount", "quoteAmount")?;
                positive_amount(params, "baseAmount")?;
                positive_amount(params, "quoteAmount")?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                params.optional_one_of("expiredType", &["1_D", "3_D", "7_D", "30_D"])?;
                params.optional_one_of(
                    "walletType",
                    &[
                        "SPOT",
                        "FUNDING",
                        "EARN",
                        "SPOT_FUNDING",
                        "FUNDING_EARN",
                        "SPOT_FUNDING_EARN",
                        "SPOT_EARN",
                    ],
                )?;
            }
            "cancel_convert_limit_order" => {
                params
                    .required("orderId")?
                    .parse::<u64>()
                    .map_err(|_| DcexError::InvalidInput("orderId must be an integer".into()))?;
            }
            _ => {}
        }
        Ok(Some(
            self.request(method, BinanceMarket::Spot, path, params.0.clone(), true)
                .await?,
        ))
    }
}
