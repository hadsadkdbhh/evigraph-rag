from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.statistical_analysis import DEFAULT_BASELINES, StatisticalAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Wilson CI and paired McNemar reports for manifest CSVs.")
    parser.add_argument("--inputs", nargs="+", required=True, help="Manifest CSV files to analyze.")
    parser.add_argument("--output", required=True, help="Markdown output path.")
    parser.add_argument("--target-method", default="full_evigraph")
    parser.add_argument("--baselines", nargs="*", default=list(DEFAULT_BASELINES))
    args = parser.parse_args()

    StatisticalAnalyzer().write(
        args.inputs,
        args.output,
        target_method=args.target_method,
        baselines=tuple(args.baselines),
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
