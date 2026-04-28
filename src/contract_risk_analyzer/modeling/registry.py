from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from contract_risk_analyzer.modeling.baseline_tfidf import TfidfLogisticBaseline


@lru_cache(maxsize=4)
def _load_local_model_cached(resolved_path: str) -> TfidfLogisticBaseline:
    return TfidfLogisticBaseline.load(resolved_path)


def load_local_model(path: str | Path) -> TfidfLogisticBaseline:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Model artifact not found: {resolved}")
    return _load_local_model_cached(str(resolved))


def clear_model_cache() -> None:
    _load_local_model_cached.cache_clear()
