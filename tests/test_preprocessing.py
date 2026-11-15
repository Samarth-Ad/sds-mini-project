from pathlib import Path

import pytest

from src.document_loader import load_documents
from src.preprocessing import tokenize


def test_tokenization_is_consistent():
    assert tokenize("Search, SEARCH 42! café") == ["search", "search", "42", "caf"]


def test_document_loader_has_stable_ids(tmp_path: Path):
    (tmp_path / "b.txt").write_text("Second", encoding="utf-8")
    (tmp_path / "a.txt").write_text("First", encoding="utf-8")
    docs = load_documents(tmp_path)
    assert [doc.id for doc in docs] == ["a.txt", "b.txt"]
    assert docs[0].title == "A"


def test_missing_document_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "missing")
