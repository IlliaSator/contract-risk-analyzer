from __future__ import annotations

from collections import Counter

from contract_risk_analyzer.config.settings import load_yaml
from contract_risk_analyzer.data.schemas import Clause, ClausePrediction, RiskReport
from contract_risk_analyzer.risk.rules import detect_risk_flags
from contract_risk_analyzer.risk.scoring import calculate_overall_risk_score, severity_breakdown


def _recommendations(flags_count: int) -> list[str]:
    if flags_count == 0:
        return ["No configured risk indicators were detected; human review is still recommended."]
    return [
        "Review high and critical flags with qualified counsel or an appropriate contract owner.",
        "Validate whether detected indicators are acceptable for the business context.",
        "Use this report as triage input, not as a legal conclusion.",
    ]


def generate_risk_report(
    document_id: str,
    clauses: list[Clause],
    predictions: list[ClausePrediction],
    config_path: str = "configs/risk_rules.yaml",
) -> RiskReport:
    config = load_yaml(config_path)
    flags = detect_risk_flags(clauses, predictions, config_path=config_path)
    label_counts = Counter(prediction.predicted_label for prediction in predictions)
    score = calculate_overall_risk_score(flags, config_path=config_path)
    summary = (
        f"Analyzed {len(clauses)} clauses and detected {len(flags)} potential risk indicators. "
        "Findings require human review."
    )
    return RiskReport(
        document_id=document_id,
        summary=summary,
        total_clauses=len(clauses),
        predicted_clause_types=dict(label_counts),
        risk_flags=flags,
        overall_risk_score=score,
        severity_breakdown=severity_breakdown(flags),
        recommendations=_recommendations(len(flags)),
        disclaimer=str(config["disclaimer"]),
    )
