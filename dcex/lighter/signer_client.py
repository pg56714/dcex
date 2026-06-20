"""Lighter private-request signer backed by Rust native helpers."""

from __future__ import annotations

import base64
import importlib
import json
import secrets
import time
from types import ModuleType
from typing import Any

from ._crypto import (
    poseidon_hash_bytes,
    private_key_from_bytes,
    public_key_bytes,
    schnorr_sign,
)

_UINT64_MASK = (1 << 64) - 1
_SCALAR_ORDER = int(
    "106799351671714695104148491657179270274505774058172723015913968518"
    "5762082554198619328292418486241"
)
_DEFAULT_TX_EXPIRY_MS = 590_000
_DEFAULT_ORDER_EXPIRY_MS = 28 * 24 * 60 * 60 * 1000

try:
    _NATIVE: ModuleType | None = importlib.import_module("dcex._native")
except ImportError:
    _NATIVE = None


def _field(value: int) -> int:
    return int(value) & _UINT64_MASK


def _attributes(
    *,
    integrator_account_index: int = 0,
    integrator_taker_fee: int = 0,
    integrator_maker_fee: int = 0,
    skip_nonce: int = 0,
    cancel_all_market_index: int = 255,
) -> dict[int, int]:
    result: dict[int, int] = {}
    if integrator_account_index:
        result[1] = integrator_account_index
    if integrator_taker_fee:
        result[2] = integrator_taker_fee
    if integrator_maker_fee:
        result[3] = integrator_maker_fee
    if skip_nonce == 1:
        result[4] = 1
    if cancel_all_market_index != 255:
        result[5] = cancel_all_market_index
    return result


def _hash_attributes(attributes: dict[int, int]) -> bytes | None:
    if not attributes:
        return None
    values: list[int] = []
    normalized_types = sorted(attributes)[:4]
    normalized_types.extend([0] * (4 - len(normalized_types)))
    for attribute_type in normalized_types:
        values.extend((attribute_type, attributes.get(attribute_type, 0)))
    return poseidon_hash_bytes(values)


def _transaction_hash(values: list[int], attributes: dict[int, int]) -> bytes:
    transaction_hash = poseidon_hash_bytes([_field(value) for value in values])
    attributes_hash = _hash_attributes(attributes)
    if attributes_hash is None:
        return transaction_hash
    combined = [
        int.from_bytes(value[offset : offset + 8], "little")
        for value in (transaction_hash, attributes_hash)
        for offset in range(0, 40, 8)
    ]
    return poseidon_hash_bytes(combined)


class SignerClient:
    """Create Lighter auth tokens and signed transaction payloads."""

    def __init__(
        self,
        url: str,
        account_index: int,
        api_private_keys: dict[int, str],
    ) -> None:
        if not api_private_keys:
            raise ValueError("Lighter private signing requires at least one API private key.")
        self.url = url.rstrip("/")
        self.chain_id = 304 if "mainnet" in url or "api" in url else 300
        self.account_index = int(account_index)
        self.api_private_keys = {
            int(index): self._normalize_private_key(key) for index, key in api_private_keys.items()
        }

    @staticmethod
    def _normalize_private_key(private_key: str) -> int:
        normalized = private_key.removeprefix("0x")
        try:
            key_bytes = bytes.fromhex(normalized)
        except ValueError as exc:
            raise ValueError("Lighter API private key must be hexadecimal.") from exc
        return private_key_from_bytes(key_bytes)

    def _private_key(self, api_key_index: int) -> int:
        if api_key_index == 255:
            if len(self.api_private_keys) != 1:
                raise ValueError("Lighter API key index is ambiguous.")
            return next(iter(self.api_private_keys.values()))
        try:
            return self.api_private_keys[api_key_index]
        except KeyError as exc:
            raise ValueError(f"Lighter API key index {api_key_index} is not configured.") from exc

    def _sign_transaction(
        self,
        tx_type: int,
        values: list[int],
        payload: dict[str, Any],
        attributes: dict[int, int],
        api_key_index: int,
    ) -> tuple[int, str, str, None]:
        if _NATIVE is not None and hasattr(_NATIVE, "lighter_sign_transaction"):
            nonce_scalar = secrets.randbelow(_SCALAR_ORDER - 1) + 1
            tx_info, message_hash = _NATIVE.lighter_sign_transaction(
                values,
                list(attributes.items()),
                json.dumps(payload, separators=(",", ":")).encode(),
                self._private_key(api_key_index).to_bytes(40, "little"),
                nonce_scalar.to_bytes(40, "little"),
            )
            return tx_type, bytes(tx_info).decode(), bytes(message_hash).hex(), None
        message_hash = _transaction_hash(values, attributes)
        payload["Sig"] = base64.b64encode(
            schnorr_sign(message_hash, self._private_key(api_key_index))
        ).decode()
        payload["L2TxAttributes"] = attributes or None
        return tx_type, json.dumps(payload, separators=(",", ":")), message_hash.hex(), None

    @staticmethod
    def _expiry_ms() -> int:
        return int(time.time() * 1000) + _DEFAULT_TX_EXPIRY_MS

    def create_auth_token_with_expiry(
        self,
        deadline: int = -1,
        *,
        timestamp: int = 0,
        api_key_index: int = 255,
    ) -> tuple[str, None]:
        """Create a signed Lighter read-only authentication token."""
        if deadline == -1:
            deadline = 600
        if timestamp == 0:
            timestamp = int(time.time())
        expiry = deadline + timestamp
        message = f"{expiry}:{self.account_index}:{api_key_index}"
        if _NATIVE is not None and hasattr(_NATIVE, "lighter_auth_token"):
            nonce_scalar = secrets.randbelow(_SCALAR_ORDER - 1) + 1
            token = _NATIVE.lighter_auth_token(
                expiry,
                self.account_index,
                api_key_index,
                self._private_key(api_key_index).to_bytes(40, "little"),
                nonce_scalar.to_bytes(40, "little"),
            )
            return str(token), None
        encoded = message.encode()
        fields = [
            int.from_bytes(encoded[offset : offset + 8].ljust(8, b"\0"), "little")
            for offset in range(0, len(encoded), 8)
        ]
        message_hash = poseidon_hash_bytes(fields)
        signature = schnorr_sign(message_hash, self._private_key(api_key_index)).hex()
        return f"{message}:{signature}", None

    def check_client(self) -> str | None:
        """Check configured private keys against Lighter public keys."""
        if _NATIVE is None or not hasattr(_NATIVE, "LighterHttpClient"):
            return "failed to get API keys: dcex._native is required"
        try:
            client = _NATIVE.LighterHttpClient(timeout=10, base_url=self.url)
            _status, _headers, body = client.public_request(
                "get_api_keys",
                [("account_index", str(self.account_index))],
            )
            data = json.loads(bytes(body))
        except (RuntimeError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return f"failed to get API keys: {exc}"
        return self.check_client_data(data)

    def check_client_data(self, data: object) -> str | None:
        """Check configured private keys against an API key response."""
        if not isinstance(data, dict) or data.get("code") not in {None, 0, 200, "0", "200"}:
            return f"failed to get API keys: {data!r}"
        api_keys = data.get("api_keys")
        if not isinstance(api_keys, list):
            return f"failed to get API keys: {data!r}"
        try:
            remote_keys = {
                int(item["api_key_index"]): str(item["public_key"]).removeprefix("0x").lower()
                for item in api_keys
                if isinstance(item, dict) and "api_key_index" in item and "public_key" in item
            }
        except (TypeError, ValueError):
            return f"failed to get API keys: {data!r}"
        for api_key_index, private_key in self.api_private_keys.items():
            own_key = public_key_bytes(private_key).hex()
            if remote_keys.get(api_key_index) != own_key:
                return f"private key does not match the one on Lighter on api key {api_key_index}"
        return None

    def sign_create_order(
        self,
        market_index: int,
        client_order_index: int,
        base_amount: int,
        price: int,
        is_ask: bool,
        order_type: int,
        time_in_force: int,
        reduce_only: bool = False,
        trigger_price: int = 0,
        order_expiry: int = -1,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign a create-order transaction."""
        expiry = self._expiry_ms()
        if order_expiry == -1:
            order_expiry = int(time.time() * 1000) + _DEFAULT_ORDER_EXPIRY_MS
        attributes = _attributes(
            integrator_account_index=integrator_account_index,
            integrator_taker_fee=integrator_taker_fee,
            integrator_maker_fee=integrator_maker_fee,
            skip_nonce=skip_nonce,
        )
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "ClientOrderIndex": client_order_index,
            "BaseAmount": base_amount,
            "Price": price,
            "IsAsk": int(is_ask),
            "Type": order_type,
            "TimeInForce": time_in_force,
            "ReduceOnly": int(reduce_only),
            "TriggerPrice": trigger_price,
            "OrderExpiry": order_expiry,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            14,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            market_index,
            client_order_index,
            base_amount,
            price,
            int(is_ask),
            order_type,
            time_in_force,
            int(reduce_only),
            trigger_price,
            order_expiry,
        ]
        return self._sign_transaction(14, values, payload, attributes, api_key_index)

    def sign_cancel_order(
        self,
        market_index: int,
        order_index: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign a cancel-order transaction."""
        expiry = self._expiry_ms()
        attributes = _attributes(skip_nonce=skip_nonce)
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "Index": order_index,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            15,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            market_index,
            order_index,
        ]
        return self._sign_transaction(15, values, payload, attributes, api_key_index)

    def sign_modify_order(
        self,
        market_index: int,
        order_index: int,
        base_amount: int,
        price: int,
        trigger_price: int = 0,
        *,
        integrator_account_index: int = 0,
        integrator_taker_fee: int = 0,
        integrator_maker_fee: int = 0,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign a modify-order transaction."""
        expiry = self._expiry_ms()
        attributes = _attributes(
            integrator_account_index=integrator_account_index,
            integrator_taker_fee=integrator_taker_fee,
            integrator_maker_fee=integrator_maker_fee,
            skip_nonce=skip_nonce,
        )
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "Index": order_index,
            "BaseAmount": base_amount,
            "Price": price,
            "TriggerPrice": trigger_price,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            17,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            market_index,
            order_index,
            base_amount,
            price,
            trigger_price,
        ]
        return self._sign_transaction(17, values, payload, attributes, api_key_index)

    def sign_cancel_all_orders(
        self,
        time_in_force: int,
        timestamp_ms: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign a cancel-all-orders transaction."""
        expiry = self._expiry_ms()
        attributes = _attributes(skip_nonce=skip_nonce)
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "TimeInForce": time_in_force,
            "Time": timestamp_ms,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            16,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            time_in_force,
            timestamp_ms,
        ]
        return self._sign_transaction(16, values, payload, attributes, api_key_index)

    def sign_update_leverage(
        self,
        market_index: int,
        fraction: int,
        margin_mode: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign an update-leverage transaction."""
        expiry = self._expiry_ms()
        attributes = _attributes(skip_nonce=skip_nonce)
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "InitialMarginFraction": fraction,
            "MarginMode": margin_mode,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            20,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            market_index,
            fraction,
            margin_mode,
        ]
        return self._sign_transaction(20, values, payload, attributes, api_key_index)

    def sign_update_margin(
        self,
        market_index: int,
        usdc_amount: int,
        direction: int,
        skip_nonce: int = 0,
        nonce: int = -1,
        api_key_index: int = 255,
    ) -> tuple[int, str, str, None]:
        """Sign an update-margin transaction."""
        expiry = self._expiry_ms()
        attributes = _attributes(skip_nonce=skip_nonce)
        payload = {
            "AccountIndex": self.account_index,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "USDCAmount": usdc_amount,
            "Direction": direction,
            "ExpiredAt": expiry,
            "Nonce": nonce,
        }
        values = [
            self.chain_id,
            29,
            nonce,
            expiry,
            self.account_index,
            api_key_index,
            market_index,
            usdc_amount & 0xFFFFFFFF,
            usdc_amount >> 32,
            direction,
        ]
        return self._sign_transaction(29, values, payload, attributes, api_key_index)

    def close(self) -> None:
        """Release signer resources."""
