"""Kraken ZIP transport and independent Spot authentication regression tests."""

from __future__ import annotations
import base64
import hashlib
import hmac
from urllib.parse import parse_qsl
import pytest
from dcex import _native
from tests.unit.native_http_helpers import _http_server


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("server_error", [False, True])
async def test_report_zip_preserves_binary_and_checks_api_errors(
    asynchronous: bool, server_error: bool
) -> None:
    report = b"PK\x03\x04\x00\xff\x80binary-report"
    with _http_server(
        {"error": ["EGeneral:Report not ready"]},
        response_bytes=None if server_error else report,
        content_type="application/json" if server_error else "application/zip",
    ) as (base, received):
        client = _native.KrakenHttpClient(
            spot_api_key="key",
            spot_api_secret=base64.b64encode(b"secret").decode(),
            spot_base_url=base,
        )
        if server_error:
            with pytest.raises(Exception, match="Report not ready"):
                if asynchronous:
                    await client.retrieve_spot_export_async("report1")
                else:
                    client.retrieve_spot_export("report1")
        elif asynchronous:
            assert await client.retrieve_spot_export_async("report1") == report
        else:
            assert client.retrieve_spot_export("report1") == report
    request = received.get_nowait()
    assert request["method"] == "POST"
    assert request["path"] == "/0/private/RetrieveExport"
    fields = dict(parse_qsl(request["body"]))
    assert fields["id"] == "report1"
    digest = hashlib.sha256((fields["nonce"] + request["body"]).encode()).digest()
    assert (
        request["kraken_api-sign"]
        == base64.b64encode(
            hmac.new(b"secret", request["path"].encode() + digest, hashlib.sha512).digest()
        ).decode()
    )
