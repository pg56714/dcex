"""Source-preserving match-arm inspection for module ownership tests."""

import hashlib
import re

TOKENS = re.compile(r'''//[^\n]*|/\*[\s\S]*?\*/|r(?P<hash>\#*)"[\s\S]*?"(?P=hash)|'(?:\\.|[^'\\\n])'|"(?:\\[\s\S]|[^"\\])*"''')


def mask(source):
    return TOKENS.sub(lambda match: "".join("\n" if char == "\n" else " " for char in match[0]), source)


def arms(source):
    clean = mask(source)
    pattern = re.compile(r'(?P<keys>"\w+"(?:\s*\|\s*"\w+")*)\s*=>')
    for match in pattern.finditer(source):
        # Strings in comments/docstrings are not code arms.
        arrow = source.rfind("=>", match.start(), match.end())
        if clean[arrow:arrow + 2] != "=>":
            continue
        stack = []
        end = match.end()
        for end in range(match.end(), len(clean)):
            char = clean[end]
            if char in "({[":
                stack.append(char)
            elif char in ")}]":
                if not stack:
                    break
                stack.pop()
                if not stack and clean[match.end():end + 1].lstrip().startswith("{"):
                    end += 1
                    break
            elif char == "," and not stack:
                break
        yield re.findall(r'"(\w+)"', match["keys"]), source[match.end():end]


def function_spans(source):
    clean = mask(source)
    for match in re.finditer(r"\bfn\s+(\w+)\b", clean):
        boundary = re.search(r"[;{]", clean[match.end():])
        if boundary is None or boundary[0] == ";":
            continue
        start = match.end() + boundary.start()
        end, depth = start + 1, 1
        while depth and end < len(clean):
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        yield match[1], match.start(), start, end


def functions(source):
    for name, _, start, end in function_spans(source):
        yield name, source[start:end]


def fund_literals(source):
    """Inspect every identifier string, independent of dispatch syntax."""
    for token in TOKENS.finditer(source):
        raw = token[0]
        if raw.startswith(('"', 'r"', 'r#')):
            name = raw[raw.index('"') + 1:raw.rindex('"')]
            if raw.startswith('"'):
                name = re.sub(r"\\x([0-9a-fA-F]{2})|\\u\{([0-9a-fA-F]+)\}", lambda match: chr(int(match[1] or match[2], 16)), name)
            if re.fullmatch(r"\w+", name) and fund_domain(name.lower()):
                yield name


def unpinned_fund_literals(source, filename, allowances=()):
    names = {name for name in fund_literals(source) if filename != fund_domain(name.lower()) + ".rs"}
    digest = hashlib.sha256(source.encode()).hexdigest()
    if any(entry["sha256"] == digest and names == set(entry["names"]) for entry in allowances):
        return []
    return sorted(names)


def enclosing_impl(source, position):
    clean = mask(source)
    for match in re.finditer(r"\bimpl\s+(?:\w+::)*(\w+)\s*\{", clean):
        end, depth = match.end(), 1
        while end < len(clean) and depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        if match.end() <= position < end:
            return match[1]
    return None


def unauthorized_transport_references(source, transport, permitted_functions=(), *, impl_owner=None, allow_definition=False):
    """Only the configured source file and impl may define the transport."""
    allowed = [
        (start, end) for name, start, _, end in function_spans(source)
        if (name in permitted_functions or allow_definition and name == transport)
        and (impl_owner is None or enclosing_impl(source, start) == impl_owner)
    ]
    return [match.start() for match in re.finditer(r"\b" + re.escape(transport) + r"\b", mask(source)) if not any(start <= match.start() < end for start, end in allowed)]


def fund_domain(name):
    if re.search(r"withdraw|send_(?:usd|spot|asset|to_evm)|bridge", name):
        return "withdrawals"
    if name in {"transfer_l2_account", "transfer_same_master_account", "sign_transfer_l2_account", "sign_transfer_same_master_account", "transfer_master_internal", "transfer_sub_account_internal"}:
        return "withdrawals"
    return "transfers" if "transfer" in name else None


# Only transport calls confer ownership. Awaiting a nonce or signer does not.
SENDS = re.compile(r"(?<![\w.])(?:post|get|request)\s*\(|\.(?:execute|signed|spot_private|submit_signed_tx|inventory_transport|private_request_bytes|post_private|get_private|request|private_post|private_get|public_get|private_post_value|get_request|post_request|submit_action|exchange_payload_at_nonce|additional_user_action|contract_get)\s*\(")
PURE_CALLS = {"Some", "Ok", "Err", "Box", "pin"}


def request_owners(source, delegates=()):
    bodies = dict(functions(source))
    owners = {name for name, body in bodies.items() if SENDS.search(mask(body)) or set(re.findall(r"self\.(\w+)\s*\(", mask(body))) & set(delegates)}
    while True:
        expanded = owners | {name for name, body in bodies.items() if set(re.findall(r"self\.(\w+)\s*\(", mask(body))) & owners}
        if expanded == owners:
            return owners
        owners = expanded


def conditional_arms(source):
    clean = mask(source)
    for match in re.finditer(r"\bif\s+", clean):
        start = clean.find("{", match.end())
        if start < 0:
            continue
        condition = source[match.start() + 2:start]
        names = re.findall(r'"(\w+)"', condition)
        if not names:
            continue
        end, depth = start + 1, 1
        while depth and end < len(clean):
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        yield names, source[start + 1:end - 1]


def misplaced_fund_arms(source, filename, owners, readonly, nondispatch=()):
    failures = []
    for names, body in [*arms(source), *conditional_arms(source)]:
        for name in names:
            domain = fund_domain(name)
            if domain is None or filename == domain + ".rs" or name in readonly:
                continue
            digest = hashlib.sha256(re.sub(r"\s+", " ", body.strip()).encode()).hexdigest()
            if any(name in entry["names"] and digest == entry["sha256"] for entry in nondispatch):
                continue
            clean = mask(body)
            clean = re.sub(r"\b(?:params|p)\.(?:get|required|u64)\s*\(", "(", clean)
            called = set(re.findall(r"\b(\w+)\s*(?:!\s*)?\(", clean))
            allowed = owners.get(domain, set())
            # A dispatch must be solely an owner delegation, never a decoy plus
            # another call, macro, route table, or unrecognised sender.
            if not called & allowed or called - allowed - PURE_CALLS or re.search(r"\b\w+!\s*[({\[]", clean):
                failures.append(name)
    return failures
