from contract_risk_analyzer.preprocessing.chunking import chunk_long_document, split_into_clauses


def test_split_into_clauses_empty() -> None:
    assert split_into_clauses("") == []


def test_chunk_length_and_overlap() -> None:
    text = "Sentence one. Sentence two is longer. Sentence three is here. " * 20
    chunks = chunk_long_document(text, max_chars=120, overlap=20, preserve_sentence_boundaries=False)
    assert len(chunks) > 1
    assert all(len(chunk.text) <= 120 for chunk in chunks)
    assert chunks[1].start_char < chunks[0].end_char


def test_long_document_handling() -> None:
    chunks = chunk_long_document("word " * 1000, max_chars=250, overlap=25)
    assert len(chunks) >= 10
