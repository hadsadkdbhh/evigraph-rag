from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_batch_eval import main as run_batch_eval


def main() -> int:
    parser = argparse.ArgumentParser(description="Run default EviGraph ablation methods.")
    parser.add_argument("--questions", default=str(ROOT / "data" / "questions.jsonl"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "eval" / "ablation.csv"))
    args = parser.parse_args()

    sys.argv = [
        "run_batch_eval.py",
        "--questions",
        args.questions,
        "--output",
        args.output,
        "--methods",
        "topk,utility_only,evigraph_wo_risk,evigraph_wo_verifier,evigraph_wo_support,full_evigraph",
    ]
    return run_batch_eval()


if __name__ == "__main__":
    raise SystemExit(main())
