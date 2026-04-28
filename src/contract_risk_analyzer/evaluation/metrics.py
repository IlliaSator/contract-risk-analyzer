from __future__ import annotations

from collections import Counter
from typing import Any

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def compute_classification_metrics(y_true: list[str], y_pred: list[str]) -> dict[str, Any]:
    labels = sorted(set(y_true) | set(y_pred))
    matrix = confusion_matrix(y_true, y_pred, labels=labels).tolist()
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "micro_f1": f1_score(y_true, y_pred, average="micro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "labels": labels,
        "confusion_matrix": matrix,
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }


def top_confusions(y_true: list[str], y_pred: list[str], limit: int = 20) -> list[dict[str, Any]]:
    counter: Counter[tuple[str, str]] = Counter()
    for expected, predicted in zip(y_true, y_pred, strict=True):
        if expected != predicted:
            counter[(expected, predicted)] += 1
    return [
        {"true_label": true, "predicted_label": predicted, "count": count}
        for (true, predicted), count in counter.most_common(limit)
    ]
