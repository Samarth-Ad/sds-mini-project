"""Shared query parsing, scoring convention, and display snippets."""

import re
from dataclasses import dataclass

from src.preprocessing import tokenize


@dataclass(frozen=True)
class Query:
    terms: tuple[str, ...]
    phrase: bool


def parse_query(text: str) -> Query:
    value = text.strip()
    phrase = len(value) >= 2 and value.startswith('"') and value.endswith('"')
    terms = tuple(tokenize(value[1:-1] if phrase else value))
    if not terms:
        raise ValueError("Enter a query containing at least one word or number.")
    return Query(terms, phrase)


def score_counts(counts: dict[str, int], terms: tuple[str, ...]) -> int:
    """OR matching; score is sum of frequencies of distinct query terms."""
    return sum(counts.get(term, 0) for term in set(terms))


def snippet(text: str, terms: tuple[str, ...], width: int = 160) -> str:
    clean = " ".join(text.split())
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b", re.I)
    match = pattern.search(clean)
    start = max(0, (match.start() if match else 0) - 45)
    end = min(len(clean), start + width)
    return ("…" if start else "") + clean[start:end] + ("…" if end < len(clean) else "")
