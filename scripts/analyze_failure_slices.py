from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.failure_slices import FailureSliceAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser(description="Slice failed examples by retrieval coverage and question intent.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--retrieval-mode", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--method", default="full_evigraph")
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()

    output = FailureSliceAnalyzer().write(
        args.csv,
        questions_path=args.questions,
        corpus_path=args.corpus,
        retrieval_mode=args.retrieval_mode,
        output_path=args.output,
        method=args.method,
        top_k=args.top_k,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
