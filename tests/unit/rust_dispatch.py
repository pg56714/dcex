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


def misplaced_fund_arms(source, filename, owners, readonly):
    failures = []
    for names, body in arms(source):
        for name in names:
            if "withdraw" not in name and "transfer" not in name:
                continue
            # Pure field-validation/configuration matches do not dispatch requests.
            if not re.search(r"\.await|HttpMethod::|(?<![\w.])(?:post|get|request)\s*\(", body):
                continue
            domain = "withdrawals" if "withdraw" in name else "transfers"
            if name in {"transfer_l2_account", "transfer_same_master_account", "sign_transfer_l2_account", "sign_transfer_same_master_account", "transfer_master_internal", "transfer_sub_account_internal"}:
                domain = "withdrawals"  # Recipient transfers may leave the account family.
            if filename == domain + ".rs" or name in readonly:
                continue
            called = set(re.findall(r"\b(\w+)\s*\(", mask(body)))
            if not called & owners.get(domain, set()):
                failures.append(name)
    return failures
