"""
Classify authenticated client methods; only reviewed plain reads may ever be called.

``--list`` writes the classification for review and calls nothing. The default for
every method is ``never``: a method is a ``read`` only when its name starts with a read
verb and it does not mint or queue anything (listen keys, tokens, downloads, exports,
statements, quotes). Names that merely contain a read verb elsewhere are ``review``
and are never called until a person moves them to ``REVIEWED_READS``.
"""

import argparse
import ast
import importlib
import inspect
import json
import logging
import os
import re
import textwrap
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from scripts.live.redaction import redact
from scripts.live.smoke_public import (
    EXCHANGES,
    FIXTURES,
    OUTCOMES,
    PAUSE_SECONDS,
    call_method,
)

PRIVATE_HELPERS = {"_native_private", "private_request"}
READ_PREFIX = re.compile(r"^(get|query|list|fetch|check)_")
READ_INFIX = re.compile(r"_(get|query|list|fetch|check)_")
# A leading write verb wins over any read word later in the name (delete_ip_list_...).
WRITE_PREFIX = re.compile(
    r"^(delete|remove|cancel|place|create|set|update|modify|amend|close|transfer|"
    r"withdraw|redeem|repay|borrow|purchase|submit|send|revoke|add|request)_"
)
# Read-named methods that still mint or queue something server-side: never called.
# (Verbs inside read names are nouns, e.g. get_withdraw_history, so they stay reads.)
MINTS = re.compile(
    r"listen_keys?|keep_alive|ws_token|websocket_token|bullet|auth_token|download|"
    r"statement|export|convert_quote|convert_limit_quote|bridge_quote"
)
# Server-side report generation (see tests/conftest.py): never called.
GENERATED = {
    "get_account_bills_history_archive",
    "get_monthly_statement",
    "post_account_bills_history_archive",
    "post_monthly_statement",
}

# Reviewed 2026-10-09 and kept out of every run: a delete, a signed upload URL,
# sub-account key material and a priced quote.
REVIEWED_NEVER = {
    "delete_ip_list_for_a_sub_account_api_key",
    "request_file_get_file_upload_sign",
    "broker_get_subaccount_apikey",
    "prediction_get_quote",
}
# Reviewed 2026-10-09: a read verb inside the name, but a plain read; approved to call.
REVIEWED_READS = {
    # binance
    "prediction_get_otc_blocktrade_detail",
    "prediction_get_otc_blocktrade_events",
    "prediction_get_otc_reserved_balances",
    "prediction_get_portfolio",
    "prediction_get_position_by_token",
    "prediction_get_quota_status",
    "prediction_get_redeem_status",
    "prediction_list_otc_blocktrades",
    "prediction_list_prediction_wallets",
    "prediction_query_active_orders",
    "prediction_query_order_history",
    "prediction_query_payment_option_balances",
    "prediction_query_pn_l",
    "prediction_query_positions",
    "prediction_query_positions_by_filter",
    "prediction_query_settled_position_history",
    "prediction_query_transfer_list",
    "prediction_query_transfer_status",
    "wallet_fetch_deposit_address_list_with_network",
    # bitget
    "broker_get_all_subaccount_deposit_withdrawal",
    "broker_get_broker_commission",
    "broker_get_subaccount_list",
    "cfd_account_get_financial_records",
    "cfd_account_get_fund_detail",
    "cfd_account_get_instruments",
    "cfd_account_get_transfer_records",
    "cfd_market_get_history_candlestick",
    "cfd_market_get_tickers",
    "cfd_trade_get_current_positions",
    "cfd_trade_get_order_history",
    "cfd_trade_get_unfilled_orders",
    "classic_affiliate_customer_info_get_commission_detail",
    "classic_affiliate_customer_info_get_customer_assets",
    "classic_affiliate_customer_info_get_customer_deposit",
    "classic_affiliate_customer_info_get_customer_kyc_result",
    "classic_affiliate_customer_info_get_customer_list",
    "classic_affiliate_customer_info_get_customer_trade_volume",
    "classic_affiliate_customer_info_get_direct_commissions",
    "classic_affiliate_customer_info_get_sub_customer_list",
    "classic_instloan_account_get_ltv",
    "classic_instloan_account_get_risk_unit",
    "classic_instloan_account_get_transferred_amount_from_spot_account",
    "classic_instloan_orders_get_loan_orders",
    "classic_instloan_orders_get_repayment_orders",
    "classic_instloan_public_get_margin_coin_info",
    "classic_instloan_public_get_product_info",
    "classic_instloan_public_get_spot_symbols",
    "classic_tax_get_future_account_record",
    "classic_tax_get_margin_account_record",
    "classic_tax_get_p2_p_account_record",
    "classic_tax_get_spot_account_record",
    "copy_trading_follower_get_copy_profit_details",
    "copy_trading_follower_get_copy_settings",
    "copy_trading_follower_get_copy_transfer_record",
    "copy_trading_follower_get_current_copy",
    "copy_trading_follower_get_current_positions",
    "copy_trading_follower_get_current_tpsl_orders",
    "copy_trading_follower_get_tpsl_order_history",
    "copy_trading_public_private_get_current_followers",
    "copy_trading_public_private_get_history_followers",
    "copy_trading_public_private_get_max_transferable",
    "copy_trading_public_private_get_portfolio_overview",
    "copy_trading_public_private_get_position_summary",
    "copy_trading_public_private_get_profit_details",
    "copy_trading_public_private_get_profit_summary",
    "copy_trading_public_private_get_trading_pairs",
    "copy_trading_public_private_get_transfer_record",
    "institutional_loan_get_loan_orders",
    "institutional_loan_get_ltv",
    "institutional_loan_get_margin_coin_info",
    "institutional_loan_get_product_info",
    "institutional_loan_get_repayment_orders",
    "institutional_loan_get_risk_unit",
    "institutional_loan_get_trade_symbols",
    "institutional_loan_get_transferred_quantity",
    "p2p_ad_management_get_ad_info",
    "p2p_ad_management_get_ad_limit",
    "p2p_ad_management_get_ad_list",
    "p2p_ad_management_get_exchange_rate",
    "p2p_ad_management_get_my_ads",
    "p2p_order_management_get_all_orders",
    "p2p_order_management_get_order_info",
    "p2p_order_management_get_pending_orders",
    "p2p_user_info_get_currencies",
    "p2p_user_info_get_pay_methods",
    "p2p_user_info_get_user_info",
    "stock_plus_assets_get_account",
    "stock_plus_assets_get_cash_flow",
    "stock_plus_assets_get_stock_position",
    "stock_plus_assets_get_transfer_records",
    "stock_plus_options_quotes_get_option_chain_info",
    "stock_plus_options_quotes_get_option_expiry_date",
    "stock_plus_options_quotes_get_option_quote",
    "stock_plus_options_quotes_get_option_volume",
    "stock_plus_orders_get_history_executions",
    "stock_plus_orders_get_history_orders",
    "stock_plus_orders_get_order_detail",
    "stock_plus_orders_get_today_executions",
    "stock_plus_orders_get_today_orders",
    "stock_plus_stock_quotes_get_candlestick",
    "stock_plus_stock_quotes_get_depth",
    "stock_plus_stock_quotes_get_history_candlestick",
    "stock_plus_stock_quotes_get_intraday",
    "stock_plus_stock_quotes_get_quote",
    "stock_plus_stock_quotes_get_static_info",
    "stock_plus_stock_quotes_get_trade_detail",
    "tax_get_tax_records",
    # kucoin
    "post_v2_copy_trade_get_cross_mode_margin_requirement",
}


def private_methods(exchange: str) -> list[str]:
    """Client methods whose body calls an authenticated request helper."""
    client_cls = importlib.import_module(f"dcex.{exchange}.client").Client
    found = []
    for name, fn in inspect.getmembers(client_cls, inspect.isfunction):
        if name.startswith("_"):
            continue
        try:
            tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
        except (OSError, TypeError):
            continue
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        if calls & PRIVATE_HELPERS:
            found.append(name)
    return found


def classify(name: str) -> str:
    """``read`` (may be called), ``review`` (needs a person) or ``never``."""
    if name in GENERATED or name in REVIEWED_NEVER or MINTS.search(name):
        return "never"
    if READ_PREFIX.search(name) or name in REVIEWED_READS:
        return "read"
    if WRITE_PREFIX.search(name):
        return "never"
    if READ_INFIX.search(name):
        return "review"
    return "never"


def classification() -> dict[str, dict[str, list[str]]]:
    """Per exchange: method names grouped by class."""
    result: dict[str, dict[str, list[str]]] = {}
    for exchange in EXCHANGES:
        groups: dict[str, list[str]] = {"read": [], "review": [], "never": []}
        for name in private_methods(exchange):
            groups[classify(name)].append(name)
        result[exchange] = groups
    return result


def markdown(groups: dict[str, dict[str, list[str]]]) -> str:
    """Render the review document."""
    lines = [
        "# Private method classification (calls nothing)",
        "",
        "- read: name starts with get/query/list/fetch/check and has no state-changing word.",
        "- review: a read verb appears only inside the name; never called until approved.",
        "- never: everything else (orders, transfers, settings, keys, reports).",
        "",
        "| exchange | read | review | never |",
        "|---|---|---|---|",
    ]
    totals: Counter[str] = Counter()
    for exchange, g in groups.items():
        totals.update({k: len(v) for k, v in g.items()})
        lines.append(f"| {exchange} | {len(g['read'])} | {len(g['review'])} | {len(g['never'])} |")
    lines.append(f"| total | {totals['read']} | {totals['review']} | {totals['never']} |")
    for kind in ("review", "read", "never"):
        lines += ["", f"## {kind}", ""]
        for exchange, g in groups.items():
            if g[kind]:
                lines.append(f"- **{exchange}** ({len(g[kind])}): " + ", ".join(g[kind]))
    return "\n".join(lines) + "\n"


# Never matches: the read list is already filtered; this only satisfies call_method.
NO_SKIP = re.compile(r"(?!x)x")


def make_client(exchange: str) -> Any:  # noqa: ANN401
    """Authenticated client from .env, with request logging disabled."""
    import pytest

    from tests.stateful_runner import client_options

    module = importlib.import_module(f"dcex.{exchange}.client")
    if exchange == "lighter":
        from dcex.lighter.credentials import credential_env_names

        if any(not os.getenv(name) for name in credential_env_names("mainnet")):
            raise LookupError("missing Lighter mainnet credentials")
        logger = logging.Logger("smoke-no-payload-logging")
        logger.disabled = True
        return module.Client.from_env(network="mainnet", logger=logger)
    try:
        return module.Client(**client_options(exchange))
    except pytest.skip.Exception as error:
        raise LookupError(str(error)) from None


def own_fixtures(exchange: str) -> dict[str, Any]:
    """The account's own identifiers from .env; sent only to that same exchange."""
    if exchange == "arcus" and os.getenv("ARCUS_ADDRESS"):
        return {"address": os.environ["ARCUS_ADDRESS"]}
    return {}


def run_exchange(exchange: str, *, reviewed_only: bool = False) -> list[dict[str, Any]]:
    """Call every ``read`` method once; record outcomes only, never response data."""
    FIXTURES.setdefault(exchange, {}).update(own_fixtures(exchange))
    try:
        client = make_client(exchange)
    except Exception as error:  # noqa: BLE001
        return [
            {
                "exchange": exchange,
                "method": "<client>",
                "outcome": "skipped",
                "message": redact(error)[:300],
            }
        ]
    client_cls = type(client)
    rows = []
    try:
        for name in private_methods(exchange):
            if classify(name) != "read":
                continue  # Only reads are ever called.
            if reviewed_only and name not in REVIEWED_READS:
                continue
            row = call_method(client, exchange, name, getattr(client_cls, name), NO_SKIP)
            if "message" in row:
                row["message"] = redact(row["message"])
            rows.append(row)
            time.sleep(PAUSE_SECONDS)
    finally:
        try:
            client.close()
        except Exception:  # noqa: BLE001, S110 - closing never hides results
            pass
    return rows


def run(exchanges: list[str], *, reviewed_only: bool = False) -> Path:
    """Run the read list for the given exchanges and write the outcome file."""
    with ThreadPoolExecutor(max_workers=len(exchanges)) as pool:
        results = pool.map(lambda e: run_exchange(e, reviewed_only=reviewed_only), exchanges)
        rows = [row for result in results for row in result]
    out = Path("live-results") / f"smoke-private-{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print("exchange | " + " | ".join(OUTCOMES))
    for exchange in exchanges:
        counts = Counter(r["outcome"] for r in rows if r["exchange"] == exchange)
        print(exchange + " | " + " | ".join(str(counts[o]) for o in OUTCOMES))
    total = Counter(r["outcome"] for r in rows)
    print("total | " + " | ".join(str(total[o]) for o in OUTCOMES))
    return out


def main() -> int:
    """``--list`` writes the classification; ``--run`` calls the read methods only."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--run", action="store_true")
    parser.add_argument("--exchange", choices=EXCHANGES, action="append")
    parser.add_argument(
        "--reviewed-only", action="store_true", help="with --run: only REVIEWED_READS"
    )
    args = parser.parse_args()
    exchanges: list[str] = args.exchange or list(EXCHANGES)
    for exchange in exchanges:
        # Import up front: concurrent first imports race on package initialisation.
        importlib.import_module(f"dcex.{exchange}.client")
    Path("live-results").mkdir(exist_ok=True)
    if args.list:
        out = Path("live-results") / "private-classification.md"
        out.write_text(markdown(classification()), encoding="utf-8")
    else:
        load_dotenv(".env")
        out = run(exchanges, reviewed_only=args.reviewed_only)
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
