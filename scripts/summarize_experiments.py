from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.experiment_report import ExperimentReport


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize experiment CSV files as a Markdown report.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", default=str(ROOT / "outputs" / "eval" / "summary.md"))
    parser.add_argument("--title", default="EviGraph Experiment Summary")
    args = parser.parse_args()

    output = ExperimentReport().write(args.inputs, args.output, title=args.title)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
