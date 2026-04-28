from __future__ import annotations

from pathlib import Path
from typing import Any

from contract_risk_analyzer.config.settings import load_yaml, resolve_path
from contract_risk_analyzer.evaluation.error_analysis import build_error_analysis
from contract_risk_analyzer.evaluation.metrics import compute_classification_metrics, top_confusions
from contract_risk_analyzer.modeling.baseline_tfidf import TfidfLogisticBaseline
from contract_risk_analyzer.modeling.train_baseline import load_supervised_jsonl
from contract_risk_analyzer.utils.io import write_json


def evaluate_baseline_model(
    model_path: str | Path,
    data_path: str | Path,
    metrics_path: str | Path = "reports/evaluation_metrics.json",
    error_analysis_path: str | Path = "reports/error_analysis.json",
    top_confusions_path: str | Path = "reports/top_confusions.json",
) -> dict[str, Any]:
    resolved_model = resolve_path(model_path)
    resolved_data = resolve_path(data_path)
    if not resolved_model.exists():
        raise FileNotFoundError(f"Model artifact not found: {resolved_model}")
    if not resolved_data.exists():
        raise FileNotFoundError(f"Evaluation data not found: {resolved_data}")

    texts, labels = load_supervised_jsonl(resolved_data)
    model = TfidfLogisticBaseline.load(str(resolved_model))
    predictions = model.predict(texts)
    probabilities = model.predict_proba(texts)
    confidences = probabilities.max(axis=1).tolist()

    metrics = compute_classification_metrics(labels, predictions)
    metrics["model_path"] = str(resolved_model)
    metrics["data_path"] = str(resolved_data)
    errors = build_error_analysis(texts, labels, predictions, confidences)
    confusions = {"top_confusions": top_confusions(labels, predictions)}

    write_json(resolve_path(metrics_path), metrics)
    write_json(resolve_path(error_analysis_path), errors)
    write_json(resolve_path(top_confusions_path), confusions)
    return metrics


def evaluate_from_config(config_path: str | Path, model_path: str | Path | None = None, split: str = "test") -> dict[str, Any]:
    config = load_yaml(config_path)
    data_path = config["data"].get(f"{split}_path")
    if data_path is None:
        raise ValueError(f"Unknown split in config: {split}")
    evaluation = config["evaluation"]
    return evaluate_baseline_model(
        model_path or config["model"]["artifact_path"],
        data_path,
        metrics_path="reports/evaluation_metrics.json",
        error_analysis_path=evaluation["error_analysis_path"],
        top_confusions_path=evaluation["top_confusions_path"],
    )
