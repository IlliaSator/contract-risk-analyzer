from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.data.download import DatasetDownloadError, prepare_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare normalized JSONL dataset splits.")
    parser.add_argument("--dataset", choices=["ledgar", "cuad", "sample"], required=True)
    parser.add_argument("--config", default="configs/data.yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = prepare_dataset(args.dataset, args.config)
    except DatasetDownloadError as exc:
        print(f"Dataset preparation failed: {exc}")
        return 2
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
