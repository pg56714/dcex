"""Independent public-interface inventory for the committed input contracts."""

import ast
import re

NUMERIC = re.compile(r"price|px|qty|quantity|amount|amt|size|sz|volume|vol|notional|funds|investment|collateral|margin|fee|leverage|ratio|percent|rate|offset|delta|spread", re.I)
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


def missing_declarations(source, methods, exemptions):
    missing = []
    for method, args, variadic in public_inputs(source):
        schema = methods.get(method)
        if OPERATIONS.search(method) and schema is None:
            missing.append((method, "<method>"))
        properties = (schema or {}).get("properties", {})
        for name, annotation in args.items():
            identity = f"{method}/{name}"
            if identity in exemptions:
                assert len(exemptions[identity].split()) >= 3, identity
                continue
            structured = OPERATIONS.search(method) and any(t in annotation for t in ["list", "dict"])
            if (NUMERIC.search(name) or structured) and name not in properties:
                missing.append((method, name))
            if structured and name in properties:
                assert properties[name].get("type") in {"array", "object"}, identity
    return missing
