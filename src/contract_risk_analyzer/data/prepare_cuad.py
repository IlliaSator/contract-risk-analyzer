from __future__ import annotations

from pathlib import Path
from typing import Any

from contract_risk_analyzer.data.schemas import DatasetRecord
from contract_risk_analyzer.utils.io import write_jsonl


def normalize_cuad_records(dataset: Any, split_name: str = "train") -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, raw in enumerate(dataset):
        item = dict(raw)
        text = str(item.get("context") or item.get("text") or item.get("clause") or "").strip()
        label = str(item.get("title") or item.get("label") or item.get("question") or "cuad_clause").strip()
        if not text:
            continue
        records.append(
            DatasetRecord(
                text=text,
                label=label,
                split=split_name,
                source="cuad",
                metadata={"record_index": index},
            ).model_dump()
        )
    return records


def write_cuad_split(dataset: Any, output_dir: str | Path, split_name: str = "train") -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    target = output_path / f"cuad_{split_name}.jsonl"
    write_jsonl(target, normalize_cuad_records(dataset, split_name=split_name))
    return target
