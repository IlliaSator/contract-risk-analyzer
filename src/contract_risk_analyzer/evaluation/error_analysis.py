from __future__ import annotations

from typing import Any


def build_error_analysis(
    texts: list[str],
    y_true: list[str],
    y_pred: list[str],
    confidences: list[float] | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    confidences = confidences or [0.0] * len(y_true)
    errors: list[dict[str, Any]] = []
    low_confidence: list[dict[str, Any]] = []
    high_confidence_wrong: list[dict[str, Any]] = []

    for text, expected, predicted, confidence in zip(texts, y_true, y_pred, confidences, strict=True):
        example = {
            "text": text[:500],
            "true_label": expected,
            "predicted_label": predicted,
            "confidence": round(float(confidence), 4),
            "text_length": len(text),
        }
        if expected != predicted:
            errors.append(example)
            if confidence >= 0.8:
                high_confidence_wrong.append(example)
        if confidence <= 0.5:
            low_confidence.append(example)

    return {
        "total_examples": len(y_true),
        "total_errors": len(errors),
        "error_examples": errors[:limit],
        "low_confidence_examples": low_confidence[:limit],
        "high_confidence_wrong_examples": high_confidence_wrong[:limit],
        "notes": [
            "Error analysis should be interpreted with dataset context and label support.",
            "Clause labels can be ambiguous; human review remains required.",
        ],
    }
