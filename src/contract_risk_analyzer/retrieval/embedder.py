from __future__ import annotations

from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedder(Protocol):
    def fit(self, texts: list[str]) -> Embedder: ...

    def encode(self, texts: list[str]) -> np.ndarray: ...


class TfidfEmbedder:
    def __init__(self, max_features: int = 20000) -> None:
        self.vectorizer = TfidfVectorizer(max_features=max_features, lowercase=True, strip_accents="unicode")

    def fit(self, texts: list[str]) -> TfidfEmbedder:
        if not texts:
            raise ValueError("Cannot fit retrieval embedder on empty texts.")
        self.vectorizer.fit(texts)
        return self

    def encode(self, texts: list[str]) -> np.ndarray:
        return self.vectorizer.transform(texts).toarray()


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install `.[retrieval]` or use the TF-IDF fallback."
            ) from exc
        self.model = SentenceTransformer(model_name)

    def fit(self, texts: list[str]) -> SentenceTransformerEmbedder:
        return self

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))
