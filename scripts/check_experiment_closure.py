from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CsvGate:
    name: str
    path: str
    method: str
    min_accuracy: float
    required: bool = True


@dataclass(frozen=True)
class TextGate:
    name: str
    path: str
    patterns: tuple[str, ...]
    required: bool = True


CSV_GATES = (
    CsvGate(
        "FinQA-600 oracle-doc final Full EviGraph",
        "outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/"
        "finqa_600_subset_oracle_doc_full_local_planner_v48_non_vested_ratio.csv",
        "full_evigraph",
        0.50,
    ),
    CsvGate(
        "FinQA-600 source-rerank final Full EviGraph",
        "outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/"
        "finqa_600_subset_source_rerank_full_local_planner_v48_non_vested_ratio.csv",
        "full_evigraph",
        0.50,
    ),
    CsvGate(
        "FinQA-600 open BM25 final Full EviGraph",
        "outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/"
        "finqa_600_subset_open_bm25_full_local_planner_v48_non_vested_ratio.csv",
        "full_evigraph",
        0.37,
    ),
    CsvGate(
        "FinQA-600 guarded retrieval portfolio",
        "outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/"
        "finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv",
        "full_evigraph",
        0.40,
    ),
    CsvGate(
        "TAT-QA-100 oracle-doc portability",
        "outputs/eval/tatqa_100_portability_v50/tatqa_100_oracle_doc_full_v50.csv",
        "full_evigraph",
        0.45,
    ),
    CsvGate(
        "TAT-QA-100 open BM25 portability",
        "outputs/eval/tatqa_100_portability_v50/tatqa_100_open_bm25_full_v50.csv",
        "full_evigraph",
        0.35,
    ),
    CsvGate(
        "FinQA-600 oracle-doc v48 component closure",
        "outputs/eval/finqa_600_submission_component_closure_v48/"
        "finqa_600_subset_oracle_doc_component_closure_v48.csv",
        "full_evigraph",
        0.50,
    ),
    CsvGate(
        "FinQA-600 open BM25 v48 component closure",
        "outputs/eval/finqa_600_submission_component_closure_v48/"
        "finqa_600_subset_open_bm25_component_closure_v48.csv",
        "full_evigraph",
        0.37,
    ),
    CsvGate(
        "FinQA-600 source-rerank v48 component closure",
        "outputs/eval/finqa_600_submission_component_closure_v48/"
        "finqa_600_subset_source_rerank_component_closure_v48.csv",
        "full_evigraph",
        0.50,
    ),
    CsvGate(
        "TAT-QA-100 oracle-doc method closure",
        "outputs/eval/tatqa_100_submission_method_closure_v50/"
        "tatqa_100_oracle_doc_method_closure_v50.csv",
        "full_evigraph",
        0.45,
    ),
    CsvGate(
        "TAT-QA-100 open BM25 method closure",
        "outputs/eval/tatqa_100_submission_method_closure_v50/"
        "tatqa_100_open_bm25_method_closure_v50.csv",
        "full_evigraph",
        0.35,
    ),
)


TEXT_GATES = (
    TextGate(
        "FinQA-600 final oracle failure analysis",
        "outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/"
        "finqa_600_subset_oracle_doc_full_local_planner_v48_non_vested_ratio_failures.md",
        ("wrong_numeric_operation_or_row",),
    ),
    TextGate(
        "FinQA-600 final open row-operation diagnostics",
        "outputs/eval/finqa_600_local_planner_non_vested_ratio_v48/"
        "finqa_600_subset_open_bm25_full_local_planner_v48_non_vested_ratio_row_operation_diagnostics.md",
        ("ambiguous_supported_wrong_number",),
    ),
    TextGate(
        "FinQA-600 portfolio significance report",
        "outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/portfolio_report.md",
        ("Portfolio EM: 0.407", "Losses vs primary: 0", "Paired McNemar p-value"),
    ),
    TextGate(
        "TAT-QA-100 row-operation diagnostics",
        "outputs/eval/tatqa_100_portability_v50/tatqa_100_open_bm25_full_v50_row_operation_diagnostics.md",
        ("ambiguous_supported_wrong_number",),
    ),
    TextGate(
        "FinQA-600 v28 component ablation exists",
        "outputs/eval/finqa_600_local_planner_ablation_v28/summary.md",
        ("evigraph_wo_operation_planner", "evigraph_wo_risk", "full_evigraph"),
    ),
)


STALE_BUT_USABLE = (
    "LLM Direct RAG baselines are complete for FinQA-300 GPT-5.4, but no final FinQA-600 "
    "LLM Direct RAG run is present. Keep the 300-sample LLM baseline unless budget allows a "
    "600-sample rerun.",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether the submission experiment closure gates are satisfied.")
    parser.add_argument("--output", default="docs/experiments/submission_closure_check.md")
    args = parser.parse_args()

    csv_results = [_check_csv_gate(gate) for gate in CSV_GATES]
    text_results = [_check_text_gate(gate) for gate in TEXT_GATES]
    passed = all(result["passed"] for result in (*csv_results, *text_results))

    output_path = ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_report(csv_results, text_results, passed), encoding="utf-8")
    print(str(output_path))
    return 0 if passed else 1


def _check_csv_gate(gate: CsvGate) -> dict[str, object]:
    path = ROOT / gate.path
    if not path.exists():
        return {"gate": gate, "passed": False, "status": "missing", "accuracy": None, "n": 0}
    rows = _read_csv(path)
    method_rows = [row for row in rows if row.get("method") == gate.method]
    accuracy = mean(_float(row.get("accuracy")) for row in method_rows) if method_rows else 0.0
    return {
        "gate": gate,
        "passed": bool(method_rows) and accuracy >= gate.min_accuracy,
        "status": "ok" if method_rows else "method_missing",
        "accuracy": accuracy,
        "n": len(method_rows),
    }


def _check_text_gate(gate: TextGate) -> dict[str, object]:
    path = ROOT / gate.path
    if not path.exists():
        return {"gate": gate, "passed": False, "status": "missing"}
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [pattern for pattern in gate.patterns if not re.search(re.escape(pattern), text)]
    return {
        "gate": gate,
        "passed": not missing,
        "status": "ok" if not missing else f"missing patterns: {', '.join(missing)}",
    }


def _render_report(csv_results: list[dict[str, object]], text_results: list[dict[str, object]], passed: bool) -> str:
    lines = [
        "# Submission Experiment Closure Check",
        "",
        f"Overall status: {'PASS' if passed else 'BLOCKED'}",
        "",
        "## Numeric Gates",
        "",
        "| Gate | n | EM | Threshold | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for result in csv_results:
        gate = result["gate"]
        assert isinstance(gate, CsvGate)
        accuracy = result["accuracy"]
        lines.append(
            "| "
            + " | ".join(
                [
                    gate.name,
                    str(result["n"]),
                    _fmt(accuracy),
                    _fmt(gate.min_accuracy),
                    "PASS" if result["passed"] else f"FAIL ({result['status']})",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Artifact Gates", "", "| Gate | Status |", "| --- | --- |"])
    for result in text_results:
        gate = result["gate"]
        assert isinstance(gate, TextGate)
        lines.append(f"| {gate.name} | {'PASS' if result['passed'] else 'FAIL'}: {result['status']} |")
    lines.extend(["", "## Version-Alignment Notes", ""])
    if passed:
        lines.extend(
            [
                "- FinQA-600 v48 component closure is complete across oracle-doc, open BM25, and source-rerank.",
                "- TAT-QA-100 v50 method closure is complete across oracle-doc and open BM25.",
                "- v28 component ablation remains useful only as historical development context.",
            ]
        )
    else:
        lines.extend(
            [
                "- Component ablation is not yet version-aligned until `configs/experiments.finqa_600.submission_component_closure_v48.json` finishes.",
                "- TAT-QA-100 has Full EviGraph portability results, but method-ordering closure is missing.",
            ]
        )
    lines.extend([*[f"- {warning}" for warning in STALE_BUT_USABLE], ""])
    if not passed:
        lines.extend(
            [
                "## Minimal Next Runs",
                "",
                "1. `python .\\scripts\\run_manifest.py --manifest .\\configs\\experiments.finqa_600.submission_component_closure_v48.json`",
                "2. `python .\\scripts\\analyze_statistics.py --inputs .\\outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv .\\outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv .\\outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv --output .\\outputs\\eval\\finqa_600_submission_component_closure_v48\\statistical_confidence.md`",
                "3. `python .\\scripts\\run_manifest.py --manifest .\\configs\\experiments.tatqa_100.submission_method_closure_v50.json`",
                "",
            ]
        )
    return "\n".join(lines)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def _fmt(value: object) -> str:
    if value is None:
        return "--"
    return f"{_float(value):.3f}"


if __name__ == "__main__":
    raise SystemExit(main())
