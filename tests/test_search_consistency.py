import json
from pathlib import Path

from src.document_loader import Document
from src.document_loader import load_documents
from src.indexes import STRATEGIES


def test_equivalent_sets_scores_and_ties():
    docs = [Document("z", "Z", "red blue blue"), Document("a", "A", "red blue blue"), Document("b", "B", "green")]
    outcomes = []
    for strategy in STRATEGIES.values():
        index = strategy()
        index.build(docs)
        outcomes.append([(hit.id, hit.score) for hit in index.search("blue red blue").hits])
    assert outcomes == [[("a", 3), ("z", 3)]] * 4


def test_fixed_workload_matches_across_strategies():
    root = Path(__file__).resolve().parents[1]
    docs = load_documents(root / "data" / "documents")
    queries = json.loads((root / "data" / "queries" / "queries.json").read_text(encoding="utf-8"))
    indexes = []
    for strategy in STRATEGIES.values():
        index = strategy()
        index.build(docs)
        indexes.append(index)
    for item in queries:
        if item["kind"] == "terms":
            outcomes = [[(hit.id, hit.score) for hit in index.search(item["query"], top_k=100).hits] for index in indexes]
            assert outcomes[1:] == outcomes[:-1]
