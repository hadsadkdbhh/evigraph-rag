from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.case_selection import PaperCaseSelector


def main() -> int:
    parser = argparse.ArgumentParser(description="Export paper-readable case studies from paired manifest CSVs.")
    parser.add_argument("--evigraph-csv", required=True)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--retrieval-mode", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--gpt-csv", default=None)
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()

    output = PaperCaseSelector().write(
        args.evigraph_csv,
        questions_path=args.questions,
        corpus_path=args.corpus,
        retrieval_mode=args.retrieval_mode,
        output_path=args.output,
        gpt_csv=args.gpt_csv,
        top_k=args.top_k,
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
