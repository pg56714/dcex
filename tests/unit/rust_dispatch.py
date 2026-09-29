"""Source-preserving match-arm inspection for module ownership tests."""

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


def functions(source):
    clean = mask(source)
    for match in re.finditer(r"\bfn\s+(\w+)\s*(?:<[^{}]*>)?\(", clean):
        start = clean.index("{", match.end())
        end, depth = start + 1, 1
        while depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        yield match[1], source[start:end]


def fund_domain(name):
    if re.search(r"withdraw|send_(?:usd|spot|asset|to_evm)|bridge", name):
        return "withdrawals"
    if name in {"transfer_l2_account", "transfer_same_master_account", "sign_transfer_l2_account", "sign_transfer_same_master_account", "transfer_master_internal", "transfer_sub_account_internal"}:
        return "withdrawals"
    return "transfers" if "transfer" in name else None


SENDS = re.compile(r"\.await|HttpMethod::|(?<![\w.])(?:post|get|request)\s*\(")
INLINE_SEND = re.compile(r"HttpMethod::|\b(?:private_|public_|signed_)(?:post|get|request|put|delete|patch)\w*\s*\(|\.(?:post|request|put|delete|patch)\s*\(|(?<![\w.])(?:post|get|request)\s*\(")
ROUTE = re.compile(r'Some\s*\(\s*\(\s*"(?:POST|GET|PUT|DELETE|PATCH)"')


def request_owners(source):
    return {name for name, body in functions(source) if SENDS.search(mask(body))}


def conditional_arms(source):
    clean = mask(source)
    for match in re.finditer(r'\b(?:if|else\s+if)\s+\w+\s*==\s*"(\w+)"\s*\{', source):
        if clean[match.start():match.start() + 2] not in {"if", "el"}:
            continue
        start, depth = match.end(), 1
        end = start
        while depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        yield [match[1]], source[start:end - 1]


def misplaced_fund_arms(source, filename, owners, readonly):
    failures = []
    for names, body in [*arms(source), *conditional_arms(source)]:
        for name in names:
            domain = fund_domain(name)
            if domain is None:
                continue
            # Pure field-validation/configuration matches do not dispatch requests.
            if not SENDS.search(mask(body)) and not ROUTE.search(body):
                continue
            if filename == domain + ".rs" or name in readonly:
                continue
            called = set(re.findall(r"\b(\w+)\s*\(", mask(body)))
            if INLINE_SEND.search(mask(body)) or ROUTE.search(body) or not called & owners.get(domain, set()):
                failures.append(name)
    return failures
