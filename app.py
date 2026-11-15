"""Local Flask interface for comparing the four search indexes."""

from pathlib import Path
from time import perf_counter_ns

from flask import Flask, render_template, request

from src.document_loader import load_documents
from src.indexes import STRATEGIES


ROOT = Path(__file__).parent


def create_app(document_dir: str | Path = ROOT / "data" / "documents") -> Flask:
    app = Flask(__name__)
    indexes = {}
    startup_error = None
    try:
        documents = load_documents(document_dir)
        if not documents:
            raise ValueError("No .txt documents were found in the document directory.")
        for name, cls in STRATEGIES.items():
            index = cls()
            index.build(documents)
            indexes[name] = index
    except (OSError, ValueError) as exc:
        startup_error = str(exc)

    @app.get("/")
    def home():
        return render_template("index.html", strategies=STRATEGIES, error=startup_error)

    @app.route("/search", methods=["GET", "POST"])
    def search():
        query = request.values.get("query", "")
        strategy = request.values.get("strategy", "inverted")
        top_k_text = request.values.get("top_k", "10")
        error = startup_error
        outcome = None
        elapsed_ms = None
        if not error:
            try:
                if strategy not in indexes:
                    raise ValueError("Choose a valid indexing strategy.")
                top_k = int(top_k_text)
                started = perf_counter_ns()
                outcome = indexes[strategy].search(query, top_k=top_k)
                elapsed_ms = (perf_counter_ns() - started) / 1_000_000
            except (ValueError, TypeError) as exc:
                error = str(exc)
        return render_template(
            "index.html", strategies=STRATEGIES, query=query, selected=strategy,
            top_k=top_k_text, outcome=outcome, elapsed_ms=elapsed_ms, error=error,
        ), (400 if error else 200)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
