use super::helpers::*;

#[test]
fn spot_status_wrapper_sets_arcus_venue() {
    let client = ArcusSpotClient::new(None, false, Duration::from_secs(1)).unwrap();
    let request = client.get_status(format!("0x{}", "11".repeat(32)));
    assert_eq!(request.method_name, "get_status");
    assert!(request.params.contains(&("venue".into(), "arcus".into())));
}
