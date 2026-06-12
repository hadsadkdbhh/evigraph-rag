from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.methods import METHODS, MethodRunner
from evigraph.metrics import summarize_result
from scripts.run_query import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a small JSONL batch evaluation.")
    parser.add_argument("--questions", required=True)
    parser.add_argument("--output", default=str(ROOT / "outputs" / "eval" / "results.csv"))
    parser.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    parser.add_argument("--methods", default="topk,full_context,utility_only,full_evigraph")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)
    methods = [method.strip() for method in args.methods.split(",") if method.strip()]
    unknown = [method for method in methods if method not in METHODS]
    if unknown:
        raise ValueError(f"Unknown methods: {', '.join(unknown)}")

    with Path(args.questions).open("r", encoding="utf-8") as input_handle, output_path.open(
        "w", encoding="utf-8", newline=""
    ) as output_handle:
        writer = csv.DictWriter(
            output_handle,
            fieldnames=[
                "id",
                "method",
                "query",
                "answer",
                "prediction",
                "accuracy",
                "answer_supported",
                "citation_correct",
                "misleading_acceptance",
                "input_tokens",
                "tool_calls",
                "latency_ms",
                "run_dir",
            ],
        )
        writer.writeheader()
        for line in input_handle:
            sample = json.loads(line)
            for method in methods:
                result = MethodRunner(config).run(sample["query"], method)
                metrics = summarize_result(result, sample.get("answer"))
                writer.writerow(
                    {
                        "id": sample.get("id"),
                        "method": method,
                        "query": sample["query"],
                        "answer": sample.get("answer"),
                        "prediction": result["answer"]["text"],
                        **metrics,
                        "run_dir": result["artifacts"]["run_dir"],
                    }
                )
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
