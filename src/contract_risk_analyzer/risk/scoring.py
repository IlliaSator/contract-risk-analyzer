from __future__ import annotations

from collections import Counter
from typing import Any

from contract_risk_analyzer.config.settings import load_yaml
from contract_risk_analyzer.data.schemas import RiskFlag


def severity_breakdown(flags: list[RiskFlag]) -> dict[str, int]:
    counts = Counter(flag.severity for flag in flags)
    return {severity: counts.get(severity, 0) for severity in ("low", "medium", "high", "critical")}


def calculate_overall_risk_score(
    flags: list[RiskFlag],
    config_path: str = "configs/risk_rules.yaml",
) -> float:
    config: dict[str, Any] = load_yaml(config_path)
    weights = config.get("severity_weights", {})
    uncertainty = config.get("uncertainty", {})
    low_confidence_threshold = float(uncertainty.get("low_confidence_threshold", 0.55))
    uncertainty_penalty = float(uncertainty.get("penalty", 6))

    score = 0.0
    for flag in flags:
        base = float(weights.get(flag.severity, 10))
        score += base * max(flag.confidence, 0.25)
        if flag.confidence < low_confidence_threshold:
            score += uncertainty_penalty
    return round(min(score, 100.0), 2)
