# SDS Mini-Project Experiment Report

## Objective and method

The project compares sequential scan, a forward index, an inverted index, and a positional inverted index for local document search. All four use the same tokenizer, OR matching for ordinary queries, and sum of distinct query-term frequencies for scoring. The positional variant also tests exact consecutive phrases.

The recorded run used Windows 11, Python 3.12.8 in a `uv`-managed `.venv`, an Intel Family 6 Model 183 processor, and 16 logical CPUs. It ran on 15 November 2026 (local time). The input was 12 sample text files (409 tokens), plus synthetic 120- and 600-document collections formed by repeating the sample text. The fixed ordinary workload contained six queries. Each query had one warmup and five measured repetitions. There were 390 timed searches in total, including positional-only phrase queries. All CSV fields were populated.

Build time was measured around `build(documents)` with `perf_counter_ns`. Query latency was measured around `search(query, include_snippets=False)`; Flask, networking, and snippets were excluded. The table reports the median of the six ordinary queries' per-query median latencies. Stored memory is a recursive `sys.getsizeof` estimate that includes documents and index objects, with shared objects counted once. See `results/environment.json` for the full recorded conditions.

## Measured results

| Documents | Strategy | Build (ms) | Median query (ms) | Stored memory (KiB) | Mean candidates |
| ---: | --- | ---: | ---: | ---: | ---: |
| 12 | Sequential | 0.0041 | 0.1644 | 8.4 | 12.0 |
| 12 | Forward | 0.1673 | 0.0110 | 35.5 | 12.0 |
| 12 | Inverted | 0.2496 | 0.0055 | 66.9 | 4.3 |
| 12 | Positional | 0.3050 | 0.0052 | 99.2 | 4.3 |
| 120 | Sequential | 0.0081 | 1.5874 | 38.9 | 120.0 |
| 120 | Forward | 1.7104 | 0.0701 | 307.0 | 120.0 |
| 120 | Inverted | 2.4736 | 0.0222 | 150.9 | 43.3 |
| 120 | Positional | 4.5856 | 0.0174 | 464.9 | 43.3 |
| 600 | Sequential | 0.0403 | 8.2924 | 177.1 | 600.0 |
| 600 | Forward | 7.2940 | 0.3262 | 1513.3 | 600.0 |
| 600 | Inverted | 8.9173 | 0.0622 | 729.6 | 216.7 |
| 600 | Positional | 16.7560 | 0.0694 | 2296.2 | 216.7 |

The exact byte counts and unrounded timings are in `results/summary.csv`.

## Interpretation

Sequential scan had almost no build cost and the smallest stored representation, but its query time grew from 0.1644 ms at 12 documents to 8.2924 ms at 600 because it re-tokenized every document. Forward indexing spent more time and memory during construction, then avoided re-tokenization; it still checked every document's term map for each query. Inverted indexing considered about 217 candidate documents on average at size 600, versus 600 for the document-oriented approaches, and had the lowest median ordinary-query latency at that size (0.0622 ms). The positional index added phrase capability and had the highest build time and stored memory at size 600, 16.7560 ms and about 2296 KiB. Its ordinary-query latency was close to the inverted index in this workload.

The 12-document memory ordering differs from the 600-document ordering: dictionary overhead makes the small inverted structure larger than the forward one, while repeated vocabulary lets postings share term keys at larger sizes. This is specific to Python objects and these repeated texts; it is not a general memory ranking of index designs. All ordinary queries returned matching-document sets and scores consistently in automated tests.

## Limitations and next steps

The synthetic collections repeat only 12 documents and share underlying text string objects. They model increasing document count with fixed vocabulary, not a growing independent corpus. The measured object sizes exclude native and interpreter allocations, and timings below a millisecond are sensitive to machine load. Query order and strategy order are fixed. A stronger follow-up experiment would add a larger independent corpus, randomize run order, repeat the whole experiment several times, and compare distributions. This mini-project deliberately does not implement semantic search, typo correction, crawling, or production deployment.

Reproduce the tables and plots with `uv run python -m src.benchmarking.runner`. The current Streamlit screenshots are `results/screenshots/streamlit_search.png` and `results/screenshots/streamlit_benchmarks.png`; plots are in `results/plots/`.
