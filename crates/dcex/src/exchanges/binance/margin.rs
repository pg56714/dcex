use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{PublicParams, normalize_order_side};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub fn get_all_margin_assets(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_all_margin_assets", Vec::new())
    }

    pub fn get_all_cross_margin_pairs(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_all_cross_margin_pairs",
            Vec::new(),
        )
    }

    pub fn get_all_isolated_margin_symbols(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_all_isolated_margin_symbols",
            Vec::new(),
        )
    }

    pub fn get_margin_price_index(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_price_index",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_cross_margin_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_cross_margin_account",
            Vec::new(),
        )
    }

    pub fn get_isolated_margin_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_isolated_margin_account",
            Vec::new(),
        )
    }

    pub fn margin_borrow_repay(
        &self,
        asset: &str,
        amount: &str,
        transaction_type: &str,
        is_isolated: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "margin_borrow_repay",
            vec![
                ("asset".to_string(), asset.to_string()),
                ("amount".to_string(), amount.to_string()),
                ("type".to_string(), transaction_type.to_string()),
                (
                    "isIsolated".to_string(),
                    if is_isolated { "TRUE" } else { "FALSE" }.to_string(),
                ),
            ],
        )
    }

    pub fn borrow_margin_asset(
        &self,
        asset: &str,
        amount: &str,
        is_isolated: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.margin_borrow_repay(asset, amount, "BORROW", is_isolated)
    }

    pub fn repay_margin_asset(
        &self,
        asset: &str,
        amount: &str,
        is_isolated: bool,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        self.margin_borrow_repay(asset, amount, "REPAY", is_isolated)
    }

    pub fn get_margin_borrow_repay_records(
        &self,
        transaction_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_borrow_repay_records",
            vec![("type".to_string(), transaction_type.to_string())],
        )
    }

    pub fn get_margin_interest_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_interest_history",
            Vec::new(),
        )
    }

    pub fn get_margin_max_borrowable(
        &self,
        asset: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_max_borrowable",
            vec![("asset".to_string(), asset.to_string())],
        )
    }

    pub fn get_margin_max_transferable(
        &self,
        asset: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_max_transferable",
            vec![("asset".to_string(), asset.to_string())],
        )
    }

    pub fn place_margin_order(
        &self,
        product_symbol: &str,
        side: &str,
        order_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_margin_order",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("side".to_string(), side.to_string()),
                ("type".to_string(), order_type.to_string()),
            ],
        )
    }

    pub fn cancel_margin_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_margin_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_margin_order(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_order",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_open_margin_orders(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_open_margin_orders", Vec::new())
    }

    pub fn cancel_all_open_margin_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_all_open_margin_orders",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_all_margin_orders(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_all_margin_orders",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub fn get_margin_account_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_margin_account_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn margin_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_all_margin_assets" => {
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_ALL_ASSETS,
                    params.without(&[]),
                )
                .await?
            }
            "get_all_cross_margin_pairs" => {
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_ALL_PAIRS,
                    params.without(&[]),
                )
                .await?
            }
            "get_all_isolated_margin_symbols" => {
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_ALL_ISOLATED_SYMBOLS,
                    params.without(&[]),
                )
                .await?
            }
            "get_margin_price_index" => {
                self.api_key_request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_PRICE_INDEX,
                    self.margin_symbol_params(params, false)?,
                )
                .await?
            }
            "get_cross_margin_account" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_CROSS_ACCOUNT, params, false)
                    .await?
            }
            "get_isolated_margin_account" => {
                let mut query = params.without(&["product_symbols"]);
                if let Some(symbols) = params.get("product_symbols") {
                    query.push(("symbols".to_string(), self.margin_symbols(symbols)?));
                }
                self.request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_ISOLATED_ACCOUNT,
                    query,
                    true,
                )
                .await?
            }
            "margin_borrow_repay" => {
                params.required("asset")?;
                params.required("amount")?;
                let transaction_type = params.required("type")?.to_ascii_uppercase();
                if !matches!(transaction_type.as_str(), "BORROW" | "REPAY") {
                    return Err(DcexError::InvalidInput(
                        "Binance margin borrow/repay type must be BORROW or REPAY.".to_string(),
                    ));
                }
                let mut query = self.margin_symbol_params(params, false)?;
                set_param(&mut query, "type", transaction_type);
                set_param(
                    &mut query,
                    "isIsolated",
                    normalize_isolated(params.get("isIsolated"))?,
                );
                self.request(
                    HttpMethod::Post,
                    BinanceMarket::Spot,
                    MARGIN_BORROW_REPAY,
                    query,
                    true,
                )
                .await?
            }
            "get_margin_borrow_repay_records" => {
                let transaction_type = params.required("type")?.to_ascii_uppercase();
                if !matches!(transaction_type.as_str(), "BORROW" | "REPAY") {
                    return Err(DcexError::InvalidInput(
                        "Binance margin record type must be BORROW or REPAY.".to_string(),
                    ));
                }
                let mut query = self.margin_symbol_params(params, false)?;
                set_param(&mut query, "type", transaction_type);
                self.request(
                    HttpMethod::Get,
                    BinanceMarket::Spot,
                    MARGIN_BORROW_REPAY,
                    query,
                    true,
                )
                .await?
            }
            "get_margin_interest_history" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_INTEREST_HISTORY, params, false)
                    .await?
            }
            "get_margin_max_borrowable" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_MAX_BORROWABLE, params, false)
                    .await?
            }
            "get_margin_max_transferable" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_MAX_TRANSFERABLE, params, false)
                    .await?
            }
            "place_margin_order" => {
                let mut query = self.margin_symbol_params(params, true)?;
                let order_type = params.required("type")?.to_ascii_uppercase();
                set_param(
                    &mut query,
                    "side",
                    normalize_order_side(params.required("side")?)?,
                );
                set_param(&mut query, "type", order_type);
                if let Some(side_effect_type) = params.get("sideEffectType") {
                    let side_effect_type = side_effect_type.to_ascii_uppercase();
                    if !matches!(
                        side_effect_type.as_str(),
                        "NO_SIDE_EFFECT" | "MARGIN_BUY" | "AUTO_REPAY" | "AUTO_BORROW_REPAY"
                    ) {
                        return Err(DcexError::InvalidInput(
                            "unsupported Binance margin sideEffectType.".to_string(),
                        ));
                    }
                    set_param(&mut query, "sideEffectType", side_effect_type);
                }
                self.request(
                    HttpMethod::Post,
                    BinanceMarket::Spot,
                    MARGIN_ORDER,
                    query,
                    true,
                )
                .await?
            }
            "cancel_margin_order" => {
                require_order_identifier(params)?;
                self.margin_signed_request(HttpMethod::Delete, MARGIN_ORDER, params, true)
                    .await?
            }
            "get_margin_order" => {
                require_order_identifier(params)?;
                self.margin_signed_request(HttpMethod::Get, MARGIN_ORDER, params, true)
                    .await?
            }
            "get_open_margin_orders" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_OPEN_ORDERS, params, false)
                    .await?
            }
            "cancel_all_open_margin_orders" => {
                self.margin_signed_request(HttpMethod::Delete, MARGIN_OPEN_ORDERS, params, true)
                    .await?
            }
            "get_all_margin_orders" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_ALL_ORDERS, params, true)
                    .await?
            }
            "get_margin_account_trades" => {
                self.margin_signed_request(HttpMethod::Get, MARGIN_ACCOUNT_TRADES, params, true)
                    .await?
            }
            _ => return Ok(None),
        };
        Ok(Some(response))
    }

    async fn margin_signed_request(
        &self,
        method: HttpMethod,
        path: &str,
        params: &PublicParams,
        require_symbol: bool,
    ) -> Result<ValidatedResponse> {
        self.request(
            method,
            BinanceMarket::Spot,
            path,
            self.margin_symbol_params(params, require_symbol)?,
            true,
        )
        .await
    }

    fn margin_symbol_params(
        &self,
        params: &PublicParams,
        require_symbol: bool,
    ) -> Result<Vec<(String, String)>> {
        let product_symbol = params.get("product_symbol");
        if require_symbol && product_symbol.is_none() {
            return Err(DcexError::InvalidInput(
                "Binance margin product_symbol is required.".to_string(),
            ));
        }
        let mut query = params.without(&["product_symbol"]);
        if let Some(symbol) = product_symbol {
            query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        }
        if let Some(isolated_symbol) = params.get("isolatedSymbol") {
            set_param(
                &mut query,
                "isolatedSymbol",
                self.exchange_symbol(isolated_symbol)?,
            );
        }
        if params.get("isIsolated").is_some() {
            set_param(
                &mut query,
                "isIsolated",
                normalize_isolated(params.get("isIsolated"))?,
            );
        }
        Ok(query)
    }

    fn margin_symbols(&self, symbols: &str) -> Result<String> {
        symbols
            .split(',')
            .map(|symbol| self.exchange_symbol(symbol.trim()))
            .collect::<Result<Vec<_>>>()
            .map(|items| items.join(","))
    }
}

fn normalize_isolated(value: Option<&str>) -> Result<String> {
    match value.unwrap_or("FALSE").to_ascii_uppercase().as_str() {
        "TRUE" | "1" => Ok("TRUE".to_string()),
        "FALSE" | "0" => Ok("FALSE".to_string()),
        _ => Err(DcexError::InvalidInput(
            "Binance isIsolated must be true or false.".to_string(),
        )),
    }
}

fn set_param(params: &mut Vec<(String, String)>, key: &str, value: String) {
    params.retain(|(name, _)| name != key);
    params.push((key.to_string(), value));
}

fn require_order_identifier(params: &PublicParams) -> Result<()> {
    if params.get("orderId").is_none() && params.get("origClientOrderId").is_none() {
        return Err(DcexError::InvalidInput(
            "Binance margin orderId or origClientOrderId is required.".to_string(),
        ));
    }
    Ok(())
}
