"""Read route expectations from the independently executed endpoint test suites."""

from __future__ import annotations

import importlib
import json
import re
from functools import cache
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
EXCHANGES = (
    "binance",
    "bybit",
    "okx",
    "bitget",
    "bingx",
    "mexc",
    "kucoin",
    "kraken",
    "aster",
    "arcus",
    "backpack",
    "extended",
    "ondo",
    "hyperliquid",
    "lighter",
)


class RouteEvidence(NamedTuple):
    """A method and route that an offline suite actually exercises."""

    exchange: str
    name: str
    method: str
    path: str
    selector: str
    evidence: str


@cache
def _path_pattern(template: str) -> re.Pattern[str]:
    template = unquote(template.split("?", 1)[0]).rstrip("/") or "/"
    template = re.sub(r"(?<=/):([A-Za-z_][\w]*)", r"{\1}", template)
    pattern = re.sub(r"\\\{[^{}]+\\\}", "[^/]+", re.escape(template))
    return re.compile(pattern)


def path_matches(template: str, actual: str) -> bool:
    """Match a documented path template against a concrete fixture path."""
    actual = unquote(actual.split("?", 1)[0]).rstrip("/") or "/"
    return _path_pattern(template).fullmatch(actual) is not None


def route_key(path: str) -> str:
    """Compare documented routes without confusing named routes with parameters."""
    path = unquote(path.split("?", 1)[0]).rstrip("/") or "/"
    path = re.sub(r"(?<=/):[A-Za-z_][\w]*", "{}", path)
    return re.sub(r"\{[^{}]+\}", "{}", path)


@cache
def literal_routes(exchange: str, method: str) -> frozenset[str]:
    """Reserved literal paths must not masquerade as dynamic resource IDs."""
    inventory = json.loads(
        (ROOT / f"docs/official-endpoint-inventory/{exchange}.json").read_text(encoding="utf-8")
    )
    return frozenset(
        route_key(e["path"])
        for e in inventory["endpoints"]
        if e["method"].upper() == method and "{}" not in route_key(e["path"])
    )


def wire_route_matches(exchange: str, method: str, template: str, actual: str) -> bool:
    """A literal route wins over a parameterized route of the same shape."""
    if "{}" in route_key(template) and route_key(actual) in literal_routes(exchange, method):
        return False
    return path_matches(template, actual)


@cache
def route_evidence() -> tuple[RouteEvidence, ...]:
    """Collect route tables; the normal Rust/Python suites validate their wire output."""
    result: set[RouteEvidence] = set()

    def add(
        exchange: str, name: str, method: str, path: str, source: str, selector: str = ""
    ) -> None:
        result.add(RouteEvidence(exchange, name, method, urlsplit(path).path, selector, source))

    for exchange in EXCHANGES:
        for file in (ROOT / "crates/dcex/src/exchanges" / exchange / "tests").glob("*.rs"):
            text = file.read_text(encoding="utf-8")
            pattern = r'\b(?:public|private)(?:_body)?\(\s*"([^"]+)"([\s\S]*?)"(GET|POST|PUT|DELETE|PATCH)",\s*"([^"\n]+)"'
            for match in re.finditer(pattern, text):
                if re.search(r'\b(?:public|private)(?:_body)?\(\s*"', match[2]):
                    continue
                add(exchange, match[1], match[3], match[4], file.relative_to(ROOT).as_posix())

    for exchange in ("bybit", "okx", "bitget", "bingx", "mexc", "kucoin", "kraken", "backpack"):
        source = f"tests/unit/test_{exchange}_endpoint_coverage.py"
        module = importlib.import_module(source.removesuffix(".py").replace("/", "."))
        if hasattr(module, "ROUTES"):
            for name, (method, path) in module.ROUTES.items():
                add(exchange, name, method, path, source)
        elif isinstance(module.CASES, dict):
            for name, case in module.CASES.items():
                add(exchange, name, case[1], case[2], source)
        else:
            for case in module.CASES:
                if exchange in {"kucoin", "backpack"}:
                    method, path = case.route.split(" ", 1)
                    add(exchange, case.method_name, method, path, source)
                elif exchange == "bybit":
                    add(exchange, case.method_name, case.verb, case.path, source)
                else:
                    add(exchange, case.name, case.method, case.path, source)

    source = "tests/unit/test_binance_risk_endpoints.py"
    module = importlib.import_module("tests.unit.test_kucoin_inventory_completion")
    for operation in module.OPERATIONS:
        add("kucoin", module.operation_name(operation), operation["method"].upper(), module.values_for(operation)[1], "tests/unit/test_kucoin_inventory_completion.py::test_inventory_wire")
    module = importlib.import_module("tests.unit.test_hyperliquid_inventory_completion")
    for operation in module.OPERATIONS:
        test = "test_info_wire" if operation["public"] else "test_action_wire"
        add("hyperliquid", operation["name"], "POST", "/info" if operation["public"] else "/exchange", "tests/unit/test_hyperliquid_inventory_completion.py::" + test, operation["type"])
    module = importlib.import_module("tests.unit.test_aster_auxiliary")
    for name, _, verb, path, _ in module.CASES:
        add("aster", name, verb, path, "tests/unit/test_aster_auxiliary.py::test_auxiliary_wire")
    module = importlib.import_module("tests.unit.test_binance_inventory_completion")
    for operation in module.OPERATIONS:
        add("binance", module.operation_name(operation), operation["method"], operation["path"], "tests/unit/test_binance_inventory_completion.py::test_inventory_wire")
    module = importlib.import_module("tests.unit.test_bingx_inventory_completion")
    for operation in module.OPERATIONS:
        add("bingx", module.operation_name(operation), operation["method"], operation["path"], "tests/unit/test_bingx_inventory_completion.py::test_inventory_wire")
    module = importlib.import_module("tests.unit.test_bitget_inventory_completion")
    for operation in module.OPERATIONS:
        add("bitget", module.snake(operation["operationId"]), operation["method"].upper(), operation["path"], "tests/unit/test_bitget_inventory_completion.py::test_inventory_wire")
    module = importlib.import_module(source.removesuffix(".py").replace("/", "."))
    for case in module.CASES:
        add("binance", case[0], case[2], case[3], source)
    bybit = json.loads((ROOT / "tests/fixtures/bybit_completion.json").read_text(encoding="utf-8"))
    for case in bybit["cases"]:
        add(
            "bybit",
            case["name"],
            case["method"],
            case["path"],
            "tests/unit/test_bybit_completion.py",
        )

    for exchange in ("aster", "arcus", "extended", "ondo"):
        source = f"tests/unit/test_{exchange}_endpoint_coverage.py"
        module = importlib.import_module(source.removesuffix(".py").replace("/", "."))
        for case in module.CASES:
            path = (
                getattr(case, "path", None)
                or getattr(case, "target", None)
                or getattr(case, "http_method_path", None)
            )
            method = getattr(case, "verb", None) or module.EXPECTED_VERBS[case.method]
            add(exchange, case.method, method, path, source)
        if exchange == "arcus":
            for _, _, case in module._time_sensitive_cases():
                add(exchange, case.method, module.EXPECTED_VERBS[case.method], case.http_method_path, source)
            for case in module.COMPLETION_CASES:
                add(exchange, case["method"], case["http_method"], case["path"], source)

    for exchange in ("hyperliquid", "lighter"):
        source = f"tests/unit/test_{exchange}_endpoint_coverage.py"
        module = importlib.import_module(source.removesuffix(".py").replace("/", "."))
        for case in module.WRAPPER_CASES:
            if exchange == "hyperliquid":
                add(
                    exchange,
                    case.method,
                    "POST",
                    "/info" if case.kind == "public" else "/exchange",
                    source,
                    case.wire_type,
                )
            elif case.kind == "sign":
                continue
            elif isinstance(case.route, int):
                add(exchange, case.method, "POST", "/api/v1/sendTx", source, str(case.route))
            else:
                add(exchange, case.method, module.EXPECTED_VERBS[case.method], case.route, source)
    module = importlib.import_module("tests.unit.test_binance_options_controls")
    for case in module.CASES:
        add("binance", case[0], case[2], case[3], "tests/unit/test_binance_options_controls.py")
    extras = [
        ("okx", "cancel_all_orders", "GET", "/api/v5/trade/orders-pending", "test_okx_endpoint_coverage", "test_sync_cancel_all_orders_batches_only_matching_pending_orders"),
        ("okx", "cancel_all_orders", "POST", "/api/v5/trade/cancel-batch-orders", "test_okx_endpoint_coverage", "test_sync_cancel_all_orders_batches_only_matching_pending_orders"),
        ("okx", "get_sbe_orderbook", "GET", "/api/v5/market/books-sbe", "test_okx_sbe", "test_sbe_binary_snapshot_and_json_error"),
        ("bingx", "export_swap_income", "GET", "/openApi/swap/v2/user/income/export", "test_bingx_income_export", "test_income_export_preserves_bytes_and_checks_errors"),
        ("extended", "update_leverage", "PATCH", "/api/v1/user/leverage", "test_extended_endpoint_coverage", "test_sync_update_leverage_patches_documented_body"),
        ("extended", "place_limit_order", "POST", "/api/v1/user/order", "test_extended_endpoint_coverage", "test_sync_auto_signed_order_fetches_market_and_fee"),
        ("arcus", "submit_internal_transfer", "POST", "/v1/transfer", "test_arcus_endpoint_coverage", "test_internal_transfer_is_wallet_signed_without_api_headers"),
        ("kraken", "retrieve_spot_export", "POST", "/0/private/RetrieveExport", "test_kraken_export", "test_report_zip_preserves_binary_and_checks_api_errors"),
    ]
    for name, verb in [("get_listen_key", "POST"), ("keep_alive_listen_key", "PUT"), ("close_listen_key", "DELETE")]:
        extras.append(("binance", name, verb, "/fapi/v1/listenKey", "test_round3_regressions", "test_binance_listen_key_alias_wire"))
    for name, path in [("get_tokens", "/v1/tokens"), ("get_price", "/v1/price"), ("get_quote", "/v1/quote")]:
        extras.append(("arcus", name, "GET", path, "test_arcus_spot_public", "test_arcus_spot_native_public_routes"))
    for name, verb, path in [("get_status", "GET", "/v1/status"), ("submit_signed_quote", "POST", "/v1/submit")]:
        extras.append(("arcus", name, verb, path, "test_arcus_spot_public", "test_arcus_spot_signed_submit_and_status_routes_are_complete"))
    for exchange, name, method, path, test, function in extras:
        module = importlib.import_module("tests.unit." + test)
        assert callable(getattr(module, function)), (test, function)
        add(exchange, name, method, path, "tests/unit/" + test + ".py::" + function)
    # Explorer routes have a separate host and their own real-native test cases.
    module = importlib.import_module("tests.unit.test_lighter_endpoint_coverage")
    for case in module.WRAPPER_CASES:
        if "explorer" in case.method:
            add(
                "lighter",
                case.method,
                "GET",
                case.route,
                "tests/unit/test_lighter_endpoint_coverage.py",
            )
    return tuple(sorted(result))
