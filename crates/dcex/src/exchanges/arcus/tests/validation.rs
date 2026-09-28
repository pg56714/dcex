use super::helpers::*;

#[test]
fn decimal_to_engine_units_is_exact() {
    assert_eq!(exact_units("0.001", "0.0001").unwrap(), 10);
    assert!(exact_units("0.0015", "0.001").is_err());
    assert!(decimal_product_below("100", "0.01", "5").unwrap());
}
