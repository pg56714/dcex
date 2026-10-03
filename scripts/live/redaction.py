"""Shared redaction for local account-check and test summaries."""

import os
import re


def redact(value: object, *, mask_environment: bool = True) -> str:
    """Keep diagnostics useful without retaining credentials or wallet identifiers."""
    text = str(value)
    for name, secret in os.environ.items() if mask_environment else ():
        if secret and "VAULT_NUMBER" in name.upper():
            text = re.sub(r"(?<!\d)" + re.escape(secret) + r"(?!\d)", "[redacted]", text)
        elif len(secret) >= 6 and any(
            part in name.upper()
            for part in (
                "KEY",
                "SECRET",
                "PASSPHRASE",
                "PASSWORD",
                "SIGNATURE",
                "ADDRESS",
                "TOKEN",
            )
        ):
            text = text.replace(secret, "[redacted]")
    text = re.sub(r"(?i)https?://[^\s]+", "[url redacted]", text)
    text = re.sub(
        r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+(?![A-Za-z0-9_-])",
        "[jwt redacted]",
        text,
    )
    text = re.sub(
        r"""(?i)["']?(?:api[-_ ]?key|api[-_ ]?secret|secret|private[-_ ]?key|"""
        r"""signature|passphrase|authorization|address|vault[-_ ]?number|collateralPosition)["']?"""
        r"""\s*[:=]\s*(?:"[^"]*"|'[^']*'|[^,;\s]+)""",
        "[credential redacted]",
        text,
    )
    text = re.sub(r"(?i)\b(?:0x)?[a-f0-9]{40,}\b", "[hex redacted]", text)
    text = re.sub(r"\b[1-9A-HJ-NP-Za-km-z]{32,}\b", "[identifier redacted]", text)
    text = re.sub(r"(?i)\b(?:bc1|tb1)[a-z0-9]{20,}\b", "[address redacted]", text)
    text = re.sub(
        r"(?<![A-Za-z0-9+/=_-])[A-Za-z0-9+/=_-]{40,}(?![A-Za-z0-9+/=_-])", "[token redacted]", text
    )
    return " ".join(text.split())[:500]
