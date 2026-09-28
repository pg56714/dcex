use super::helpers::*;

#[test]
fn timestamp_matches_python_format() {
    assert_eq!(iso_timestamp(1_700_000_000_000), "2023-11-14T22:13:20.000Z");
}
