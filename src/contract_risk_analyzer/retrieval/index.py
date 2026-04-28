from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from contract_risk_analyzer.data.schemas import SearchResult
from contract_risk_analyzer.retrieval.embedder import Embedder, TfidfEmbedder
from contract_risk_analyzer.utils.io import ensure_parent, read_jsonl


@dataclass
class ClauseIndex:
    texts: list[str]
    clause_ids: list[str]
    labels: list[str | None]
    metadata: list[dict[str, Any]]
    embeddings: np.ndarray
    embedder: Embedder

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not self.texts:
            return []
        query_embedding = self.embedder.encode([query])
        scores = cosine_similarity(query_embedding, self.embeddings)[0]
        order = np.argsort(scores)[::-1][:top_k]
        return [
            SearchResult(
                clause_id=self.clause_ids[index],
                text=self.texts[index],
                score=float(scores[index]),
                label=self.labels[index],
                metadata=self.metadata[index],
            )
            for index in order
        ]

    def save(self, output_dir: str | Path) -> Path:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        target = output_path / "clause_index.joblib"
        joblib.dump(self, target)
        return target

    @classmethod
    def load(cls, path: str | Path) -> "ClauseIndex":
        payload = joblib.load(path)
        if not isinstance(payload, cls):
            raise TypeError(f"Unsupported retrieval index artifact: {path}")
        return payload


def build_clause_index(records: list[dict[str, Any]], embedder: Embedder | None = None) -> ClauseIndex:
    texts = [str(record["text"]) for record in records]
    if not texts:
        raise ValueError("Cannot build retrieval index from empty records.")
    clause_ids = [str(record.get("clause_id") or f"clause-{index + 1}") for index, record in enumerate(records)]
    labels = [record.get("label") for record in records]
    metadata = [dict(record.get("metadata", {})) for record in records]
    fitted_embedder = embedder or TfidfEmbedder()
    fitted_embedder.fit(texts)
    embeddings = fitted_embedder.encode(texts)
    return ClauseIndex(texts, clause_ids, labels, metadata, embeddings, fitted_embedder)


def build_index_from_jsonl(input_path: str | Path, output_dir: str | Path) -> Path:
    records = read_jsonl(input_path)
    index = build_clause_index(records)
    return index.save(ensure_parent(Path(output_dir) / "clause_index.joblib").parent)
