"""Load UTF-8 plain text files with stable, relative-path IDs."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str


def load_documents(directory: str | Path) -> list[Document]:
    root = Path(directory)
    if not root.is_dir():
        raise FileNotFoundError(f"Document directory does not exist: {root}")
    files = sorted(root.rglob("*.txt"))
    return [
        Document(path.relative_to(root).as_posix(), path.stem.replace("_", " ").title(), path.read_text(encoding="utf-8"))
        for path in files
    ]
