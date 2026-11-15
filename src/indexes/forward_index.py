"""Document-oriented term-frequency mapping."""

from collections import Counter

from src.indexes.base import BaseIndex
from src.preprocessing import tokenize
from src.ranking import score_counts


class ForwardIndex(BaseIndex):
    name = "forward"

    def _build(self) -> None:
        self.term_counts = {doc_id: Counter(tokenize(doc.text)) for doc_id, doc in self.documents.items()}

    def _matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        scores = {}
        for doc_id, counts in self.term_counts.items():
            score = score_counts(counts, terms)
            if score:
                scores[doc_id] = score
        return scores, len(self.documents)
