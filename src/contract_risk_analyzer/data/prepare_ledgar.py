from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from contract_risk_analyzer.data.schemas import DatasetRecord
from contract_risk_analyzer.utils.io import write_json, write_jsonl


def _extract_text(record: dict[str, Any]) -> str:
    for key in ("text", "paragraph", "clause", "sentence"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"Could not find text field in LEDGAR record keys: {sorted(record)}")


def _extract_label(record: dict[str, Any], features: Any | None = None) -> str:
    value = record.get("label")
    if value is None:
        value = record.get("labels")
    if isinstance(value, list) and value:
        value = value[0]
    if isinstance(value, int) and features is not None:
        try:
            return str(features["label"].names[value])
        except Exception:
            return str(value)
    return str(value).strip()


def normalize_ledgar_split(split_name: str, dataset_split: Any) -> list[dict[str, Any]]:
    features = getattr(dataset_split, "features", None)
    normalized: list[dict[str, Any]] = []
    for raw in dataset_split:
        normalized.append(
            DatasetRecord(
                text=_extract_text(dict(raw)),
                label=_extract_label(dict(raw), features),
                split=split_name,
                source="lexglue_ledgar",
                metadata={"source_dataset": "coastalcph/lex_glue:ledgar"},
            ).model_dump()
        )
    return normalized


def write_ledgar_splits(dataset: Any, output_dir: str | Path, reports_dir: str | Path = "reports") -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"dataset": "lexglue_ledgar", "splits": {}}

    for split_name in dataset.keys():
        records = normalize_ledgar_split(split_name, dataset[split_name])
        write_jsonl(output_path / f"ledgar_{split_name}.jsonl", records)
        labels = Counter(record["label"] for record in records)
        summary["splits"][split_name] = {
            "records": len(records),
            "labels": len(labels),
            "top_labels": labels.most_common(20),
        }

    write_json(Path(reports_dir) / "dataset_summary.json", summary)
    return summary
