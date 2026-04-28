from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from contract_risk_analyzer.config.settings import load_yaml
from contract_risk_analyzer.data.schemas import Clause, ClausePrediction, RiskFlag


@dataclass
class RiskRule:
    flag_type: str
    severity: str
    labels: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    reason: str = "Potential risk indicator may require human review."


def load_risk_config(config_path: str = "configs/risk_rules.yaml") -> dict[str, Any]:
    return load_yaml(config_path)


def load_rules(config_path: str = "configs/risk_rules.yaml") -> list[RiskRule]:
    config = load_risk_config(config_path)
    return [RiskRule(**rule) for rule in config.get("rules", [])]


def _stable_flag_id(clause_id: str, flag_type: str, evidence: str) -> str:
    digest = hashlib.sha1(f"{clause_id}:{flag_type}:{evidence}".encode("utf-8")).hexdigest()[:10]
    return f"flag-{digest}"


def _label_matches(predicted_label: str, labels: list[str]) -> bool:
    normalized = predicted_label.lower()
    return any(label.lower() in normalized or normalized in label.lower() for label in labels)


def _pattern_matches(text: str, patterns: list[str]) -> list[str]:
    matches: list[str] = []
    for pattern in patterns:
        if re.search(re.escape(pattern), text, flags=re.IGNORECASE):
            matches.append(pattern)
    return matches


def detect_risk_flags(
    clauses: list[Clause],
    predictions: list[ClausePrediction],
    config_path: str = "configs/risk_rules.yaml",
) -> list[RiskFlag]:
    rules = load_rules(config_path)
    prediction_by_clause = {prediction.clause_id: prediction for prediction in predictions}
    flags: list[RiskFlag] = []

    for clause in clauses:
        prediction = prediction_by_clause.get(clause.clause_id)
        predicted_label = prediction.predicted_label if prediction else ""
        confidence = prediction.confidence if prediction else 0.5
        for rule in rules:
            matched_patterns = _pattern_matches(clause.text, rule.patterns)
            matched_label = bool(predicted_label and _label_matches(predicted_label, rule.labels))
            if not matched_patterns and not matched_label:
                continue
            evidence = matched_patterns[0] if matched_patterns else predicted_label
            flags.append(
                RiskFlag(
                    flag_id=_stable_flag_id(clause.clause_id, rule.flag_type, evidence),
                    clause_id=clause.clause_id,
                    flag_type=rule.flag_type,
                    severity=rule.severity,  # type: ignore[arg-type]
                    reason=rule.reason,
                    evidence_text=clause.text[:500],
                    confidence=float(confidence),
                    metadata={
                        "matched_patterns": matched_patterns,
                        "matched_label": matched_label,
                        "predicted_label": predicted_label,
                        "requires_human_review": True,
                    },
                )
            )
    return flags
