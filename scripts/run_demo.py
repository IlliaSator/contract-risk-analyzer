from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    command = [
        sys.executable,
        str(root / "scripts" / "analyze_document.py"),
        "--input",
        str(root / "data" / "samples" / "sample_contract.txt"),
        "--output",
        str(root / "data" / "outputs" / "risk_report.json"),
        "--mock",
    ]
    return subprocess.call(command, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
