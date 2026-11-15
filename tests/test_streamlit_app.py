from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"


def test_search_and_empty_results():
    at = AppTest.from_file(APP, default_timeout=15).run()
    assert not at.exception
    assert len(at.metric) == 4  # sidebar count plus three search metrics

    at.text_input[0].input("zzznomatch")
    at.button[0].click().run()
    assert not at.exception
    assert any("No documents matched" in message.value for message in at.info)


def test_benchmark_and_guide_pages():
    at = AppTest.from_file(APP, default_timeout=15).run()
    at.radio[0].set_value("Benchmarks").run()
    assert not at.exception
    assert len(at.metric) >= 4
    at.radio[0].set_value("How it works").run()
    assert not at.exception
