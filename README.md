# Smart Search Engine Using Multiple Indexing Techniques

An SDS mini-project that searches local text files and compares four data structures on the same documents and queries. The main interface is a Streamlit dashboard with search, benchmark, and explanation views. The original Flask interface is also available. `uv` manages dependencies and creates the local `.venv`.

## Run locally

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use Python 3.12 or let `uv` download it. From the repository root in PowerShell:

```powershell
uv sync --python 3.12
uv run pytest -q
uv run streamlit run streamlit_app.py
```

Open `http://localhost:8501`. The Streamlit sidebar switches between Search, Benchmarks, and How it works. `uv sync` creates `.venv`; `uv run` uses it. To activate the environment manually in PowerShell, run `.\.venv\Scripts\Activate.ps1`.

The earlier Flask interface remains available with `uv run flask --app app run` at `http://127.0.0.1:5000`.

To reproduce the measured experiment and regenerate all CSVs and plots:

```powershell
uv run python -m src.benchmarking.runner
```

Optional parameters: `--sizes 12 120 600`, `--repetitions 5`, `--documents data/documents`, `--queries data/queries/queries.json`, and `--output results`.

## Search behavior

- Documents are UTF-8 `.txt` files under `data/documents`; relative filenames are stable IDs. Add more local text files there and restart Flask.
- Documents and queries use the same tokenizer: lowercase ASCII letters and digits. Punctuation separates words. No stemming, stop-word removal, or semantic search is used.
- Ordinary multi-term queries use **OR**. The relevance score sums each distinct query term's frequency in a document. Results sort by descending score, then ID for deterministic ties.
- Put a whole query in double quotes and select **Positional** for an exact consecutive phrase, for example `"search engine"`. Other strategies reject phrase queries with an explanatory message.
- Empty queries are rejected. No-match queries display a clear message. The total match count can exceed the displayed top-k results.

## Strategies

| Strategy | Stored representation | Query work |
| --- | --- | --- |
| Sequential scan | Documents only | Re-tokenize and inspect every document per query |
| Forward index | Document ID → term frequencies | Inspect every document's term map |
| Inverted index | Term → document IDs and frequencies | Inspect postings for the requested terms |
| Positional inverted index | Term → document IDs and token positions | Inspect postings; intersect positions for phrases |

The positional index extends the inverted index with position lists. The same normal-query scoring rule applies to all four strategies.

## Benchmark design

The fixed workload is in `data/queries/queries.json`: common and rare terms, multi-term queries, a no-match query, and two phrase queries. Six ordinary queries run on all four strategies; the phrase queries run only on the positional strategy. Each query receives one warmup, followed by five timed repetitions by default. The runner times `search` with snippets disabled; Flask and network overhead are excluded. It times index construction separately. Each per-query result reports median and mean latency; `summary.csv` reports the median of the six per-query medians.

The checked-in corpus has 12 documents and 409 tokens. Sizes 120 and 600 repeat its texts with distinct synthetic IDs. These larger sets demonstrate scaling under repeated content, not performance on independent real-world documents. The runner labels each generated collection as synthetic and records document and token counts.

Candidate count means documents inspected for sequential/forward, union of postings for ordinary inverted queries, and intersected posting candidates for phrases. This is a coarse measure of query work, not an instruction count. Memory is recursive `sys.getsizeof` of reachable index and stored document objects, counting shared objects once. It excludes native allocations, interpreter state, allocator overhead, and temporary search objects. Synthetic documents reuse text strings, so their memory totals should not be extrapolated to independent corpora. Extremely short query timings can vary across runs; compare trends and rerun on your own machine.

## Outputs and report

- `results/raw_measurements.csv`: every timed query repetition, result/candidate counts, build time, memory, dataset and runtime details.
- `results/per_query_summary.csv`: median and mean latency for each query.
- `results/summary.csv`: ordinary-query comparison by strategy and dataset size.
- `results/environment.json`: machine, Python, experiment settings, and measurement definitions.
- `results/plots/`: build time, median query latency (log scale), and memory plots generated from the summary CSV.
- `results/screenshots/`: screenshots of the running Streamlit search and benchmark views, plus the earlier Flask views.
- `REPORT.md`: observed results, interpretation, and limitations.

To recapture the Streamlit screenshots on Windows with Microsoft Edge installed, start the Streamlit app and run `uv run --with playwright python scripts/capture_streamlit.py` in a second terminal. Playwright is used temporarily by this command and is not a project dependency.

No external database or web crawler is required. The apps load and build the indexes at startup, so newly added files appear after restart.
