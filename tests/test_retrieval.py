import numpy as np

from contract_risk_analyzer.retrieval.index import build_clause_index


class FakeEmbedder:
    def fit(self, texts: list[str]) -> "FakeEmbedder":
        return self

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray([[1.0, 0.0] if "terminate" in text.lower() else [0.0, 1.0] for text in texts])


def test_retrieval_returns_top_k_with_fake_embeddings() -> None:
    records = [
        {"text": "Terminate on notice", "label": "termination", "clause_id": "c1"},
        {"text": "Keep information confidential", "label": "confidentiality", "clause_id": "c2"},
    ]
    index = build_clause_index(records, embedder=FakeEmbedder())
    results = index.search("terminate agreement", top_k=1)
    assert len(results) == 1
    assert results[0].clause_id == "c1"


def test_empty_index_handling() -> None:
    try:
        build_clause_index([], embedder=FakeEmbedder())
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("Expected empty index failure")
