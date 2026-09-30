"""Offline coverage for extended bridge requests."""
# ruff: noqa: ANN001, ANN201, D103

from urllib.parse import parse_qsl, urlsplit

from tests.unit.native_http_helpers import _http_server


def test_extended_commit_bridge_quote_uses_post_query():
    from dcex.extended.client import Client

    with _http_server({"status": "OK", "data": "commitment"}) as (base, received):
        client = Client(api_key="key", base_url=base, preload_product_table=False)
        try:
            client.commit_bridge_quote("quote-123")
        finally:
            client.close()
        request = received.get(timeout=10)
        assert request["method"] == "POST"
        assert urlsplit(request["path"]).path == "/api/v1/user/bridge/quote"
        assert dict(parse_qsl(urlsplit(request["path"]).query)) == {"id": "quote-123"}
        assert request["body"] == ""
