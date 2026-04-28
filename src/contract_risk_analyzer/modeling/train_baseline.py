from __future__ import annotations

from pathlib import Path
from typing import Any

from contract_risk_analyzer.config.settings import load_yaml, resolve_path
from contract_risk_analyzer.modeling.baseline_tfidf import TfidfBaselineConfig, TfidfLogisticBaseline
from contract_risk_analyzer.utils.io import ensure_parent, read_jsonl, write_json
from contract_risk_analyzer.utils.reproducibility import set_seed


def load_supervised_jsonl(path: str | Path) -> tuple[list[str], list[str]]:
    records = read_jsonl(path)
    texts = [str(record["text"]) for record in records]
    labels = [str(record["label"]) for record in records]
    return texts, labels


def _basic_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    from sklearn.metrics import accuracy_score, classification_report, f1_score

    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "micro_f1": f1_score(y_true, y_pred, average="micro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }


def train_baseline(config_path: str | Path, allow_sample: bool = False) -> dict[str, Any]:
    config = load_yaml(config_path)
    data_config = config["data"]
    model_config = config["model"]
    evaluation_config = config["evaluation"]
    set_seed(int(model_config.get("random_state", 42)))

    train_path = resolve_path(data_config["train_path"])
    validation_path = resolve_path(data_config["validation_path"])
    test_path = resolve_path(data_config["test_path"])
    sample_mode = False

    if not train_path.exists() or not validation_path.exists() or not test_path.exists():
        if not allow_sample:
            raise FileNotFoundError(
                "Prepared LEDGAR splits were not found. Run `make download-ledgar` first, "
                "or use `--allow-sample` only for smoke testing."
            )
        fallback_path = resolve_path(data_config["fallback_sample_path"])
        texts, labels = load_supervised_jsonl(fallback_path)
        train_texts, train_labels = texts[:4], labels[:4]
        validation_texts, validation_labels = texts[4:5], labels[4:5]
        test_texts, test_labels = texts[5:], labels[5:]
        sample_mode = True
    else:
        train_texts, train_labels = load_supervised_jsonl(train_path)
        validation_texts, validation_labels = load_supervised_jsonl(validation_path)
        test_texts, test_labels = load_supervised_jsonl(test_path)

    ngram_range = tuple(model_config.get("ngram_range", [1, 2]))
    baseline = TfidfLogisticBaseline(
        TfidfBaselineConfig(
            max_features=int(model_config.get("max_features", 50000)),
            ngram_range=(int(ngram_range[0]), int(ngram_range[1])),
            min_df=int(model_config.get("min_df", 2)),
            class_weight=model_config.get("class_weight"),
            random_state=int(model_config.get("random_state", 42)),
        )
    )
    baseline.fit(train_texts, train_labels)

    validation_pred = baseline.predict(validation_texts)
    test_pred = baseline.predict(test_texts)
    metrics = {
        "model_name": baseline.model_name,
        "sample_mode": sample_mode,
        "validation": _basic_metrics(validation_labels, validation_pred),
        "test": _basic_metrics(test_labels, test_pred),
        "notes": "Sample-mode metrics are smoke-test only and must not be reported as LEDGAR results."
        if sample_mode
        else "Metrics computed on prepared LEDGAR splits.",
    }

    artifact_path = resolve_path(model_config["artifact_path"])
    ensure_parent(artifact_path)
    baseline.save(str(artifact_path))
    write_json(resolve_path(evaluation_config["metrics_path"]), metrics)
    return metrics
