from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from contract_risk_analyzer.data.schemas import Clause, ClausePrediction, RiskReport
from contract_risk_analyzer.modeling.registry import load_local_model
from contract_risk_analyzer.preprocessing.chunking import split_into_clauses
from contract_risk_analyzer.risk.report import generate_risk_report

MOCK_LABEL_KEYWORDS = {
    "termination": ["terminate", "termination", "breach", "notice"],
    "confidentiality": ["confidential", "secret", "non-disclosure"],
    "payment": ["pay", "invoice", "payment", "interest"],
    "indemnification": ["indemnify", "indemnification", "hold harmless", "defend"],
    "governing law": ["governed by", "jurisdiction", "venue"],
    "assignment": ["assign", "assignment", "consent"],
    "liability": ["liability", "damages"],
}


def mock_predict_clauses(clauses: list[Clause]) -> list[ClausePrediction]:
    predictions: list[ClausePrediction] = []
    for clause in clauses:
        text = clause.text.lower()
        matched_label = "general"
        confidence = 0.52
        for label, keywords in MOCK_LABEL_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                matched_label = label
                confidence = 0.78
                break
        digest = int(hashlib.sha1(clause.text.encode("utf-8")).hexdigest()[:4], 16)
        confidence = min(0.95, confidence + (digest % 10) / 100)
        top_k = [(matched_label, confidence), ("general", max(0.0, 1.0 - confidence))]
        predictions.append(
            ClausePrediction(
                clause_id=clause.clause_id,
                predicted_label=matched_label,
                confidence=round(confidence, 4),
                top_k_labels=top_k,
                model_name="deterministic_mock_model",
                metadata={"mock": True},
            )
        )
    return predictions


def predict_clauses(
    clauses: list[Clause],
    model_path: str | Path | None = None,
    mock: bool = False,
) -> list[ClausePrediction]:
    if mock:
        return mock_predict_clauses(clauses)
    if model_path is None:
        raise FileNotFoundError("No model path provided. Use --mock for deterministic demo mode.")
    model = load_local_model(model_path)
    return model.predict_clauses([clause.clause_id for clause in clauses], [clause.text for clause in clauses])


def analyze_document_text(
    text: str,
    document_id: str = "document",
    model_path: str | Path | None = None,
    mock: bool = False,
    risk_config_path: str = "configs/risk_rules.yaml",
) -> RiskReport:
    clauses = split_into_clauses(text, document_id=document_id)
    predictions = predict_clauses(clauses, model_path=model_path, mock=mock)
    return generate_risk_report(document_id, clauses, predictions, config_path=risk_config_path)


def risk_report_to_dict(report: RiskReport, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = report.model_dump(mode="json")
    if extra:
        payload["metadata"] = extra
    return payload
