"""HTTP manager for Hyperliquid exchange API with optimized authentication and request handling."""

import logging
from dataclasses import dataclass, field
from typing import Any, Self, cast

import httpx
import msgspec
from coincurve import PrivateKey
from Crypto.Hash import keccak

from ..._native_http import NativeResponse, load_native
from ...base.http_manager import BaseHTTPManager
from ...utils.address_utils import address_to_bytes
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

_native = load_native()

HTTP_URL = "https://{SUBDOMAIN}.{DOMAIN}.{TLD}"
SUBDOMAIN_MAIN = "api"
DOMAIN_MAINNET = "hyperliquid"
DOMAIN_TESTNET = "hyperliquid-testnet"
TLD_MAIN = "xyz"


def get_header() -> dict[str, str]:
    """
    Get default HTTP headers for API requests.

    Returns:
        Dict containing Content-Type header
    """
    return {"Content-Type": "application/json"}


@dataclass
class HTTPManager(BaseHTTPManager):
    """
    HTTP manager for Hyperliquid exchange API with optimized authentication and request handling.

    This class provides high-performance HTTP client functionality with optimized cryptographic
    operations using coincurve, pycryptodome, and msgspec for better performance.
    """

    EXCHANGE = Common.HYPERLIQUID

    testnet: bool = field(default=False)
    subdomain: str = field(default=SUBDOMAIN_MAIN)
    tld: str = field(default=TLD_MAIN)
    wallet_address: str | None = field(default=None)
    private_key: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(init=False, default=None)
    ptm: ProductTableManager | None = field(init=False, default=None)
    preload_product_table: bool = field(default=True)
    use_native: bool = field(default=True)
    _native_client: Any | None = field(default=None, init=False, repr=False)

    async def async_init(self) -> Self:
        """
        Initialize the HTTP manager asynchronously.

        Returns:
            Self for method chaining
        """
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.HYPERLIQUID)
        domain = DOMAIN_TESTNET if self.testnet else DOMAIN_MAINNET
        self.endpoint = HTTP_URL.format(SUBDOMAIN=self.subdomain, DOMAIN=domain, TLD=self.tld)
        native_client_type = getattr(_native, "HyperliquidHttpClient", None)
        if self.use_native and native_client_type is not None and self._native_client is None:
            self._native_client = native_client_type(
                testnet=self.testnet,
                wallet_address=self.wallet_address,
                private_key=self.private_key,
                timeout=self.timeout,
                endpoint=self.endpoint,
            )
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    def _uses_native_transport(self) -> bool:
        return (
            self.use_native
            and self._native_client is not None
            and type(self.session) is httpx.AsyncClient
        )

    async def _get_ptm(self) -> ProductTableManager:
        """Lazily obtain the product table manager instance."""
        ptm = self.ptm
        if ptm is None:
            ptm = await ProductTableManager.get_instance(Common.HYPERLIQUID)
            self.ptm = ptm
        return ptm

    def _auth(self, query: dict[str, Any], timestamp: int) -> dict[str, str | int]:
        """
        Generate authentication signature for signed requests.

        Args:
            query: Request query parameters
            timestamp: Request timestamp

        Returns:
            Dict containing signature components (r, s, v)

        Raises:
            ValueError: If private key is not provided
        """
        if not self.private_key:
            raise ValueError("Private key is required for authentication")
        normalized_pk = (
            self.private_key[2:] if self.private_key.startswith("0x") else self.private_key
        )
        private_key = PrivateKey.from_hex(normalized_pk)

        # Use msgspec instead of msgpack, performance improvement 5-8 times
        data = msgspec.msgpack.encode(query["action"])
        data += timestamp.to_bytes(8, "big")

        if query.get("vaultAddress"):
            data += b"\x01"
            data += address_to_bytes(query["vaultAddress"])
        else:
            data += b"\x00"
        if query.get("expireAfter") is not None:
            data += b"\x00"
            data += query["expireAfter"].to_bytes(8, "big")

        # Use pycryptodome instead of eth_utils.keccak, performance improvement 3-5 times
        hash_bytes = keccak.new(digest_bits=256).update(data).digest()
        phantom_agent = {"source": "b" if self.testnet else "a", "connectionId": hash_bytes}

        # EIP712 signature structure
        chain_id = 1337
        domain = {
            "chainId": chain_id,
            "name": "Exchange",
            "verifyingContract": "0x0000000000000000000000000000000000000000",
            "version": "1",
        }

        types = {
            "Agent": [
                {"name": "source", "type": "string"},
                {"name": "connectionId", "type": "bytes32"},
            ],
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
        }

        # Manually implement EIP712 signature (avoid using eth_account)
        encoded_data = self._encode_typed_data(domain, types, "Agent", phantom_agent)
        message_hash = keccak.new(digest_bits=256).update(encoded_data).digest()

        # Use coincurve to sign
        signature = private_key.sign_recoverable(message_hash, hasher=None)

        # Parse signature (use 0/1 for v as expected by Hyperliquid)
        r = signature[:32].hex()
        s = signature[32:64].hex()
        v = int(signature[64]) + 27

        return {"r": r, "s": s, "v": v}

    def _encode_typed_data(
        self,
        domain: dict[str, Any],
        types: dict[str, list],
        primary_type: str,
        message: dict[str, Any],
    ) -> bytes:
        """
        Manually implement EIP712 typed data encoding.

        Args:
            domain: EIP712 domain parameters
            types: Type definitions
            primary_type: Primary type name
            message: Message data

        Returns:
            Encoded typed data bytes
        """
        domain_separator = self._encode_struct_hash(types, "EIP712Domain", domain)

        # Encode message hash
        message_hash = self._encode_struct_hash(types, primary_type, message)

        # EIP-712 digest input (domainSeparator and messageHash are already keccak-256 outputs)
        return b"\x19\x01" + domain_separator + message_hash

    def _encode_struct_hash(
        self, types: dict[str, list], primary_type: str, data: dict[str, Any]
    ) -> bytes:
        """
        Encode struct hash for EIP712.

        Args:
            types: Type definitions
            primary_type: Primary type name
            data: Data to encode

        Returns:
            Encoded struct hash bytes
        """
        # keccak256(encodeType(primaryType))
        type_hash = (
            keccak.new(digest_bits=256)
            .update(self._encode_type(types, primary_type).encode())
            .digest()
        )

        # encodeData(primaryType, data)
        encoded_data = self._encode_data(types, primary_type, data)

        # structHash = keccak256(typeHash || encodedData)
        return keccak.new(digest_bits=256).update(type_hash + encoded_data).digest()

    def _encode_type(self, types: dict[str, list], primary_type: str) -> str:
        """
        Encode type definition for EIP712.

        Args:
            types: Type definitions
            primary_type: Primary type name

        Returns:
            Encoded type definition string
        """
        # Collect all related types (dependencies)
        deps: set[str] = set()
        deps.add(primary_type)
        self._find_type_dependencies(types, primary_type, deps)

        # Build primary type definition first
        def_strs: list[str] = []
        primary_fields = self._encode_type_definition(types.get(primary_type, []))
        def_strs.append(f"{primary_type}({primary_fields})")

        # Append dependency type definitions sorted alphabetically (excluding primary)
        for dep in sorted(t for t in deps if t != primary_type):
            dep_fields = self._encode_type_definition(types.get(dep, []))
            def_strs.append(f"{dep}({dep_fields})")

        return "".join(def_strs)

    def _find_type_dependencies(
        self, types: dict[str, list], primary_type: str, deps: set[str]
    ) -> None:
        """
        Recursively find type dependencies for EIP712.

        Args:
            types: Type definitions
            primary_type: Primary type name
            deps: Set to store dependencies
        """
        if primary_type not in types:
            return

        for field_def in types[primary_type]:
            field_type = field_def["type"]
            if field_type in types and field_type not in deps:
                deps.add(field_type)
                self._find_type_dependencies(types, field_type, deps)

    def _encode_type_definition(self, fields: list[dict[str, str]]) -> str:
        """
        Encode type definition for EIP712.

        Args:
            fields: List of field definitions

        Returns:
            Encoded type definition string
        """
        return ",".join(f"{field['type']} {field['name']}" for field in fields)

    def _encode_data(
        self, types: dict[str, list], primary_type: str, data: dict[str, Any]
    ) -> bytes:
        """
        Encode data for EIP712.

        Args:
            types: Type definitions
            primary_type: Primary type name
            data: Data to encode

        Returns:
            Encoded data bytes
        """
        encoded = b""

        for field_def in types[primary_type]:
            field_name = field_def["name"]
            field_type = field_def["type"]
            value = data[field_name]

            if field_type == "string":
                encoded += keccak.new(digest_bits=256).update(value.encode()).digest()
            elif field_type == "bytes32":
                if isinstance(value, str):
                    encoded += bytes.fromhex(value[2:] if value.startswith("0x") else value)
                else:
                    encoded += value
            elif field_type == "uint256":
                encoded += int(value).to_bytes(32, "big")
            elif field_type == "address":
                addr_bytes = bytes.fromhex(value[2:] if value.startswith("0x") else value)
                encoded += addr_bytes.rjust(32, b"\x00")
            else:
                # Handle other types
                encoded += keccak.new(digest_bits=256).update(str(value).encode()).digest()

        return encoded

    async def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        signed: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to the API.

        Args:
            method: HTTP method (GET, POST)
            path: API path
            query: Query parameters
            signed: Whether to sign the request

        Returns:
            Response data as dictionary

        Raises:
            ValueError: If session not initialized or unsupported method
            FailedRequestError: If request fails
        """
        if self.session is None or self.session.is_closed:
            await self.async_init()

        query = dict(query or {})

        timestamp = int(generate_timestamp())
        uses_native = self._uses_native_transport()

        # Add signing fields before building URL/body so GET also carries signature
        if signed:
            if not (self.wallet_address and self.private_key):
                raise ValueError("Signed request requires Address and Private Key of wallet.")
            if not uses_native:
                query["nonce"] = timestamp
                query["signature"] = self._auth(query, timestamp)

        if method.upper() == "GET" and not uses_native:
            if query:
                from urllib.parse import urlencode

                # URL-encode and sort by key for stability
                sorted_items = sorted((k, v) for k, v in query.items() if v is not None)
                encoded = urlencode(sorted_items, doseq=True, safe="")
                path += ("?" + encoded) if encoded else ""

        headers = get_header()

        url = self.endpoint + path
        self._log_request(method, url)

        try:
            if self.session is None:
                raise ValueError("Session is not initialized")
            if uses_native:
                action_msgpack = (
                    msgspec.msgpack.encode(query["action"])
                    if signed and "action" in query
                    else None
                )
                status, response_headers, response_body = await cast(
                    Any,
                    self._native_client,
                ).request_raw_async(
                    method,
                    path,
                    msgspec.json.encode(query),
                    action_msgpack,
                    signed,
                )
                response = NativeResponse(
                    status,
                    dict(response_headers),
                    bytes(response_body),
                )
            elif method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.session.post(
                    url, headers=headers, json=query if query else {}
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except (httpx.HTTPError, RuntimeError) as e:
            status_code, resp_headers = self._exception_response_details(e)
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {str(e)}",
                status_code=status_code,
                time=str(timestamp),
                resp_headers=resp_headers,
            ) from e
        else:
            self._store_response_headers(response)
            try:
                data = response.json()
            except Exception as exc:
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"Failed to decode JSON response: {exc}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                ) from exc

            if not response.status_code // 100 == 2:
                self._log_failed_request(
                    f"HTTP Error {response.status_code}: {response.text}", response.status_code
                )
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"HTTP Error {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    time=str(timestamp),
                    resp_headers=dict(response.headers),
                )

            return data

    async def close(self) -> None:
        """Close the underlying HTTP session if it exists."""
        if self.session is not None:
            await self.session.aclose()
            self.session = None
