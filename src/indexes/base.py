"""Common search contract and a consistent Python object-size estimate."""

import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.document_loader import Document
from src.ranking import parse_query, snippet


def deep_size(value: object, seen: set[int] | None = None) -> int:
    """Sum reachable Python object sizes once; excludes interpreter/native overhead."""
    if seen is None:
        seen = set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    total = sys.getsizeof(value)
    if isinstance(value, dict):
        for key, item in value.items():
            total += deep_size(key, seen) + deep_size(item, seen)
    elif isinstance(value, (list, tuple, set, frozenset)):
        total += sum(deep_size(item, seen) for item in value)
    elif hasattr(value, "__dict__"):
        total += deep_size(vars(value), seen)
    return total


@dataclass(frozen=True)
class SearchHit:
    id: str
    title: str
    snippet: str
    score: int


@dataclass(frozen=True)
class SearchOutcome:
    hits: list[SearchHit]
    result_count: int
    candidate_count: int


class BaseIndex(ABC):
    name = "base"

    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}

    def build(self, documents: list[Document]) -> None:
        self.documents = {doc.id: doc for doc in documents}
        if len(self.documents) != len(documents):
            raise ValueError("Document IDs must be unique.")
        self._build()

    @abstractmethod
    def _build(self) -> None:
        pass

    @abstractmethod
    def _matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        """Return document scores and number of documents considered."""

    def _phrase_matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        raise ValueError("Phrase queries require the positional index.")

    def search(self, query: str, top_k: int = 10, include_snippets: bool = True) -> SearchOutcome:
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100.")
        parsed = parse_query(query)
        scores, candidates = (self._phrase_matching(parsed.terms) if parsed.phrase else self._matching(parsed.terms))
        ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        hits = [
            SearchHit(doc_id, self.documents[doc_id].title, snippet(self.documents[doc_id].text, parsed.terms) if include_snippets else "", score)
            for doc_id, score in ordered[:top_k]
        ]
        return SearchOutcome(hits, len(scores), candidates)

    def memory_usage(self) -> int:
        return deep_size(self)
