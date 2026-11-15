import pandas as pd

from src.benchmarking.runner import collection_of_size, run_benchmarks
from src.document_loader import Document


def test_synthetic_dataset_is_labeled():
    sample = [Document("one", "One", "alpha beta")]
    docs, synthetic = collection_of_size(sample, 3)
    assert synthetic and len(docs) == 3
    assert len({doc.id for doc in docs}) == 3


def test_benchmark_measurements_are_exported(tmp_path):
    paths = run_benchmarks(sizes=(3, 6, 9), repetitions=2, output_dir=tmp_path, make_plots=False)
    raw = pd.read_csv(paths["raw"])
    summary = pd.read_csv(paths["summary"])
    assert set(summary["doc_count"]) == {3, 6, 9}
    assert set(summary["strategy"]) == {"sequential", "forward", "inverted", "positional"}
    assert len(summary) == 12
    assert (raw["latency_ms"] >= 0).all()
    assert (raw["memory_bytes"] > 0).all()
    assert (raw["candidate_count"] >= raw["result_count"]).all()
    assert (summary["query_count"] == 6).all()
