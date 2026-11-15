"""Streamlit front end for the SDS indexing comparison project."""

import json
from html import escape
from pathlib import Path
from time import perf_counter_ns

import pandas as pd
import streamlit as st

from src.document_loader import load_documents
from src.indexes import STRATEGIES
from src.preprocessing import tokenize


ROOT = Path(__file__).parent
STRATEGY_LABELS = {
    "sequential": "Sequential scan",
    "forward": "Forward index",
    "inverted": "Inverted index",
    "positional": "Positional index",
}

st.set_page_config(page_title="IndexLab · Smart Search", page_icon="🔎", layout="wide", initial_sidebar_state="expanded")

st.html("""
<style>
  .block-container { max-width: 1180px; padding-top: 2.1rem; padding-bottom: 4rem; }
  [data-testid="stSidebar"] { background: #173043; }
  [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #F7F5ED; }
  [data-testid="stSidebar"] [data-testid="stMetricValue"] { color: #F7F5ED; }
  .brand { color: #F7F5ED; font-weight: 800; font-size: 1.4rem; letter-spacing: -.04em; margin: .5rem 0 1.8rem; }
  .brand-mark { display: inline-flex; width: 2.2rem; height: 2.2rem; align-items: center; justify-content: center;
                border-radius: 12px; background: #E76C42; color: white; margin-right: .45rem; }
  .hero { min-height: 245px; padding: 2.7rem 3rem; margin: .2rem 0 1.7rem; color: #fff; border-radius: 24px;
          background: radial-gradient(circle at 86% 25%, #2E756E 0, transparent 31%),
                      linear-gradient(120deg, #102839 15%, #1B4554 100%); position: relative; overflow: hidden; }
  .hero:after { content: ""; position: absolute; width: 280px; height: 280px; right: -85px; bottom: -155px;
                border: 1px solid #ffffff50; border-radius: 50%; box-shadow: 0 0 0 45px #ffffff12, 0 0 0 90px #ffffff0a; }
  .hero .kicker { color: #F6B18D; font-size: .76rem; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }
  .hero h1 { color: #fff; font-size: clamp(2.8rem, 5vw, 4.6rem); line-height: 1.03; letter-spacing: -.065em;
             max-width: 650px; margin: .55rem 0 .7rem; }
  .hero p { color: #D8E5E7; font-size: 1.05rem; max-width: 580px; margin: 0; line-height: 1.55; }
  .section-kicker { color: #C75731; font-size: .75rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase;
                    margin: 1.6rem 0 .2rem; }
  .section-title { color: #173043; font-size: 1.8rem; font-weight: 800; letter-spacing: -.04em; margin: 0 0 1rem; }
  .result-card { background: #fff; border: 1px solid #E4E7E5; border-radius: 18px; min-height: 195px;
                 padding: 1.35rem 1.5rem; margin: .45rem 0; box-shadow: 0 7px 20px #1730430a; }
  .result-meta { display: flex; justify-content: space-between; gap: .5rem; align-items: center; color: #758391;
                 font-size: .72rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
  .score-pill { background: #FFF0E8; color: #BD4D2C; padding: .35rem .65rem; border-radius: 999px; letter-spacing: .02em; }
  .result-card h3 { color: #173043; font-size: 1.2rem; margin: .75rem 0 .5rem; letter-spacing: -.025em; }
  .result-card p { color: #4B5C68; line-height: 1.5; margin: 0 0 .9rem; }
  .result-card small { color: #8996A0; font-size: .76rem; }
  .note-box { background: #E8EFED; border-left: 4px solid #2E756E; padding: 1rem 1.25rem; border-radius: 0 12px 12px 0;
              color: #2D4C50; margin-top: 1.1rem; }
  @media (max-width: 700px) { .hero { padding: 2rem 1.5rem; } .hero h1 { font-size: 2.7rem; } }
</style>
""")


@st.cache_resource(show_spinner="Building the four indexes…")
def load_engine():
    documents = load_documents(ROOT / "data" / "documents")
    if not documents:
        raise ValueError("No .txt documents were found in data/documents.")
    indexes = {}
    for name, cls in STRATEGIES.items():
        index = cls()
        index.build(documents)
        indexes[name] = index
    return documents, indexes


def render_result(hit, number: int) -> None:
    st.html(
        f'<div class="result-card">'
        f'<div class="result-meta"><span>Document {number:02d}</span><span class="score-pill">Score {hit.score}</span></div>'
        f'<h3>{escape(hit.title)}</h3><p>{escape(hit.snippet)}</p><small>{escape(hit.id)}</small>'
        f'</div>'
    )


def render_search(indexes) -> None:
    st.html('<div class="hero"><div class="kicker">Scalable data structures / mini project</div>'
            '<h1>Find the signal<br>in the documents.</h1>'
            '<p>One collection. Four index strategies. See what changes when the data structure changes.</p></div>')

    with st.container(border=True):
        with st.form("search_form"):
            query = st.text_input("Search the collection", value="index", placeholder="Try ‘index memory’ or ‘search engine’", key="search_query")
            col_strategy, col_limit = st.columns([3, 1])
            with col_strategy:
                strategy = st.selectbox("Index strategy", list(STRATEGIES), index=2, format_func=lambda key: STRATEGY_LABELS[key], key="search_strategy")
            with col_limit:
                top_k = st.selectbox("Show top", [5, 10, 20], index=1, key="search_limit")
            submitted = st.form_submit_button("Search documents", type="primary", key="search_submit")
        st.caption('Use multiple words for OR matching. For an exact phrase, choose Positional index and wrap the words in quotes: "search engine".')

    if "search_request" not in st.session_state:
        st.session_state.search_request = ("index", "inverted", 10)
    if submitted:
        st.session_state.search_request = (query, strategy, top_k)

    active_query, active_strategy, active_limit = st.session_state.search_request
    try:
        started = perf_counter_ns()
        outcome = indexes[active_strategy].search(active_query, top_k=active_limit)
        elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    except ValueError as exc:
        st.error(str(exc))
        return

    st.html('<div class="section-kicker">Search results</div><div class="section-title">Matches for “' + escape(active_query) + '”</div>')
    count_col, time_col, work_col = st.columns(3)
    count_col.metric("Matching documents", outcome.result_count)
    time_col.metric("Search time", f"{elapsed_ms:.3f} ms")
    work_col.metric("Candidates checked", outcome.candidate_count)

    if not outcome.hits:
        st.info("No documents matched this query. Try a different term or strategy.")
        return
    for start in range(0, len(outcome.hits), 2):
        columns = st.columns(2)
        for offset, hit in enumerate(outcome.hits[start:start + 2]):
            with columns[offset]:
                render_result(hit, start + offset + 1)


def render_benchmarks() -> None:
    st.html('<div class="hero"><div class="kicker">Measured, not estimated</div>'
            '<h1>Index performance<br>at a glance.</h1>'
            '<p>Build time, query latency, and memory from the same fixed workload.</p></div>')
    summary_path = ROOT / "results" / "summary.csv"
    if not summary_path.exists():
        st.info("Run `uv run python -m src.benchmarking.runner` to generate benchmark results.")
        return
    summary = pd.read_csv(summary_path)
    largest_count = int(summary["doc_count"].max())
    largest = summary[summary["doc_count"] == largest_count]
    environment_path = ROOT / "results" / "environment.json"
    repetitions = json.loads(environment_path.read_text(encoding="utf-8")).get("repetitions", "—") if environment_path.exists() else "—"
    st.html(f'<div class="section-kicker">Largest collection</div><div class="section-title">The {largest_count:,}-document run</div>')
    a, b, c = st.columns(3)
    a.metric("Documents", int(largest["doc_count"].max()))
    b.metric("Tokens", f"{int(largest['token_count'].max()):,}")
    c.metric("Query repetitions", repetitions)
    st.caption("Collections larger than the sample repeat its source texts and are labeled synthetic.")

    tabs = st.tabs(["Query latency", "Build time", "Memory"])
    for tab, filename, explanation in zip(
        tabs,
        ["query_latency.png", "build_time.png", "memory_usage.png"],
        ["Median of per-query medians; log scale.", "Time to build each representation, separate from search.", "Recursive Python object-size estimate, including stored documents."],
    ):
        with tab:
            st.caption(explanation)
            image_path = ROOT / "results" / "plots" / filename
            if image_path.exists():
                st.image(str(image_path), width="stretch")
            else:
                st.info("Run the benchmark command to generate this plot.")

    with st.expander("See the measurements"):
        displayed = summary[["doc_count", "strategy", "build_ms", "median_query_latency_ms", "memory_bytes", "mean_candidate_count"]].copy()
        displayed.columns = ["Documents", "Strategy", "Build (ms)", "Median query (ms)", "Memory (bytes)", "Mean candidates"]
        st.dataframe(displayed.sort_values(["Documents", "Strategy"]), hide_index=True, width="stretch")
        st.download_button("Download summary CSV", data=summary_path.read_bytes(), file_name="summary.csv", mime="text/csv")


def render_guide(documents) -> None:
    st.html('<div class="hero"><div class="kicker">The idea behind the project</div>'
            '<h1>Same search.<br>Different structure.</h1>'
            '<p>Each strategy answers the same ordinary queries. Their build cost, memory, and query work differ.</p></div>')
    st.html('<div class="section-kicker">Four strategies</div><div class="section-title">What each one stores</div>')
    descriptions = [
        ("Sequential scan", "No persistent search index. Tokenizes and checks every document for each query."),
        ("Forward index", "Stores term frequencies by document. Search still checks document-level maps."),
        ("Inverted index", "Stores term postings by word. Search visits the requested words' postings."),
        ("Positional index", "Adds word positions to postings, enabling exact consecutive phrase search."),
    ]
    for start in (0, 2):
        columns = st.columns(2)
        for offset, (title, description) in enumerate(descriptions[start:start + 2]):
            with columns[offset], st.container(border=True):
                st.subheader(title)
                st.write(description)
    st.html('<div class="note-box">All strategies use lowercase ASCII word tokens, OR matching for ordinary queries, and the sum of distinct query-term frequencies as the relevance score.</div>')
    st.caption(f"Current sample: {len(documents)} local documents · {sum(len(tokenize(doc.text)) for doc in documents)} tokens. See README.md and REPORT.md for setup and measurement details.")


def main() -> None:
    try:
        documents, indexes = load_engine()
    except (OSError, ValueError) as exc:
        st.error(f"Could not load the local document collection: {exc}")
        st.stop()

    with st.sidebar:
        st.html('<div class="brand"><span class="brand-mark">⌕</span> IndexLab</div>')
        page = st.radio("Explore", ["Search", "Benchmarks", "How it works"], label_visibility="collapsed")
        st.divider()
        st.caption("COLLECTION")
        st.metric("Local documents", len(documents))
        st.caption("Four indexing strategies · one consistent query rule")
        st.divider()
        st.caption("SDS MINI PROJECT")
        st.caption("Built with Python, Streamlit, and uv")

    if page == "Search":
        render_search(indexes)
    elif page == "Benchmarks":
        render_benchmarks()
    else:
        render_guide(documents)


main()
