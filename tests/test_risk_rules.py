from contract_risk_analyzer.data.schemas import Clause, ClausePrediction
from contract_risk_analyzer.risk.rules import detect_risk_flags


def test_known_clause_triggers_termination_flag() -> None:
    clause = Clause(
        clause_id="c1",
        text="Either party may terminate this Agreement without cause.",
        source_document_id="d1",
    )
    prediction = ClausePrediction(
        clause_id="c1",
        predicted_label="termination",
        confidence=0.9,
        top_k_labels=[("termination", 0.9)],
        model_name="test",
    )
    flags = detect_risk_flags([clause], [prediction])
    assert any(flag.flag_type == "TERMINATION_RISK" for flag in flags)
