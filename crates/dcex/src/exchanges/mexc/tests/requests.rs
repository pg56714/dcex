use super::helpers::*;

#[test]
fn contract_details_uses_documented_endpoint() {
    assert_eq!(CONTRACT_DETAIL, "/api/v1/contract/detail/country");
}
