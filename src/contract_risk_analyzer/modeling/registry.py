from __future__ import annotations

from pathlib import Path

from contract_risk_analyzer.modeling.baseline_tfidf import TfidfLogisticBaseline


def load_local_model(path: str | Path) -> TfidfLogisticBaseline:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Model artifact not found: {resolved}")
    return TfidfLogisticBaseline.load(str(resolved))
