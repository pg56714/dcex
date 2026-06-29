# ruff: noqa: D100, D103

import json
import queue
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


@contextmanager
def _http_server(
    response_payload: dict[str, Any] | None = None,
    response_status: int = 200,
) -> Iterator[tuple[str, queue.Queue[dict[str, Any]]]]:
    received: queue.Queue[dict[str, Any]] = queue.Queue()
    response_payload = response_payload or {"ok": True}

    class Handler(BaseHTTPRequestHandler):
        def _handle(self) -> None:
            request = {
                "path": self.path,
                "header": self.headers.get("X-Test"),
                "api_key": self.headers.get("X-MBX-APIKEY"),
            }
            if bingx_api_key := self.headers.get("X-BX-APIKEY"):
                request["bingx_api_key"] = bingx_api_key
            for header in (
                "X-MEXC-APIKEY",
                "ApiKey",
                "Request-Time",
                "Signature",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            if value := self.headers.get("api-key"):
                request["bitmex_api_key"] = value
            for header in ("api-signature", "api-expires"):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("X-BM-KEY", "X-BM-SIGN", "X-BM-TIMESTAMP", "X-BM-MEMO"):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "ACCESS-KEY",
                "ACCESS-SIGN",
                "ACCESS-TIMESTAMP",
                "ACCESS-PASSPHRASE",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "X-BAPI-API-KEY",
                "X-BAPI-SIGN",
                "X-BAPI-TIMESTAMP",
                "X-BAPI-RECV-WINDOW",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("KEY", "Timestamp", "SIGN"):
                if value := self.headers.get(header):
                    request[f"gateio_{header.lower()}"] = value
            for header in (
                "OK-ACCESS-KEY",
                "OK-ACCESS-SIGN",
                "OK-ACCESS-TIMESTAMP",
                "OK-ACCESS-PASSPHRASE",
                "x-simulated-trading",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in (
                "KC-API-KEY",
                "KC-API-SIGN",
                "KC-API-TIMESTAMP",
                "KC-API-PASSPHRASE",
                "KC-API-KEY-VERSION",
            ):
                if value := self.headers.get(header):
                    request[header] = value
            for header in ("API-Key", "API-Sign", "APIKey", "Authent", "Nonce"):
                if value := self.headers.get(header):
                    request[f"kraken_{header.lower()}"] = value
            for header in ("X-API-Key", "X-Signature", "X-Timestamp", "X-Window"):
                if value := self.headers.get(header):
                    request[f"backpack_{header.lower()}"] = value
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length:
                request["body"] = self.rfile.read(content_length).decode()
            received.put(request)
            payload = (
                {"serverTime": 1}
                if self.path.split("?", 1)[0] in {"/api/v3/time", "/fapi/v1/time"}
                else response_payload
            )
            body = json.dumps(payload, separators=(",", ":")).encode()
            self.send_response(response_status)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-Response", "native")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_DELETE(self) -> None:  # noqa: N802
            self._handle()

        def do_GET(self) -> None:  # noqa: N802
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def do_PUT(self) -> None:  # noqa: N802
            self._handle()

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", received
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
