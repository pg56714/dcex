use std::future::{Future, IntoFuture};
use std::pin::Pin;

use crate::exchange::ValidatedResponse;
use crate::Result;

pub type ExchangeMethodFuture<'a> =
    Pin<Box<dyn Future<Output = Result<ValidatedResponse>> + Send + 'a>>;

pub trait ExchangeMethodRequestClient {
    fn public_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> ExchangeMethodFuture<'a>;

    fn private_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> ExchangeMethodFuture<'a>;
}

impl<T> ExchangeMethodRequestClient for &T
where
    T: ExchangeMethodRequestClient + Sync + ?Sized,
{
    fn public_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> ExchangeMethodFuture<'a> {
        (*self).public_request_boxed(method_name, params)
    }

    fn private_request_boxed<'a>(
        &'a self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> ExchangeMethodFuture<'a> {
        (*self).private_request_boxed(method_name, params)
    }
}

pub struct ExchangeMethodRequest<'a, C: ExchangeMethodRequestClient> {
    client: &'a C,
    method_name: &'static str,
    params: Vec<(String, String)>,
    signed: bool,
}

impl<'a, C: ExchangeMethodRequestClient> ExchangeMethodRequest<'a, C> {
    pub(crate) fn public(
        client: &'a C,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> Self {
        Self {
            client,
            method_name,
            params,
            signed: false,
        }
    }

    pub(crate) fn private(
        client: &'a C,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> Self {
        Self {
            client,
            method_name,
            params,
            signed: true,
        }
    }

    pub fn param(mut self, key: impl Into<String>, value: impl ToString) -> Self {
        let key = key.into();
        let value = value.to_string();
        if let Some((_, existing_value)) = self
            .params
            .iter_mut()
            .find(|(existing_key, _)| existing_key == &key)
        {
            *existing_value = value;
        } else {
            self.params.push((key, value));
        }
        self
    }

    pub fn push_param(mut self, key: impl Into<String>, value: impl ToString) -> Self {
        self.params.push((key.into(), value.to_string()));
        self
    }

    // BEGIN GENERATED OPTIONAL PARAM SETTERS
    pub fn account(self, value: impl ToString) -> Self {
        self.param("account", value)
    }

    pub fn account_index(self, value: impl ToString) -> Self {
        self.param("account_index", value)
    }

    pub fn account_type(self, value: impl ToString) -> Self {
        self.param("accountType", value)
    }

    pub fn aclass(self, value: impl ToString) -> Self {
        self.param("aclass", value)
    }

    pub fn action_mode(self, value: impl ToString) -> Self {
        self.param("action_mode", value)
    }

    pub fn activate_price(self, value: impl ToString) -> Self {
        self.param("activatePrice", value)
    }

    pub fn activation_price(self, value: impl ToString) -> Self {
        self.param("activationPrice", value)
    }

    pub fn active_only(self, value: impl ToString) -> Self {
        self.param("active_only", value)
    }

    pub fn after(self, value: impl ToString) -> Self {
        self.param("after", value)
    }

    pub fn aggregate(self, value: impl ToString) -> Self {
        self.param("aggregate", value)
    }

    pub fn aggregate_by_time(self, value: impl ToString) -> Self {
        self.param("aggregateByTime", value)
    }

    pub fn algo_id(self, value: impl ToString) -> Self {
        self.param("algoId", value)
    }

    pub fn algo_type(self, value: impl ToString) -> Self {
        self.param("algoType", value)
    }

    pub fn allow_max_time_window(self, value: impl ToString) -> Self {
        self.param("allowMaxTimeWindow", value)
    }

    pub fn amend_text(self, value: impl ToString) -> Self {
        self.param("amend_text", value)
    }

    pub fn amount(self, value: impl ToString) -> Self {
        self.param("amount", value)
    }

    pub fn api_key(self, value: impl ToString) -> Self {
        self.param("apiKey", value)
    }

    pub fn api_key_index(self, value: impl ToString) -> Self {
        self.param("api_key_index", value)
    }

    pub fn ask_filter(self, value: impl ToString) -> Self {
        self.param("ask_filter", value)
    }

    pub fn asset(self, value: impl ToString) -> Self {
        self.param("asset", value)
    }

    pub fn asset_id(self, value: impl ToString) -> Self {
        self.param("asset_id", value)
    }

    pub fn asset_type(self, value: impl ToString) -> Self {
        self.param("assetType", value)
    }

    pub fn at_timestamp(self, value: impl ToString) -> Self {
        self.param("at_timestamp", value)
    }

    pub fn auth(self, value: impl ToString) -> Self {
        self.param("auth", value)
    }

    pub fn authorization(self, value: impl ToString) -> Self {
        self.param("authorization", value)
    }

    pub fn auto_borrow_repay(self, value: impl ToString) -> Self {
        self.param("autoBorrowRepay", value)
    }

    pub fn auto_close_type(self, value: impl ToString) -> Self {
        self.param("autoCloseType", value)
    }

    pub fn auto_cxl(self, value: impl ToString) -> Self {
        self.param("autoCxl", value)
    }

    pub fn auto_lend(self, value: impl ToString) -> Self {
        self.param("autoLend", value)
    }

    pub fn auto_lend_redeem(self, value: impl ToString) -> Self {
        self.param("autoLendRedeem", value)
    }

    pub fn auto_repay(self, value: impl ToString) -> Self {
        self.param("auto_repay", value)
    }

    pub fn auto_size(self, value: impl ToString) -> Self {
        self.param("auto_size", value)
    }

    pub fn ban_amend(self, value: impl ToString) -> Self {
        self.param("banAmend", value)
    }

    pub fn bar(self, value: impl ToString) -> Self {
        self.param("bar", value)
    }

    pub fn base_coin(self, value: impl ToString) -> Self {
        self.param("baseCoin", value)
    }

    pub fn batch_mode(self, value: impl ToString) -> Self {
        self.param("batchMode", value)
    }

    pub fn bbo(self, value: impl ToString) -> Self {
        self.param("bbo", value)
    }

    pub fn before(self, value: impl ToString) -> Self {
        self.param("before", value)
    }

    pub fn begin(self, value: impl ToString) -> Self {
        self.param("begin", value)
    }

    pub fn between_timestamps(self, value: impl ToString) -> Self {
        self.param("between_timestamps", value)
    }

    pub fn bin_size(self, value: impl ToString) -> Self {
        self.param("binSize", value)
    }

    pub fn biz_info(self, value: impl ToString) -> Self {
        self.param("biz_info", value)
    }

    pub fn builder_address(self, value: impl ToString) -> Self {
        self.param("builder_address", value)
    }

    pub fn business_type(self, value: impl ToString) -> Self {
        self.param("businessType", value)
    }

    pub fn callback_rate(self, value: impl ToString) -> Self {
        self.param("callbackRate", value)
    }

    pub fn cancel_after(self, value: impl ToString) -> Self {
        self.param("cancelAfter", value)
    }

    pub fn cancel_client_order_id(self, value: impl ToString) -> Self {
        self.param("cancelClientOrderId", value)
    }

    pub fn cancel_order_id(self, value: impl ToString) -> Self {
        self.param("cancelOrderId", value)
    }

    pub fn cancel_restrictions(self, value: impl ToString) -> Self {
        self.param("cancelRestrictions", value)
    }

    pub fn category(self, value: impl ToString) -> Self {
        self.param("category", value)
    }

    pub fn ccy(self, value: impl ToString) -> Self {
        self.param("ccy", value)
    }

    pub fn chain(self, value: impl ToString) -> Self {
        self.param("chain", value)
    }

    pub fn change_type(self, value: impl ToString) -> Self {
        self.param("change_type", value)
    }

    pub fn cl_ord_link_id(self, value: impl ToString) -> Self {
        self.param("clOrdLinkID", value)
    }

    pub fn cl_t_req_id(self, value: impl ToString) -> Self {
        self.param("clTReqId", value)
    }

    pub fn cli_ord_id(self, value: impl ToString) -> Self {
        self.param("cliOrdId", value)
    }

    pub fn cli_ord_ids(self, value: impl ToString) -> Self {
        self.param("cliOrdIds", value)
    }

    pub fn client_algo_id(self, value: impl ToString) -> Self {
        self.param("clientAlgoId", value)
    }

    pub fn client_id(self, value: impl ToString) -> Self {
        self.param("clientId", value)
    }

    pub fn client_oid(self, value: impl ToString) -> Self {
        self.param("clientOid", value)
    }

    pub fn client_order_id_list(self, value: impl ToString) -> Self {
        self.param("clientOrderIdList", value)
    }

    pub fn client_strategy_id(self, value: impl ToString) -> Self {
        self.param("clientStrategyId", value)
    }

    pub fn client_timestamp(self, value: impl ToString) -> Self {
        self.param("clientTimestamp", value)
    }

    pub fn client_tran_id(self, value: impl ToString) -> Self {
        self.param("clientTranId", value)
    }

    pub fn cloid(self, value: impl ToString) -> Self {
        self.param("cloid", value)
    }

    pub fn close(self, value: impl ToString) -> Self {
        self.param("close", value)
    }

    pub fn close_on_trigger(self, value: impl ToString) -> Self {
        self.param("closeOnTrigger", value)
    }

    pub fn close_order(self, value: impl ToString) -> Self {
        self.param("closeOrder", value)
    }

    pub fn close_position(self, value: impl ToString) -> Self {
        self.param("closePosition", value)
    }

    pub fn closetime(self, value: impl ToString) -> Self {
        self.param("closetime", value)
    }

    pub fn code(self, value: impl ToString) -> Self {
        self.param("code", value)
    }

    pub fn coin(self, value: impl ToString) -> Self {
        self.param("coin", value)
    }

    pub fn columns(self, value: impl ToString) -> Self {
        self.param("columns", value)
    }

    pub fn consolidate_taker(self, value: impl ToString) -> Self {
        self.param("consolidate_taker", value)
    }

    pub fn consolidation(self, value: impl ToString) -> Self {
        self.param("consolidation", value)
    }

    pub fn contingency_type(self, value: impl ToString) -> Self {
        self.param("contingencyType", value)
    }

    pub fn contract(self, value: impl ToString) -> Self {
        self.param("contract", value)
    }

    pub fn contract_type(self, value: impl ToString) -> Self {
        self.param("contractType", value)
    }

    pub fn count(self, value: impl ToString) -> Self {
        self.param("count", value)
    }

    pub fn count_total(self, value: impl ToString) -> Self {
        self.param("count_total", value)
    }

    pub fn country(self, value: impl ToString) -> Self {
        self.param("country", value)
    }

    pub fn cross_leverage_limit(self, value: impl ToString) -> Self {
        self.param("cross_leverage_limit", value)
    }

    pub fn ct_type(self, value: impl ToString) -> Self {
        self.param("ctType", value)
    }

    pub fn currencies(self, value: impl ToString) -> Self {
        self.param("currencies", value)
    }

    pub fn currency(self, value: impl ToString) -> Self {
        self.param("currency", value)
    }

    pub fn currency_pair(self, value: impl ToString) -> Self {
        self.param("currency_pair", value)
    }

    pub fn current(self, value: impl ToString) -> Self {
        self.param("current", value)
    }

    pub fn current_page(self, value: impl ToString) -> Self {
        self.param("currentPage", value)
    }

    pub fn cursor(self, value: impl ToString) -> Self {
        self.param("cursor", value)
    }

    pub fn cxl_on_fail(self, value: impl ToString) -> Self {
        self.param("cxlOnFail", value)
    }

    pub fn deadline(self, value: impl ToString) -> Self {
        self.param("deadline", value)
    }

    pub fn delta_limit(self, value: impl ToString) -> Self {
        self.param("deltaLimit", value)
    }

    pub fn dep_id(self, value: impl ToString) -> Self {
        self.param("depId", value)
    }

    pub fn depth(self, value: impl ToString) -> Self {
        self.param("depth", value)
    }

    pub fn dex(self, value: impl ToString) -> Self {
        self.param("dex", value)
    }

    pub fn display_qty(self, value: impl ToString) -> Self {
        self.param("displayQty", value)
    }

    pub fn docalcs(self, value: impl ToString) -> Self {
        self.param("docalcs", value)
    }

    pub fn enabled(self, value: impl ToString) -> Self {
        self.param("enabled", value)
    }

    pub fn end(self, value: impl ToString) -> Self {
        self.param("end", value)
    }

    pub fn end_at(self, value: impl ToString) -> Self {
        self.param("endAt", value)
    }

    pub fn end_timestamp(self, value: impl ToString) -> Self {
        self.param("end_timestamp", value)
    }

    pub fn exclude_platform(self, value: impl ToString) -> Self {
        self.param("excludePlatform", value)
    }

    pub fn exec_inst(self, value: impl ToString) -> Self {
        self.param("execInst", value)
    }

    pub fn expire_after(self, value: impl ToString) -> Self {
        self.param("expireAfter", value)
    }

    pub fn expired(self, value: impl ToString) -> Self {
        self.param("expired", value)
    }

    pub fn expiretm(self, value: impl ToString) -> Self {
        self.param("expiretm", value)
    }

    pub fn external_oid(self, value: impl ToString) -> Self {
        self.param("externalOid", value)
    }

    pub fn fee_info(self, value: impl ToString) -> Self {
        self.param("fee_info", value)
    }

    pub fn fee_ten_bp(self, value: impl ToString) -> Self {
        self.param("fee_ten_bp", value)
    }

    pub fn filter(self, value: impl ToString) -> Self {
        self.param("filter", value)
    }

    pub fn flow_type(self, value: impl ToString) -> Self {
        self.param("flow_type", value)
    }

    pub fn force(self, value: impl ToString) -> Self {
        self.param("force", value)
    }

    pub fn from_(self, value: impl ToString) -> Self {
        self.param("from_", value)
    }

    pub fn from_account(self, value: impl ToString) -> Self {
        self.param("fromAccount", value)
    }

    pub fn from_id(self, value: impl ToString) -> Self {
        self.param("fromId", value)
    }

    pub fn from_symbol(self, value: impl ToString) -> Self {
        self.param("fromSymbol", value)
    }

    pub fn from_time(self, value: impl ToString) -> Self {
        self.param("from_time", value)
    }

    pub fn from_timestamp(self, value: impl ToString) -> Self {
        self.param("from_timestamp", value)
    }

    pub fn from_type(self, value: impl ToString) -> Self {
        self.param("fromType", value)
    }

    pub fn from_user_id(self, value: impl ToString) -> Self {
        self.param("fromUserId", value)
    }

    pub fn from_wd_id(self, value: impl ToString) -> Self {
        self.param("fromWdId", value)
    }

    pub fn funds(self, value: impl ToString) -> Self {
        self.param("funds", value)
    }

    pub fn good_till_date(self, value: impl ToString) -> Self {
        self.param("goodTillDate", value)
    }

    pub fn group_type(self, value: impl ToString) -> Self {
        self.param("groupType", value)
    }

    pub fn grouping(self, value: impl ToString) -> Self {
        self.param("grouping", value)
    }

    pub fn hidden(self, value: impl ToString) -> Self {
        self.param("hidden", value)
    }

    pub fn hold_side(self, value: impl ToString) -> Self {
        self.param("holdSide", value)
    }

    pub fn holding(self, value: impl ToString) -> Self {
        self.param("holding", value)
    }

    pub fn iceberg(self, value: impl ToString) -> Self {
        self.param("iceberg", value)
    }

    pub fn id(self, value: impl ToString) -> Self {
        self.param("id", value)
    }

    pub fn id_less_than(self, value: impl ToString) -> Self {
        self.param("idLessThan", value)
    }

    pub fn ignore_transfers(self, value: impl ToString) -> Self {
        self.param("ignore_transfers", value)
    }

    pub fn info(self, value: impl ToString) -> Self {
        self.param("info", value)
    }

    pub fn inst_family(self, value: impl ToString) -> Self {
        self.param("instFamily", value)
    }

    pub fn inst_type(self, value: impl ToString) -> Self {
        self.param("instType", value)
    }

    pub fn integrator_account_index(self, value: impl ToString) -> Self {
        self.param("integrator_account_index", value)
    }

    pub fn integrator_maker_fee(self, value: impl ToString) -> Self {
        self.param("integrator_maker_fee", value)
    }

    pub fn integrator_taker_fee(self, value: impl ToString) -> Self {
        self.param("integrator_taker_fee", value)
    }

    pub fn interval(self, value: impl ToString) -> Self {
        self.param("interval", value)
    }

    pub fn interval_time(self, value: impl ToString) -> Self {
        self.param("intervalTime", value)
    }

    pub fn is_leverage(self, value: impl ToString) -> Self {
        self.param("isLeverage", value)
    }

    pub fn is_market(self, value: impl ToString) -> Self {
        self.param("isMarket", value)
    }

    pub fn last_end_id(self, value: impl ToString) -> Self {
        self.param("lastEndId", value)
    }

    pub fn last_fill_time(self, value: impl ToString) -> Self {
        self.param("lastFillTime", value)
    }

    pub fn last_id(self, value: impl ToString) -> Self {
        self.param("last_id", value)
    }

    pub fn last_time(self, value: impl ToString) -> Self {
        self.param("lastTime", value)
    }

    pub fn late_id(self, value: impl ToString) -> Self {
        self.param("late_id", value)
    }

    pub fn leaves_qty(self, value: impl ToString) -> Self {
        self.param("leavesQty", value)
    }

    pub fn leverage(self, value: impl ToString) -> Self {
        self.param("leverage", value)
    }

    pub fn limit(self, value: impl ToString) -> Self {
        self.param("limit", value)
    }

    pub fn limit_price(self, value: impl ToString) -> Self {
        self.param("limitPrice", value)
    }

    pub fn loan_trans(self, value: impl ToString) -> Self {
        self.param("loanTrans", value)
    }

    pub fn long_leverage(self, value: impl ToString) -> Self {
        self.param("longLeverage", value)
    }

    pub fn margin_coin(self, value: impl ToString) -> Self {
        self.param("marginCoin", value)
    }

    pub fn margin_mode(self, value: impl ToString) -> Self {
        self.param("marginMode", value)
    }

    pub fn market(self, value: impl ToString) -> Self {
        self.param("market", value)
    }

    pub fn market_id(self, value: impl ToString) -> Self {
        self.param("market_id", value)
    }

    pub fn market_unit(self, value: impl ToString) -> Self {
        self.param("marketUnit", value)
    }

    pub fn max_chase_offset(self, value: impl ToString) -> Self {
        self.param("maxChaseOffset", value)
    }

    pub fn max_chase_offset_type(self, value: impl ToString) -> Self {
        self.param("maxChaseOffsetType", value)
    }

    pub fn member_id(self, value: impl ToString) -> Self {
        self.param("memberId", value)
    }

    pub fn mgn_ccy(self, value: impl ToString) -> Self {
        self.param("mgnCcy", value)
    }

    pub fn mgn_mode(self, value: impl ToString) -> Self {
        self.param("mgnMode", value)
    }

    pub fn mode(self, value: impl ToString) -> Self {
        self.param("mode", value)
    }

    pub fn month(self, value: impl ToString) -> Self {
        self.param("month", value)
    }

    pub fn multi_asset(self, value: impl ToString) -> Self {
        self.param("multi_asset", value)
    }

    pub fn need_btc_valuation(self, value: impl ToString) -> Self {
        self.param("needBtcValuation", value)
    }

    pub fn need_usd_valuation(self, value: impl ToString) -> Self {
        self.param("needUsdValuation", value)
    }

    pub fn network(self, value: impl ToString) -> Self {
        self.param("network", value)
    }

    pub fn new_client_order_id(self, value: impl ToString) -> Self {
        self.param("newClientOrderId", value)
    }

    pub fn new_order_resp_type(self, value: impl ToString) -> Self {
        self.param("newOrderRespType", value)
    }

    pub fn new_px(self, value: impl ToString) -> Self {
        self.param("newPx", value)
    }

    pub fn new_px_usd(self, value: impl ToString) -> Self {
        self.param("newPxUsd", value)
    }

    pub fn new_px_vol(self, value: impl ToString) -> Self {
        self.param("newPxVol", value)
    }

    pub fn new_sz(self, value: impl ToString) -> Self {
        self.param("newSz", value)
    }

    pub fn nonce(self, value: impl ToString) -> Self {
        self.param("nonce", value)
    }

    pub fn notional(self, value: impl ToString) -> Self {
        self.param("notional", value)
    }

    pub fn offset(self, value: impl ToString) -> Self {
        self.param("offset", value)
    }

    pub fn oflags(self, value: impl ToString) -> Self {
        self.param("oflags", value)
    }

    pub fn ofs(self, value: impl ToString) -> Self {
        self.param("ofs", value)
    }

    pub fn ord_id(self, value: impl ToString) -> Self {
        self.param("ordId", value)
    }

    pub fn ord_type(self, value: impl ToString) -> Self {
        self.param("ordType", value)
    }

    pub fn order(self, value: impl ToString) -> Self {
        self.param("order", value)
    }

    pub fn order_expiry(self, value: impl ToString) -> Self {
        self.param("order_expiry", value)
    }

    pub fn order_filter(self, value: impl ToString) -> Self {
        self.param("orderFilter", value)
    }

    pub fn order_id_list(self, value: impl ToString) -> Self {
        self.param("orderIdList", value)
    }

    pub fn order_ids(self, value: impl ToString) -> Self {
        self.param("orderIds", value)
    }

    pub fn order_index(self, value: impl ToString) -> Self {
        self.param("order_index", value)
    }

    pub fn order_iv(self, value: impl ToString) -> Self {
        self.param("orderIv", value)
    }

    pub fn order_link_id(self, value: impl ToString) -> Self {
        self.param("orderLinkId", value)
    }

    pub fn order_mode(self, value: impl ToString) -> Self {
        self.param("orderMode", value)
    }

    pub fn order_qty(self, value: impl ToString) -> Self {
        self.param("orderQty", value)
    }

    pub fn order_state(self, value: impl ToString) -> Self {
        self.param("order_state", value)
    }

    pub fn order_type(self, value: impl ToString) -> Self {
        self.param("order_type", value)
    }

    pub fn orig_cl_ord_id(self, value: impl ToString) -> Self {
        self.param("origClOrdID", value)
    }

    pub fn orig_client_order_id(self, value: impl ToString) -> Self {
        self.param("origClientOrderId", value)
    }

    pub fn orig_client_order_id_list(self, value: impl ToString) -> Self {
        self.param("origClientOrderIdList", value)
    }

    pub fn page(self, value: impl ToString) -> Self {
        self.param("page", value)
    }

    pub fn page_index(self, value: impl ToString) -> Self {
        self.param("pageIndex", value)
    }

    pub fn page_no(self, value: impl ToString) -> Self {
        self.param("pageNo", value)
    }

    pub fn pair(self, value: impl ToString) -> Self {
        self.param("pair", value)
    }

    pub fn partial(self, value: impl ToString) -> Self {
        self.param("partial", value)
    }

    pub fn path(self, value: impl ToString) -> Self {
        self.param("path", value)
    }

    pub fn peg_offset_value(self, value: impl ToString) -> Self {
        self.param("pegOffsetValue", value)
    }

    pub fn peg_price_type(self, value: impl ToString) -> Self {
        self.param("pegPriceType", value)
    }

    pub fn period(self, value: impl ToString) -> Self {
        self.param("period", value)
    }

    pub fn pnl(self, value: impl ToString) -> Self {
        self.param("pnl", value)
    }

    pub fn pos_side(self, value: impl ToString) -> Self {
        self.param("posSide", value)
    }

    pub fn position_idx(self, value: impl ToString) -> Self {
        self.param("positionIdx", value)
    }

    pub fn position_mode(self, value: impl ToString) -> Self {
        self.param("positionMode", value)
    }

    pub fn position_side(self, value: impl ToString) -> Self {
        self.param("positionSide", value)
    }

    pub fn position_type(self, value: impl ToString) -> Self {
        self.param("positionType", value)
    }

    pub fn post_only(self, value: impl ToString) -> Self {
        self.param("postOnly", value)
    }

    pub fn precision(self, value: impl ToString) -> Self {
        self.param("precision", value)
    }

    pub fn preset_stop_loss_price(self, value: impl ToString) -> Self {
        self.param("preset_stop_loss_price", value)
    }

    pub fn preset_stop_loss_price_type(self, value: impl ToString) -> Self {
        self.param("preset_stop_loss_price_type", value)
    }

    pub fn preset_take_profit_price(self, value: impl ToString) -> Self {
        self.param("preset_take_profit_price", value)
    }

    pub fn preset_take_profit_price_type(self, value: impl ToString) -> Self {
        self.param("preset_take_profit_price_type", value)
    }

    pub fn price(self, value: impl ToString) -> Self {
        self.param("price", value)
    }

    pub fn price2(self, value: impl ToString) -> Self {
        self.param("price2", value)
    }

    pub fn price_limit(self, value: impl ToString) -> Self {
        self.param("priceLimit", value)
    }

    pub fn price_match(self, value: impl ToString) -> Self {
        self.param("priceMatch", value)
    }

    pub fn price_protect(self, value: impl ToString) -> Self {
        self.param("priceProtect", value)
    }

    pub fn price_protection(self, value: impl ToString) -> Self {
        self.param("price_protection", value)
    }

    pub fn price_rate(self, value: impl ToString) -> Self {
        self.param("priceRate", value)
    }

    pub fn price_type(self, value: impl ToString) -> Self {
        self.param("priceType", value)
    }

    pub fn process(self, value: impl ToString) -> Self {
        self.param("process", value)
    }

    pub fn product_symbol(self, value: impl ToString) -> Self {
        self.param("product_symbol", value)
    }

    pub fn product_symbols(self, value: impl ToString) -> Self {
        self.param("product_symbols", value)
    }

    pub fn product_type(self, value: impl ToString) -> Self {
        self.param("productType", value)
    }

    pub fn px(self, value: impl ToString) -> Self {
        self.param("px", value)
    }

    pub fn px_usd(self, value: impl ToString) -> Self {
        self.param("pxUsd", value)
    }

    pub fn px_vol(self, value: impl ToString) -> Self {
        self.param("pxVol", value)
    }

    pub fn qty(self, value: impl ToString) -> Self {
        self.param("qty", value)
    }

    pub fn qty_limit(self, value: impl ToString) -> Self {
        self.param("qtyLimit", value)
    }

    pub fn quantity(self, value: impl ToString) -> Self {
        self.param("quantity", value)
    }

    pub fn query_state(self, value: impl ToString) -> Self {
        self.param("queryState", value)
    }

    pub fn quick_mgn_type(self, value: impl ToString) -> Self {
        self.param("quickMgnType", value)
    }

    pub fn quote_asset(self, value: impl ToString) -> Self {
        self.param("quoteAsset", value)
    }

    pub fn quote_order_qty(self, value: impl ToString) -> Self {
        self.param("quoteOrderQty", value)
    }

    pub fn quote_quantity(self, value: impl ToString) -> Self {
        self.param("quoteQuantity", value)
    }

    pub fn rebase_multiplier(self, value: impl ToString) -> Self {
        self.param("rebase_multiplier", value)
    }

    pub fn recv_window(self, value: impl ToString) -> Self {
        self.param("recvWindow", value)
    }

    pub fn remark(self, value: impl ToString) -> Self {
        self.param("remark", value)
    }

    pub fn req_id(self, value: impl ToString) -> Self {
        self.param("reqId", value)
    }

    pub fn reverse(self, value: impl ToString) -> Self {
        self.param("reverse", value)
    }

    pub fn role(self, value: impl ToString) -> Self {
        self.param("role", value)
    }

    pub fn rule_type(self, value: impl ToString) -> Self {
        self.param("ruleType", value)
    }

    pub fn self_trade_prevention(self, value: impl ToString) -> Self {
        self.param("selfTradePrevention", value)
    }

    pub fn self_trade_prevention_mode(self, value: impl ToString) -> Self {
        self.param("selfTradePreventionMode", value)
    }

    pub fn set_timestamp_to_end(self, value: impl ToString) -> Self {
        self.param("set_timestamp_to_end", value)
    }

    pub fn settle_coin(self, value: impl ToString) -> Self {
        self.param("settleCoin", value)
    }

    pub fn settle(self, value: impl ToString) -> Self {
        self.param("settle", value)
    }

    pub fn short_leverage(self, value: impl ToString) -> Self {
        self.param("shortLeverage", value)
    }

    pub fn side(self, value: impl ToString) -> Self {
        self.param("side", value)
    }

    pub fn since(self, value: impl ToString) -> Self {
        self.param("since", value)
    }

    pub fn size(self, value: impl ToString) -> Self {
        self.param("size", value)
    }

    pub fn skip_ask_order_id(self, value: impl ToString) -> Self {
        self.param("skip_ask_order_id", value)
    }

    pub fn skip_bid_order_id(self, value: impl ToString) -> Self {
        self.param("skip_bid_order_id", value)
    }

    pub fn skip_nonce(self, value: impl ToString) -> Self {
        self.param("skip_nonce", value)
    }

    pub fn sl_limit_price(self, value: impl ToString) -> Self {
        self.param("slLimitPrice", value)
    }

    pub fn sl_order_type(self, value: impl ToString) -> Self {
        self.param("slOrderType", value)
    }

    pub fn sl_trigger_by(self, value: impl ToString) -> Self {
        self.param("slTriggerBy", value)
    }

    pub fn sort_dir(self, value: impl ToString) -> Self {
        self.param("sort_dir", value)
    }

    pub fn sort_direction(self, value: impl ToString) -> Self {
        self.param("sortDirection", value)
    }

    pub fn source(self, value: impl ToString) -> Self {
        self.param("source", value)
    }

    pub fn source_wallet(self, value: impl ToString) -> Self {
        self.param("sourceWallet", value)
    }

    pub fn start(self, value: impl ToString) -> Self {
        self.param("start", value)
    }

    pub fn start_at(self, value: impl ToString) -> Self {
        self.param("startAt", value)
    }

    pub fn start_timestamp(self, value: impl ToString) -> Self {
        self.param("start_timestamp", value)
    }

    pub fn starttm(self, value: impl ToString) -> Self {
        self.param("starttm", value)
    }

    pub fn state(self, value: impl ToString) -> Self {
        self.param("state", value)
    }

    pub fn states(self, value: impl ToString) -> Self {
        self.param("states", value)
    }

    pub fn stats_end_timestamp(self, value: impl ToString) -> Self {
        self.param("stats_end_timestamp", value)
    }

    pub fn stats_start_timestamp(self, value: impl ToString) -> Self {
        self.param("stats_start_timestamp", value)
    }

    pub fn status(self, value: impl ToString) -> Self {
        self.param("status", value)
    }

    pub fn stop(self, value: impl ToString) -> Self {
        self.param("stop", value)
    }

    pub fn stop_guaranteed(self, value: impl ToString) -> Self {
        self.param("stopGuaranteed", value)
    }

    pub fn stop_loss(self, value: impl ToString) -> Self {
        self.param("stopLoss", value)
    }

    pub fn stop_loss_price(self, value: impl ToString) -> Self {
        self.param("stopLossPrice", value)
    }

    pub fn stop_price(self, value: impl ToString) -> Self {
        self.param("stopPrice", value)
    }

    pub fn stop_price_type(self, value: impl ToString) -> Self {
        self.param("stopPriceType", value)
    }

    pub fn stop_px(self, value: impl ToString) -> Self {
        self.param("stopPx", value)
    }

    pub fn stp(self, value: impl ToString) -> Self {
        self.param("stp", value)
    }

    pub fn stp_act(self, value: impl ToString) -> Self {
        self.param("stp_act", value)
    }

    pub fn stp_id(self, value: impl ToString) -> Self {
        self.param("stpId", value)
    }

    pub fn strategy_id(self, value: impl ToString) -> Self {
        self.param("strategyId", value)
    }

    pub fn sub_acct(self, value: impl ToString) -> Self {
        self.param("subAcct", value)
    }

    pub fn sub_type(self, value: impl ToString) -> Self {
        self.param("subType", value)
    }

    pub fn sub_uid(self, value: impl ToString) -> Self {
        self.param("sub_uid", value)
    }

    pub fn subaccount_id(self, value: impl ToString) -> Self {
        self.param("subaccountId", value)
    }

    pub fn symbol(self, value: impl ToString) -> Self {
        self.param("symbol", value)
    }

    pub fn symbol_status(self, value: impl ToString) -> Self {
        self.param("symbolStatus", value)
    }

    pub fn symbols(self, value: impl ToString) -> Self {
        self.param("symbols", value)
    }

    pub fn sz(self, value: impl ToString) -> Self {
        self.param("sz", value)
    }

    pub fn tag(self, value: impl ToString) -> Self {
        self.param("tag", value)
    }

    pub fn tags(self, value: impl ToString) -> Self {
        self.param("tags", value)
    }

    pub fn take_profit(self, value: impl ToString) -> Self {
        self.param("takeProfit", value)
    }

    pub fn take_profit_price(self, value: impl ToString) -> Self {
        self.param("takeProfitPrice", value)
    }

    pub fn target_account_ids_array(self, value: impl ToString) -> Self {
        self.param("targetAccountIds_array", value)
    }

    pub fn td_mode(self, value: impl ToString) -> Self {
        self.param("tdMode", value)
    }

    pub fn text(self, value: impl ToString) -> Self {
        self.param("text", value)
    }

    pub fn tgt_ccy(self, value: impl ToString) -> Self {
        self.param("tgtCcy", value)
    }

    pub fn tick_type(self, value: impl ToString) -> Self {
        self.param("tick_type", value)
    }

    pub fn tier(self, value: impl ToString) -> Self {
        self.param("tier", value)
    }

    pub fn tier_id(self, value: impl ToString) -> Self {
        self.param("tierId", value)
    }

    pub fn tif(self, value: impl ToString) -> Self {
        self.param("tif", value)
    }

    pub fn time(self, value: impl ToString) -> Self {
        self.param("time", value)
    }

    pub fn timeinforce(self, value: impl ToString) -> Self {
        self.param("timeinforce", value)
    }

    pub fn timezone(self, value: impl ToString) -> Self {
        self.param("timezone", value)
    }

    pub fn to(self, value: impl ToString) -> Self {
        self.param("to", value)
    }

    pub fn to_account(self, value: impl ToString) -> Self {
        self.param("toAccount", value)
    }

    pub fn to_account_index(self, value: impl ToString) -> Self {
        self.param("to_account_index", value)
    }

    pub fn to_account_type(self, value: impl ToString) -> Self {
        self.param("toAccountType", value)
    }

    pub fn to_symbol(self, value: impl ToString) -> Self {
        self.param("toSymbol", value)
    }

    pub fn to_time(self, value: impl ToString) -> Self {
        self.param("to_time", value)
    }

    pub fn to_timestamp(self, value: impl ToString) -> Self {
        self.param("to_timestamp", value)
    }

    pub fn to_user_id(self, value: impl ToString) -> Self {
        self.param("toUserId", value)
    }

    pub fn tp_limit_price(self, value: impl ToString) -> Self {
        self.param("tpLimitPrice", value)
    }

    pub fn tp_order_type(self, value: impl ToString) -> Self {
        self.param("tpOrderType", value)
    }

    pub fn tp_trigger_by(self, value: impl ToString) -> Self {
        self.param("tpTriggerBy", value)
    }

    pub fn tpsl(self, value: impl ToString) -> Self {
        self.param("tpsl", value)
    }

    pub fn tpsl_mode(self, value: impl ToString) -> Self {
        self.param("tpslMode", value)
    }

    pub fn tpsl_type(self, value: impl ToString) -> Self {
        self.param("tpslType", value)
    }

    pub fn trade_side(self, value: impl ToString) -> Self {
        self.param("tradeSide", value)
    }

    pub fn trade_side_type(self, value: impl ToString) -> Self {
        self.param("tradeSideType", value)
    }

    pub fn trade_type(self, value: impl ToString) -> Self {
        self.param("trade_type", value)
    }

    pub fn trade_types(self, value: impl ToString) -> Self {
        self.param("tradeTypes", value)
    }

    pub fn trades(self, value: impl ToString) -> Self {
        self.param("trades", value)
    }

    pub fn tran_id(self, value: impl ToString) -> Self {
        self.param("tranId", value)
    }

    pub fn trans_id(self, value: impl ToString) -> Self {
        self.param("transId", value)
    }

    pub fn transfer_type(self, value: impl ToString) -> Self {
        self.param("transfer_type", value)
    }

    pub fn trigger_by(self, value: impl ToString) -> Self {
        self.param("triggerBy", value)
    }

    pub fn trigger_direction(self, value: impl ToString) -> Self {
        self.param("triggerDirection", value)
    }

    pub fn trigger_px(self, value: impl ToString) -> Self {
        self.param("triggerPx", value)
    }

    pub fn trigger_signal(self, value: impl ToString) -> Self {
        self.param("triggerSignal", value)
    }

    pub fn tx_id(self, value: impl ToString) -> Self {
        self.param("txId", value)
    }

    pub fn txid(self, value: impl ToString) -> Self {
        self.param("txid", value)
    }

    pub fn uly(self, value: impl ToString) -> Self {
        self.param("uly", value)
    }

    pub fn userref(self, value: impl ToString) -> Self {
        self.param("userref", value)
    }

    pub fn validate(self, value: impl ToString) -> Self {
        self.param("validate", value)
    }

    pub fn value(self, value: impl ToString) -> Self {
        self.param("value", value)
    }

    pub fn value_limit(self, value: impl ToString) -> Self {
        self.param("valueLimit", value)
    }

    pub fn vault_address(self, value: impl ToString) -> Self {
        self.param("vaultAddress", value)
    }

    pub fn vip_level(self, value: impl ToString) -> Self {
        self.param("vipLevel", value)
    }

    pub fn visible_size(self, value: impl ToString) -> Self {
        self.param("visibleSize", value)
    }

    pub fn wd_id(self, value: impl ToString) -> Self {
        self.param("wdId", value)
    }

    pub fn with_id(self, value: impl ToString) -> Self {
        self.param("with_id", value)
    }

    pub fn without_count(self, value: impl ToString) -> Self {
        self.param("without_count", value)
    }

    pub fn working_type(self, value: impl ToString) -> Self {
        self.param("workingType", value)
    }
    // END GENERATED OPTIONAL PARAM SETTERS

    pub fn optional_param<T: ToString>(self, key: impl Into<String>, value: Option<T>) -> Self {
        if let Some(value) = value {
            self.param(key, value)
        } else {
            self
        }
    }

    pub async fn send(self) -> Result<ValidatedResponse> {
        if self.signed {
            self.client
                .private_request_boxed(self.method_name, self.params)
                .await
        } else {
            self.client
                .public_request_boxed(self.method_name, self.params)
                .await
        }
    }
}

impl<'a, C: ExchangeMethodRequestClient + Sync> IntoFuture for ExchangeMethodRequest<'a, C> {
    type Output = Result<ValidatedResponse>;
    type IntoFuture = ExchangeMethodFuture<'a>;

    fn into_future(self) -> Self::IntoFuture {
        Box::pin(self.send())
    }
}

macro_rules! impl_exchange_method_wrappers {
    (
        $client:ty;
        public [$($public_method:ident($($public_param:ident => $public_key:literal),*)),* $(,)?];
        private [$($private_method:ident($($private_param:ident => $private_key:literal),*)),* $(,)?] $(;)?
    ) => {
        impl crate::exchanges::ExchangeMethodRequestClient for $client {
            fn public_request_boxed<'a>(
                &'a self,
                method_name: &'static str,
                params: Vec<(String, String)>,
            ) -> crate::exchanges::ExchangeMethodFuture<'a> {
                Box::pin(async move { self.public_request(method_name, params).await })
            }

            fn private_request_boxed<'a>(
                &'a self,
                method_name: &'static str,
                params: Vec<(String, String)>,
            ) -> crate::exchanges::ExchangeMethodFuture<'a> {
                Box::pin(async move { self.private_request(method_name, params).await })
            }
        }

        impl $client {
            $(
                #[allow(clippy::too_many_arguments)]
                pub fn $public_method(
                    &self
                    $(, $public_param: impl ToString)*
                ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
                    let params = vec![$(($public_key.to_string(), $public_param.to_string())),*];
                    crate::exchanges::ExchangeMethodRequest::public(
                        self,
                        stringify!($public_method),
                        params,
                    )
                }
            )*

            $(
                #[allow(clippy::too_many_arguments)]
                pub fn $private_method(
                    &self
                    $(, $private_param: impl ToString)*
                ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
                    let params = vec![$(($private_key.to_string(), $private_param.to_string())),*];
                    crate::exchanges::ExchangeMethodRequest::private(
                        self,
                        stringify!($private_method),
                        params,
                    )
                }
            )*
        }
    };
}

pub(crate) use impl_exchange_method_wrappers;

#[cfg(test)]
mod tests {
    use super::*;

    struct DummyClient;

    impl ExchangeMethodRequestClient for DummyClient {
        fn public_request_boxed<'a>(
            &'a self,
            _method_name: &'static str,
            _params: Vec<(String, String)>,
        ) -> ExchangeMethodFuture<'a> {
            unreachable!("request dispatch is not used by these tests")
        }

        fn private_request_boxed<'a>(
            &'a self,
            _method_name: &'static str,
            _params: Vec<(String, String)>,
        ) -> ExchangeMethodFuture<'a> {
            unreachable!("request dispatch is not used by these tests")
        }
    }

    #[test]
    fn param_replaces_existing_key() {
        let client = DummyClient;
        let request = ExchangeMethodRequest::public(&client, "example", Vec::new())
            .param("limit", 10)
            .param("limit", 20);

        assert_eq!(
            request.params,
            vec![("limit".to_string(), "20".to_string())]
        );
    }

    #[test]
    fn push_param_preserves_repeated_keys() {
        let client = DummyClient;
        let request = ExchangeMethodRequest::public(&client, "example", Vec::new())
            .param("product_symbols", "BTC-USDT-SPOT")
            .push_param("product_symbols", "ETH-USDT-SPOT");

        assert_eq!(
            request.params,
            vec![
                ("product_symbols".to_string(), "BTC-USDT-SPOT".to_string()),
                ("product_symbols".to_string(), "ETH-USDT-SPOT".to_string())
            ]
        );
    }

    #[test]
    fn gateio_optional_setters_use_native_parameter_names() {
        let client = DummyClient;
        let request = ExchangeMethodRequest::private(&client, "wallet_transfer", Vec::new())
            .currency_pair("BTC_USDT")
            .settle("usdt");

        assert_eq!(
            request.params,
            vec![
                ("currency_pair".to_string(), "BTC_USDT".to_string()),
                ("settle".to_string(), "usdt".to_string())
            ]
        );
    }
}

pub mod aster;
pub mod backpack;
pub mod binance;
pub mod bingx;
pub mod bitget;
pub mod bitmart;
pub mod bitmex;
pub mod bybit;
pub mod gateio;
pub mod hyperliquid;
pub mod kraken;
pub mod kucoin;
pub mod lighter;
pub mod mexc;
pub mod okx;
