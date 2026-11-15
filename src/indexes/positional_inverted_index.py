"""Inverted postings with positions for exact consecutive phrase matching."""

from collections import defaultdict

from src.indexes.base import BaseIndex

from src.preprocessing import tokenize


class PositionalInvertedIndex(BaseIndex):
    name = "positional"

    def _build(self) -> None:
        postings = defaultdict(lambda: defaultdict(list))
        for doc_id, doc in self.documents.items():
            for position, term in enumerate(tokenize(doc.text)):
                postings[term][doc_id].append(position)
        self.postings = {term: dict(doc_map) for term, doc_map in postings.items()}

    def _matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        scores: dict[str, int] = {}
        for term in set(terms):
            for doc_id, positions in self.postings.get(term, {}).items():
                scores[doc_id] = scores.get(doc_id, 0) + len(positions)
        return scores, len(scores)

    def _phrase_matching(self, terms: tuple[str, ...]) -> tuple[dict[str, int], int]:
        maps = [self.postings.get(term, {}) for term in terms]
        candidates = set(maps[0])
        for posting in maps[1:]:
            candidates.intersection_update(posting)
        scores = {}
        for doc_id in candidates:
            position_sets = [set(posting[doc_id]) for posting in maps[1:]]
            if any(all(start + offset in positions for offset, positions in enumerate(position_sets, 1)) for start in maps[0][doc_id]):
                scores[doc_id] = sum(len(self.postings[term][doc_id]) for term in set(terms))
        return scores, len(candidates)
