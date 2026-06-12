from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.pipeline import EviGraphPipeline
from scripts.run_query import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a small JSONL batch evaluation.")
    parser.add_argument("--questions", required=True)
    parser.add_argument("--output", default=str(ROOT / "outputs" / "eval" / "results.csv"))
    parser.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)

    with Path(args.questions).open("r", encoding="utf-8") as input_handle, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as output_handle:
        writer = csv.DictWriter(
            output_handle,
            fieldnames=["id", "query", "answer", "prediction", "supported", "run_dir"],
        )
        writer.writeheader()
        for line in input_handle:
            sample = json.loads(line)
            result = EviGraphPipeline(config).run(sample["query"])
            writer.writerow(
                {
                    "id": sample.get("id"),
                    "query": sample["query"],
                    "answer": sample.get("answer"),
                    "prediction": result["answer"]["text"],
                    "supported": result["verification"]["answer_supported"],
                    "run_dir": result["artifacts"]["run_dir"],
                }
            )
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
