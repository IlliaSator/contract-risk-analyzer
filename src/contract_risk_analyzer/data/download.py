from __future__ import annotations

from pathlib import Path
from typing import Any

from contract_risk_analyzer.config.settings import load_yaml, resolve_path
from contract_risk_analyzer.data.prepare_cuad import write_cuad_split
from contract_risk_analyzer.data.prepare_ledgar import write_ledgar_splits
from contract_risk_analyzer.utils.io import read_jsonl, write_json, write_jsonl


class DatasetDownloadError(RuntimeError):
    """Raised when an external dataset cannot be downloaded or normalized."""


def _load_hf_dataset(*args: Any, **kwargs: Any) -> Any:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise DatasetDownloadError(
            "Hugging Face datasets is not installed. Run `python -m pip install '.[data]'` "
            "or `python -m pip install datasets` and retry."
        ) from exc
    return load_dataset(*args, **kwargs)


def download_ledgar(config_path: str | Path = "configs/data.yaml") -> dict[str, Any]:
    config = load_yaml(config_path)["datasets"]["ledgar"]
    try:
        dataset = _load_hf_dataset(config["hf_path"], config["hf_name"])
    except Exception as exc:
        raise DatasetDownloadError(
            "Could not download LexGLUE LEDGAR from Hugging Face. "
            "Check network access and try: "
            "`python scripts/download_data.py --dataset ledgar`."
        ) from exc
    return write_ledgar_splits(dataset, resolve_path(config["output_dir"]))


def download_cuad(config_path: str | Path = "configs/data.yaml") -> dict[str, Any]:
    config = load_yaml(config_path)["datasets"]["cuad"]
    last_error: Exception | None = None
    for candidate in config.get("hf_candidates", []):
        try:
            dataset = _load_hf_dataset(candidate)
            split_name = "train" if "train" in dataset else next(iter(dataset.keys()))
            target = write_cuad_split(dataset[split_name], resolve_path(config["output_dir"]), split_name)
            return {"dataset": candidate, "split": split_name, "output": str(target)}
        except Exception as exc:
            last_error = exc
    raise DatasetDownloadError(
        "CUAD could not be downloaded cleanly from the configured public sources. "
        "This project keeps CUAD as an optional extension; LEDGAR and sample mode are not blocked."
    ) from last_error


def prepare_sample(config_path: str | Path = "configs/data.yaml") -> dict[str, Any]:
    config = load_yaml(config_path)["datasets"]["sample"]
    records = read_jsonl(resolve_path(config["input"]))
    output_dir = resolve_path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped = {"train": records[:4], "validation": records[4:5], "test": records[5:]}
    for split_name, split_records in grouped.items():
        write_jsonl(output_dir / f"sample_{split_name}.jsonl", split_records)
    summary = {
        "dataset": "sample",
        "splits": {split: {"records": len(items)} for split, items in grouped.items()},
    }
    write_json(resolve_path("reports/sample_dataset_summary.json"), summary)
    return summary


def prepare_dataset(dataset: str, config_path: str | Path = "configs/data.yaml") -> dict[str, Any]:
    if dataset == "ledgar":
        return download_ledgar(config_path)
    if dataset == "cuad":
        return download_cuad(config_path)
    if dataset == "sample":
        return prepare_sample(config_path)
    raise ValueError(f"Unsupported dataset: {dataset}")


def clean_processed_dataset(dataset_prefix: str, output_dir: str | Path = "data/processed") -> None:
    output_path = resolve_path(output_dir)
    for path in output_path.glob(f"{dataset_prefix}_*.jsonl"):
        if path.is_file():
            path.unlink()
    summary = resolve_path("reports/dataset_summary.json")
    if summary.exists() and dataset_prefix == "ledgar":
        summary.unlink()
