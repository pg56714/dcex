"""Independent public-interface inventory for the committed input contracts."""

import ast
import re
from collections import Counter

NUMERIC = re.compile(r"price|px|qty|quantity|amount|amt|size|sz|volume|vol|notional|funds|investment|collateral|margin|fee|lever|ratio|percent|pct|rate|offset|delta|spread|take_?profit|stop_?loss|loss_?reserve|(?:^|_)(?:tp|sl)(?:$|_)|trigger|trail|cost|budget|premium|slippage|value", re.I)
OPERATIONS = re.compile(r"order|amend|transfer|withdraw|batch", re.I)


def public_inputs(source):
    for cls in ast.parse(source).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for node in cls.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
                continue
            args = {a.arg: ast.unparse(a.annotation) if a.annotation else "" for a in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs] if a.arg != "self"}
            # Wire aliases must be checked independently of the public spelling.
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr in {"_native_params", "_params"}:
                    for keyword in call.keywords:
                        if keyword.arg:
                            args.setdefault(keyword.arg, args.get(keyword.value.id, "") if isinstance(keyword.value, ast.Name) else "")
            yield node.name, args, node.args.kwarg is not None


NEVER_EXEMPT = re.compile(r"price|amount|size|qty|quantity|fee|margin|collateral|share|volume|(?:^|_)(?:px|amt|sz)(?:$|_)", re.I)
MAX_REASON_REPETITIONS = 4


def normalized_reason(reason, identities=()):
    reason = re.sub(r"\bFor\s+[^,]+,\s*", "", reason, flags=re.I)
    for identity in sorted(identities, key=len, reverse=True):
        for token in [identity, *re.split(r"[/.:]", identity)]:
            reason = re.sub(r"\b" + re.escape(token) + r"\b", " ", reason, flags=re.I)
    return re.sub(r"[^a-z0-9]+", " ", reason.lower()).strip()


def validate_exemptions(exemptions):
    reasons = Counter(normalized_reason(reason, exemptions) for reason in exemptions.values())
    assert all(count <= MAX_REASON_REPETITIONS for count in reasons.values()), reasons


def missing_declarations(source, methods, exemptions, exchange=""):
    validate_exemptions(exemptions)
    missing = []
    for method, args, variadic in public_inputs(source):
        schema = methods.get(method)
        if OPERATIONS.search(method) and schema is None:
            missing.append((method, "<method>"))
        properties = (schema or {}).get("properties", {})
        for name, annotation in args.items():
            identity = f"{method}/{name}"
            if identity in exemptions:
                assert not NEVER_EXEMPT.search(name), (exchange, identity)
                reason = exemptions[identity]
                assert identity in reason and len(set(reason.split())) >= 8, identity
                assert not NUMERIC.search(name) or re.fullmatch(r"(?:bool|int)(?: \| None)?", annotation), (identity, annotation)
                continue
            structured = OPERATIONS.search(method) and any(t in annotation for t in ["list", "dict"])
            if (NUMERIC.search(name) or structured) and name not in properties:
                missing.append((method, name))
            if structured and name in properties:
                assert properties[name].get("type") in {"array", "object"}, identity
    return missing


def missing_wire_declarations(value, schema, path=()):
    """Compare a captured payload with declarations, including nested wire names."""
    missing = []
    if isinstance(value, dict):
        for name, child in value.items():
            declared = schema.get("properties", {}).get(name, {})
            field = (*path, name)
            if NUMERIC.search(name) and not isinstance(child, (dict, list, bool)):
                if declared.get("format") != "decimal":
                    missing.append(field)
            missing.extend(missing_wire_declarations(child, declared, field))
    elif isinstance(value, list):
        for child in value:
            missing.extend(missing_wire_declarations(child, schema.get("items", {}), (*path, "[]")))
    return missing
