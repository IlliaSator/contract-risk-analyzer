from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.evaluation.evaluate import evaluate_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained baseline model.")
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--model", default=None)
    parser.add_argument("--split", default="test", choices=["validation", "test"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics = evaluate_from_config(args.config, model_path=args.model, split=args.split)
    except FileNotFoundError as exc:
        print(f"Evaluation skipped: {exc}")
        return 2
    print(f"accuracy={metrics['accuracy']:.4f}")
    print(f"macro_f1={metrics['macro_f1']:.4f}")
    print(f"weighted_f1={metrics['weighted_f1']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
