"""Offline signing unit tests for Rust-backed local signers."""


def test_aster_eip712_signature_recovers_signer() -> None:
    """Aster EIP-712 signing is delegated to the Rust native extension."""
    from dcex.aster._http_manager import sign_message

    private_key = "0x" + "11" * 32
    message = (
        "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001"
        "&nonce=1700000000000000"
        "&signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    )

    assert sign_message(message, private_key) == (
        "0x3ca64e9c82501b8f15cd31348beaaf1aa6636cbba5fb2bc8d1bccf8ee2ffd310"
        "1a3724dfa8fd2f36de42d3a641b95599d0d4dee5ffb9010eb33b44784d3f60191c"
    )
