from __future__ import annotations

import os
import time
from dataclasses import dataclass

from fastapi import APIRouter

from contract_risk_analyzer.api.schemas import (
    ClauseAnalyzeRequest,
    ClauseAnalyzeResponse,
    DocumentAnalyzeRequest,
    MetricsResponse,
    ModelInfoResponse,
    SearchRequest,
    SearchResponse,
)
from contract_risk_analyzer.config.settings import load_yaml, resolve_path
from contract_risk_analyzer.data.schemas import Clause
from contract_risk_analyzer.modeling.predict import analyze_document_text, predict_clauses
from contract_risk_analyzer.retrieval.index import build_clause_index
from contract_risk_analyzer.retrieval.search import search_index
from contract_risk_analyzer.risk.rules import detect_risk_flags
from contract_risk_analyzer.utils.io import read_jsonl

router = APIRouter()


@dataclass
class ServiceMetrics:
    analyzed_clauses: int = 0
    analyzed_documents: int = 0
    total_latency_ms: float = 0.0
    total_requests: int = 0
    total_risk_flags: int = 0

    @property
    def average_latency_ms(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return round(self.total_latency_ms / self.total_requests, 2)


metrics = ServiceMetrics()


def _mock_mode() -> bool:
    return os.getenv("CONTRACT_RISK_MOCK_MODEL", "true").lower() in {"1", "true", "yes"}


def _model_path() -> str | None:
    return os.getenv("CONTRACT_RISK_MODEL_PATH", "models/baseline_tfidf.joblib")


def _disclaimer() -> str:
    return str(load_yaml("configs/risk_rules.yaml")["disclaimer"])


def _record_latency(start: float) -> None:
    metrics.total_latency_ms += (time.perf_counter() - start) * 1000
    metrics.total_requests += 1


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    mock = _mock_mode()
    model_path = _model_path()
    model_loaded = False if mock or model_path is None else resolve_path(model_path).exists()
    return ModelInfoResponse(
        model_name="deterministic_mock_model" if mock else "tfidf_logistic_regression",
        mock_mode=mock,
        model_loaded=model_loaded,
        disclaimer=_disclaimer(),
    )


@router.post("/analyze/clause", response_model=ClauseAnalyzeResponse)
def analyze_clause(request: ClauseAnalyzeRequest) -> ClauseAnalyzeResponse:
    start = time.perf_counter()
    clause = Clause(
        clause_id="api-clause-1",
        text=request.text,
        source_document_id="api-clause",
        start_char=0,
        end_char=len(request.text),
    )
    predictions = predict_clauses([clause], model_path=_model_path(), mock=_mock_mode())
    flags = detect_risk_flags([clause], predictions)
    metrics.analyzed_clauses += 1
    metrics.total_risk_flags += len(flags)
    _record_latency(start)
    prediction = predictions[0]
    return ClauseAnalyzeResponse(
        predicted_label=prediction.predicted_label,
        confidence=prediction.confidence,
        top_k_labels=prediction.top_k_labels,
        risk_flags=flags,
        disclaimer=_disclaimer(),
    )


@router.post("/analyze/document")
def analyze_document(request: DocumentAnalyzeRequest):
    start = time.perf_counter()
    report = analyze_document_text(
        request.text,
        document_id=request.document_id,
        model_path=_model_path(),
        mock=_mock_mode(),
    )
    metrics.analyzed_documents += 1
    metrics.analyzed_clauses += report.total_clauses
    metrics.total_risk_flags += len(report.risk_flags)
    _record_latency(start)
    return report


@router.post("/search/similar", response_model=SearchResponse)
def search_similar(request: SearchRequest) -> SearchResponse:
    start = time.perf_counter()
    index_path = os.getenv("CONTRACT_RISK_RETRIEVAL_INDEX", "models/retrieval")
    results = search_index(index_path, request.query, top_k=request.top_k)
    if not results:
        records = read_jsonl(resolve_path("data/samples/sample_clauses.jsonl"))
        index = build_clause_index(records)
        results = index.search(request.query, top_k=request.top_k)
    _record_latency(start)
    return SearchResponse(results=results)


@router.get("/metrics", response_model=MetricsResponse)
def service_metrics() -> MetricsResponse:
    return MetricsResponse(
        analyzed_clauses=metrics.analyzed_clauses,
        analyzed_documents=metrics.analyzed_documents,
        average_latency_ms=metrics.average_latency_ms,
        total_risk_flags=metrics.total_risk_flags,
    )
