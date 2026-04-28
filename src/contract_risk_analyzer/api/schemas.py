from __future__ import annotations

from pydantic import BaseModel, Field

from contract_risk_analyzer.data.schemas import RiskFlag, RiskReport, SearchResult


class ClauseAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class ClauseAnalyzeResponse(BaseModel):
    predicted_label: str
    confidence: float
    top_k_labels: list[tuple[str, float]]
    risk_flags: list[RiskFlag]
    disclaimer: str


class DocumentAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    document_id: str = "api-document"


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResponse(BaseModel):
    results: list[SearchResult]


class MetricsResponse(BaseModel):
    analyzed_clauses: int
    analyzed_documents: int
    average_latency_ms: float
    total_risk_flags: int


class ModelInfoResponse(BaseModel):
    model_name: str
    mock_mode: bool
    model_loaded: bool
    disclaimer: str


class DocumentAnalyzeResponse(RiskReport):
    pass
