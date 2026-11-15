import pytest

from src.document_loader import Document
from src.indexes import STRATEGIES


DOCS = [
    Document("a", "A", "search engine search index"),
    Document("b", "B", "engine for search and indexing"),
    Document("c", "C", "memory only"),
]


@pytest.mark.parametrize("strategy", STRATEGIES.values())
def test_empty_and_known_queries(strategy):
    index = strategy()
    index.build([])
    assert index.search("search").hits == []
    index.build(DOCS)
    assert [hit.id for hit in index.search("search").hits] == ["a", "b"]
    assert index.search("absent").result_count == 0
    assert [hit.id for hit in index.search("memory search").hits] == ["a", "b", "c"]
    assert index.memory_usage() > 0


def test_phrase_positions():
    index = STRATEGIES["positional"]()
    index.build(DOCS)
    assert [hit.id for hit in index.search('"search engine"').hits] == ["a"]
    assert index.search('"engine index"').result_count == 0
    assert [hit.id for hit in index.search('"search index"').hits] == ["a"]


@pytest.mark.parametrize("strategy", STRATEGIES.values())
def test_invalid_queries(strategy):
    index = strategy()
    index.build(DOCS)
    with pytest.raises(ValueError):
        index.search(" ")
    with pytest.raises(ValueError):
        index.search("!!!")
    with pytest.raises(ValueError):
        index.search("search", top_k=0)


def test_nonpositional_rejects_phrase():
    index = STRATEGIES["inverted"]()
    index.build(DOCS)
    with pytest.raises(ValueError):
        index.search('"search engine"')
