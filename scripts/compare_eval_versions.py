from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.version_compare import EvalVersionComparator


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare matched manifest CSVs between two eval versions.")
    parser.add_argument("--baseline-dir", required=True, help="Older manifest output directory.")
    parser.add_argument("--target-dir", required=True, help="Newer manifest output directory.")
    parser.add_argument("--output", required=True, help="Markdown report path.")
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--target-label", default="target")
    args = parser.parse_args()

    path = EvalVersionComparator().write(
        args.baseline_dir,
        args.target_dir,
        args.output,
        baseline_label=args.baseline_label,
        target_label=args.target_label,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
