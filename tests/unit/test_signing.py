"""
Offline signing unit tests.

These tests pin each exchange's signature algorithm against known-good outputs
computed from fixed fake credentials and a fixed timestamp. They require no API
keys and make no network calls (``preload_product_table=False`` keeps the HTTP
managers offline), so they are safe to run in CI on every push.

The golden signatures below were captured once from the current implementation
and independently cross-checked against a direct HMAC computation. Their job is
to fail loudly if a refactor ever changes signing behaviour.
"""

import base64
import hashlib
import hmac
from importlib import import_module
from urllib.parse import urlencode

import pytest
from coincurve import PrivateKey
from Crypto.Hash import keccak

# Fixed, fake credentials shared across the tests. Not real secrets.
API_KEY = "test_api_key_0000"
API_SECRET = "test_api_secret_0000"
MEMO = "test_memo"
TS_MS = 1700000000000
TS_S = "1700000000"
RECV_WINDOW = 5000


class _FakeResponse:
    def __init__(self, payload: dict, status_code: int = 200, text: str = "") -> None:
        self._payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}
        self.text = text

    def json(self) -> dict:
        return self._payload


class _CaptureBitmartSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict]] = []

    def get(self, url: str, **kwargs: object) -> _FakeResponse:
        self.calls.append(("GET", url, kwargs))
        return _FakeResponse({"code": 1000})

    def post(self, url: str, **kwargs: object) -> _FakeResponse:
        self.calls.append(("POST", url, kwargs))
        return _FakeResponse({"code": 1000})


def test_aster_eip712_signature_recovers_signer() -> None:
    """Aster EIP-712 signatures recover the wallet that signed the message."""
    from dcex.aster._http_manager import _eip712_digest, sign_message

    private_key = "0x" + "11" * 32
    message = (
        "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001"
        "&nonce=1700000000000000"
        "&signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"
    )
    signature = bytes.fromhex(sign_message(message, private_key).removeprefix("0x"))
    recoverable = signature[:64] + bytes([signature[64] - 27])
    public_key = PrivateKey(bytes.fromhex(private_key.removeprefix("0x"))).public_key
    recovered = public_key.from_signature_and_message(
        recoverable,
        _eip712_digest(message),
        hasher=None,
    )
    digest = keccak.new(digest_bits=256)
    digest.update(recovered.format(compressed=False)[1:])

    assert f"0x{digest.digest()[-20:].hex()}" == ("0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a")


def test_binance_sign_matches_hmac_sha256() -> None:
    """Binance signs urlencoded params with HMAC-SHA256 (hex)."""
    from dcex.binance._http_manager import HTTPManager

    manager = HTTPManager(api_secret=API_SECRET, preload_product_table=False)
    params = {"symbol": "BTCUSDT", "timestamp": TS_MS, "recvWindow": RECV_WINDOW}

    signature = manager._sign(params)

    expected = hmac.new(API_SECRET.encode(), urlencode(params).encode(), hashlib.sha256).hexdigest()
    assert signature == expected
    assert signature == "b64fbb3537cfe45d61d16ef4426dcb9c1f86e5a438660d4d25fb0cf541817c48"


def test_binance_sign_requires_secret() -> None:
    """Binance signing raises a clear error without a secret."""
    import pytest

    from dcex.binance._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    with pytest.raises(ValueError, match="secret"):
        manager._sign({"symbol": "BTCUSDT"})


def test_okx_sign_matches_hmac_sha256_base64() -> None:
    """OKX signs the pre-hash string with HMAC-SHA256 (base64)."""
    from dcex.okx._http_manager import _sign, pre_hash

    message = pre_hash(TS_S, "GET", "/api/v5/account/balance", "")
    assert message == "1700000000GET/api/v5/account/balance"

    signature = _sign(message, API_SECRET)

    expected = base64.b64encode(
        hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).digest()
    ).decode()
    assert signature == expected
    assert signature == "Ls74ct2P5Xi0SXq7smDS5O2D8cy4VmItOq3VDxnTQYE="


def test_bybit_auth_matches_hmac_sha256() -> None:
    """Bybit signs ``timestamp+key+recv_window+payload`` with HMAC-SHA256."""
    from dcex.bybit._http_manager import HTTPManager

    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        recv_window=RECV_WINDOW,
        preload_product_table=False,
    )
    payload = "symbol=BTCUSDT&category=linear"

    signature = manager._auth(payload, TS_MS)

    expected = hmac.new(
        API_SECRET.encode(),
        f"{TS_MS}{API_KEY}{RECV_WINDOW}{payload}".encode(),
        hashlib.sha256,
    ).hexdigest()
    assert signature == expected
    assert signature == "19d2105cd8e63df9c9c40f77abeba86ad80851cf4b89bb0487d9062defaf21b8"


def test_bitmart_sign_matches_hmac_sha256() -> None:
    """BitMart signs ``timestamp#memo#body`` with HMAC-SHA256."""
    from dcex.bitmart._http_manager import sign_message

    body = '{"symbol":"BTCUSDT"}'

    signature = sign_message(TS_MS, MEMO, body, API_SECRET)

    expected = hmac.new(
        API_SECRET.encode(), f"{TS_MS}#{MEMO}#{body}".encode(), hashlib.sha256
    ).hexdigest()
    assert signature == expected
    assert signature == "a5a38bab707890a577d96959ca82a1b7a4c0db7ffd9b40ba17b20ad57932a542"


def test_bitmart_signed_get_uses_empty_body_for_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """BitMart signed GET signs an empty body and sends params in the URL."""
    from dcex.bitmart._http_manager import HTTPManager, sign_message
    from dcex.bitmart.endpoints.account import FundingAccount

    bitmart_http = import_module("dcex.bitmart._http_manager")
    monkeypatch.setattr(bitmart_http, "generate_timestamp", lambda: TS_MS)
    session = _CaptureBitmartSession()
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        memo=MEMO,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "GET",
        FundingAccount.GET_ACCOUNT_BALANCE,
        query={"currency": "USDT"},
        signed=True,
    )

    method, url, kwargs = session.calls[0]
    expected_sign = sign_message(TS_MS, MEMO, "", API_SECRET)
    assert method == "GET"
    assert url.endswith("/account/v1/wallet?currency=USDT")
    assert kwargs["headers"]["X-BM-SIGN"] == expected_sign


def test_bitmart_signed_post_sends_the_exact_body_used_for_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """BitMart signed POST uses the same compact JSON string for signing and body."""
    from dcex.bitmart._http_manager import HTTPManager, sign_message
    from dcex.bitmart.endpoints.trade import SpotTrade

    bitmart_http = import_module("dcex.bitmart._http_manager")
    monkeypatch.setattr(bitmart_http, "generate_timestamp", lambda: TS_MS)
    session = _CaptureBitmartSession()
    manager = HTTPManager(
        api_key=API_KEY,
        api_secret=API_SECRET,
        memo=MEMO,
        preload_product_table=False,
    )
    manager.session = session  # type: ignore[assignment]

    manager._request(
        "POST",
        SpotTrade.SUBMIT_ORDER,
        query={"symbol": "BTC_USDT", "side": "buy", "type": "market", "size": "1"},
        signed=True,
    )

    method, _url, kwargs = session.calls[0]
    body = '{"symbol":"BTC_USDT","side":"buy","type":"market","size":"1"}'
    expected_sign = sign_message(TS_MS, MEMO, body, API_SECRET)
    assert method == "POST"
    assert kwargs["data"] == body
    assert "json" not in kwargs
    assert kwargs["headers"]["X-BM-SIGN"] == expected_sign


def test_bitmex_sign_matches_hmac_sha256() -> None:
    """BitMEX signs ``method+path+expires+body`` with HMAC-SHA256."""
    from dcex.bitmex._http_manager import HTTPManager

    manager = HTTPManager(api_secret=API_SECRET, preload_product_table=False)
    expires = 1700000005

    signature = manager._sign("GET", "/api/v1/order", expires, "")

    expected = hmac.new(
        API_SECRET.encode(),
        f"GET/api/v1/order{expires}".encode(),
        hashlib.sha256,
    ).hexdigest()
    assert signature == expected
    assert signature == "e3b74b1d2d858717fdaf0211e18b11f87f402811570391bc962cc626ab3e7bf0"


def test_gateio_sign_matches_hmac_sha512() -> None:
    """Gate.io signs the canonical request string with HMAC-SHA512."""
    from dcex.gateio._http_manager import HTTPManager

    manager = HTTPManager(api_secret=API_SECRET, preload_product_table=False)
    query = {"a": "1"}
    body = {"b": "2"}

    signature = manager._sign("POST", "/api/v4/spot/orders", query, body, TS_S)

    # Recompute independently to document the canonical string layout.
    payload_string = '{"b":"2"}'
    hashed_payload = hashlib.sha512(payload_string.encode()).hexdigest()
    query_string = "a=1"
    canonical = f"POST\n/api/v4/spot/orders\n{query_string}\n{hashed_payload}\n{TS_S}"
    expected = hmac.new(API_SECRET.encode(), canonical.encode(), hashlib.sha512).hexdigest()
    assert signature == expected
    assert signature == (
        "3a314366c1367344b6abbad3a7f0b0519a5f1f606acde4c269a8cada67d7ddbd"
        "33504564f284bd0f8f7be971075a6ef0f8a47f95f310cad579fdb483f0330b7a"
    )


def test_hyperliquid_auth_is_deterministic_eip712() -> None:
    """Hyperliquid wallet signing is deterministic for fixed input."""
    from dcex.hyperliquid._http_manager import HTTPManager

    private_key = "0x" + "11" * 32
    manager = HTTPManager(
        private_key=private_key,
        wallet_address="0x" + "22" * 20,
        preload_product_table=False,
    )
    action = {"action": {"type": "order", "a": 1}}

    signature = manager._auth(dict(action), TS_MS)

    # ECDSA over a fixed message hash is deterministic (RFC 6979).
    assert signature == {
        "r": "193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671",
        "s": "0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047",
        "v": 27,
    }


def test_hyperliquid_auth_requires_private_key() -> None:
    """Hyperliquid signing raises a clear error without a private key."""
    import pytest

    from dcex.hyperliquid._http_manager import HTTPManager

    manager = HTTPManager(preload_product_table=False)
    with pytest.raises(ValueError, match="[Pp]rivate key"):
        manager._auth({"action": {"type": "order"}}, TS_MS)
