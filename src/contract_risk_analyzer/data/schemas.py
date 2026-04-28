from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Clause(BaseModel):
    clause_id: str
    text: str
    source_document_id: str
    start_char: int = 0
    end_char: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ClausePrediction(BaseModel):
    clause_id: str
    predicted_label: str
    confidence: float = Field(ge=0.0, le=1.0)
    top_k_labels: list[tuple[str, float]] = Field(default_factory=list)
    model_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskFlag(BaseModel):
    flag_id: str
    clause_id: str
    flag_type: str
    severity: Literal["low", "medium", "high", "critical"]
    reason: str
    evidence_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskReport(BaseModel):
    document_id: str
    summary: str
    total_clauses: int
    predicted_clause_types: dict[str, int]
    risk_flags: list[RiskFlag]
    overall_risk_score: float = Field(ge=0.0, le=100.0)
    severity_breakdown: dict[str, int]
    recommendations: list[str]
    disclaimer: str


class SearchResult(BaseModel):
    clause_id: str
    text: str
    score: float
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DatasetRecord(BaseModel):
    text: str
    label: str
    split: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)
