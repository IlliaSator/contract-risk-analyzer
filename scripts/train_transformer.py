from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.modeling.train_transformer import (
    TransformerTrainingUnavailable,
    train_transformer,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fine-tune a Hugging Face transformer classifier.")
    parser.add_argument("--config", default="configs/transformer.yaml")
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-eval-samples", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        metrics = train_transformer(
            args.config,
            max_train_samples=args.max_train_samples,
            max_eval_samples=args.max_eval_samples,
            epochs=args.epochs,
        )
    except (TransformerTrainingUnavailable, FileNotFoundError) as exc:
        print(f"Transformer training skipped: {exc}")
        return 2
    print(f"test_macro_f1={metrics['macro_f1']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
