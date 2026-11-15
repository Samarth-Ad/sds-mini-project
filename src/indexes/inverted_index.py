"""Term-to-document frequency postings."""

from collections import Counter, defaultdict

from src.indexes.base import BaseIndex
from src.preprocessing import tokenize


class InvertedIndex(BaseIndex):
    name = "inverted"

    def _build(self) -> None:
        postings = defaultdict(dict)
        for doc_id, doc in self.documents.items():
            for term, count in Counter(tokenize(doc.text)).items():
                postings[term][doc_id] = count
        self.postings = dict(postings)

    def _matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        scores: dict[str, int] = {}
        for term in set(terms):
            for doc_id, count in self.postings.get(term, {}).items():
                scores[doc_id] = scores.get(doc_id, 0) + count
        return scores, len(scores)
