from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contract_risk_analyzer.modeling.predict import analyze_document_text, risk_report_to_dict
from contract_risk_analyzer.retrieval.search import search_index
from contract_risk_analyzer.utils.io import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a contract text file and write a risk report.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model", default=None)
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--retrieval-index", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input document not found: {input_path}")
        return 2
    text = input_path.read_text(encoding="utf-8")
    try:
        report = analyze_document_text(
            text,
            document_id=input_path.stem,
            model_path=args.model,
            mock=args.mock,
        )
    except FileNotFoundError as exc:
        print(f"Document analysis skipped: {exc}")
        return 2

    extra = {"mock_mode": args.mock}
    if args.retrieval_index:
        extra["similar_clause_examples"] = [
            result.model_dump(mode="json")
            for result in search_index(args.retrieval_index, text[:1000], top_k=3)
        ]
    write_json(args.output, risk_report_to_dict(report, extra=extra))
    print(f"Wrote risk report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
