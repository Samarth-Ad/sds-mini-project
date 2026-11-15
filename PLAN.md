# Plan --- Smart Search Engine Using Multiple Indexing Techniques

## 1. Project Brief

**Course:** Scalable Data Structures (SDS)\
**Mini-project topic:** Smart Search Engine Using Multiple Indexing
Techniques\
**Required tools:** Python, Flask, Pandas

Build a working document-search application and use it to compare
indexing strategies. The comparison must focus on:

-   Index construction time
-   Search/query latency
-   Query-processing work
-   Memory usage

The project should demonstrate how the choice of data structure affects
search performance as the document collection grows. Keep the
implementation understandable, reproducible, and appropriate for an
academic mini-project. Do not turn it into a production-scale search
platform.

## 2. Instructions to Codex Before Implementation

1.  Inspect the current repository, its files, dependencies, and
    existing implementation before changing anything.
2.  If the repository already contains useful code, preserve and extend
    it. Do not replace working code merely to match the proposed folder
    structure.
3.  If the repository is empty, create the structure proposed in this
    plan.
4.  Implement in small phases. After each phase, run the relevant tests
    and fix failures before proceeding.
5.  Keep the indexing implementations separate behind a common interface
    so they can be benchmarked with the same documents and queries.
6.  Do not fabricate benchmark results. Generate results by running the
    benchmark code and clearly record the machine/runtime conditions.
7.  Avoid unnecessary dependencies, premature optimization, distributed
    infrastructure, external databases, authentication, and unrelated
    features.
8.  Document assumptions and limitations. Prefer simple, readable
    implementations over clever but difficult-to-explain code.

## 3. Scope and Features

### Core functionality

-   Load a collection of text documents from a local dataset directory.
-   Extract document IDs, filenames, and text content.
-   Normalize text consistently before indexing and querying.
-   Build and select among multiple indexing strategies.
-   Accept a user query and return ranked matching documents.
-   Display document title/name, a relevant text snippet, and a
    relevance score.
-   Provide a Flask web interface for searching and viewing results.
-   Benchmark the indexing strategies on identical datasets and query
    sets.
-   Export benchmark measurements to CSV using Pandas.

### Explicitly out of scope

-   Large language model or generative-AI search.
-   Semantic/vector search and embeddings.
-   Web crawling or scraping.
-   Distributed indexing or cluster deployment.
-   User accounts, permissions, and production authentication.
-   Production-grade typo correction or sophisticated relevance
    learning.

These features are not required by the supplied project brief and should
not be added unless explicitly requested later.

## 4. Indexing Strategies to Implement

Implement a common interface, for example:

-   `build(documents)`
-   `search(query, top_k=10)`
-   `memory_usage()`
-   Optional diagnostic method such as `candidate_count(query)`

All strategies must use the same tokenizer, normalization rules,
dataset, and query set wherever applicable.

### Strategy A --- Sequential Scan (No Persistent Search Index)

**Purpose:** Baseline against which indexed approaches can be compared.

-   Store the documents in their ordinary in-memory representation.
-   For each query, tokenize/normalize the query and inspect each
    document.
-   Determine whether the query terms occur in the document.
-   Rank results using a simple, documented scoring rule.

Measure query latency and memory usage. Explain that this approach
avoids index-construction overhead but repeats work for every query.

### Strategy B --- Forward Index

**Purpose:** Represent each document by the terms it contains.

-   Build a mapping from document ID to its unique terms and, where
    useful, term frequencies.
-   Process a query by checking the query terms against document-level
    term data.
-   Return matching documents using the same scoring convention as the
    other strategies where possible.

Measure construction time, query latency, and memory usage. Explain that
the representation is document-oriented, so query processing may need to
inspect many documents.

### Strategy C --- Inverted Index

**Purpose:** Implement the principal search-engine indexing technique.

-   Build a mapping from each term to the documents containing it.
-   Store term frequency or other minimal posting information if needed
    for ranking.
-   For a query, retrieve postings for its terms rather than scanning
    every document.
-   Combine candidate documents and rank them using a simple, documented
    scoring method.

Measure construction time, query latency, and memory usage. This is the
central indexing technique named in the assignment.

### Strategy D --- Positional Inverted Index

**Purpose:** Demonstrate an enhanced inverted index that stores term
positions.

-   Map each term to postings containing document IDs and the positions
    at which the term occurs.
-   Support ordinary term queries.
-   Add phrase-query support by checking whether query terms occur at
    consecutive positions in a document.
-   Measure the additional construction and memory cost, as well as
    query performance.

This is an extension of the inverted index, not a completely unrelated
data structure. Explain that distinction in the report.

### Fair-comparison rules

-   Apply identical text normalization and tokenization across all
    strategies.
-   Use the same documents and query inputs for each strategy.
-   Separate index-building time from query time.
-   Warm up implementations consistently before timed measurements.
-   Run each query multiple times and report a robust statistic (at
    minimum median latency; optionally mean and standard deviation).
-   Do not include Flask rendering or network overhead in core indexing
    benchmarks.
-   Report memory measurement methodology and its limitations. Use one
    consistent method for all strategies.
-   Do not claim one strategy is universally best: interpret results in
    relation to the tested workload and dataset.

## 5. Text Processing and Ranking

Create a shared preprocessing module used by every indexing strategy.

Suggested initial normalization:

1.  Convert text to lowercase.
2.  Extract word tokens consistently (document and query paths must
    match).
3.  Remove empty tokens.
4.  Optionally support a configurable stop-word list, but keep the
    default behavior consistent across all strategies.
5.  Do not introduce stemming or lemmatization unless it is implemented
    consistently and documented.

Use a simple and explainable ranking rule. A suitable initial choice is
the sum of term frequencies for the query terms. If implementing TF-IDF,
implement it consistently and explain the formula. Avoid mixing
incompatible scoring rules in the comparison.

Define query behavior explicitly:

-   **Single-term query:** return documents containing the term.
-   **Multi-term query:** document whether the default behavior is OR
    (any query term) or AND (all query terms); use the same behavior
    across strategies.
-   **Phrase query:** supported by the positional inverted index.
-   **No-match query:** return an empty result with a clear UI message.
-   **Empty query:** validate it and do not run a benchmark/search.

For reproducibility, document the chosen defaults in the README.

## 6. Dataset and Benchmark Design

### Dataset

Start with a small, version-controlled sample of text documents so the
project works immediately after cloning. Keep documents as separate
files with stable IDs or derive stable IDs from filenames.

For scalability experiments, support generating larger collections from
the sample corpus or loading additional local text files. Do not
silently duplicate documents and present them as independent real-world
data; clearly label generated or repeated data as synthetic.

Use at least three dataset sizes (small, medium, large). Choose sizes
that can run on an ordinary student laptop, and record the actual
document counts and total token counts used.

### Query set

Create a fixed query file containing a mix of:

-   Common terms appearing in many documents
-   Rare terms appearing in few documents
-   Multi-term queries
-   Queries with no matches
-   Phrase queries for the positional index

Use the same applicable query set for every strategy. Keep query inputs
fixed between runs.

### Measurements

Capture at least:

  -----------------------------------------------------------------------
  Metric                              What it measures
  ----------------------------------- -----------------------------------
  Index build time                    Time to construct the strategy's
                                      data structure

  Search latency                      Time taken by the strategy to
                                      process a query

  Median query latency                Median across repeated measurements

  Memory usage                        Memory attributable to the stored
                                      documents/index, measured
                                      consistently

  Result count                        Number of documents returned

  Candidate count                     Number of documents examined or
                                      considered, where measurable
  -----------------------------------------------------------------------

Also record dataset size, number of tokens, number of queries,
repetitions, Python version, and machine details where available.

### Benchmark procedure

1.  Load one dataset size.
2.  Initialize one strategy and measure its build time.
3.  Measure memory after construction using the chosen consistent
    method.
4.  Warm up the strategy.
5.  Execute every benchmark query for multiple repetitions.
6.  Record per-query latency and compute summary statistics.
7.  Repeat for each strategy and dataset size.
8.  Export raw measurements and aggregated summaries to CSV.
9.  Generate plots from the measured CSV data, not manually entered
    values.

Keep benchmark execution separate from the Flask request path so
measurements are not distorted by UI overhead.

## 7. Application Architecture

Use a small modular Python application.

Suggested structure (adapt it to the existing repository if one already
exists):

``` text
project/
├── app.py
├── requirements.txt
├── README.md
├── PLAN.md
├── data/
│   ├── documents/
│   └── queries/
├── src/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── document_loader.py
│   ├── ranking.py
│   ├── indexes/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── sequential_scan.py
│   │   ├── forward_index.py
│   │   ├── inverted_index.py
│   │   └── positional_inverted_index.py
│   └── benchmarking/
│       ├── __init__.py
│       ├── runner.py
│       ├── metrics.py
│       └── plots.py
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── styles.css
├── results/
│   ├── .gitkeep
│   └── plots/
└── tests/
    ├── test_preprocessing.py
    ├── test_indexes.py
    ├── test_search_consistency.py
    └── test_benchmarking.py
```

The structure is a proposal, not a requirement to restructure an
existing repository. Keep generated benchmark output out of source
modules.

### Responsibilities

-   `document_loader.py`: read documents and expose a consistent
    document representation.
-   `preprocessing.py`: tokenize and normalize both documents and
    queries.
-   `ranking.py`: provide shared, explainable scoring behavior.
-   `indexes/`: implement each strategy behind the same interface.
-   `benchmarking/`: run repeatable experiments, aggregate metrics,
    export CSV, and create plots.
-   `app.py`: initialize/load the selected strategy and expose Flask
    routes.
-   `templates/` and `static/`: provide a minimal, usable search
    interface.
-   `tests/`: verify correctness, consistency, and benchmark output
    shape.

## 8. Flask Interface

Build a clean, minimal interface rather than spending time on elaborate
styling.

### Search page

Include:

-   Project title and short description.
-   Search input.
-   Indexing strategy selector.
-   Search button.
-   Optional top-k selector.
-   Clear validation for empty input.

### Results page or results section

For each result, show:

-   Document title or filename.
-   Relevance score.
-   Short matching snippet.
-   Selected indexing strategy.

Also show a concise search summary such as query time and result count.
Label timing units clearly.

### Benchmark page or command-line workflow

The benchmark does not need to run inside a web request. Prefer a
command-line command/script to run experiments and save CSVs/plots. The
Flask app may display previously generated benchmark summaries if
convenient.

Suggested routes:

-   `GET /` --- search page.
-   `POST /search` --- execute search using the selected strategy.
-   `GET /benchmarks` --- optionally display existing benchmark
    summaries.

Validate user input and handle missing files or unavailable strategies
gracefully.

## 9. Testing and Correctness

Write tests before treating a strategy as complete.

### Required checks

-   Tokenization and normalization are consistent.
-   Each index can be built from an empty and a non-empty collection.
-   A known term returns the expected documents.
-   A term absent from the collection returns no results.
-   Multi-term behavior follows the documented AND/OR rule.
-   Search results are valid document IDs and contain no duplicates.
-   Ranking order is deterministic for tied scores.
-   All strategies return equivalent matching-document sets for query
    types they claim to support.
-   Positional phrase queries match consecutive positions and reject
    non-consecutive occurrences.
-   Empty queries are rejected or handled consistently.
-   Benchmark output contains the expected metrics and no fabricated or
    missing measurements.

Do not require identical ranking across strategies if their data
structures support different query capabilities; require matching result
sets and scoring semantics for equivalent queries.

## 10. Implementation Milestones

### Phase 0 --- Repository inspection and baseline

-   Inspect files, current code, Python version, and environment.
-   Identify what already exists and what is missing.
-   Run existing tests, if present.
-   Record a short implementation checklist before editing.

**Exit condition:** Codex understands the existing project and has a
non-destructive implementation plan.

### Phase 1 --- Data model and preprocessing

-   Define the document representation.
-   Implement local document loading.
-   Implement shared tokenization and normalization.
-   Add a small sample corpus and fixed query set.
-   Add unit tests.

**Exit condition:** Documents load reliably and preprocessing tests
pass.

### Phase 2 --- Index implementations

-   Implement sequential scan.
-   Implement forward index.
-   Implement inverted index.
-   Implement positional inverted index and phrase matching.
-   Add a common interface and correctness tests.

**Exit condition:** Every strategy works independently and equivalent
queries produce consistent matching-document sets.

### Phase 3 --- Search behavior

-   Implement shared scoring and top-k behavior.
-   Add query validation and snippets.
-   Verify behavior for single-term, multi-term, phrase, and no-match
    queries.

**Exit condition:** Search results are correct, deterministic, and
explainable.

### Phase 4 --- Flask application

-   Build the search page.
-   Add strategy selection.
-   Connect the selected strategy to the search endpoint.
-   Display results, scores, snippets, and latency.
-   Handle invalid input and errors.

**Exit condition:** A user can launch the app locally and search the
sample corpus with each strategy.

### Phase 5 --- Benchmarking

-   Implement repeated timing and memory measurement.
-   Support multiple dataset sizes.
-   Execute a fixed query workload.
-   Export raw and aggregated measurements with Pandas.
-   Generate comparison plots from measured results.

**Exit condition:** A single documented command can reproduce the
benchmark CSVs and plots.

### Phase 6 --- Validation and academic deliverables

-   Run the full test suite.
-   Run the benchmark from a clean environment.
-   Inspect the CSVs and plots for missing or implausible values.
-   Document setup, architecture, algorithms, experiment methodology,
    results, observations, and limitations.
-   Capture screenshots of the working application and benchmark
    visualizations.

**Exit condition:** The project can be set up, demonstrated, tested, and
explained without relying on undocumented manual steps.

## 11. Expected Deliverables

1.  Working Python document-search engine.
2.  Four indexing strategies with a common interface.
3.  Flask-based search interface.
4.  Sample document corpus and reproducible query set.
5.  Automated benchmark runner.
6.  Raw and aggregated benchmark CSV files.
7.  Plots comparing build time, query latency, and memory usage.
8.  Automated tests.
9.  README with installation and run instructions.
10. Short experiment/results write-up suitable for the SDS mini-project
    report.
11. Screenshots for the demonstration.

## 12. Acceptance Criteria

The project is considered complete when:

-   [ ] The application runs locally using the documented setup
    instructions.
-   [ ] Documents can be loaded from the local corpus.
-   [ ] All four indexing strategies can be selected and queried.
-   [ ] Equivalent queries return consistent matching-document sets.
-   [ ] Positional indexing supports phrase queries.
-   [ ] Search results display useful document information and relevance
    scores.
-   [ ] Benchmarking separates index construction from query execution.
-   [ ] At least three dataset sizes can be benchmarked.
-   [ ] Memory and latency are measured consistently and their
    methodology is documented.
-   [ ] CSV files and plots are generated from actual benchmark runs.
-   [ ] Tests pass.
-   [ ] README explains how to install, run, test, and benchmark the
    project.
-   [ ] The report discusses observed trade-offs rather than asserting
    unsupported conclusions.

## 13. Final Instructions for Codex

Prioritize correctness, measurable comparisons, and explainability over
feature count.

Before adding a feature, check whether it directly supports the stated
project topic or its evaluation. Keep the baseline simple. Do not
hardcode expected benchmark outcomes, fabricate performance numbers, or
make claims that are not supported by executed experiments.

At completion, provide:

1.  A summary of files created or modified.
2.  Exact commands to install dependencies, run tests, start Flask, and
    execute benchmarks.
3.  A concise explanation of each indexing strategy.
4.  The locations of generated CSVs and plots.
5.  Actual benchmark observations, clearly tied to the measured dataset
    and environment.
6.  Any incomplete work, known limitations, and recommended next steps.
