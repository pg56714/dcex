use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::AsterParams;

impl AsterClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_spot_account" => {
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_ACCOUNT, Vec::new())
                    .await
            }
            "get_spot_transaction_history" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Spot,
                    SPOT_TRANSACTION_HISTORY,
                    params.only(&["asset", "type", "startTime", "endTime", "limit"]),
                )
                .await
            }
            "transfer_spot_futures" => {
                let market = params.get("market").unwrap_or("spot").to_ascii_lowercase();
                let (market, path) = match market.as_str() {
                    "spot" => (AsterMarket::Spot, SPOT_TRANSFER),
                    "futures" => (AsterMarket::Futures, FUTURES_TRANSFER),
                    _ => unreachable!("validated Aster transfer market"),
                };
                self.signed(
                    HttpMethod::Post,
                    market,
                    path,
                    params.only(&["amount", "asset", "clientTranId", "kindType"]),
                )
                .await
            }
            "get_futures_position_mode" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_POSITION_MODE,
                    Vec::new(),
                )
                .await
            }
            "set_futures_position_mode" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_POSITION_MODE,
                    params.only(&["dualSidePosition"]),
                )
                .await
            }
            "get_futures_stp_mode" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_STP_MODE,
                    Vec::new(),
                )
                .await
            }
            "set_futures_stp_mode" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_STP_MODE,
                    params.only(&["stpMode"]),
                )
                .await
            }
            "get_futures_multi_assets_mode" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_MULTI_ASSETS_MODE,
                    Vec::new(),
                )
                .await
            }
            "set_futures_multi_assets_mode" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_MULTI_ASSETS_MODE,
                    params.only(&["multiAssetsMargin"]),
                )
                .await
            }
            "get_futures_balance" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_BALANCE,
                    Vec::new(),
                )
                .await
            }
            "get_futures_account" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_ACCOUNT,
                    Vec::new(),
                )
                .await
            }
            "modify_futures_position_margin" => {
                let mut query = params.only(&["positionSide", "amount", "type"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_POSITION_MARGIN,
                    query,
                )
                .await
            }
            "get_futures_position_margin_history" => {
                let mut query = params.only(&["type", "startTime", "endTime", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_POSITION_MARGIN_HISTORY,
                    query,
                )
                .await
            }
            "get_futures_position_risk" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_POSITION_RISK,
                    query,
                )
                .await
            }
            "get_futures_user_trades" => {
                let mut query = params.only(&["startTime", "endTime", "fromId", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_USER_TRADES,
                    query,
                )
                .await
            }
            "get_futures_income" => {
                let mut query = params.only(&["incomeType", "startTime", "endTime", "limit"]);
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Futures, FUTURES_INCOME, query)
                    .await
            }
            "get_futures_leverage_bracket" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_LEVERAGE_BRACKET,
                    query,
                )
                .await
            }
            "get_futures_adl_quantile" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_ADL_QUANTILE,
                    query,
                )
                .await
            }
            "get_futures_force_orders" => {
                let mut query = params.only(&["autoCloseType", "startTime", "endTime", "limit"]);
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_FORCE_ORDERS,
                    query,
                )
                .await
            }
            "get_spot_commission_rate" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Spot,
                    SPOT_COMMISSION_RATE,
                    query,
                )
                .await
            }
            "get_futures_commission_rate" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_COMMISSION_RATE,
                    query,
                )
                .await
            }
            "update_futures_mmp" => {
                let mut query = params.only(&[
                    "windowTimeInMilliseconds",
                    "frozenTimeInMilliseconds",
                    "qtyLimit",
                    "valueLimit",
                    "deltaLimit",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Futures, FUTURES_MMP, query)
                    .await
            }
            "get_futures_mmp" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Futures, FUTURES_MMP, query)
                    .await
            }
            "delete_futures_mmp" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Delete, AsterMarket::Futures, FUTURES_MMP, query)
                    .await
            }
            "reset_futures_mmp" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_MMP_RESET,
                    query,
                )
                .await
            }
            "create_spot_listen_key" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Spot,
                    SPOT_LISTEN_KEY,
                    Vec::new(),
                )
                .await
            }
            "keep_alive_spot_listen_key" => {
                self.signed(
                    HttpMethod::Put,
                    AsterMarket::Spot,
                    SPOT_LISTEN_KEY,
                    params.only(&["listenKey"]),
                )
                .await
            }
            "close_spot_listen_key" => {
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Spot,
                    SPOT_LISTEN_KEY,
                    params.only(&["listenKey"]),
                )
                .await
            }
            "create_futures_listen_key" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_LISTEN_KEY,
                    Vec::new(),
                )
                .await
            }
            "keep_alive_futures_listen_key" => {
                self.signed(
                    HttpMethod::Put,
                    AsterMarket::Futures,
                    FUTURES_LISTEN_KEY,
                    Vec::new(),
                )
                .await
            }
            "close_futures_listen_key" => {
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_LISTEN_KEY,
                    Vec::new(),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    pub(super) async fn signed(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(method, market, path, params, true).await
    }

    pub(super) fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &AsterParams,
    ) -> Result<()> {
        let symbol = params.required_any(&["product_symbol", "symbol"])?;
        query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        Ok(())
    }

    pub(super) fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &AsterParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get_any(&["product_symbol", "symbol"]) {
            query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        }
        Ok(())
    }
}
