use dcex_core::lighter;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

fn to_py_value_error(error: dcex_core::DcexError) -> PyErr {
    PyValueError::new_err(error.to_string())
}

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

#[pymodule]
fn _native(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(lighter_poseidon_hash_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_public_key_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(lighter_schnorr_sign, m)?)?;
    Ok(())
}
