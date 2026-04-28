from contract_risk_analyzer.data.schemas import Clause, ClausePrediction, RiskFlag
from contract_risk_analyzer.risk.report import generate_risk_report
from contract_risk_analyzer.risk.scoring import calculate_overall_risk_score


def _flag(severity: str, confidence: float) -> RiskFlag:
    return RiskFlag(
        flag_id=f"{severity}-{confidence}",
        clause_id="c1",
        flag_type="TEST",
        severity=severity,  # type: ignore[arg-type]
        reason="Potential risk indicator.",
        evidence_text="evidence",
        confidence=confidence,
    )


def test_low_confidence_changes_score() -> None:
    high = calculate_overall_risk_score([_flag("high", 0.9)])
    low = calculate_overall_risk_score([_flag("high", 0.3)])
    assert low != high


def test_multiple_high_severity_flags_increase_total_risk() -> None:
    one = calculate_overall_risk_score([_flag("critical", 0.9)])
    two = calculate_overall_risk_score([_flag("critical", 0.9), _flag("high", 0.9)])
    assert two > one


def test_empty_document_returns_safe_structured_response() -> None:
    report = generate_risk_report("empty", [], [])
    assert report.total_clauses == 0
    assert report.overall_risk_score == 0
    assert report.disclaimer


def test_report_disclaimer_always_present() -> None:
    clause = Clause(clause_id="c1", text="Customer shall pay invoices.", source_document_id="d1")
    prediction = ClausePrediction(
        clause_id="c1",
        predicted_label="payment",
        confidence=0.8,
        top_k_labels=[("payment", 0.8)],
        model_name="test",
    )
    report = generate_risk_report("d1", [clause], [prediction])
    assert "not legal advice" in report.disclaimer.lower()
