use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BackpackClient;
use super::endpoints::*;
use super::params::{
    insert_optional_integer, insert_optional_string, insert_required_string, BackpackParams,
};

impl BackpackClient {
    pub fn get_rfqs(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_rfqs", Vec::new())
    }

    pub fn submit_rfq(
        &self,
        product_symbol: &str,
        side: &str,
        execution_mode: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "submit_rfq",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("side".to_string(), side.to_string()),
                ("executionMode".to_string(), execution_mode.to_string()),
            ],
        )
    }

    pub fn accept_rfq_quote(
        &self,
        rfq_id: &str,
        quote_id: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "accept_rfq_quote",
            vec![
                ("rfqId".to_string(), rfq_id.to_string()),
                ("quoteId".to_string(), quote_id.to_string()),
            ],
        )
    }

    pub fn refresh_rfq(&self, rfq_id: &str) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "refresh_rfq",
            vec![("rfqId".to_string(), rfq_id.to_string())],
        )
    }

    pub fn cancel_rfq(&self, rfq_id: &str) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_rfq",
            vec![("rfqId".to_string(), rfq_id.to_string())],
        )
    }

    pub fn get_rfq_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_rfq_history", Vec::new())
    }

    pub fn get_quote_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_quote_history", Vec::new())
    }

    pub fn get_rfq_fill_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_rfq_fill_history", Vec::new())
    }

    pub fn get_quote_fill_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_quote_fill_history", Vec::new())
    }

    pub(super) async fn rfq_private_request(
        &self,
        method_name: &str,
        params: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_rfqs" => {
                validate_get_rfqs(params)?;
                let mut query = params.only(&["rfqId", "deferredSettlement"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(RFQS, query, "rfqQuery").await
            }
            "submit_rfq" => {
                self.validate_submit_rfq(params)?;
                self.private_post_value(
                    RFQ,
                    Value::Object(self.rfq_submit_body(params)?),
                    "rfqSubmit",
                )
                .await
            }
            "accept_rfq_quote" => {
                validate_accept_rfq(params)?;
                let mut body = Map::new();
                insert_optional_string(&mut body, "rfqId", params.get("rfqId"));
                insert_optional_integer(&mut body, "clientId", params.get("clientId"));
                insert_required_string(&mut body, "quoteId", params.required("quoteId")?);
                self.private_post_value(RFQ_ACCEPT, Value::Object(body), "quoteAccept")
                    .await
            }
            "refresh_rfq" => {
                params.ensure_allowed(&["rfqId"], &[])?;
                let mut body = Map::new();
                insert_required_string(&mut body, "rfqId", params.required("rfqId")?);
                self.private_post_value(RFQ_REFRESH, Value::Object(body), "rfqRefresh")
                    .await
            }
            "cancel_rfq" => {
                params.ensure_allowed(&["rfqId", "clientId"], &[])?;
                params.ensure_exactly_one(&["rfqId", "clientId"])?;
                params.optional_u64_range("clientId", 0, u32::MAX.into())?;
                let mut body = Map::new();
                insert_optional_string(&mut body, "rfqId", params.get("rfqId"));
                insert_optional_integer(&mut body, "clientId", params.get("clientId"));
                self.private_post_value(RFQ_CANCEL, Value::Object(body), "rfqCancel")
                    .await
            }
            "get_rfq_history" => {
                validate_rfq_history(params)?;
                let mut query = params.only(&[
                    "rfqId",
                    "status",
                    "side",
                    "limit",
                    "offset",
                    "sortDirection",
                    "deferredSettlement",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(RFQ_HISTORY, query, "rfqHistoryQueryAll")
                    .await
            }
            "get_quote_history" => {
                validate_quote_history(params)?;
                let mut query = params.only(&[
                    "quoteId",
                    "status",
                    "limit",
                    "offset",
                    "sortDirection",
                    "deferredSettlement",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(QUOTE_HISTORY, query, "quoteHistoryQueryAll")
                    .await
            }
            "get_rfq_fill_history" => {
                validate_rfq_fill_history(params)?;
                let mut query = params.only(&[
                    "rfqId",
                    "quoteId",
                    "side",
                    "fillType",
                    "deferredSettlement",
                    "limit",
                    "offset",
                    "sortDirection",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(RFQ_FILL_HISTORY, query, "rfqFillHistoryQueryAll")
                    .await
            }
            "get_quote_fill_history" => {
                validate_quote_fill_history(params)?;
                let mut query =
                    params.only(&["quoteId", "side", "limit", "offset", "sortDirection"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(QUOTE_FILL_HISTORY, query, "quoteFillHistoryQueryAll")
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    fn validate_submit_rfq(&self, params: &BackpackParams) -> Result<()> {
        params.ensure_allowed(
            &[
                "product_symbol",
                "symbol",
                "clientId",
                "quantity",
                "quoteQuantity",
                "price",
                "side",
                "executionMode",
                "autoLend",
                "autoLendRedeem",
                "autoBorrow",
                "autoBorrowRepay",
            ],
            &[],
        )?;
        super::market::validate_symbol_selector(params, true)?;
        params.ensure_exactly_one(&["quantity", "quoteQuantity"])?;
        params.required("side")?;
        params.required("executionMode")?;
        params.optional_one_of("side", &["Bid", "Ask"])?;
        params.optional_one_of("executionMode", &["AwaitAccept", "Immediate"])?;
        params.optional_u64_range("clientId", 0, u32::MAX.into())?;
        for key in [
            "autoLend",
            "autoLendRedeem",
            "autoBorrow",
            "autoBorrowRepay",
        ] {
            params.optional_bool(key)?;
        }
        if params.get("price").is_some() && params.get("executionMode") != Some("Immediate") {
            return Err(DcexError::InvalidInput(
                "Backpack RFQ price is supported only with executionMode=Immediate.".to_string(),
            ));
        }
        if params.get("quoteQuantity").is_some() {
            let symbol = params.required_any(&["product_symbol", "symbol"])?;
            if symbol.contains(".US") && symbol.ends_with("RFQ") {
                return Err(DcexError::InvalidInput(
                    "Backpack stock RFQs require quantity; quoteQuantity is not supported."
                        .to_string(),
                ));
            }
        }
        Ok(())
    }

    pub(super) fn rfq_submit_body(&self, params: &BackpackParams) -> Result<Map<String, Value>> {
        let mut body = params.body(
            &[
                "quantity",
                "quoteQuantity",
                "price",
                "side",
                "executionMode",
            ],
            &["clientId"],
            &[
                "autoLend",
                "autoLendRedeem",
                "autoBorrow",
                "autoBorrowRepay",
            ],
        );
        let product_symbol = params.required_any(&["product_symbol", "symbol"])?;
        insert_required_string(&mut body, "symbol", &self.exchange_symbol(product_symbol)?);
        Ok(body)
    }
}

fn validate_get_rfqs(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(
        &["product_symbol", "symbol", "rfqId", "deferredSettlement"],
        &[],
    )?;
    super::market::validate_symbol_selector(params, false)?;
    params.optional_bool("deferredSettlement")
}

fn validate_accept_rfq(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(&["rfqId", "clientId", "quoteId"], &[])?;
    params.ensure_exactly_one(&["rfqId", "clientId"])?;
    params.required("quoteId")?;
    params.optional_u64_range("clientId", 0, u32::MAX.into())
}

fn validate_rfq_history(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(
        &[
            "product_symbol",
            "symbol",
            "rfqId",
            "status",
            "side",
            "limit",
            "offset",
            "sortDirection",
            "deferredSettlement",
        ],
        &[],
    )?;
    validate_history_common(params)?;
    params.optional_one_of("side", &["Bid", "Ask"])
}

fn validate_quote_history(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(
        &[
            "product_symbol",
            "symbol",
            "quoteId",
            "status",
            "limit",
            "offset",
            "sortDirection",
            "deferredSettlement",
        ],
        &[],
    )?;
    validate_history_common(params)
}

fn validate_rfq_fill_history(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(
        &[
            "product_symbol",
            "symbol",
            "rfqId",
            "quoteId",
            "side",
            "fillType",
            "deferredSettlement",
            "limit",
            "offset",
            "sortDirection",
        ],
        &[],
    )?;
    validate_history_common(params)?;
    params.optional_one_of("side", &["Bid", "Ask"])?;
    params.optional_one_of("fillType", &["User", "CollateralConversion"])
}

fn validate_quote_fill_history(params: &BackpackParams) -> Result<()> {
    params.ensure_allowed(
        &[
            "product_symbol",
            "symbol",
            "quoteId",
            "side",
            "limit",
            "offset",
            "sortDirection",
        ],
        &[],
    )?;
    validate_history_common(params)?;
    params.optional_one_of("side", &["Bid", "Ask"])
}

fn validate_history_common(params: &BackpackParams) -> Result<()> {
    super::market::validate_symbol_selector(params, false)?;
    params.optional_u64_range("limit", 1, 1_000)?;
    params.optional_u64_range("offset", 0, u64::MAX)?;
    params.optional_one_of("sortDirection", &["Asc", "Desc"])?;
    params.optional_bool("deferredSettlement")
}
