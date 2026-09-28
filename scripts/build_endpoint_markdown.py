"""Rebuild the bilingual audit and method index; run from the repository root."""

# ruff: noqa: E501 - bilingual Markdown paragraphs and table templates.

import ast
import collections
import importlib
import inspect
import json
import re
import shutil
import subprocess
from pathlib import Path

from scripts.build_endpoint_docs import EXCHANGE_ORDER as EXCHANGES

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")
if GIT is None:
    raise RuntimeError("git is required to compare the documented baseline")

d = json.loads(Path("docs/endpoint-coverage-ledger.json").read_text(encoding="utf-8"))
counts = d["counts"]
rows = d["rows"]
methods = {}
additions = {}
method_info = {}
for ex in EXCHANGES:
    names = {}
    modules = [importlib.import_module(f"dcex.{ex}.client")]
    if ex == "arcus":
        modules.append(importlib.import_module("dcex.arcus.spot"))
    for module in modules:
        for cls in vars(module).values():
            if not isinstance(cls, type) or not cls.__module__.startswith(f"dcex.{ex}"):
                continue
            for name in dir(cls):
                if name.startswith("_") or name in {"close", "async_init"}:
                    continue
                function = getattr(cls, name)
                if not callable(function):
                    continue
                try:
                    source_file = inspect.getsourcefile(inspect.unwrap(function))
                    if source_file is None:
                        continue
                    file = Path(source_file).relative_to(ROOT)
                except (TypeError, ValueError):
                    continue
                if not file.as_posix().startswith(f"dcex/{ex}/"):
                    continue
                doc = inspect.getdoc(function) or "See the method signature and endpoint ledger."
                names[name] = (file.as_posix(), doc.splitlines()[0].rstrip("."))
    old = set()
    files = subprocess.check_output(  # noqa: S603 - fixed revision and known exchange names.
        [GIT, "ls-tree", "-r", "--name-only", "d0bbf8b0", f"dcex/{ex}"], text=True
    ).splitlines()
    for file in files:
        if not file.endswith(".py"):
            continue
        source = subprocess.run(  # noqa: S603 - paths returned by git for the fixed revision.
            [GIT, "show", f"d0bbf8b0:{file}"], capture_output=True, check=True
        ).stdout.decode("utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                old.add(node.name)
    methods[ex] = len(names)
    additions[ex] = len(names.keys() - old)
    method_info[ex] = {name: info for name, info in sorted(names.items()) if name not in old}

status_meaning = {
    "implemented": (
        "Exact offline HTTP route and public Rust/Python wrappers",
        "具備精確離線 HTTP 路由證據及 Rust／Python 公開方法",
    ),
    "protocol": (
        "Asynchronous WebSocket protocol support with cited offline evidence; no live certification",
        "非同步 WebSocket 協定支援，附離線驗證證據；不代表線上認證",
    ),
    "superseded": (
        "Historical or grouped row replaced by explicit current rows",
        "歷史端點或群組列，已由目前的明確列取代",
    ),
    "unavailable": (
        "Retired/unavailable operation, or documentation-only section with no endpoint",
        "官方停用、目前不可用的操作，或沒有獨立端點的文件章節",
    ),
    "unverified": (
        "Wrapper exists, but part of the official specification is incomplete",
        "已有包裝，但部分官方規格不完整",
    ),
    "blocked": (
        "Required signing or authorization specification is missing",
        "缺少必要簽章或授權規格",
    ),
    "partial": ("Grouped capability still has a documented gap", "群組能力仍有明確記錄的缺口"),
    "pending": (
        "Documented operation awaiting implementation or dedicated verification",
        "已列入官方清冊，待實作或專屬驗證",
    ),
}

for zh in [False, True]:
    suffix = ".zh_tw" if zh else ""
    nav = (
        "[English](endpoint-audit.md) | **繁體中文**"
        if zh
        else "**English** | [繁體中文](endpoint-audit.zh_tw.md)"
    )
    title = "端點覆蓋與驗證" if zh else "Endpoint coverage and verification"
    intro = (
        f"核對日期：{d['reviewed']}。原始報表有 3,180 列；目前清冊共 {d['row_count']:,} 列，另保存 15 家交易所的官方文件清冊。"
        if zh
        else f"Reviewed: {d['reviewed']}. The original report contained 3,180 rows; the reconciled ledger contains {d['row_count']:,} rows, with official documentation inventories for all 15 exchanges."
    )
    scope = (
        "所有官方端點均納入範圍，包含提款、地址管理、做市商、RFQ、經紀商、推薦與合作夥伴操作。原先 111 個 excluded 列已處理，沒有保留範圍排除；這不代表所有新發現端點均已實作。"
        if zh
        else "All documented endpoints are in scope, including withdrawals, address management, market making, RFQ, broker, referral and partner operations. All 111 originally excluded rows have been addressed; there are no scope exclusions. This does not mean every newly discovered endpoint is implemented."
    )
    safety = (
        "API 提款沒有第二次確認，送出即執行。建議交易用 API 金鑰不要開啟提款權限。需要錢包授權的操作保留呼叫端提供的簽章；不臆測未公開的簽章規格。"
        if zh
        else "API withdrawals have no second confirmation; they execute on submit. Trading API keys should not have withdrawal permission. Wallet-authorized operations retain caller-provided signatures; undocumented signing rules are not guessed."
    )
    text = f"# {title}\n\n{nav}\n\n{intro}\n\n{scope}\n\n{safety}\n\n"
    text += (
        "[互動覆蓋表](endpoint-coverage.html) · [逐列證據](endpoint-coverage-ledger.json) · [待處理項目](endpoint-recheck.zh_tw.md) · [方法索引](endpoint-methods.zh_tw.md)\n\n"
        if zh
        else "[Interactive coverage table](endpoint-coverage.html) · [Per-row evidence](endpoint-coverage-ledger.json) · [Remaining items](endpoint-recheck.md) · [Method index](endpoint-methods.md)\n\n"
    )
    text += (
        "## 覆蓋狀態\n\n清冊可能包含歷史列、分組列與重疊操作，不能用列數計算官方端點覆蓋百分比。\n\n| 狀態 | 列數 | 定義 |\n| --- | ---: | --- |\n"
        if zh
        else "## Coverage status\n\nHistorical, grouped and overlapping rows prevent converting these counts into an endpoint coverage percentage.\n\n| Status | Rows | Definition |\n| --- | ---: | --- |\n"
    )
    for status, meaning in status_meaning.items():
        text += f"| `{status}` | {counts.get(status, 0):,} | {meaning[int(zh)]} |\n"
    text += (
        "\n## 交易所與 Python 方法\n\n方法數包含別名與簽章輔助方法，不是端點數；新增數以 `d0bbf8b0` 為基準。\n\n| 交易所 | 公開方法 | 新增 | 已實作列 | 待處理列 |\n| --- | ---: | ---: | ---: | ---: |\n"
        if zh
        else "\n## Exchanges and Python methods\n\nMethod counts include aliases and signing helpers, not endpoints. Additions are relative to `d0bbf8b0`.\n\n| Exchange | Public methods | Added | Implemented rows | Pending rows |\n| --- | ---: | ---: | ---: | ---: |\n"
    )
    for ex in EXCHANGES:
        c = collections.Counter(r["status"] for r in rows if r["exchange"] == ex)
        text += f"| [{ex}](official-endpoint-inventory/{ex}.json) | {methods[ex]} | {additions[ex]} | {c['implemented']} | {c['pending']} |\n"
    text += "\n## 驗證與限制\n\n" if zh else "\n## Verification and limits\n\n"
    previous = Path(f"docs/endpoint-audit{suffix}.md").read_text(encoding="utf-8")
    verification = re.search(r"<!-- VERIFICATION -->(.*?)<!-- /VERIFICATION -->", previous, re.S)
    text += (
        "<!-- VERIFICATION -->"
        + (verification[1] if verification else "\nVerification pending.\n")
        + "<!-- /VERIFICATION -->\n\n"
    )
    text += (
        "離線測試驗證路由、HTTP 方法、參數、簽章、WebSocket 訊息與回應處理，不能證明真實帳戶權限或交易所線上可用性。沒有送出真實訂單、提款或帳戶管理操作。\n\n- OKX/Bitget SBE 回傳原始位元組，未內建解碼器。\n- Lighter explorer 使用獨立 base URL；歷史匯出不會自動付費。\n- `unverified` 與 `blocked` 的具體缺口及解除條件保留在清冊中。\n"
        if zh
        else "Offline tests verify routes, HTTP methods, parameters, signatures, WebSocket messages and response handling. They do not establish live account eligibility or exchange availability. No live orders, withdrawals or account-administration requests were submitted.\n\n- OKX/Bitget SBE returns raw bytes without a built-in decoder.\n- Lighter explorer uses a separate base URL; historical exports never automatically pay a fee.\n- The ledger records the exact gaps and resolution requirements for `unverified` and `blocked` rows.\n"
    )
    Path(f"docs/endpoint-audit{suffix}.md").write_text(text, encoding="utf-8")
    nav = (
        "[English](endpoint-recheck.md) | **繁體中文**"
        if zh
        else "**English** | [繁體中文](endpoint-recheck.zh_tw.md)"
    )
    text = (
        "# 端點複查：待處理項目" if zh else "# Endpoint recheck: remaining items"
    ) + f"\n\n{nav}\n\n{intro}\n\n{scope}\n\n{safety}\n\n"
    text += (
        "[清冊與逐列原因](endpoint-coverage-ledger.json) · [可篩選的待處理列表](endpoint-coverage.html)\n\n"
        if zh
        else "[Ledger and per-row reasons](endpoint-coverage-ledger.json) · [Filterable remaining items](endpoint-coverage.html)\n\n"
    )
    text += (
        "## 規格與可用性缺口\n\n| 列 | 交易所 | 操作 | 狀態 | 官方文件 |\n| ---: | --- | --- | --- | --- |\n"
        if zh
        else "## Specification and availability gaps\n\n| Row | Exchange | Operation | Status | Official reference |\n| ---: | --- | --- | --- | --- |\n"
    )
    for r in rows:
        if r["status"] not in {"blocked", "unverified", "unavailable", "partial"}:
            continue
        text += f"| {r['row']} | {r['exchange']} | {r['endpoint'].replace('|', '/')} | `{r['status']}` | [Docs]({r['official_source']}) |\n"
    text += (
        "\n## 新增清冊的待處理列\n\n目前所有清冊列均有明確處理狀態；未公開規格或仍待確認者保留在上表。一般 WebSocket 支援不會自動算成每個官方主題均驗證完成。\n\n| 交易所 | REST／操作待處理 | WebSocket 待處理 |\n| --- | ---: | ---: |\n"
        if zh
        else "\n## Pending inventory rows\n\nEvery inventory row now has an explicit disposition; unresolved specifications and verification gaps remain in the table above. Generic WebSocket support does not automatically certify every documented topic.\n\n| Exchange | REST/action pending | WebSocket pending |\n| --- | ---: | ---: |\n"
    )
    for ex in EXCHANGES:
        rs = [r for r in rows if r["exchange"] == ex and r["status"] == "pending"]
        text += f"| {ex} | {sum(r['kind'] != 'WS' for r in rs)} | {sum(r['kind'] == 'WS' for r in rs)} |\n"
    Path(f"docs/endpoint-recheck{suffix}.md").write_text(text, encoding="utf-8")
    nav = (
        "[English](endpoint-methods.md) | **繁體中文**"
        if zh
        else "**English** | [繁體中文](endpoint-methods.zh_tw.md)"
    )
    text = ("# 新增方法索引" if zh else "# New method index") + f"\n\n{nav}\n\n"
    text += (
        "相較 `d0bbf8b0` 新增的 Python 同步／非同步公開方法。數量包含別名及簽章輔助方法，不是端點數。提款與合作夥伴操作均納入範圍；API 提款沒有第二次確認，送出即執行。建議交易金鑰不要開啟提款權限。詳見[覆蓋與限制](endpoint-audit.zh_tw.md)。\n"
        if zh
        else "Public Python sync/async methods added relative to `d0bbf8b0`. Counts include aliases and signing helpers, not endpoints. Withdrawals and partner operations are in scope. API withdrawals have no second confirmation; they execute on submit. Trading keys should not have withdrawal permission. See [coverage and limitations](endpoint-audit.md).\n"
    )
    for ex in EXCHANGES:
        text += f"\n## {ex.title()}\n\n"
        for name, (file, doc) in method_info[ex].items():
            text += f"- [`{name}`](../{file}) — {doc}.\n"
    Path(f"docs/endpoint-methods{suffix}.md").write_text(text, encoding="utf-8")
print("Public documentation updated", sum(additions.values()), "new methods")
