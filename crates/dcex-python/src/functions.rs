use super::*;

#[pyfunction]
fn lighter_poseidon_hash_bytes(values: Vec<u64>) -> PyResult<Vec<u8>> {
    Ok(lighter::poseidon_hash_bytes(&values).to_vec())
}

#[pyfunction]
fn lighter_public_key_bytes(private_key: &[u8]) -> PyResult<Vec<u8>> {
    let scalar = lighter::private_key_from_bytes(private_key).map_err(to_py_value_error)?;
    lighter::public_key_bytes(&scalar)
        .map(|value| value.to_vec())
        .map_err(to_py_value_error)
}

#[pyfunction]
fn lighter_schnorr_sign(
    message_hash: &[u8],
    private_key: &[u8],
    nonce: &[u8],
) -> PyResult<Vec<u8>> {
    let private_key = lighter::private_key_from_bytes(private_key).map_err(to_py_value_error)?;
    let nonce =
        lighter::scalar_from_bytes(nonce, "Lighter nonce scalar").map_err(to_py_value_error)?;
    lighter::schnorr_sign_with_nonce(message_hash, &private_key, &nonce)
        .map(|value| value.to_vec())
        .map_err(to_py_value_error)
}

#[pyfunction]
fn lighter_sign_transaction(
    values: Vec<i128>,
    attributes: Vec<(u64, u64)>,
    payload_json: Vec<u8>,
    private_key: Vec<u8>,
    nonce: Vec<u8>,
) -> PyResult<(Py<PyBytes>, Py<PyBytes>)> {
    let (payload, message_hash) = lighter::sign_transaction_payload(
        &values,
        &attributes,
        &payload_json,
        &private_key,
        &nonce,
    )
    .map_err(to_py_value_error)?;
    Python::with_gil(|py| {
        Ok((
            PyBytes::new(py, &payload).unbind(),
            PyBytes::new(py, &message_hash).unbind(),
        ))
    })
}

#[pyfunction]
fn lighter_auth_token(
    expiry: u64,
    account_index: u64,
    api_key_index: u64,
    private_key: Vec<u8>,
    nonce: Vec<u8>,
) -> PyResult<String> {
    lighter::auth_token(expiry, account_index, api_key_index, &private_key, &nonce)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn exchange_names() -> Vec<String> {
    common::exchange_names()
        .into_iter()
        .map(str::to_string)
        .collect()
}

#[pyfunction]
fn order_side_parse(value: &str) -> PyResult<String> {
    OrderSide::parse(value)
        .map(|side| {
            if side.is_buy() {
                "BUY".to_string()
            } else {
                "SELL".to_string()
            }
        })
        .map_err(to_py_value_error)
}

#[pyfunction]
fn order_side_to_exchange(side: &str, exchange: &str) -> PyResult<String> {
    OrderSide::parse(side)
        .and_then(|side| side.to_exchange(exchange).map(str::to_string))
        .map_err(to_py_value_error)
}

#[pyfunction]
fn order_side_is_buy(side: &str) -> PyResult<bool> {
    OrderSide::parse(side)
        .map(OrderSide::is_buy)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn generate_timestamp_ms() -> PyResult<u64> {
    common::generate_timestamp_ms().map_err(to_py_runtime_error)
}

#[pyfunction]
fn generate_timestamp_iso() -> PyResult<String> {
    common::generate_timestamp_iso().map_err(to_py_runtime_error)
}

#[pyfunction]
fn get_decimal_places(value: f64) -> PyResult<u32> {
    common::get_decimal_places(value).map_err(to_py_value_error)
}

#[pyfunction]
fn reverse_decimal_places(decimal_places: i32) -> f64 {
    common::reverse_decimal_places(decimal_places)
}

#[pyfunction]
fn bybit_convert_timeframe(timeframe: &str) -> PyResult<String> {
    common::bybit_convert_timeframe(timeframe)
        .map(str::to_string)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn bitmart_convert_timeframe(timeframe: &str) -> PyResult<u32> {
    common::bitmart_convert_timeframe(timeframe).map_err(to_py_value_error)
}

#[pyfunction]
fn kucoin_convert_timeframe(timeframe: &str) -> PyResult<String> {
    common::kucoin_convert_timeframe(timeframe)
        .map(str::to_string)
        .map_err(to_py_value_error)
}

#[pyfunction]
fn address_to_bytes(address: &str) -> PyResult<Py<PyBytes>> {
    let bytes = common::address_to_bytes(address).map_err(to_py_value_error)?;
    Python::with_gil(|py| Ok(PyBytes::new(py, &bytes).unbind()))
}

#[pyfunction]
fn sanitize_url(url: &str) -> String {
    common::sanitize_url(url)
}

#[pyfunction]
fn sanitize_message(message: &str) -> String {
    common::sanitize_message(message)
}

#[pyfunction]
fn sanitize_request(request: &str) -> String {
    common::sanitize_request(request)
}

pub(super) fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(lighter_poseidon_hash_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_public_key_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_schnorr_sign, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_sign_transaction, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_auth_token, m)?)?;
    m.add_function(wrap_pyfunction!(exchange_names, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_parse, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_to_exchange, m)?)?;
    m.add_function(wrap_pyfunction!(order_side_is_buy, m)?)?;
    m.add_function(wrap_pyfunction!(generate_timestamp_ms, m)?)?;
    m.add_function(wrap_pyfunction!(generate_timestamp_iso, m)?)?;
    m.add_function(wrap_pyfunction!(get_decimal_places, m)?)?;
    m.add_function(wrap_pyfunction!(reverse_decimal_places, m)?)?;
    m.add_function(wrap_pyfunction!(bybit_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(bitmart_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(kucoin_convert_timeframe, m)?)?;
    m.add_function(wrap_pyfunction!(address_to_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_url, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_message, m)?)?;
    m.add_function(wrap_pyfunction!(sanitize_request, m)?)?;
    Ok(())
}
