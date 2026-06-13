# ruff: noqa: D100, D103

import base64
import json

import pytest

from dcex.lighter import signer_client as signer_module
from dcex.lighter._crypto import poseidon_hash_bytes, public_key_bytes, schnorr_sign
from dcex.lighter.signer_client import SignerClient


def _scalar(limbs: list[int]) -> int:
    return sum(limb << (64 * index) for index, limb in enumerate(limbs))


def _limbs(value: bytes) -> list[int]:
    return [
        int.from_bytes(value[offset : offset + 8], "little") for offset in range(0, len(value), 8)
    ]


def test_poseidon_matches_official_vector() -> None:
    result = poseidon_hash_bytes(
        [
            3451004116618606032,
            11263134342958518251,
            10957204882857370932,
            5369763041201481933,
            7695734348563036858,
            1393419330378128434,
            7387917082382606332,
        ]
    )

    assert _limbs(result) == [
        17992684813643984528,
        5243896189906434327,
        7705560276311184368,
        2785244775876017560,
        14449776097783372302,
    ]


def test_schnorr_matches_official_vector() -> None:
    private_key = _scalar(
        [
            12235002942052073545,
            1175977464658719998,
            8536934969147463310,
            6524687619313720391,
            2922072024880609112,
        ]
    )
    nonce = _scalar(
        [
            5245666847777449560,
            15178169970799106939,
            4403065012435293749,
            15306540389399388999,
            8935555081913173844,
        ]
    )
    message_hash = b"".join(
        limb.to_bytes(8, "little")
        for limb in [
            8398652514106806347,
            11069112711939986896,
            9732488227085561369,
            18076754337204438535,
            17155407358725346236,
        ]
    )

    signature = schnorr_sign(message_hash, private_key, nonce)

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
    assert public_key_bytes(1) == (4).to_bytes(8, "little") + bytes(32)


def test_native_lighter_crypto_matches_official_vectors_when_available() -> None:
    native = pytest.importorskip("dcex._native")

    poseidon = bytes(
        native.lighter_poseidon_hash_bytes(
            [
                3451004116618606032,
                11263134342958518251,
                10957204882857370932,
                5369763041201481933,
                7695734348563036858,
                1393419330378128434,
                7387917082382606332,
            ]
        )
    )
    assert _limbs(poseidon) == [
        17992684813643984528,
        5243896189906434327,
        7705560276311184368,
        2785244775876017560,
        14449776097783372302,
    ]

    private_key = _scalar(
        [
            12235002942052073545,
            1175977464658719998,
            8536934969147463310,
            6524687619313720391,
            2922072024880609112,
        ]
    )
    nonce = _scalar(
        [
            5245666847777449560,
            15178169970799106939,
            4403065012435293749,
            15306540389399388999,
            8935555081913173844,
        ]
    )
    message_hash = b"".join(
        limb.to_bytes(8, "little")
        for limb in [
            8398652514106806347,
            11069112711939986896,
            9732488227085561369,
            18076754337204438535,
            17155407358725346236,
        ]
    )

    signature = bytes(
        native.lighter_schnorr_sign(
            message_hash,
            private_key.to_bytes(40, "little"),
            nonce.to_bytes(40, "little"),
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


def test_zero_private_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not reduce to zero"):
        SignerClient(
            url="https://mainnet.zklighter.elliot.ai",
            account_index=12,
            api_private_keys={3: "00" * 40},
        )


def test_create_order_payload_uses_lighter_wire_format(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(signer_module.time, "time", lambda: 1_000.0)
    monkeypatch.setattr(signer_module, "schnorr_sign", lambda *_args: bytes(range(80)))
    client = SignerClient(
        url="https://mainnet.zklighter.elliot.ai",
        account_index=12,
        api_private_keys={3: "01" + "00" * 39},
    )

    tx_type, tx_info, tx_hash, error = client.sign_create_order(
        market_index=4,
        client_order_index=5,
        base_amount=6,
        price=7,
        is_ask=True,
        order_type=0,
        time_in_force=2,
        order_expiry=8,
        integrator_account_index=9,
        integrator_taker_fee=10,
        skip_nonce=1,
        nonce=11,
        api_key_index=3,
    )

    payload = json.loads(tx_info)
    assert error is None
    assert tx_type == 14
    assert len(tx_hash) == 80
    assert payload == {
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
        "Sig": base64.b64encode(bytes(range(80))).decode(),
        "L2TxAttributes": {"1": 9, "2": 10, "4": 1},
    }


def test_auth_token_is_fully_python_signed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(signer_module.time, "time", lambda: 1_000.0)
    client = SignerClient(
        url="https://mainnet.zklighter.elliot.ai",
        account_index=12,
        api_private_keys={3: "01" + "00" * 39},
    )

    token, error = client.create_auth_token_with_expiry(deadline=600, api_key_index=3)

    assert error is None
    expiry, account_index, api_key_index, signature = token.split(":")
    assert (expiry, account_index, api_key_index) == ("1600", "12", "3")
    assert len(bytes.fromhex(signature)) == 80


def test_check_client_data_matches_derived_public_key() -> None:
    client = SignerClient(
        url="https://mainnet.zklighter.elliot.ai",
        account_index=12,
        api_private_keys={3: "01" + "00" * 39},
    )

    error = client.check_client_data(
        {
            "code": 200,
            "api_keys": [
                {
                    "api_key_index": 3,
                    "public_key": public_key_bytes(1).hex(),
                }
            ],
        }
    )

    assert error is None
