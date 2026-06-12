from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.case_study import CaseStudyExporter


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a run directory as a readable case study.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    output = CaseStudyExporter().export(args.run_dir, args.output)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
