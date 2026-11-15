"""Baseline: re-tokenize every document on every query."""

from collections import Counter

from src.indexes.base import BaseIndex
from src.preprocessing import tokenize
from src.ranking import score_counts


class SequentialScan(BaseIndex):
    name = "sequential"

    def _build(self) -> None:
        pass

    def _matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        scores = {}
        for doc_id, doc in self.documents.items():
            score = score_counts(Counter(tokenize(doc.text)), terms)
            if score:
                scores[doc_id] = score
        return scores, len(self.documents)
