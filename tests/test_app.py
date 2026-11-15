from app import create_app


def test_search_page_and_results():
    client = create_app().test_client()
    assert client.get("/").status_code == 200
    response = client.post("/search", data={"query": "index", "strategy": "inverted", "top_k": "5"})
    assert response.status_code == 200
    assert b"Results" in response.data and b"Score" in response.data


def test_invalid_input_and_phrase():
    client = create_app().test_client()
    assert client.post("/search", data={"query": " ", "strategy": "forward"}).status_code == 400
    assert client.post("/search", data={"query": '"search engine"', "strategy": "forward"}).status_code == 400
    assert client.post("/search", data={"query": '"search engine"', "strategy": "positional"}).status_code == 200


def test_missing_corpus_is_explained(tmp_path):
    client = create_app(tmp_path / "missing").test_client()
    assert b"does not exist" in client.get("/").data
    assert client.post("/search", data={"query": "index"}).status_code == 400
