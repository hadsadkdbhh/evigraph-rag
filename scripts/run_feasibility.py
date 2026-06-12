from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.indexing import LocalIndexBuilder
from evigraph.methods import MethodRunner
from evigraph.metrics import summarize_result


QUERY = "According to the chart, how much higher was 2023 than 2022?"
GOLD = "12.5"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run feasibility checks for the current EviGraph plan.")
    parser.add_argument("--corpus", default=str(ROOT / "data" / "corpus"))
    parser.add_argument("--index", default=str(ROOT / "outputs" / "index" / "feasibility_index.json"))
    parser.add_argument("--report", default=str(ROOT / "outputs" / "eval" / "feasibility_report.json"))
    args = parser.parse_args()

    report: dict[str, Any] = {
        "checks": [],
        "summary": {"passed": 0, "failed": 0},
    }

    index_result = LocalIndexBuilder().build(args.corpus, args.index)
    _check(report, "build_index_has_chunks", index_result["chunks"] > 0, index_result)

    rule_config = {"run": {"output_dir": "outputs/runs"}, "selection": {"max_nodes": 4, "risk_threshold": 0.65}, "scoring": {"provider": "rule"}}
    hybrid_fallback_config = {
        "run": {"output_dir": "outputs/runs"},
        "selection": {"max_nodes": 4, "risk_threshold": 0.65},
        "scoring": {"provider": "hybrid", "llm_provider": "none", "llm_weight": 0.5},
    }

    toy_runner = MethodRunner(rule_config)
    utility_only = toy_runner.run(QUERY, "utility_only", log_run=False)
    full_evigraph = toy_runner.run(QUERY, "full_evigraph", log_run=False)
    _check(
        report,
        "toy_utility_only_accepts_misleading",
        summarize_result(utility_only, GOLD)["misleading_acceptance"] == 1.0,
        {"selected_ids": utility_only["selected_ids"]},
    )
    _check(
        report,
        "toy_full_evigraph_rejects_misleading",
        summarize_result(full_evigraph, GOLD)["misleading_acceptance"] == 0.0,
        {"selected_ids": full_evigraph["selected_ids"]},
    )
    _check(
        report,
        "toy_full_evigraph_supported_and_correct",
        summarize_result(full_evigraph, GOLD)["accuracy"] == 1.0 and full_evigraph["verification"]["answer_supported"],
        {"answer": full_evigraph["answer"], "verification": full_evigraph["verification"]},
    )

    local_result = MethodRunner(rule_config).run(QUERY, "full_evigraph", corpus_path=args.index, log_run=False)
    local_metrics = summarize_result(local_result, GOLD)
    _check(
        report,
        "local_bm25_index_correct",
        local_metrics["accuracy"] == 1.0 and local_result["verification"]["answer_supported"],
        {"metrics": local_metrics, "selected_ids": local_result["selected_ids"]},
    )
    _check(
        report,
        "local_bm25_triggers_calculation",
        any(action["action_type"] == "RUN_CALCULATION" for action in local_result["actions"]),
        {"actions": local_result["actions"]},
    )

    hybrid_result = MethodRunner(hybrid_fallback_config).run(QUERY, "full_evigraph", corpus_path=args.index, log_run=False)
    hybrid_metrics = summarize_result(hybrid_result, GOLD)
    _check(
        report,
        "hybrid_llm_fallback_still_correct",
        hybrid_metrics["accuracy"] == 1.0 and hybrid_result["verification"]["answer_supported"],
        {"metrics": hybrid_metrics},
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["summary"]["failed"] == 0 else 1


def _check(report: dict[str, Any], name: str, passed: bool, details: dict[str, Any]) -> None:
    report["checks"].append({"name": name, "passed": passed, "details": details})
    key = "passed" if passed else "failed"
    report["summary"][key] += 1


if __name__ == "__main__":
    raise SystemExit(main())
