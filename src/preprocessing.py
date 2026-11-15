"""One normalization rule shared by documents and queries."""

import re

TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Return lowercase ASCII letter/number runs; no stop words or stemming."""
    return [match.group().lower() for match in TOKEN_RE.finditer(text)]
