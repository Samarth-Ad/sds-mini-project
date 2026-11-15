"""Plots derived only from measured summary CSV data."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def create_plots(summary_csv: str | Path, output_dir: str | Path) -> list[Path]:
    data = pd.read_csv(summary_csv)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    metrics = [
        ("build_ms", "Index build time (ms)", "build_time.png"),
        ("median_query_latency_ms", "Median query latency (ms)", "query_latency.png"),
        ("memory_bytes", "Estimated stored memory (bytes)", "memory_usage.png"),
    ]
    paths = []
    for column, label, filename in metrics:
        fig, ax = plt.subplots(figsize=(8, 5))
        for strategy, rows in data.groupby("strategy", sort=True):
            rows = rows.sort_values("doc_count")
            ax.plot(rows["doc_count"], rows[column], marker="o", linewidth=2, label=strategy.title())
        ax.set_xlabel("Document count")
        ax.set_ylabel(label)
        ax.set_title(label + " by collection size")
        if column == "median_query_latency_ms":
            ax.set_yscale("log")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        path = target / filename
        fig.savefig(path, dpi=160)
        plt.close(fig)
        paths.append(path)
    return paths
