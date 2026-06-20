from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.methods import MethodRunner
from evigraph.metrics import summarize_result
from evigraph.retrieval import RETRIEVAL_MODES
from scripts.run_query import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny accuracy-cost Pareto sweep.")
    parser.add_argument("--questions", default=str(ROOT / "data" / "questions.jsonl"))
    parser.add_argument("--output", default=str(ROOT / "outputs" / "eval" / "pareto.csv"))
    parser.add_argument("--config", default=str(ROOT / "configs" / "default.yaml"))
    parser.add_argument("--budgets", default="1,2,4,8")
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--retrieval-mode", default="oracle_doc", choices=RETRIEVAL_MODES)
    args = parser.parse_args()

    config = load_config(args.config)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    budgets = [int(value) for value in args.budgets.split(",") if value.strip()]

    with Path(args.questions).open("r", encoding="utf-8") as input_handle:
        samples = [json.loads(line) for line in input_handle]

    with output_path.open("w", encoding="utf-8", newline="") as output_handle:
        writer = csv.DictWriter(
            output_handle,
            fieldnames=["id", "method", "budget_nodes", "accuracy", "input_tokens", "tool_calls", "latency_ms"],
        )
        writer.writeheader()
        for budget in budgets:
            config.setdefault("selection", {})["max_nodes"] = budget
            runner = MethodRunner(config)
            for sample in samples:
                result = runner.run(
                    sample["query"],
                    "full_evigraph",
                    corpus_path=args.corpus,
                    source_doc=sample.get("source_doc"),
                    retrieval_mode=args.retrieval_mode,
                )
                metrics = summarize_result(result, sample.get("answer"))
                writer.writerow(
                    {
                        "id": sample.get("id"),
                        "method": "full_evigraph",
                        "budget_nodes": budget,
                        "accuracy": metrics["accuracy"],
                        "input_tokens": metrics["input_tokens"],
                        "tool_calls": metrics["tool_calls"],
                        "latency_ms": metrics["latency_ms"],
                    }
                )
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
