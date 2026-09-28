"""Cross-check new L2 transaction fields against hashes from official lighter-go."""

import json
from pathlib import Path

import pytest

import dcex._native as native
from tests.unit.test_lighter_endpoint_coverage import _signing_native

VECTORS = json.loads(
    (Path(__file__).parents[1] / "fixtures/signing/lighter_withdraw_official.json").read_text(
        encoding="utf-8"
    )
)


def _fields(kind: int, payload: dict[str, object]) -> list[int]:
    account = "FromAccountIndex" if kind == 13 else "AccountIndex"
    keys = ["Nonce", "ExpiredAt", account, "ApiKeyIndex"]
    values = [304, kind, *(int(payload[key]) for key in keys)]
    if kind == 13:
        amount = int(payload["Amount"])
        values.extend(
            [
                int(payload["AssetIndex"]),
                int(payload["RouteType"]),
                amount & 0xFFFFFFFF,
                amount >> 32,
            ]
        )
    else:
        values.extend(
            int(payload[key])
            for key in (
                "IntegratorAccountIndex",
                "MaxPerpsTakerFee",
                "MaxPerpsMakerFee",
                "MaxSpotTakerFee",
                "MaxSpotMakerFee",
                "ApprovalExpiry",
            )
        )
    return values


@pytest.mark.parametrize("case", VECTORS["cases"])
def test_official_withdraw_and_approval_hashes(case: dict) -> None:
    """The independent SDK hashes cover amount splitting and skip-nonce aggregation."""
    payload = case["payload"]
    attributes = [(int(k), v) for k, v in payload.get("L2TxAttributes", {}).items()]
    _, digest = native.lighter_sign_transaction(
        _fields(case["tx_type"], payload),
        attributes,
        json.dumps(payload).encode(),
        (1).to_bytes(40, "little"),
        (2).to_bytes(40, "little"),
    )
    assert bytes(digest).hex() == case["hash"]


@pytest.mark.parametrize("kind", [13, 45])
@pytest.mark.parametrize("skip_nonce", [0, 1])
def test_native_transaction_preserves_every_hashed_field(kind: int, skip_nonce: int) -> None:
    """The actual dispatcher must serialize and hash the same official transaction fields."""
    fields = {"nonce": 5, "api_key_index": 3, "skip_nonce": skip_nonce}
    if kind == 13:
        name = "sign_withdraw_l2"
        fields.update(asset_index=3, route_type=1, amount=(1 << 40) + 123)
    else:
        name = "sign_approve_integrator"
        fields.update(
            integrator_account_index=99,
            max_perps_taker_fee=100,
            max_perps_maker_fee=20,
            max_spot_taker_fee=50,
            max_spot_maker_fee=10,
            approval_expiry=1900000000000,
            l1_signature="0x" + "11" * 64 + "1b",
        )
    tx_type, info, digest, error = _signing_native("http://127.0.0.1:1").sign_request(
        name, [(key, str(value)) for key, value in fields.items()]
    )
    assert (tx_type, error) == (kind, None)
    payload = json.loads(info)
    expected = next(
        c["payload"]
        for c in VECTORS["cases"]
        if c["tx_type"] == kind and c["skip_nonce"] == bool(skip_nonce)
    )
    for key, value in expected.items():
        if key not in {"ExpiredAt", "Sig", "L1Sig", "L2TxAttributes"}:
            assert payload[key] == value
    if kind == 45:
        assert payload["L1Sig"] == fields["l1_signature"]
    assert (payload.get("L2TxAttributes") or {}) == ({"4": 1} if skip_nonce else {})
    _, expected_hash = native.lighter_sign_transaction(
        _fields(kind, payload),
        [(4, 1)] if skip_nonce else [],
        json.dumps(payload).encode(),
        (1).to_bytes(40, "little"),
        (2).to_bytes(40, "little"),
    )
    assert digest == bytes(expected_hash).hex()


@pytest.mark.parametrize(
    "changes",
    [
        {"amount": "0"},
        {"amount": str(1 << 60)},
        {"route_type": "2"},
        {"asset_index": "63"},
        {"price_protection": "true"},
    ],
)
def test_invalid_withdrawal_rejected_before_transport(changes: dict[str, str]) -> None:
    """Invalid raw-unit withdrawals cannot request a nonce or submit funds."""
    fields = {"asset_index": "3", "route_type": "1", "amount": "1000000", **changes}
    with pytest.raises(ValueError):
        _signing_native("http://127.0.0.1:1").private_request_json(
            "withdraw_l2", list(fields.items())
        )


def test_revocation_requires_zero_fees_before_transport() -> None:
    """An expiry of zero cannot accidentally authorize a nonzero fee cap."""
    fields = {
        "integrator_account_index": "99",
        "max_perps_taker_fee": "1",
        "max_perps_maker_fee": "0",
        "max_spot_taker_fee": "0",
        "max_spot_maker_fee": "0",
        "approval_expiry": "0",
        "l1_signature": "0x" + "11" * 64 + "1b",
        "nonce": "5",
    }
    with pytest.raises(ValueError, match="revocation"):
        _signing_native("http://127.0.0.1:1").private_request_json(
            "approve_integrator", list(fields.items())
        )
