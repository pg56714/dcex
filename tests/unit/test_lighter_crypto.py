# ruff: noqa: D100, D103

import base64
import json

import pytest

native = pytest.importorskip("dcex._native")

HASH_VALUES = [
    3451004116618606032,
    11263134342958518251,
    10957204882857370932,
    5369763041201481933,
    7695734348563036858,
    1393419330378128434,
    7387917082382606332,
]
PRIVATE_KEY_LIMBS = [
    12235002942052073545,
    1175977464658719998,
    8536934969147463310,
    6524687619313720391,
    2922072024880609112,
]
NONCE_LIMBS = [
    5245666847777449560,
    15178169970799106939,
    4403065012435293749,
    15306540389399388999,
    8935555081913173844,
]
MESSAGE_HASH = b"".join(
    limb.to_bytes(8, "little")
    for limb in [
        8398652514106806347,
        11069112711939986896,
        9732488227085561369,
        18076754337204438535,
        17155407358725346236,
    ]
)
TX_VALUES = [
    304,
    14,
    11,
    1_590_000,
    12,
    3,
    4,
    5,
    6,
    7,
    1,
    0,
    2,
    0,
    0,
    8,
]
TX_ATTRIBUTES = [(1, 9), (2, 10), (4, 1)]
TX_PAYLOAD = {
    "AccountIndex": 12,
    "ApiKeyIndex": 3,
    "MarketIndex": 4,
    "ClientOrderIndex": 5,
    "BaseAmount": 6,
    "Price": 7,
    "IsAsk": 1,
    "Type": 0,
    "TimeInForce": 2,
    "ReduceOnly": 0,
    "TriggerPrice": 0,
    "OrderExpiry": 8,
    "ExpiredAt": 1_590_000,
    "Nonce": 11,
}


def _scalar_bytes(limbs: list[int]) -> bytes:
    return b"".join(limb.to_bytes(8, "little") for limb in limbs)


def _limbs(value: bytes) -> list[int]:
    return [
        int.from_bytes(value[offset : offset + 8], "little") for offset in range(0, len(value), 8)
    ]


def test_poseidon_matches_official_vector() -> None:
    result = bytes(native.lighter_poseidon_hash_bytes(HASH_VALUES))

    assert _limbs(result) == [
        17992684813643984528,
        5243896189906434327,
        7705560276311184368,
        2785244775876017560,
        14449776097783372302,
    ]


def test_schnorr_matches_official_vector() -> None:
    signature = bytes(
        native.lighter_schnorr_sign(
            MESSAGE_HASH,
            _scalar_bytes(PRIVATE_KEY_LIMBS),
            _scalar_bytes(NONCE_LIMBS),
        )
    )

    assert _limbs(signature[:40]) == [
        6950590877883398434,
        17178336263794770543,
        11012823478139181320,
        16445091359523510936,
        5882925226143600273,
    ]
    assert _limbs(signature[40:]) == [
        4544744459434870309,
        4180764085957612004,
        3024669018778978615,
        15433417688859446606,
        6775027260348937828,
    ]


def test_public_key_for_scalar_one_is_generator_encoding() -> None:
    public_key = bytes(native.lighter_public_key_bytes((1).to_bytes(40, "little")))

    assert public_key == (4).to_bytes(8, "little") + bytes(32)


def test_zero_private_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not reduce to zero"):
        native.lighter_public_key_bytes(bytes(40))


def test_transaction_signing_builds_wire_payload() -> None:
    tx_info, message_hash = native.lighter_sign_transaction(
        TX_VALUES,
        TX_ATTRIBUTES,
        json.dumps(TX_PAYLOAD, separators=(",", ":")).encode(),
        _scalar_bytes(PRIVATE_KEY_LIMBS),
        _scalar_bytes(NONCE_LIMBS),
    )

    payload = json.loads(bytes(tx_info))
    assert len(bytes(message_hash)) == 40
    assert len(base64.b64decode(payload["Sig"])) == 80
    assert payload["L2TxAttributes"] == {"1": 9, "2": 10, "4": 1}
    assert {key: payload[key] for key in TX_PAYLOAD} == TX_PAYLOAD


def test_auth_token_is_signed_by_rust_core() -> None:
    token = native.lighter_auth_token(
        1600,
        12,
        3,
        _scalar_bytes(PRIVATE_KEY_LIMBS),
        _scalar_bytes(NONCE_LIMBS),
    )

    expiry, account_index, api_key_index, signature = token.split(":")
    assert (expiry, account_index, api_key_index) == ("1600", "12", "3")
    assert len(bytes.fromhex(signature)) == 80
