from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.modeling.train_baseline import train_baseline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train TF-IDF + Logistic Regression baseline.")
    parser.add_argument("--config", default="configs/baseline.yaml")
    parser.add_argument("--allow-sample", action="store_true", help="Use tiny committed sample data for smoke tests.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics = train_baseline(args.config, allow_sample=args.allow_sample)
    except FileNotFoundError as exc:
        print(f"Baseline training skipped: {exc}")
        return 2
    print(metrics["notes"])
    print(f"validation_macro_f1={metrics['validation']['macro_f1']:.4f}")
    print(f"test_macro_f1={metrics['test']['macro_f1']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
