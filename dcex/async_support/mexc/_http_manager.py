"""MEXC asynchronous HTTP manager."""

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Literal, Self
from urllib.parse import urlencode

import httpx

from ...base.http_manager import BaseHTTPManager
from ...utils.common import Common
from ...utils.errors import FailedRequestError
from ...utils.helpers import generate_timestamp
from ..product_table.manager import ProductTableManager

RequestPayload = dict[str, Any] | list[Any]


def _format_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _filtered_query(query: RequestPayload | None) -> RequestPayload:
    if isinstance(query, list):
        return [
            {key: value for key, value in item.items() if value is not None}
            if isinstance(item, dict)
            else item
            for item in query
        ]
    return {key: value for key, value in (query or {}).items() if value is not None}


def _encoded_query(query: dict[str, Any], *, sort: bool = False) -> str:
    items = sorted(query.items()) if sort else query.items()
    return urlencode({key: _format_value(value) for key, value in items}, doseq=True)


def _json_body(query: RequestPayload) -> str:
    return json.dumps(query, separators=(",", ":"), ensure_ascii=False) if query else ""


def _sign(payload: str, api_secret: str) -> str:
    return hmac.new(api_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


@dataclass
class HTTPManager(BaseHTTPManager):
    """HTTP manager for MEXC Spot V3 and Contract V1 REST APIs."""

    EXCHANGE = Common.MEXC

    base_url: str = field(default="https://api.mexc.com")
    contract_base_url: str | None = field(default=None)
    api_key: str | None = field(default=None, repr=False)
    api_secret: str | None = field(default=None, repr=False)
    timeout: int = field(default=10)
    logger: logging.Logger | None = field(default=None)
    session: httpx.AsyncClient | None = field(default=None, init=False)
    ptm: ProductTableManager = field(init=False)
    preload_product_table: bool = field(default=True)

    async def async_init(self) -> Self:
        """Initialize async HTTP manager."""
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        self._logger = self._setup_logger(self.logger)
        if self.preload_product_table:
            self.ptm = await ProductTableManager.get_instance(Common.MEXC)
        return self

    async def __aenter__(self) -> Self:
        if self.session is None or self.session.is_closed:
            await self.async_init()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()

    def _headers(
        self,
        *,
        signed: bool,
        api: Literal["spot", "contract"],
        request_time: str | None = None,
        signature: str | None = None,
    ) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if not signed:
            return headers
        if not (self.api_key and self.api_secret):
            raise ValueError("Signed MEXC requests require api_key and api_secret.")
        if api == "spot":
            headers["X-MEXC-APIKEY"] = self.api_key
        else:
            if request_time is None or signature is None:
                raise ValueError("Contract signed requests require request_time and signature.")
            headers.update(
                {
                    "ApiKey": self.api_key,
                    "Request-Time": request_time,
                    "Signature": signature,
                }
            )
        return headers

    def _prepare_spot_request(
        self,
        query: dict[str, Any],
        signed: bool,
    ) -> tuple[str, str | None, dict[str, str]]:
        if not signed:
            return _encoded_query(query), None, self._headers(signed=False, api="spot")
        query = dict(query)
        query.setdefault("timestamp", int(time.time() * 1000))
        query_string = _encoded_query(query)
        query["signature"] = _sign(query_string, self.api_secret or "")
        signed_query_string = _encoded_query(query)
        return signed_query_string, None, self._headers(signed=True, api="spot")

    def _prepare_contract_request(
        self,
        method: str,
        query: RequestPayload,
        signed: bool,
    ) -> tuple[str, str | None, dict[str, str]]:
        if not signed:
            query_string = _encoded_query(query) if isinstance(query, dict) else ""
            body = _json_body(query) if method.upper() not in {"GET", "DELETE"} else None
            return query_string, body, self._headers(signed=False, api="contract")

        request_time = str(int(time.time() * 1000))
        if method.upper() in {"GET", "DELETE"}:
            if not isinstance(query, dict):
                raise TypeError("MEXC Contract GET and DELETE requests require a mapping query.")
            query_string = _encoded_query(query, sort=True)
            body = None
            request_param = query_string
        else:
            query_string = ""
            body = _json_body(query)
            request_param = body or ""
        signature = _sign(f"{self.api_key}{request_time}{request_param}", self.api_secret or "")
        headers = self._headers(
            signed=True,
            api="contract",
            request_time=request_time,
            signature=signature,
        )
        return query_string, body, headers

    async def _request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        query: RequestPayload | None = None,
        signed: bool = True,
        api: Literal["spot", "contract"] = "spot",
    ) -> dict[str, Any] | list[Any]:
        """Make an HTTP request to MEXC REST APIs."""
        if self.session is None or self.session.is_closed:
            await self.async_init()
        if self.session is None:
            raise RuntimeError("Failed to initialize HTTP session.")

        request_path = str(path)
        filtered_query = _filtered_query(query)
        base_url = (self.contract_base_url or self.base_url) if api == "contract" else self.base_url
        url = f"{base_url}{request_path}"

        if api == "contract":
            query_string, body, headers = self._prepare_contract_request(
                method,
                filtered_query,
                signed,
            )
        else:
            if not isinstance(filtered_query, dict):
                raise TypeError("MEXC Spot requests require a mapping query.")
            query_string, body, headers = self._prepare_spot_request(filtered_query, signed)

        if query_string:
            url = f"{url}?{query_string}"

        response = None
        try:
            self._log_request(method, url)
            method_upper = method.upper()
            if method_upper == "GET":
                response = await self.session.get(url, headers=headers)
            elif method_upper == "POST":
                response = await self.session.post(url, headers=headers, content=body)
            elif method_upper == "PUT":
                response = await self.session.put(url, headers=headers, content=body)
            elif method_upper == "DELETE":
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except httpx.RequestError as exc:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Request failed: {exc}",
                status_code=response.status_code if response else "Unknown",
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers) if response else None,
            ) from exc

        self._store_response_headers(response)
        try:
            data = response.json()
        except Exception as exc:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"Failed to decode JSON response: {exc}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            ) from exc

        if response.status_code // 100 != 2:
            raise FailedRequestError(
                request=f"{method.upper()} {url} | Body: {query}",
                message=f"HTTP Error {response.status_code}: {response.text}",
                status_code=response.status_code,
                time=str(generate_timestamp(iso_format=True)),
                resp_headers=dict(response.headers),
            )

        if isinstance(data, dict):
            code = data.get("code")
            success = data.get("success")
            if success is False or (code is not None and code not in {0, "0", 200, "200"}):
                message = data.get("msg") or data.get("message") or "Unknown error"
                raise FailedRequestError(
                    request=f"{method.upper()} {url} | Body: {query}",
                    message=f"MEXC API Error: [{code}] {message}",
                    status_code=response.status_code,
                    time=str(generate_timestamp(iso_format=True)),
                    resp_headers=dict(response.headers),
                )

        return data

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session is not None and not self.session.is_closed:
            await self.session.aclose()
