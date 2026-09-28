pub(super) fn decode_hex_len(value: &str) -> Option<usize> {
    hex::decode(value).ok().map(|bytes| bytes.len())
}
