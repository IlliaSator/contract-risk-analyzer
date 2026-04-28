from __future__ import annotations

from pathlib import Path

from contract_risk_analyzer.data.schemas import SearchResult
from contract_risk_analyzer.retrieval.index import ClauseIndex


def search_index(index_path: str | Path, query: str, top_k: int = 5) -> list[SearchResult]:
    path = Path(index_path)
    if path.is_dir():
        path = path / "clause_index.joblib"
    if not path.exists():
        return []
    return ClauseIndex.load(path).search(query, top_k=top_k)
