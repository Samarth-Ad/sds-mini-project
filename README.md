# Smart Search Engine Using Multiple Indexing Techniques

A Scalable Data Structures (SDS) mini-project for searching local text documents and measuring how the choice of index changes build time, query latency, query work, and memory use.

The **Streamlit dashboard is the main interface**. It provides document search, a view of measured benchmark plots, and an explanation of the four strategies. A small Flask interface remains available for the original project plan. The search engine, benchmark runner, and both interfaces share the same Python indexing code. Dependencies and the local `.venv` are managed with `uv`.

## Contents

- [Quick start](#quick-start)
- [Using the dashboard](#using-the-dashboard)
- [Search rules](#search-rules)
- [Indexing strategies](#indexing-strategies)
- [Project layout](#project-layout)
- [Documents and query workload](#documents-and-query-workload)
- [Run the benchmarks](#run-the-benchmarks)
- [Recorded results](#recorded-results)
- [Tests](#tests)
- [Screenshots](#screenshots)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)

## Quick start

You need `uv` and access to Python 3.12. Install `uv` using its [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/). If Python 3.12 is not installed, `uv` can obtain it during setup.

Clone the repository and run these commands in its root directory:

```powershell
git clone https://github.com/Samarth-Ad/sds-mini-project.git
cd sds-mini-project
uv sync --locked --python 3.12
uv run streamlit run streamlit_app.py
```

Open **http://localhost:8501**. Stop the server with Ctrl+C.

`uv sync` creates `.venv` and installs the versions in `uv.lock`. `uv run` uses that environment automatically, so manual activation is optional. If you want to activate it, use `.\.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in Bash.

### Optional Flask interface

The original Flask page remains available:

```powershell
uv run flask --app app run
```

Open **http://127.0.0.1:5000**. The Streamlit app is the recommended way to explore the project.

## Using the dashboard

The sidebar has three views:

| View | What you can do |
| --- | --- |
| **Search** | Enter a query, select an index, choose 5, 10, or 20 results, and inspect titles, snippets, scores, result count, candidate count, and search time. |
| **Benchmarks** | Compare the recorded query latency, build time, and memory plots. Expand the measurement table or download the summary CSV. |
| **How it works** | Read a short explanation of each data structure and the shared scoring rule. |

The Search view opens with an example query, `index`. To try phrase search, select **Positional index** and enter `"search engine"`. The benchmark view reads previously generated files; it does not run experiments inside a web request.

## Search rules

All four strategies use the same rules for ordinary queries:

1. Text is converted to lowercase ASCII letter and digit tokens. Punctuation separates tokens. The same tokenizer processes documents and queries.
2. Multiple terms use **OR** matching: a document is a match if it contains any query term.
3. A result's relevance score is the sum of the term frequencies for **distinct** query terms. For example, a document containing `index index search` scores **3** for `index search index`.
4. Results are ordered by descending score, then by document ID for stable ties.
5. The result count includes every match; the selected top-k limit controls how many cards are shown.

A fully quoted query is an **exact consecutive phrase query**. Only the positional index supports it. Other strategies display a clear error for phrase queries. Empty or punctuation-only queries are rejected; a query with no matches produces an empty-result message. There is no stemming, stop-word removal, typo correction, or semantic search.

## Indexing strategies

Let `N` be the document count, `T` the total number of tokens, and `Q` the distinct query terms. These are useful descriptions of the work involved, not fixed runtime guarantees for Python dictionaries.

| Strategy | Stored data | Build behavior | Query behavior |
| --- | --- | --- | --- |
| **Sequential scan** | Documents only | Stores the document references with little preparation. | Re-tokenizes and checks every document; work grows with the collection's text. |
| **Forward index** | Document ID → term-frequency map | Tokenizes documents and stores their term counts. | Checks each document's term map for the requested terms. |
| **Inverted index** | Term → document-frequency postings | Builds one posting map per term. | Retrieves postings for the query terms and combines matching document IDs. |
| **Positional inverted index** | Term → document positions | Stores token positions in postings, which costs more build time and memory. | Handles ordinary queries like an inverted index and checks consecutive positions for phrases. |

The positional structure is an extension of the inverted index. The **same ordinary-query score** is used by every strategy, so their matching sets and scores can be compared directly. The implementation lives under `src/indexes/` behind a common `build`, `search`, and `memory_usage` interface.

## Project layout

```text
.
├── streamlit_app.py          # Main search and benchmark dashboard
├── app.py                    # Optional Flask interface
├── pyproject.toml            # uv-managed project dependencies
├── uv.lock                   # Resolved dependency versions
├── data/
│   ├── documents/            # Checked-in UTF-8 sample .txt files
│   └── queries/queries.json  # Fixed benchmark workload
├── src/
│   ├── preprocessing.py      # Shared tokenizer
│   ├── document_loader.py    # Stable document IDs and titles
│   ├── ranking.py            # Query parsing, scores, snippets
│   ├── indexes/              # Four search strategies
│   └── benchmarking/         # Runner and CSV-derived plots
├── tests/                    # Search, benchmark, Flask, Streamlit tests
├── results/                  # Measured CSVs, plots, environment, screenshots
├── README.md                 # Setup and usage guide
├── REPORT.md                 # Experiment discussion
└── PLAN.md                   # Original project plan
```

## Documents and query workload

The app loads UTF-8 `.txt` files recursively from `data/documents/`. A document's ID is its path relative to that folder; its display title comes from the filename. Twelve small sample files are included, so the app works immediately after cloning. The checked-in sample contains **409 tokens** under the project's tokenizer.

To search your own collection, add `.txt` files under `data/documents/` and restart the app to rebuild its cached indexes. Other file types are ignored. The command-line benchmark can instead read a different directory with `--documents`.

The fixed workload in `data/queries/queries.json` includes common and rare terms, multi-term queries, a no-match query, and two phrases. Its entries have this shape:

```json
[
  {"kind": "terms", "query": "index"},
  {"kind": "phrase", "query": "\"search engine\""}
]
```

Ordinary queries run on all four strategies. Phrase queries run only on the positional strategy.

## Run the benchmarks

From the repository root:

```powershell
uv run python -m src.benchmarking.runner
```

The defaults use **12, 120, and 600 documents** and **five timed repetitions per applicable query**. The 12-document set is the real checked-in sample. The 120- and 600-document sets repeat its text with new IDs and are explicitly labeled **synthetic**; they are useful for a controlled scaling demonstration, not a substitute for an independent larger corpus.

You can choose different settings and an output folder:

```powershell
uv run python -m src.benchmarking.runner --sizes 12 120 600 --repetitions 10 --output results/custom-run
```

Other options are `--documents PATH` and `--queries PATH`. For sizes no larger than the input corpus, the runner uses the first files in sorted order. For larger sizes, it repeats the input texts with synthetic IDs. Dataset and query inputs are identical across applicable strategies.

### What is measured

- **Build time:** `perf_counter_ns` around `build(documents)`, separate from query timing.
- **Search latency:** `perf_counter_ns` around `search(query, include_snippets=False)`. One warmup precedes the timed repetitions for each query. Flask rendering, Streamlit rendering, snippets, and network time are excluded.
- **Per-query latency:** median and mean across repetitions. The comparison summary uses the median of the six ordinary queries' per-query medians.
- **Candidate count:** all documents inspected for sequential and forward search; union of postings for ordinary inverted queries; intersected postings before position checks for phrases. It is a coarse work measure, not an instruction count.
- **Stored memory:** recursive `sys.getsizeof` of reachable index and document objects, counting shared objects once. It is an estimate, not total process memory.

The runner uses Pandas to export measurements and generates plots from the measured summary CSV. It records Python, platform, processor, logical CPU count, timestamp, dataset counts, and experiment settings.

| Output | Contents |
| --- | --- |
| `results/raw_measurements.csv` | Every timed repetition, including latency, build time, memory, result/candidate counts, query, dataset, and runtime fields. |
| `results/per_query_summary.csv` | Median and mean latency plus result/candidate counts for each query. |
| `results/summary.csv` | Ordinary-query comparison for each strategy and dataset size. |
| `results/environment.json` | Recorded machine/runtime details and measurement definitions. |
| `results/plots/build_time.png` | Index construction time by collection size. |
| `results/plots/query_latency.png` | Median query latency by collection size, with a log-scale latency axis. |
| `results/plots/memory_usage.png` | Estimated stored memory by collection size. |

The default command rewrites the files in `results/`. Use `--output` to keep a separate run.

## Recorded results

The included run was made on **15 November 2026**, on Windows 11 with Python 3.12.8 and 16 logical CPUs. At **600 synthetic documents / 20,450 tokens**, the measured ordinary-query results were:

| Strategy | Build (ms) | Median query (ms) | Stored memory (KiB) | Mean candidates |
| --- | ---: | ---: | ---: | ---: |
| Sequential scan | 0.0403 | 8.2924 | 177.1 | 600.0 |
| Forward index | 7.2940 | 0.3262 | 1513.3 | 600.0 |
| Inverted index | 8.9173 | 0.0622 | 729.6 | 216.7 |
| Positional inverted index | 16.7560 | 0.0694 | 2296.2 | 216.7 |

This run shows the scan's low build cost and higher repeated-query cost, and the positional index's additional memory and build cost for phrase capability. It does **not** establish a universal winner. See [REPORT.md](REPORT.md) for all three sizes, interpretation, and limitations; see `results/summary.csv` for unrounded measurements.

## Tests

Run the full suite with:

```powershell
uv run pytest -q
```

The suite covers tokenization and document loading; empty and populated indexes; known, absent, multi-term, and phrase queries; deterministic ranking; agreement across strategies on the fixed workload; benchmark output; and both Flask and Streamlit interfaces. The current suite has **22 passing tests**.

## Screenshots

- [Streamlit search view](results/screenshots/streamlit_search.png)
- [Streamlit benchmark view](results/screenshots/streamlit_benchmarks.png)

To recapture them on Windows with Microsoft Edge installed, start Streamlit on port 8501, then run this in a second terminal:

```powershell
uv run --with playwright python scripts/capture_streamlit.py
```

`--with playwright` provides a temporary screenshot tool; Playwright is not a runtime dependency of the search app.

## Limitations

- The sample is deliberately small. The larger benchmark sizes repeat its text and vocabulary, so the results do not predict behavior on an independent corpus.
- Synthetic documents share text string objects. The recursive memory estimate counts shared objects once and excludes interpreter, allocator, native-library, and temporary query allocations.
- Very short query timings can change with machine load. The strategy and query order is fixed; repeated whole experiments and a larger independent corpus would strengthen conclusions.
- The tokenizer uses ASCII words and numbers; it is not suitable for full multilingual search.
- Indexes are built on first load after the app starts. There is no live document update, database, crawling, authentication, or production deployment layer.

## Troubleshooting

| Problem | What to try |
| --- | --- |
| `uv` is not found | Install it from the official link above, then open a new terminal. |
| Python 3.12 is unavailable | Run `uv python install 3.12`, then `uv sync --locked --python 3.12`. |
| No documents appear | Confirm that `data/documents/` contains UTF-8 `.txt` files and restart the app. |
| An exact phrase shows an error | Select **Positional index** and put the entire phrase in double quotes. |
| Benchmark charts are missing | Run `uv run python -m src.benchmarking.runner`. |
| Port 8501 is in use | Run `uv run streamlit run streamlit_app.py --server.port 8502` and open the new port. |
| PowerShell blocks environment activation | Use `uv run` directly; activation is optional. |
