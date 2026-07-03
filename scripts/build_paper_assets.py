from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.paper_assets import PaperAssetBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Build paper-ready tables from experiment outputs.")
    parser.add_argument("--eval-dir", default=str(ROOT / "outputs" / "eval" / "finqa"))
    parser.add_argument("--output-dir", default=str(ROOT / "paper" / "generated"))
    parser.add_argument(
        "--preset",
        default="finqa",
        choices=[
            "finqa",
            "finqa_300_local",
            "finqa_300_local_ablation",
            "finqa_300_local_retrieval_baselines",
            "finqa_300_local_strong_retrieval_baselines",
            "finqa_300_llm_direct_rag",
            "finqa_300_gpt54_direct_rag",
            "finqa_600_local",
            "finqa_600_llm_direct_rag",
        ],
    )
    args = parser.parse_args()

    paths = PaperAssetBuilder().build(args.eval_dir, args.output_dir, preset=args.preset)
    print(json.dumps(paths, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
