from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from contract_risk_analyzer.utils.io import read_jsonl


REQUIRED_FIELDS = {"text", "label", "split", "source"}


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records):
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            errors.append(f"record {index}: missing fields {sorted(missing)}")
        if not str(record.get("text", "")).strip():
            errors.append(f"record {index}: empty text")
        if not str(record.get("label", "")).strip():
            errors.append(f"record {index}: empty label")
    return errors


def summarize_jsonl(path: str | Path) -> dict[str, Any]:
    records = read_jsonl(path)
    labels = Counter(str(record["label"]) for record in records if "label" in record)
    return {
        "path": str(path),
        "records": len(records),
        "labels": len(labels),
        "top_labels": labels.most_common(20),
        "errors": validate_records(records),
    }
