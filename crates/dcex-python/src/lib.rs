use std::collections::BTreeMap;
use std::time::Duration;

use dcex::common::{self, OrderSide};
use dcex::exchange::ValidatedResponse;
use dcex::exchanges::aster::{AsterClient, AsterMarket};
use dcex::exchanges::backpack::{BackpackClient, SignaturePayload};
use dcex::exchanges::binance::{BinanceClient, BinanceMarket};
use dcex::exchanges::bingx::BingxClient;
use dcex::exchanges::bitget::BitgetClient;
use dcex::exchanges::bitmart::{BitmartClient, BitmartMarket};
use dcex::exchanges::bitmex::BitmexClient;
use dcex::exchanges::bybit::BybitClient;
use dcex::exchanges::gateio::GateioClient;
use dcex::exchanges::hyperliquid::HyperliquidClient;
use dcex::exchanges::kraken::{KrakenAuth, KrakenClient};
use dcex::exchanges::kucoin::{KucoinClient, KucoinMarket};
use dcex::exchanges::lighter::{LighterClient, LighterContentType};
use dcex::exchanges::mexc::{MexcApi, MexcClient};
use dcex::exchanges::okx::OkxClient;
use dcex::http::{
    block_on, AsyncHttpClient, BlockingHttpClient, HttpMethod, HttpRequest, HttpResponse,
};
use dcex::lighter;
use dcex::product_table::{MarketInfo, ProductFilter, ProductTable};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyBytes;

fn to_py_value_error(error: dcex::DcexError) -> PyErr {
    PyValueError::new_err(error.to_string())
}

fn to_py_runtime_error(error: dcex::DcexError) -> PyErr {
    match error {
        dcex::DcexError::InvalidInput(_) => to_py_value_error(error),
        _ => PyRuntimeError::new_err(error.to_string()),
    }
}

fn http_method(method: &str) -> PyResult<HttpMethod> {
    match method.to_ascii_uppercase().as_str() {
        "DELETE" => Ok(HttpMethod::Delete),
        "GET" => Ok(HttpMethod::Get),
        "PATCH" => Ok(HttpMethod::Patch),
        "POST" => Ok(HttpMethod::Post),
        "PUT" => Ok(HttpMethod::Put),
        _ => Err(PyValueError::new_err(format!(
            "unsupported HTTP method: {method}"
        ))),
    }
}

fn http_request(
    method: &str,
    base_url: String,
    path: String,
    query: Option<Vec<(String, String)>>,
    headers: Option<BTreeMap<String, String>>,
    body: Option<Vec<u8>>,
) -> PyResult<HttpRequest> {
    let mut request = HttpRequest::new(http_method(method)?, base_url, path);
    request.query = query.unwrap_or_default();
    request.headers = headers.unwrap_or_default();
    if let Some(body) = body {
        request = request.raw(body);
    }
    Ok(request)
}

type PythonHttpResponse = (u16, BTreeMap<String, String>, Py<PyBytes>);

fn python_http_response(response: HttpResponse) -> PythonHttpResponse {
    let body = Python::with_gil(|py| PyBytes::new(py, &response.body).unbind());
    (response.status, response.headers, body)
}

fn python_validated_response(response: ValidatedResponse) -> PyResult<PythonHttpResponse> {
    let body = serde_json::to_vec(&response.data)
        .map_err(|error| PyRuntimeError::new_err(error.to_string()))?;
    let body = Python::with_gil(|py| PyBytes::new(py, &body).unbind());
    Ok((response.status, response.headers, body))
}

pub(crate) use product_table::PythonProductTable;

fn binance_market(market: &str) -> PyResult<BinanceMarket> {
    match market.to_ascii_lowercase().as_str() {
        "futures" | "future" | "swap" => Ok(BinanceMarket::Futures),
        "spot" | "wallet" => Ok(BinanceMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Binance market: {market}"
        ))),
    }
}

fn parse_json_body(body: Option<Vec<u8>>) -> PyResult<Option<serde_json::Value>> {
    body.map(|body| {
        serde_json::from_slice(&body).map_err(|error| PyValueError::new_err(error.to_string()))
    })
    .transpose()
}

fn mexc_api(api: &str) -> PyResult<MexcApi> {
    match api.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(MexcApi::Contract),
        "spot" => Ok(MexcApi::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported MEXC API: {api}"
        ))),
    }
}

fn bitmart_market(market: &str) -> PyResult<BitmartMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(BitmartMarket::Futures),
        "spot" | "wallet" => Ok(BitmartMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported BitMart market: {market}"
        ))),
    }
}

fn kucoin_market(market: &str) -> PyResult<KucoinMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(KucoinMarket::Futures),
        "spot" | "wallet" => Ok(KucoinMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported KuCoin market: {market}"
        ))),
    }
}

fn kraken_auth(auth: &str) -> PyResult<KrakenAuth> {
    match auth.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(KrakenAuth::Futures),
        "spot" | "wallet" => Ok(KrakenAuth::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Kraken auth type: {auth}"
        ))),
    }
}

fn lighter_content_type(content_type: &str) -> PyResult<LighterContentType> {
    match content_type.to_ascii_lowercase().as_str() {
        "form" => Ok(LighterContentType::Form),
        "json" => Ok(LighterContentType::Json),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Lighter content type: {content_type}"
        ))),
    }
}

fn aster_market(market: &str) -> PyResult<AsterMarket> {
    match market.to_ascii_lowercase().as_str() {
        "contract" | "futures" | "swap" => Ok(AsterMarket::Futures),
        "spot" | "wallet" => Ok(AsterMarket::Spot),
        _ => Err(PyValueError::new_err(format!(
            "unsupported Aster market: {market}"
        ))),
    }
}

mod functions;
mod product_table;

#[path = "clients/aster.rs"]
mod aster_client;
#[path = "clients/backpack.rs"]
mod backpack_client;
#[path = "clients/binance.rs"]
mod binance_client;
#[path = "ws/binance.rs"]
mod binance_ws;
#[path = "clients/bingx.rs"]
mod bingx_client;
#[path = "clients/bitget.rs"]
mod bitget_client;
#[path = "clients/bitmart.rs"]
mod bitmart_client;
#[path = "clients/bitmex.rs"]
mod bitmex_client;
#[path = "clients/bybit.rs"]
mod bybit_client;
#[path = "clients/gateio.rs"]
mod gateio_client;
#[path = "clients/http.rs"]
mod http_client;
#[path = "clients/hyperliquid.rs"]
mod hyperliquid_client;
#[path = "clients/kraken.rs"]
mod kraken_client;
#[path = "clients/kucoin.rs"]
mod kucoin_client;
#[path = "clients/lighter.rs"]
mod lighter_client;
#[path = "clients/mexc.rs"]
mod mexc_client;
#[path = "clients/okx.rs"]
mod okx_client;
#[path = "ws/okx.rs"]
mod okx_ws;

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    aster_client::register(m)?;
    backpack_client::register(m)?;
    binance_client::register(m)?;
    bingx_client::register(m)?;
    bitget_client::register(m)?;
    bitmart_client::register(m)?;
    bitmex_client::register(m)?;
    bybit_client::register(m)?;
    gateio_client::register(m)?;
    hyperliquid_client::register(m)?;
    http_client::register(m)?;
    kraken_client::register(m)?;
    kucoin_client::register(m)?;
    lighter_client::register(m)?;
    mexc_client::register(m)?;
    okx_client::register(m)?;
    binance_ws::register(m)?;
    okx_ws::register(m)?;
    product_table::register(m)?;
    functions::register(m)?;
    Ok(())
}
