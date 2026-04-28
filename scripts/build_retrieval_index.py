from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.retrieval.index import build_index_from_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local clause retrieval index.")
    parser.add_argument("--input", default="data/samples/sample_clauses.jsonl")
    parser.add_argument("--output", default="models/retrieval")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        target = build_index_from_jsonl(args.input, args.output)
    except ValueError as exc:
        print(f"Retrieval index build skipped: {exc}")
        return 2
    print(f"Wrote retrieval index to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
