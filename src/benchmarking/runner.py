"""Command-line benchmark; no Flask rendering or network request is timed."""

import argparse
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter_ns

import pandas as pd

from src.benchmarking.plots import create_plots
from src.document_loader import Document, load_documents
from src.indexes import STRATEGIES
from src.preprocessing import tokenize


ROOT = Path(__file__).resolve().parents[2]


def collection_of_size(sample: list[Document], size: int) -> tuple[list[Document], bool]:
    if size < 1:
        raise ValueError("Dataset sizes must be positive.")
    if not sample:
        raise ValueError("The sample corpus is empty.")
    if size <= len(sample):
        return sample[:size], False
    return [
        Document(f"synthetic/{number + 1:05d}.txt", f"Synthetic {number + 1}: {sample[number % len(sample)].title}", sample[number % len(sample)].text)
        for number in range(size)
    ], True


def run_benchmarks(
    document_dir: str | Path = ROOT / "data" / "documents",
    query_file: str | Path = ROOT / "data" / "queries" / "queries.json",
    sizes: tuple[int, ...] = (12, 120, 600),
    repetitions: int = 5,
    output_dir: str | Path = ROOT / "results",
    make_plots: bool = True,
) -> dict[str, Path]:
    if repetitions < 1:
        raise ValueError("Repetitions must be positive.")
    sample = load_documents(document_dir)
    if not sample:
        raise ValueError("The sample corpus is empty.")
    queries = json.loads(Path(query_file).read_text(encoding="utf-8"))
    if not queries or any(row.get("kind") not in {"terms", "phrase"} or not row.get("query", "").strip() for row in queries):
        raise ValueError("The query file must contain nonempty terms or phrase queries.")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    environment = {
        "timestamp": datetime.now().astimezone().isoformat(),
        "python_version": platform.python_version(),
        "python_executable": Path(sys.executable).name,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "sample_document_count": len(sample),
        "sizes": list(sizes),
        "repetitions": repetitions,
        "memory_method": "Recursive sys.getsizeof over reachable Python objects, each object counted once; includes stored Document objects and index but excludes interpreter/native allocations.",
        "latency_method": "perf_counter_ns around search(query, include_snippets=False); one warmup per query before repetitions; Flask excluded.",
    }
    (target / "environment.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")

    rows = []
    for size in sizes:
        docs, synthetic = collection_of_size(sample, size)
        token_count = sum(len(tokenize(doc.text)) for doc in docs)
        for strategy_name, cls in STRATEGIES.items():
            index = cls()
            start = perf_counter_ns()
            index.build(docs)
            build_ms = (perf_counter_ns() - start) / 1_000_000
            memory_bytes = index.memory_usage()
            applicable = [row for row in queries if row["kind"] == "terms" or strategy_name == "positional"]
            for item in applicable:
                query = item["query"]
                index.search(query, include_snippets=False)  # identical warmup policy
                for repetition in range(1, repetitions + 1):
                    start = perf_counter_ns()
                    outcome = index.search(query, include_snippets=False)
                    latency_ms = (perf_counter_ns() - start) / 1_000_000
                    rows.append({
                        "dataset": f"{size}_{'synthetic' if synthetic else 'sample'}",
                        "synthetic": synthetic,
                        "doc_count": len(docs),
                        "token_count": token_count,
                        "strategy": strategy_name,
                        "kind": item["kind"],
                        "query": query,
                        "repetition": repetition,
                        "latency_ms": latency_ms,
                        "result_count": outcome.result_count,
                        "candidate_count": outcome.candidate_count,
                        "build_ms": build_ms,
                        "memory_bytes": memory_bytes,
                        "python_version": environment["python_version"],
                        "platform": environment["platform"],
                    })

    raw = pd.DataFrame(rows)
    raw_path = target / "raw_measurements.csv"
    raw.to_csv(raw_path, index=False)
    per_query = raw.groupby(
        ["dataset", "synthetic", "doc_count", "token_count", "strategy", "kind", "query", "build_ms", "memory_bytes", "python_version", "platform"],
        as_index=False,
    ).agg(
        median_latency_ms=("latency_ms", "median"),
        mean_latency_ms=("latency_ms", "mean"),
        result_count=("result_count", "first"),
        candidate_count=("candidate_count", "first"),
        repetitions=("repetition", "count"),
    )
    per_query_path = target / "per_query_summary.csv"
    per_query.to_csv(per_query_path, index=False)
    summary = per_query[per_query["kind"] == "terms"].groupby(
        ["dataset", "synthetic", "doc_count", "token_count", "strategy", "build_ms", "memory_bytes", "python_version", "platform"],
        as_index=False,
    ).agg(
        median_query_latency_ms=("median_latency_ms", "median"),
        mean_candidate_count=("candidate_count", "mean"),
        mean_result_count=("result_count", "mean"),
        query_count=("query", "count"),
    )
    summary_path = target / "summary.csv"
    summary.to_csv(summary_path, index=False)
    paths = {"raw": raw_path, "per_query": per_query_path, "summary": summary_path, "environment": target / "environment.json"}
    if make_plots:
        for path in create_plots(summary_path, target / "plots"):
            paths[path.stem] = path
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark four document search strategies.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[12, 120, 600])
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--documents", type=Path, default=ROOT / "data" / "documents")
    parser.add_argument("--queries", type=Path, default=ROOT / "data" / "queries" / "queries.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    paths = run_benchmarks(args.documents, args.queries, tuple(args.sizes), args.repetitions, args.output)
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
