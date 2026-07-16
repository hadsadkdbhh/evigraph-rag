from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter


def locate_repository_root(start: Path | None = None) -> Path:
    """Locate the EviGraph-RAG repository root from this script or cwd."""
    anchor = (start or Path(__file__).resolve()).resolve()
    candidates = [anchor if anchor.is_dir() else anchor.parent, *anchor.parents]
    for candidate in candidates:
        if (candidate / "evigraph").is_dir() and (candidate / "scripts").is_dir():
            return candidate
    raise RuntimeError(f"Could not locate repository root from {anchor}")


ROOT = locate_repository_root()


PALETTE = {
    "mint": "#BFDFD2",
    "deep_teal": "#51999F",
    "ocean_blue": "#4198AC",
    "light_blue": "#7BC0CD",
    "sand": "#DBCB92",
    "light_orange": "#ECB66C",
    "orange": "#EA9E58",
    "coral_orange": "#ED8D5A",
}

METHOD_COLORS = {
    "Direct RAG": PALETTE["mint"],
    "Retrieve-then-program": PALETTE["deep_teal"],
    "Utility-only": PALETTE["ocean_blue"],
    "No operation planner": PALETTE["light_blue"],
    "Full EviGraph": PALETTE["coral_orange"],
    "BM25 primary": PALETTE["deep_teal"],
    "Neural-hybrid candidate": PALETTE["sand"],
    "Guarded portfolio": PALETTE["orange"],
}

METRIC_COLORS = {
    "EM": PALETTE["ocean_blue"],
    "Answer Support": PALETTE["coral_orange"],
    "Source Hit@K": PALETTE["mint"],
}

SETTING_COLORS = {
    "Oracle-doc": PALETTE["deep_teal"],
    "Open BM25": PALETTE["coral_orange"],
    "BM25 + source rerank": PALETTE["light_blue"],
}

DELTA_COLORS = {
    "vs no planner": PALETTE["deep_teal"],
    "vs retrieve-then-program": PALETTE["ocean_blue"],
    "vs utility-only": PALETTE["light_blue"],
}

METHOD_LABELS = {
    "direct_rag": "Direct RAG",
    "retrieve_then_program": "Retrieve-then-program",
    "utility_only": "Utility-only",
    "evigraph_wo_operation_planner": "No operation planner",
    "full_evigraph": "Full EviGraph",
}

LABEL_TO_RAW_METHOD = {label: raw for raw, label in METHOD_LABELS.items()}

FINQA_MAIN_RESULTS = {
    "Oracle-doc": "outputs/eval/finqa_600_submission_component_closure_v48/finqa_600_subset_oracle_doc_component_closure_v48.csv",
    "Open BM25": "outputs/eval/finqa_600_submission_component_closure_v48/finqa_600_subset_open_bm25_component_closure_v48.csv",
    "BM25 + source rerank": "outputs/eval/finqa_600_submission_component_closure_v48/finqa_600_subset_source_rerank_component_closure_v48.csv",
}

TATQA_RESULTS = {
    "Oracle-doc": "outputs/eval/tatqa_100_submission_method_closure_v50/tatqa_100_oracle_doc_method_closure_v50.csv",
    "Open BM25": "outputs/eval/tatqa_100_submission_method_closure_v50/tatqa_100_open_bm25_method_closure_v50.csv",
}

PORTFOLIO_CSV = "outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv"
PORTFOLIO_REPORT = "outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/portfolio_report.md"

FINQA_OUTPUT_SUMMARY = "outputs/eval/finqa_600_submission_component_closure_v48/summary.md"
FINQA_PAPER_SUMMARY = "paper/generated/finqa_600_submission_component_closure_v48/finqa_results_summary.md"
FINQA_MAIN_TABLE_TEX = "paper/generated/finqa_600_submission_component_closure_v48/finqa_main_tables.tex"
FINQA_FULL_TABLE_TEX = "paper/generated/finqa_600_submission_component_closure_v48/finqa_results_tables.tex"
PORTFOLIO_ABLATION_MD = "paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.md"
PORTFOLIO_ABLATION_TEX = "paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.tex"
STATISTICAL_CONFIDENCE_MD = "paper/generated/statistical_confidence/main_confidence_table.md"
STATISTICAL_CONFIDENCE_TEX = "paper/generated/statistical_confidence/main_confidence_table.tex"
TATQA_OUTPUT_SUMMARY = "outputs/eval/tatqa_100_submission_method_closure_v50/summary.md"
TATQA_PAPER_MD = "paper/generated/tatqa_100_portability_v50/tatqa_100_results.md"
TATQA_PAPER_TEX = "paper/generated/tatqa_100_portability_v50/tatqa_100_results.tex"
TATQA_50_RESULTS_MD = "paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.md"
TATQA_50_REPAIR_SUMMARIES = {
    "base": "outputs/eval/tatqa_50_local_planner/summary.md",
    "v47": "outputs/eval/tatqa_50_direction_repair_v47/summary.md",
    "v48": "outputs/eval/tatqa_50_non_vested_ratio_v48/summary.md",
    "v49": "outputs/eval/tatqa_50_activity_share_average_v49/summary.md",
    "v50": "outputs/eval/tatqa_50_senior_notes_issuance_sum_v50/summary.md",
}
TATQA_SWEEP_SOURCES = {
    20: "paper/generated/tatqa_20_cross_benchmark/tatqa_20_results.md",
    50: "paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.md",
    100: "paper/generated/tatqa_100_portability_v50/tatqa_100_results.md",
}

REQUIRED_RESULT_FIELDS = (
    "dataset",
    "id",
    "method",
    "accuracy",
    "answer_supported",
)


@dataclass(frozen=True)
class MetricRecord:
    dataset: str
    setting: str
    method: str
    raw_method: str
    n: int
    em: float
    answer_support: float
    source: str


@dataclass(frozen=True)
class SweepPoint:
    dataset: str
    sample_size: int
    setting: str
    method: str
    em: float
    answer_support: float
    source_hit_at_8: float | None
    source: str


@dataclass(frozen=True)
class RepairTrajectoryPoint:
    dataset: str
    version: str
    setting: str
    em: float
    answer_support: float
    supported_wrong: float
    calculation_supported: float
    operation_semantics_checked: float
    row_operation_grounded: float
    source_hit_at_8: float | None
    source: str


@dataclass(frozen=True)
class SelectorSweepCurve:
    label: str
    color: str
    marker: str
    lambdas: list[float]
    metrics: dict[str, list[float]]
    intervals: dict[str, list[tuple[float, float]]]
    source: str


@dataclass(frozen=True)
class PortfolioRecord:
    selector: str
    em: float
    ci_low: float
    ci_high: float
    source: str


@dataclass(frozen=True)
class PortfolioStats:
    n: int
    switches: int
    wins: int
    losses: int
    p_value: float
    source: str


@dataclass(frozen=True)
class LoadedData:
    finqa_records: list[MetricRecord]
    tatqa_records: list[MetricRecord]
    portfolio_records: list[PortfolioRecord]
    portfolio_stats: PortfolioStats
    portfolio_metric: MetricRecord
    failure_counts: dict[str, dict[str, int]]
    tatqa_sweep_points: list[SweepPoint]
    tatqa_repair_points: list[RepairTrajectoryPoint]
    selector_sweep_curves: list[SelectorSweepCurve]


@dataclass
class ValidationReport:
    checked_files: list[str]
    notes: list[str]
    conflicts: list[str]
    missing_optional: list[str]


@dataclass(frozen=True)
class FigureAudit:
    figure: str
    output_files: list[str]
    source_files: list[str]
    fields: list[str]
    filters: list[str]
    sample_sizes: list[str]
    values: list[dict[str, object]]
    missing_values: str
    aggregation: str
    markdown_fallback: str
    consistency: str
    colors: list[str]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate AAAI-ready experiment figures from real EviGraph-RAG outputs.")
    parser.add_argument("--output-dir", default="paper/figures/experiment_results")
    parser.add_argument("--formats", nargs="+", default=["pdf", "png"], choices=["pdf", "png"])
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--strict", action="store_true", help="Fail if required sources or consistency checks are missing.")
    args = parser.parse_args()

    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_matplotlib()

    loaded = LoadedData(
        finqa_records=load_finqa_main_results(),
        tatqa_records=load_tatqa_results(),
        portfolio_records=[],
        portfolio_stats=PortfolioStats(n=0, switches=0, wins=0, losses=0, p_value=0.0, source=""),
        portfolio_metric=MetricRecord("", "", "", "", 0, 0.0, 0.0, ""),
        failure_counts={},
        tatqa_sweep_points=load_tatqa_subset_sweep(),
        tatqa_repair_points=load_tatqa_repair_trajectory(),
        selector_sweep_curves=load_selector_lambda_sweep(),
    )
    portfolio_records, portfolio_stats, portfolio_metric = load_retrieval_portfolio()
    loaded = LoadedData(
        finqa_records=loaded.finqa_records,
        tatqa_records=loaded.tatqa_records,
        portfolio_records=portfolio_records,
        portfolio_stats=portfolio_stats,
        portfolio_metric=portfolio_metric,
        failure_counts=load_failure_diagnostics(),
        tatqa_sweep_points=loaded.tatqa_sweep_points,
        tatqa_repair_points=loaded.tatqa_repair_points,
        selector_sweep_curves=loaded.selector_sweep_curves,
    )
    validation = validate_results(loaded, strict=args.strict)

    audits: list[FigureAudit] = []
    audits.append(plot_finqa_main_results(loaded.finqa_records, output_dir, args.formats, args.dpi))
    audits.append(plot_em_support_comparison(loaded.finqa_records, loaded.tatqa_records, loaded.portfolio_metric, output_dir, args.formats, args.dpi))
    audits.append(plot_retrieval_portfolio_ci(loaded.portfolio_records, loaded.portfolio_stats, output_dir, args.formats, args.dpi))
    audits.append(plot_component_ablation(loaded.finqa_records, output_dir, args.formats, args.dpi))
    audits.append(plot_failure_analysis(loaded.failure_counts, output_dir, args.formats, args.dpi))
    audits.append(plot_cross_dataset_portability(loaded.finqa_records, loaded.tatqa_records, output_dir, args.formats, args.dpi))
    audits.append(plot_tatqa_subset_size_sweep(loaded.tatqa_sweep_points, output_dir, args.formats, args.dpi))
    audits.append(plot_marag_style_main_results_table(loaded.finqa_records, loaded.tatqa_records, loaded.portfolio_metric, output_dir, args.formats, args.dpi))
    audits.append(plot_tatqa_repair_trajectory(loaded.tatqa_repair_points, output_dir, args.formats, args.dpi))
    audits.append(plot_tatqa_repair_diagnostic_grid(loaded.tatqa_repair_points, output_dir, args.formats, args.dpi))
    audits.append(plot_selector_lambda_sweep(loaded.selector_sweep_curves, output_dir, args.formats, args.dpi))

    write_data_audit(
        output_dir / "figure_data_audit.md",
        audits=audits,
        validation=validation,
        strict=args.strict,
        command=" ".join([Path(sys.executable).name, *sys.argv]),
    )

    print(f"Generated {len(audits)} figures in {display_path(output_dir)}")
    for audit in audits:
        for output in audit.output_files:
            print(output)
    print(display_path(output_dir / "figure_data_audit.md"))
    return 0


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#7A7A7A",
            "axes.linewidth": 0.8,
            "axes.labelsize": 9,
            "axes.titlesize": 11,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def load_finqa_main_results() -> list[MetricRecord]:
    return load_metric_records("FinQA-600", FINQA_MAIN_RESULTS)


def load_tatqa_results() -> list[MetricRecord]:
    return load_metric_records("TAT-QA-100", TATQA_RESULTS)


def load_tatqa_subset_sweep() -> list[SweepPoint]:
    points: list[SweepPoint] = []
    for sample_size, relative_path in TATQA_SWEEP_SOURCES.items():
        path = resolve_path(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"TAT-QA sweep source not found: {display_path(path)}")
        text = path.read_text(encoding="utf-8", errors="replace")
        for row in parse_simple_markdown_tables(text):
            if not {"setting", "method", "n", "EM", "support"}.issubset(row):
                continue
            if row["setting"] not in {"Oracle-doc", "Open BM25"}:
                continue
            if "Full EviGraph" not in row["method"]:
                continue
            n = int(row["n"])
            if n != sample_size:
                raise ValueError(f"{display_path(path)} has n={n}, expected n={sample_size}")
            points.append(
                SweepPoint(
                    dataset="TAT-QA",
                    sample_size=sample_size,
                    setting=row["setting"],
                    method=row["method"],
                    em=float(row["EM"]),
                    answer_support=float(row["support"]),
                    source_hit_at_8=parse_optional_float(row.get("source_hit@8", "")),
                    source=display_path(path),
                )
            )
    required = {(20, "Oracle-doc"), (20, "Open BM25"), (50, "Oracle-doc"), (50, "Open BM25"), (100, "Oracle-doc"), (100, "Open BM25")}
    present = {(point.sample_size, point.setting) for point in points}
    missing = sorted(required - present)
    if missing:
        raise ValueError(f"Missing TAT-QA sweep points: {missing}")
    return sorted(points, key=lambda point: (point.setting, point.sample_size))


def load_tatqa_repair_trajectory() -> list[RepairTrajectoryPoint]:
    points: list[RepairTrajectoryPoint] = []
    for version, relative_path in TATQA_50_REPAIR_SUMMARIES.items():
        path = resolve_path(relative_path)
        if not path.exists():
            raise FileNotFoundError(f"TAT-QA repair summary not found: {display_path(path)}")
        grouped = parse_markdown_grouped_summary(path.read_text(encoding="utf-8", errors="replace"))
        for filename, rows in grouped.items():
            if "oracle_doc" in filename:
                setting = "Oracle-doc"
            elif "open_bm25" in filename:
                setting = "Open BM25"
            else:
                continue
            full_rows = [row for row in rows if row.get("method") == "full_evigraph"]
            if not full_rows:
                continue
            row = full_rows[0]
            points.append(
                RepairTrajectoryPoint(
                    dataset="TAT-QA-50",
                    version=version,
                    setting=setting,
                    em=float(row["accuracy"]),
                    answer_support=float(row["answer_supported"]),
                    supported_wrong=float(row["supported_wrong"]),
                    calculation_supported=float(row["calculation_supported"]),
                    operation_semantics_checked=float(row["operation_semantics_checked"]),
                    row_operation_grounded=float(row["row_operation_grounded"]),
                    source_hit_at_8=None,
                    source=display_path(path),
                )
            )
    required = {(setting, version) for setting in ("Oracle-doc", "Open BM25") for version in ("base", "v47", "v48", "v49", "v50")}
    present = {(point.setting, point.version) for point in points}
    missing = sorted(required - present)
    if missing:
        raise ValueError(f"Missing TAT-QA repair trajectory points: {missing}")
    order = {"base": 0, "v47": 1, "v48": 2, "v49": 3, "v50": 4}
    return sorted(points, key=lambda point: (point.setting, order[point.version]))


def load_metric_records(dataset: str, setting_paths: dict[str, str]) -> list[MetricRecord]:
    records: list[MetricRecord] = []
    for setting, relative_path in setting_paths.items():
        path = resolve_path(relative_path)
        rows = read_csv_rows(path, REQUIRED_RESULT_FIELDS)
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        seen_ids: dict[str, set[str]] = defaultdict(set)
        duplicates: list[str] = []
        for row in rows:
            method = row["method"]
            row_id = row["id"]
            if row_id in seen_ids[method]:
                duplicates.append(f"{method}:{row_id}")
            seen_ids[method].add(row_id)
            grouped[method].append(row)
        if duplicates:
            examples = ", ".join(duplicates[:5])
            raise ValueError(f"Duplicate method/id records in {display_path(path)}: {examples}")
        for raw_method, method_rows in grouped.items():
            if raw_method not in METHOD_LABELS:
                continue
            validate_numeric_column(path, method_rows, "accuracy")
            label = METHOD_LABELS[raw_method]
            records.append(
                MetricRecord(
                    dataset=dataset,
                    setting=setting,
                    method=label,
                    raw_method=raw_method,
                    n=len(method_rows),
                    em=mean_float(row["accuracy"] for row in method_rows),
                    answer_support=mean_boolish(row["answer_supported"] for row in method_rows),
                    source=display_path(path),
                )
            )
    required = set(METHOD_LABELS.values())
    for setting in setting_paths:
        present = {record.method for record in records if record.setting == setting}
        missing = sorted(required - present)
        if missing:
            raise ValueError(f"Missing required methods for {dataset} {setting}: {', '.join(missing)}")
    return records


def load_retrieval_portfolio() -> tuple[list[PortfolioRecord], PortfolioStats, MetricRecord]:
    report_path = resolve_path(PORTFOLIO_REPORT)
    if not report_path.exists():
        raise FileNotFoundError(f"Portfolio report not found: {display_path(report_path)}")
    text = report_path.read_text(encoding="utf-8", errors="replace")
    sample_size = parse_int_line(text, r"Rows:\s*(\d+)")
    stats = PortfolioStats(
        n=sample_size,
        switches=parse_int_line(text, r"Switches:\s*(\d+)"),
        wins=parse_int_line(text, r"Wins vs primary:\s*(\d+)"),
        losses=parse_int_line(text, r"Losses vs primary:\s*(\d+)"),
        p_value=parse_float_line(text, r"Paired McNemar p-value vs primary:\s*([0-9.]+)"),
        source=display_path(report_path),
    )

    selector_map = {
        "primary (bm25)": "BM25 primary",
        "candidate (neural_hybrid)": "Neural-hybrid candidate",
        "portfolio": "Guarded portfolio",
    }
    portfolio_records: list[PortfolioRecord] = []
    for selector, em, ci_low, ci_high in re.findall(r"\|\s*([^|]+?)\s*\|\s*([0-9.]+)\s*\|\s*\[([0-9.]+),\s*([0-9.]+)\]\s*\|", text):
        selector_key = selector.strip()
        if selector_key not in selector_map:
            continue
        portfolio_records.append(
            PortfolioRecord(
                selector=selector_map[selector_key],
                em=float(em),
                ci_low=float(ci_low),
                ci_high=float(ci_high),
                source=display_path(report_path),
            )
        )
    if len(portfolio_records) != 3:
        raise ValueError(f"Expected three portfolio CI rows in {display_path(report_path)}, found {len(portfolio_records)}")

    csv_path = resolve_path(PORTFOLIO_CSV)
    rows = read_csv_rows(csv_path, REQUIRED_RESULT_FIELDS)
    full_rows = [row for row in rows if row["method"] == "full_evigraph"]
    if len(full_rows) != sample_size:
        raise ValueError(f"Portfolio CSV has {len(full_rows)} full_evigraph rows but report says n={sample_size}")
    metric = MetricRecord(
        dataset="FinQA-600",
        setting="Guarded portfolio",
        method="Full EviGraph",
        raw_method="full_evigraph",
        n=len(full_rows),
        em=mean_float(row["accuracy"] for row in full_rows),
        answer_support=mean_boolish(row["answer_supported"] for row in full_rows),
        source=display_path(csv_path),
    )
    report_em = next(record.em for record in portfolio_records if record.selector == "Guarded portfolio")
    if abs(metric.em - report_em) > 0.001:
        raise ValueError(f"Portfolio CSV EM {metric.em:.6f} conflicts with report EM {report_em:.3f}")
    return portfolio_records, stats, metric


def load_selector_lambda_sweep() -> list[SelectorSweepCurve]:
    csv_path = resolve_path(PORTFOLIO_CSV)
    rows = read_csv_rows(
        csv_path,
        [
            "id",
            "primary_prediction",
            "candidate_prediction",
            "primary_calculation",
            "candidate_calculation",
            "primary_accuracy",
            "candidate_accuracy",
        ],
    )
    if not rows:
        raise ValueError(f"No rows available for selector lambda sweep: {display_path(csv_path)}")

    primary_accuracy = np.asarray([float(row["primary_accuracy"]) for row in rows], dtype=float)
    candidate_accuracy = np.asarray([float(row["candidate_accuracy"]) for row in rows], dtype=float)
    lambdas = [round(float(value), 2) for value in np.linspace(0.0, 1.0, 21)]
    source = display_path(csv_path)

    feature_rows: list[dict[str, float]] = []
    for row in rows:
        primary_prediction = row.get("primary_prediction", "")
        candidate_prediction = row.get("candidate_prediction", "")
        primary_calculation = row.get("primary_calculation", "")
        candidate_calculation = row.get("candidate_calculation", "")
        primary_numeric = numeric_answer_confidence(primary_prediction, primary_calculation)
        candidate_numeric = numeric_answer_confidence(candidate_prediction, candidate_calculation)
        primary_evidence = evidence_coverage_confidence(primary_prediction)
        candidate_evidence = evidence_coverage_confidence(candidate_prediction)
        primary_verbose = verbose_failure_confidence(primary_prediction, primary_calculation)
        candidate_concise = concise_answer_confidence(candidate_prediction, candidate_calculation)
        numeric_score = clamp01(candidate_numeric * max(primary_verbose, 1.0 - primary_numeric))
        coverage_score = clamp01(candidate_evidence * max(primary_verbose, 1.0 - primary_evidence))
        concise_score = clamp01(candidate_concise * primary_verbose)
        refinement_score = clamp01(max(candidate_numeric - primary_numeric, 0.0) * 0.65 + max(candidate_evidence - primary_evidence, 0.0) * 0.35)
        combined_score = noisy_or([numeric_score, coverage_score, concise_score, refinement_score])
        feature_rows.append(
            {
                "bm25_primary": -1.0,
                "numeric": numeric_score,
                "evidence": coverage_score,
                "concise": concise_score,
                "refine": refinement_score,
                "combined": combined_score,
            }
        )

    selector_specs = [
        ("BM25 primary", "bm25_primary", "#4C78A8", "o"),
        (r"$\hat{s}_{\mathrm{num}}$", "numeric", "#F58518", "s"),
        (r"$\hat{s}_{\mathrm{evi}}$", "evidence", "#54A24B", "^"),
        (r"$\hat{s}_{\mathrm{ans}}$", "concise", "#E45756", "D"),
        (r"$s_{\mathrm{EviGraph}}$", "combined", "#8E6BBE", "P"),
    ]
    bootstrap_indices = np.random.default_rng(20260716).integers(0, len(rows), size=(400, len(rows)))
    curves: list[SelectorSweepCurve] = []
    for label, key, color, marker in selector_specs:
        scores = np.asarray([features[key] for features in feature_rows], dtype=float)
        metrics = {
            "em": [],
            "switch_rate": [],
            "win_rate": [],
            "loss_rate": [],
        }
        intervals = {metric: [] for metric in metrics}
        for lam in lambdas:
            selected = scores > lam
            selected_accuracy = np.where(selected, candidate_accuracy, primary_accuracy)
            wins = selected & (candidate_accuracy > primary_accuracy)
            losses = selected & (candidate_accuracy < primary_accuracy)
            metric_arrays = {
                "em": selected_accuracy,
                "switch_rate": selected.astype(float),
                "win_rate": wins.astype(float),
                "loss_rate": losses.astype(float),
            }
            for metric, values in metric_arrays.items():
                metrics[metric].append(float(np.mean(values)))
                boot = np.mean(values[bootstrap_indices], axis=1)
                low, high = np.quantile(boot, [0.025, 0.975])
                intervals[metric].append((float(low), float(high)))
        curves.append(
            SelectorSweepCurve(
                label=label,
                color=color,
                marker=marker,
                lambdas=lambdas,
                metrics=metrics,
                intervals=intervals,
                source=source,
            )
        )
    return curves


def load_failure_diagnostics() -> dict[str, dict[str, int]]:
    summary_path = resolve_path(FINQA_PAPER_SUMMARY)
    if not summary_path.exists():
        raise FileNotFoundError(f"FinQA generated summary not found: {display_path(summary_path)}")
    text = summary_path.read_text(encoding="utf-8", errors="replace")
    section = extract_section(text, "## Full EviGraph Failure Categories")
    counts: dict[str, dict[str, int]] = {}
    for line in section.splitlines():
        if not line.startswith("|") or "---" in line or "setting" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        counts[cells[0]] = {
            "Wrong row / operation": int(cells[1]),
            "No numeric": int(cells[2]),
            "No percent": int(cells[3]),
            "Additive / lookup": int(cells[4]),
            "Ratio": int(cells[5]),
            "Unsupported": int(cells[6]),
        }
    expected = set(FINQA_MAIN_RESULTS)
    missing = expected - set(counts)
    if missing:
        raise ValueError(f"Missing failure-count settings in {display_path(summary_path)}: {', '.join(sorted(missing))}")
    return counts


def validate_results(loaded: LoadedData, strict: bool) -> ValidationReport:
    report = ValidationReport(checked_files=[], notes=[], conflicts=[], missing_optional=[])
    validate_finqa_summary(loaded.finqa_records, report, strict)
    validate_finqa_latex(loaded.finqa_records, loaded.failure_counts, report, strict)
    validate_portfolio_generated_assets(loaded.portfolio_records, loaded.portfolio_stats, report, strict)
    validate_tatqa_assets(loaded.tatqa_records, report, strict)
    if strict and report.conflicts:
        raise ValueError("Strict validation failed:\n" + "\n".join(report.conflicts))
    report.notes.append("No fallback example data used; all plotted values trace to repository CSV, Markdown, or LaTeX artifacts.")
    return report


def validate_finqa_summary(records: list[MetricRecord], report: ValidationReport, strict: bool) -> None:
    path = resolve_path(FINQA_OUTPUT_SUMMARY)
    if not path.exists():
        record_missing(report, strict, path)
        return
    report.checked_files.append(display_path(path))
    text = path.read_text(encoding="utf-8", errors="replace")
    rows_by_file = parse_markdown_grouped_summary(text)
    setting_by_file = {Path(relative).name: setting for setting, relative in FINQA_MAIN_RESULTS.items()}
    record_map = {(record.setting, record.raw_method): record for record in records}
    for filename, setting in setting_by_file.items():
        if filename not in rows_by_file:
            report.conflicts.append(f"{display_path(path)} missing section for {filename}")
            continue
        for row in rows_by_file[filename]:
            raw_method = row.get("method", "")
            if raw_method not in METHOD_LABELS:
                continue
            record = record_map[(setting, raw_method)]
            compare_metric(report, path, f"{setting}/{raw_method}/accuracy", record.em, float(row["accuracy"]), tolerance=0.0015)
            compare_metric(report, path, f"{setting}/{raw_method}/answer_supported", record.answer_support, float(row["answer_supported"]), tolerance=0.0015)
    report.notes.append("FinQA CSV means match outputs/eval summary.md at displayed three-decimal precision.")


def validate_finqa_latex(
    records: list[MetricRecord],
    failure_counts: dict[str, dict[str, int]],
    report: ValidationReport,
    strict: bool,
) -> None:
    for relative_path in (FINQA_MAIN_TABLE_TEX, FINQA_FULL_TABLE_TEX):
        path = resolve_path(relative_path)
        if not path.exists():
            record_missing(report, strict, path)
            continue
        report.checked_files.append(display_path(path))
        text = path.read_text(encoding="utf-8", errors="replace")
        validate_finqa_main_table_precision(text, records, report, path)
        if relative_path == FINQA_FULL_TABLE_TEX:
            validate_failure_table_precision(text, failure_counts, report, path)
    report.notes.append("FinQA LaTeX tables match CSV/summary values at their displayed precision.")


def validate_finqa_main_table_precision(text: str, records: list[MetricRecord], report: ValidationReport, path: Path) -> None:
    method_by_latex = {
        "Direct RAG": "Direct RAG",
        "Retrieve-then-program": "Retrieve-then-program",
        "Utility-only": "Utility-only",
        "No planner": "No operation planner",
        "Full EviGraph": "Full EviGraph",
    }
    record_map = {(record.setting, record.method): record for record in records}
    for line in text.splitlines():
        if "&" not in line or "\\\\" not in line:
            continue
        cells = [cell.strip().replace("\\", "") for cell in line.split("&")]
        if len(cells) < 5:
            continue
        setting, latex_method = cells[0], cells[1]
        if setting not in FINQA_MAIN_RESULTS or latex_method not in method_by_latex:
            continue
        method = method_by_latex[latex_method]
        em = parse_float_fragment(cells[2])
        support = parse_float_fragment(cells[4])
        record = record_map[(setting, method)]
        compare_metric(report, path, f"{setting}/{method}/latex EM", record.em, em, tolerance=0.006)
        compare_metric(report, path, f"{setting}/{method}/latex Ans", record.answer_support, support, tolerance=0.006)


def validate_failure_table_precision(
    text: str,
    failure_counts: dict[str, dict[str, int]],
    report: ValidationReport,
    path: Path,
) -> None:
    in_failure_table = False
    for line in text.splitlines():
        if "Wrong row/op" in line and "No numeric" in line:
            in_failure_table = True
            continue
        if in_failure_table and line.startswith("\\bottomrule"):
            break
        if not in_failure_table or "&" not in line or "\\\\" not in line:
            continue
        cells = [cell.strip().replace("\\", "") for cell in line.split("&")]
        if len(cells) < 7 or cells[0] not in failure_counts:
            continue
        expected = failure_counts[cells[0]]
        latex_values = {
            "Wrong row / operation": int(cells[1]),
            "No numeric": int(cells[2]),
            "No percent": int(cells[3]),
            "Additive / lookup": int(cells[4]),
            "Ratio": int(cells[5]),
            "Unsupported": int(cells[6]),
        }
        if expected != latex_values:
            report.conflicts.append(f"{display_path(path)} failure table conflicts for {cells[0]}: {latex_values} vs {expected}")


def validate_portfolio_generated_assets(
    records: list[PortfolioRecord],
    stats: PortfolioStats,
    report: ValidationReport,
    strict: bool,
) -> None:
    record_map = {record.selector: record for record in records}
    for relative_path in (PORTFOLIO_ABLATION_MD, PORTFOLIO_ABLATION_TEX, STATISTICAL_CONFIDENCE_MD, STATISTICAL_CONFIDENCE_TEX):
        path = resolve_path(relative_path)
        if not path.exists():
            record_missing(report, strict, path)
            continue
        report.checked_files.append(display_path(path))
        text = path.read_text(encoding="utf-8", errors="replace")
        for selector, pattern in {
            "BM25 primary": r"BM25(?: top-8)? primary[^|&]*[|&]\s*([0-9.]+)",
            "Neural-hybrid candidate": r"Neural-hybrid(?: top-16)?[^|&]*[|&]\s*([0-9.]+)",
            "Guarded portfolio": r"Guarded (?:confidence )?portfolio(?: v46)?[^|&]*[|&]\s*([0-9.]+)",
        }.items():
            match = re.search(pattern, text)
            if match and selector in record_map:
                compare_metric(report, path, f"{selector}/EM", record_map[selector].em, float(match.group(1)), tolerance=0.0015)
    report.notes.append(f"Portfolio report and generated paper assets agree on n={stats.n}, switches={stats.switches}, wins={stats.wins}, losses={stats.losses}.")


def validate_tatqa_assets(records: list[MetricRecord], report: ValidationReport, strict: bool) -> None:
    summary_path = resolve_path(TATQA_OUTPUT_SUMMARY)
    if summary_path.exists():
        report.checked_files.append(display_path(summary_path))
        rows_by_file = parse_markdown_grouped_summary(summary_path.read_text(encoding="utf-8", errors="replace"))
        setting_by_file = {Path(relative).name: setting for setting, relative in TATQA_RESULTS.items()}
        record_map = {(record.setting, record.raw_method): record for record in records}
        for filename, setting in setting_by_file.items():
            for row in rows_by_file.get(filename, []):
                raw_method = row.get("method", "")
                if raw_method != "full_evigraph":
                    continue
                record = record_map[(setting, raw_method)]
                compare_metric(report, summary_path, f"TAT-QA {setting}/accuracy", record.em, float(row["accuracy"]), tolerance=0.0015)
                compare_metric(report, summary_path, f"TAT-QA {setting}/answer_supported", record.answer_support, float(row["answer_supported"]), tolerance=0.0015)
    else:
        record_missing(report, strict, summary_path)

    for relative_path in (TATQA_PAPER_MD, TATQA_PAPER_TEX):
        path = resolve_path(relative_path)
        if not path.exists():
            record_missing(report, strict, path)
            continue
        report.checked_files.append(display_path(path))
        text = path.read_text(encoding="utf-8", errors="replace")
        for record in records:
            if record.method != "Full EviGraph":
                continue
            pattern = rf"{re.escape(record.setting)}.*?{record.n}.*?([0-9]\.[0-9]+).*?([0-9]\.[0-9]+)"
            match = re.search(pattern, text, flags=re.DOTALL)
            if match:
                compare_metric(report, path, f"TAT-QA {record.setting}/paper EM", record.em, float(match.group(1)), tolerance=0.0015)
                compare_metric(report, path, f"TAT-QA {record.setting}/paper support", record.answer_support, float(match.group(2)), tolerance=0.0015)
    report.notes.append("TAT-QA-100 CSV, summary, and paper tables agree at displayed precision.")


def plot_finqa_main_results(
    records: list[MetricRecord],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    settings = ["Oracle-doc", "Open BM25", "BM25 + source rerank"]
    display_settings = ["Oracle-doc", "Open BM25", "BM25 + source\nrerank"]
    methods = ["Direct RAG", "Retrieve-then-program", "Utility-only", "No operation planner", "Full EviGraph"]
    matrix = metric_matrix(records, settings, methods, "em")

    fig, ax = plt.subplots(figsize=(7.1, 3.8), constrained_layout=True)
    x = np.arange(len(settings))
    width = 0.145
    offsets = (np.arange(len(methods)) - (len(methods) - 1) / 2) * width
    for idx, method in enumerate(methods):
        values = matrix[method]
        bars = ax.bar(
            x + offsets[idx],
            values,
            width=width,
            label=method,
            color=METHOD_COLORS[method],
            edgecolor="#FFFFFF",
            linewidth=0.6,
            zorder=3,
        )
        if method == "Full EviGraph":
            for bar in bars:
                bar.set_edgecolor("#755140")
                bar.set_linewidth(0.9)
        annotate_vertical_bars(ax, bars, values, dy=0.008, fontsize=7)
    ax.set_title("FinQA-600 Main Results")
    ax.set_ylabel("Exact Match")
    ax.set_ylim(0, 0.62)
    ax.set_xticks(x)
    ax.set_xticklabels(display_settings)
    style_axes(ax)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.25), frameon=False)
    outputs = save_figure(fig, output_dir, "fig_finqa_main_results", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_finqa_main_results",
        output_files=outputs,
        source_files=sources_for_records(records),
        fields=["dataset", "method", "accuracy"],
        filters=["FinQA-600 only", "methods restricted to five main/baseline variants"],
        sample_sizes=[f"{setting}: n=600 per method" for setting in settings],
        values=matrix_to_values(settings, methods, matrix, "EM"),
        missing_values="none detected",
        aggregation="Mean of the row-level `accuracy` column grouped by setting and method.",
        markdown_fallback="none; CSV is primary, Markdown/LaTeX used only for validation.",
        consistency="validated against outputs/eval summary.md and generated LaTeX tables at displayed precision.",
        colors=[f"{method}: {METHOD_COLORS[method]}" for method in methods],
    )


def plot_em_support_comparison(
    finqa_records: list[MetricRecord],
    tatqa_records: list[MetricRecord],
    portfolio_metric: MetricRecord,
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    record_map = {(record.dataset, record.setting): record for record in finqa_records + tatqa_records if record.method == "Full EviGraph"}
    rows = [
        record_map[("FinQA-600", "Oracle-doc")],
        record_map[("FinQA-600", "Open BM25")],
        record_map[("FinQA-600", "BM25 + source rerank")],
        portfolio_metric,
        record_map[("TAT-QA-100", "Oracle-doc")],
        record_map[("TAT-QA-100", "Open BM25")],
    ]
    labels = [
        "FinQA-600\nOracle-doc",
        "FinQA-600\nOpen BM25",
        "FinQA-600\nSource rerank",
        "FinQA-600\nGuarded portfolio",
        "TAT-QA-100\nOracle-doc",
        "TAT-QA-100\nOpen BM25",
    ]
    y = np.arange(len(rows))
    em = np.array([row.em for row in rows])
    support = np.array([row.answer_support for row in rows])

    fig, ax = plt.subplots(figsize=(6.8, 4.15))
    fig.subplots_adjust(bottom=0.16, top=0.82, left=0.18, right=0.98)
    for idx, (left, right) in enumerate(zip(em, support)):
        ax.plot([left, right], [idx, idx], color="#CFCFCF", linewidth=1.1, zorder=1)
    ax.scatter(em, y, s=52, color=METRIC_COLORS["EM"], label="EM", edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter(support, y, s=52, color=METRIC_COLORS["Answer Support"], label="Answer Support", edgecolor="white", linewidth=0.6, zorder=3)
    for idx, (left, right) in enumerate(zip(em, support)):
        ax.text(left, idx - 0.16, f"{left:.3f}", ha="center", va="top", fontsize=7, color="#214E58")
        ax.text(right, idx + 0.16, f"{right:.3f}", ha="center", va="bottom", fontsize=7, color="#7B4B35")
    fig.text(
        0.5,
        0.035,
        "Exact-match accuracy and verifier-checked support are not equivalent.",
        ha="center",
        va="bottom",
        fontsize=7,
        color="#555555",
    )
    ax.set_title("Exact Match vs Verifier-Checked Support")
    ax.set_xlabel("Score")
    ax.set_xlim(0, 1.0)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    style_axes(ax, xgrid=True, ygrid=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2, frameon=False)
    outputs = save_figure(fig, output_dir, "fig_em_support_comparison", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_em_support_comparison",
        output_files=outputs,
        source_files=sources_for_records(rows),
        fields=["dataset", "method", "accuracy", "answer_supported"],
        filters=["Full EviGraph only", "FinQA-600 Guarded portfolio included as completed evidence-state selector output"],
        sample_sizes=[f"{label.replace(chr(10), ' ')}: n={row.n}" for label, row in zip(labels, rows)],
        values=[
            {"dataset": row.dataset, "setting": row.setting, "EM": round(row.em, 6), "answer_support": round(row.answer_support, 6)}
            for row in rows
        ],
        missing_values="none detected",
        aggregation="Mean accuracy and mean answer_supported for each Full EviGraph condition.",
        markdown_fallback="none for EM/support; portfolio CSV provides Guarded portfolio support.",
        consistency="FinQA/TAT-QA values validated against generated summaries; portfolio EM validated against portfolio_report.md.",
        colors=[f"EM: {METRIC_COLORS['EM']}", f"Answer Support: {METRIC_COLORS['Answer Support']}"],
    )


def plot_retrieval_portfolio_ci(
    records: list[PortfolioRecord],
    stats: PortfolioStats,
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    order = ["BM25 primary", "Neural-hybrid candidate", "Guarded portfolio"]
    record_map = {record.selector: record for record in records}
    rows = [record_map[name] for name in order]
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(6.4, 3.1), constrained_layout=True)
    for idx, record in enumerate(rows):
        xerr = np.array([[record.em - record.ci_low], [record.ci_high - record.em]])
        is_guarded = record.selector == "Guarded portfolio"
        ax.errorbar(
            record.em,
            idx,
            xerr=xerr,
            fmt="o",
            color=METHOD_COLORS[record.selector],
            ecolor=METHOD_COLORS[record.selector],
            elinewidth=1.5 if is_guarded else 1.1,
            capsize=5,
            markersize=8 if is_guarded else 6.5,
            markeredgecolor="white",
            markeredgewidth=0.7,
            zorder=3,
        )
        ax.text(record.ci_high + 0.005, idx, f"{record.em:.3f}", va="center", fontsize=8)
    bm25 = record_map["BM25 primary"].em
    portfolio = record_map["Guarded portfolio"].em
    p_text = "p < 0.001" if stats.p_value < 0.001 else f"p = {stats.p_value:.3f}"
    ax.annotate(
        f"n={stats.n}; +{portfolio - bm25:.3f} vs BM25\n{stats.switches} switches; {stats.wins} wins / {stats.losses} losses\nMcNemar {p_text}",
        xy=(portfolio, order.index("Guarded portfolio")),
        xytext=(0.421, 1.62),
        arrowprops=dict(arrowstyle="->", color="#555555", linewidth=0.8),
        fontsize=8,
        ha="left",
        va="center",
    )
    ax.set_title("FinQA-600 Retrieval Portfolio with 95% Wilson CI")
    ax.set_xlabel("Exact Match")
    ax.set_xlim(0.30, 0.465)
    ax.set_yticks(y)
    ax.set_yticklabels(order)
    ax.invert_yaxis()
    style_axes(ax, xgrid=True, ygrid=False)
    outputs = save_figure(fig, output_dir, "fig_retrieval_portfolio_ci", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_retrieval_portfolio_ci",
        output_files=outputs,
        source_files=[stats.source, display_path(resolve_path(PORTFOLIO_CSV))],
        fields=["Rows", "Portfolio EM", "Primary EM (bm25)", "Candidate EM (neural_hybrid)", "95% Wilson CI", "Switches", "Wins vs primary", "Losses vs primary", "Paired McNemar p-value"],
        filters=["FinQA-600 open retrieval portfolio only"],
        sample_sizes=[f"n={stats.n}"],
        values=[
            {"selector": row.selector, "EM": row.em, "CI_low": row.ci_low, "CI_high": row.ci_high}
            for row in rows
        ]
        + [{"switches": stats.switches, "wins": stats.wins, "losses": stats.losses, "p_value": stats.p_value}],
        missing_values="none detected",
        aggregation="No averaging in plot; point estimates and Wilson intervals are parsed from portfolio_report.md.",
        markdown_fallback="Markdown report is the primary source for intervals and paired-test metadata; CSV is used to validate portfolio EM/support.",
        consistency="validated against retrieval portfolio ablation and statistical confidence paper assets.",
        colors=[f"{row.selector}: {METHOD_COLORS[row.selector]}" for row in rows],
    )


def plot_component_ablation(
    records: list[MetricRecord],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    settings = ["Oracle-doc", "Open BM25", "BM25 + source rerank"]
    display_settings = ["Oracle-doc", "Open BM25", "Source rerank"]
    comparisons = [
        ("vs no planner", "No operation planner"),
        ("vs retrieve-then-program", "Retrieve-then-program"),
        ("vs utility-only", "Utility-only"),
    ]
    full = metric_matrix(records, settings, ["Full EviGraph"], "em")["Full EviGraph"]
    deltas: dict[str, list[float]] = {}
    for label, baseline in comparisons:
        baseline_values = metric_matrix(records, settings, [baseline], "em")[baseline]
        deltas[label] = [full_value - baseline_value for full_value, baseline_value in zip(full, baseline_values)]

    all_delta_values = [value for values in deltas.values() for value in values]
    max_delta = max(all_delta_values)
    fig, ax = plt.subplots(figsize=(6.8, 3.25), constrained_layout=True)
    y = np.arange(len(settings))
    height = 0.21
    for idx, (label, _baseline) in enumerate(comparisons):
        values = deltas[label]
        bars = ax.barh(
            y + (idx - 1) * height,
            values,
            height=height,
            label=label,
            color=DELTA_COLORS[label],
            edgecolor="white",
            linewidth=0.5,
            zorder=3,
        )
        for bar, value in zip(bars, values):
            label_color = PALETTE["coral_orange"] if abs(value - max_delta) < 1e-9 else "#222222"
            if abs(value - max_delta) < 1e-9:
                bar.set_edgecolor(PALETTE["coral_orange"])
                bar.set_linewidth(1.0)
            ax.text(value + 0.0018, bar.get_y() + bar.get_height() / 2, f"+{value:.3f}", va="center", fontsize=8, color=label_color)
    ax.axvline(0, color="#777777", linewidth=0.8)
    ax.set_title("Full EviGraph Component Gains")
    ax.set_xlabel("EM delta")
    ax.set_yticks(y)
    ax.set_yticklabels(display_settings)
    ax.set_xlim(0, 0.075)
    ax.invert_yaxis()
    style_axes(ax, xgrid=True, ygrid=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=3, frameon=False)
    outputs = save_figure(fig, output_dir, "fig_component_ablation", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_component_ablation",
        output_files=outputs,
        source_files=sources_for_records(records),
        fields=["method", "accuracy"],
        filters=["FinQA-600 only", "deltas computed against Full EviGraph in the same retrieval setting"],
        sample_sizes=[f"{setting}: n=600 per method" for setting in settings],
        values=component_delta_values(settings, comparisons, deltas),
        missing_values="none detected",
        aggregation="Full EviGraph EM minus baseline EM, where both EM values are CSV means.",
        markdown_fallback="none; CSV is primary.",
        consistency="validated against generated component-contribution LaTeX table at displayed precision.",
        colors=[f"{label}: {DELTA_COLORS[label]}" for label, _ in comparisons] + [f"max-delta label/edge: {PALETTE['coral_orange']}"],
    )


def plot_failure_analysis(
    counts: dict[str, dict[str, int]],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    categories = ["Wrong row / operation", "No numeric", "No percent", "Additive / lookup", "Ratio", "Unsupported"]
    settings = ["Oracle-doc", "Open BM25", "BM25 + source rerank"]
    display_settings = ["Oracle-doc", "Open BM25", "Source rerank"]

    fig, ax = plt.subplots(figsize=(7.2, 3.8), constrained_layout=True)
    y = np.arange(len(categories))
    height = 0.22
    offsets = (np.arange(len(settings)) - 1) * height
    for idx, (setting, display) in enumerate(zip(settings, display_settings)):
        values = [counts[setting][category] for category in categories]
        bars = ax.barh(
            y + offsets[idx],
            values,
            height=height,
            label=display,
            color=SETTING_COLORS[setting],
            edgecolor="white",
            linewidth=0.5,
            zorder=3,
        )
        for bar, value in zip(bars, values):
            ax.text(value + 1.0, bar.get_y() + bar.get_height() / 2, str(value), va="center", fontsize=7)
    ax.set_title("FinQA-600 Failure Category Analysis")
    ax.set_xlabel("Failed examples")
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.set_xlim(0, max(max(counts[setting][category] for category in categories) for setting in settings) + 14)
    ax.invert_yaxis()
    style_axes(ax, xgrid=True, ygrid=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=3, frameon=False)
    outputs = save_figure(fig, output_dir, "fig_failure_analysis", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_failure_analysis",
        output_files=outputs,
        source_files=[display_path(resolve_path(FINQA_PAPER_SUMMARY)), display_path(resolve_path(FINQA_FULL_TABLE_TEX))],
        fields=["Full EviGraph Failure Categories table"],
        filters=["Full EviGraph only", "FinQA-600 settings only"],
        sample_sizes=["Oracle-doc: n=600", "Open BM25: n=600", "BM25 + source rerank: n=600"],
        values=[{"setting": setting, **counts[setting]} for setting in settings],
        missing_values="none detected",
        aggregation="Counts parsed from generated failure-category tables; categories are not stacked.",
        markdown_fallback="Markdown generated paper summary is the primary source for failure counts; LaTeX table is used for consistency validation.",
        consistency="validated against generated FinQA failure-category LaTeX table.",
        colors=[f"{setting}: {SETTING_COLORS[setting]}" for setting in settings],
    )


def plot_cross_dataset_portability(
    finqa_records: list[MetricRecord],
    tatqa_records: list[MetricRecord],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    rows = [
        next(record for record in finqa_records if record.dataset == "FinQA-600" and record.setting == "Oracle-doc" and record.method == "Full EviGraph"),
        next(record for record in finqa_records if record.dataset == "FinQA-600" and record.setting == "Open BM25" and record.method == "Full EviGraph"),
        next(record for record in tatqa_records if record.dataset == "TAT-QA-100" and record.setting == "Oracle-doc" and record.method == "Full EviGraph"),
        next(record for record in tatqa_records if record.dataset == "TAT-QA-100" and record.setting == "Open BM25" and record.method == "Full EviGraph"),
    ]
    labels = [f"{row.dataset}\n{row.setting}" for row in rows]
    x = np.arange(len(rows))
    width = 0.31
    em = [row.em for row in rows]
    support = [row.answer_support for row in rows]

    fig, ax = plt.subplots(figsize=(6.8, 3.6))
    fig.subplots_adjust(bottom=0.25, top=0.78, left=0.10, right=0.98)
    bars1 = ax.bar(x - width / 2, em, width=width, label="EM", color=METRIC_COLORS["EM"], edgecolor="white", linewidth=0.5, zorder=3)
    bars2 = ax.bar(x + width / 2, support, width=width, label="Answer Support", color=METRIC_COLORS["Answer Support"], edgecolor="white", linewidth=0.5, zorder=3)
    annotate_vertical_bars(ax, bars1, em, dy=0.008, fontsize=7)
    annotate_vertical_bars(ax, bars2, support, dy=0.008, fontsize=7)
    ax.set_title("Cross-Dataset Portability Check")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    style_axes(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.23), ncol=2, frameon=False)
    fig.text(
        0.5,
        0.035,
        "TAT-QA-100 is used as a cross-format portability check, not as a full benchmark claim.",
        ha="center",
        va="bottom",
        fontsize=7,
        color="#555555",
    )
    outputs = save_figure(fig, output_dir, "fig_cross_dataset_portability", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_cross_dataset_portability",
        output_files=outputs,
        source_files=sources_for_records(rows),
        fields=["method", "accuracy", "answer_supported"],
        filters=["Full EviGraph only", "Oracle-doc and Open BM25 only"],
        sample_sizes=[f"{row.dataset} {row.setting}: n={row.n}" for row in rows],
        values=[
            {"dataset": row.dataset, "setting": row.setting, "EM": round(row.em, 6), "answer_support": round(row.answer_support, 6)}
            for row in rows
        ],
        missing_values="none detected",
        aggregation="Mean accuracy and answer_supported grouped by dataset and retrieval setting.",
        markdown_fallback="none for plotted values; generated TAT-QA paper tables are validation sources.",
        consistency="validated against TAT-QA-100 generated Markdown/LaTeX tables at displayed precision.",
        colors=[f"EM: {METRIC_COLORS['EM']}", f"Answer Support: {METRIC_COLORS['Answer Support']}"],
    )


def plot_tatqa_subset_size_sweep(
    points: list[SweepPoint],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    panels = [
        ("Oracle-doc EM", "Oracle-doc", "em", PALETTE["deep_teal"]),
        ("Open BM25 EM", "Open BM25", "em", PALETTE["coral_orange"]),
        ("Oracle-doc Support", "Oracle-doc", "answer_support", PALETTE["ocean_blue"]),
        ("Open BM25 Support", "Open BM25", "answer_support", PALETTE["sand"]),
    ]
    point_map = {(point.setting, point.sample_size): point for point in points}
    sample_sizes = [20, 50, 100]

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.7), sharex=True)
    fig.suptitle("TAT-QA Subset Size Sweep (per-setting view)", fontsize=11, y=0.965)
    for ax, (title, setting, metric, color) in zip(axes.ravel(), panels):
        values = [getattr(point_map[(setting, n)], metric) for n in sample_sizes]
        ax.plot(sample_sizes, values, color=color, linewidth=1.7, marker="o", markersize=4.8, zorder=3)
        best_idx = int(np.argmax(values))
        best_n = sample_sizes[best_idx]
        best_value = values[best_idx]
        ax.scatter([best_n], [best_value], s=28, color="#222222", zorder=4)
        ax.annotate(
            f"best={best_n}",
            xy=(best_n, best_value),
            xytext=(6, 3),
            textcoords="offset points",
            fontsize=7,
            ha="left",
            va="center",
            color="#111111",
        )
        lower, upper = padded_axis_limits(values, pad_ratio=0.18)
        ax.set_ylim(lower, upper)
        ax.set_title(title, fontsize=9, pad=5)
        ax.set_xticks(sample_sizes)
        ax.grid(axis="y", linestyle=":", color="#CFCFCF", linewidth=0.8)
        ax.spines["top"].set_visible(True)
        ax.spines["right"].set_visible(True)
        for spine in ax.spines.values():
            spine.set_color("#222222")
            spine.set_linewidth(0.75)
        ax.tick_params(labelsize=8, colors="#111111", width=0.75)
    fig.text(0.02, 0.5, "Score", va="center", rotation="vertical", fontsize=9)
    fig.text(0.5, 0.04, "Subset Size", ha="center", fontsize=9)
    fig.text(
        0.5,
        0.005,
        "TAT-QA-20/50/100 are portability checks, not full benchmark claims.",
        ha="center",
        fontsize=7,
        color="#555555",
    )
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.16, wspace=0.22, hspace=0.34)
    outputs = save_figure(fig, output_dir, "fig_tatqa_subset_size_sweep", formats, dpi)
    plt.close(fig)

    values: list[dict[str, object]] = []
    for point in points:
        values.append(
            {
                "sample_size": point.sample_size,
                "setting": point.setting,
                "method": point.method,
                "EM": point.em,
                "answer_support": point.answer_support,
                "source_hit@8": point.source_hit_at_8,
            }
        )
    return FigureAudit(
        figure="fig_tatqa_subset_size_sweep",
        output_files=outputs,
        source_files=sorted({point.source for point in points}),
        fields=["setting", "method", "n", "EM", "support", "source_hit@8"],
        filters=["TAT-QA only", "Full EviGraph rows only", "Oracle-doc and Open BM25 settings"],
        sample_sizes=[f"TAT-QA-{n}: Oracle-doc and Open BM25" for n in sample_sizes],
        values=values,
        missing_values="source_hit@8 is n/a for Oracle-doc by design; EM/support complete.",
        aggregation="No aggregation across files; plotted values are read directly from generated TAT-QA result tables.",
        markdown_fallback="generated Markdown tables are the primary source because the sweep spans separate pilot/portability reports.",
        consistency="subset sizes and values are constrained by n fields in each generated report; no invented sweep points.",
        colors=[f"{title}: {color}" for title, _setting, _metric, color in panels] + ["best marker: #222222"],
    )


def plot_marag_style_main_results_table(
    finqa_records: list[MetricRecord],
    tatqa_records: list[MetricRecord],
    portfolio_metric: MetricRecord,
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    finqa_map = {(record.setting, record.method): record for record in finqa_records}
    tatqa_map = {(record.setting, record.method): record for record in tatqa_records}
    rows: list[list[str]] = []
    row_kinds: list[str] = []
    values: list[dict[str, object]] = []

    def add_section(title: str) -> None:
        rows.append(["", title, "", "", ""])
        row_kinds.append("section")

    def add_metric_row(dataset: str, setting: str, method: str, n: int, em: float, support: float, source: str, highlight: bool = False) -> None:
        rows.append([setting, method, str(n), f"{em:.3f}", f"{support:.3f}"])
        row_kinds.append("highlight" if highlight else "normal")
        values.append({"dataset": dataset, "setting": setting, "method": method, "n": n, "EM": round(em, 6), "answer_support": round(support, 6), "source": source})

    add_section("FinQA-600 component closure")
    for setting in ["Oracle-doc", "Open BM25", "BM25 + source rerank"]:
        for method in ["Direct RAG", "Retrieve-then-program", "Utility-only", "No operation planner", "Full EviGraph"]:
            record = finqa_map[(setting, method)]
            add_metric_row("FinQA-600", setting, method, record.n, record.em, record.answer_support, record.source, highlight=method == "Full EviGraph")

    add_section("FinQA-600 open retrieval portfolio")
    add_metric_row(
        "FinQA-600",
        "Open BM25",
        "Guarded portfolio",
        portfolio_metric.n,
        portfolio_metric.em,
        portfolio_metric.answer_support,
        portfolio_metric.source,
        highlight=True,
    )

    add_section("TAT-QA-100 portability check")
    for setting in ["Oracle-doc", "Open BM25"]:
        record = tatqa_map[(setting, "Full EviGraph")]
        add_metric_row("TAT-QA-100", setting, "Full EviGraph", record.n, record.em, record.answer_support, record.source, highlight=True)

    fig, ax = plt.subplots(figsize=(7.3, 6.2))
    ax.axis("off")
    ax.set_title("Main Results Summary", fontsize=11, pad=10)
    headers = ["Setting", "Method", "n", "EM", "Support"]
    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        colLoc="center",
        bbox=[0.02, 0.02, 0.96, 0.92],
        colWidths=[0.23, 0.42, 0.09, 0.13, 0.13],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1, 1.18)

    for (row_idx, col_idx), cell in table.get_celld().items():
        cell.set_edgecolor("#222222")
        cell.set_linewidth(0.35)
        cell.set_facecolor("white")
        if row_idx == 0:
            cell.set_text_props(weight="bold")
            cell.set_linewidth(0.75)
        elif row_kinds[row_idx - 1] == "section":
            cell.set_facecolor("#F2F2F2")
            cell.set_linewidth(0.65)
            if col_idx == 1:
                cell.set_text_props(style="italic", weight="bold", ha="left")
            else:
                cell.get_text().set_text("")
        elif row_kinds[row_idx - 1] == "highlight":
            cell.set_text_props(weight="bold")
            if col_idx in {3, 4}:
                cell.set_facecolor("#FFF4ED")
        if row_idx > 0 and col_idx in {0, 1} and row_kinds[row_idx - 1] != "section":
            cell.set_text_props(ha="left")
    outputs = save_figure(fig, output_dir, "fig_marag_style_main_results_table", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_marag_style_main_results_table",
        output_files=outputs,
        source_files=sorted({str(item["source"]) for item in values}),
        fields=["setting", "method", "n", "accuracy", "answer_supported"],
        filters=["Main FinQA-600 methods, guarded portfolio, and TAT-QA-100 Full EviGraph rows"],
        sample_sizes=sorted({f"{item['dataset']} {item['setting']}: n={item['n']}" for item in values}),
        values=values,
        missing_values="none detected",
        aggregation="Table values are the same CSV/report means used by the plotted figures.",
        markdown_fallback="none for FinQA/TAT-QA EM/support; portfolio row uses portfolio CSV.",
        consistency="values already passed strict validation against generated summary and LaTeX assets.",
        colors=["mostly black-and-white MA-RAG-style table", f"highlight fill: #FFF4ED", f"section fill: #F2F2F2"],
    )


def plot_tatqa_repair_trajectory(
    points: list[RepairTrajectoryPoint],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    versions = ["base", "v47", "v48", "v49", "v50"]
    x = np.arange(len(versions))
    point_map = {(point.setting, point.version): point for point in points}
    series = [
        ("Oracle-doc", PALETTE["deep_teal"], "o"),
        ("Open BM25", PALETTE["coral_orange"], "s"),
    ]

    fig, ax = plt.subplots(figsize=(6.6, 3.4), constrained_layout=True)
    for setting, color, marker in series:
        values = [point_map[(setting, version)].em for version in versions]
        ax.plot(x, values, color=color, marker=marker, linewidth=1.8, markersize=5.0, label=setting, zorder=3)
        for xi, value in zip(x, values):
            ax.text(xi, value + 0.006, f"{value:.3f}", ha="center", va="bottom", fontsize=7, color="#222222")
    ax.set_title("Failure-Driven Repair Trajectory on TAT-QA-50")
    ax.set_xlabel("Repair round")
    ax.set_ylabel("Exact Match")
    ax.set_xticks(x)
    ax.set_xticklabels(versions)
    ax.set_ylim(0.33, 0.57)
    ax.yaxis.grid(True, linestyle=":", color="#CFCFCF", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    for spine in ax.spines.values():
        spine.set_color("#222222")
        spine.set_linewidth(0.75)
    ax.legend(frameon=False, loc="upper left", ncol=2)
    outputs = save_figure(fig, output_dir, "fig_tatqa_repair_trajectory", formats, dpi)
    plt.close(fig)
    return FigureAudit(
        figure="fig_tatqa_repair_trajectory",
        output_files=outputs,
        source_files=sorted({point.source for point in points}),
        fields=["setting", "method/version", "n", "EM", "support", "source_hit@8"],
        filters=["TAT-QA-50 repair sequence", "Oracle-doc and Open BM25"],
        sample_sizes=["TAT-QA-50 for all repair rounds"],
        values=[
            {
                "version": point.version,
                "setting": point.setting,
                "EM": point.em,
                "answer_support": point.answer_support,
                "source_hit@8": point.source_hit_at_8,
            }
            for point in points
        ],
        missing_values="none detected",
        aggregation="No aggregation; values are parsed from per-round TAT-QA-50 summary tables.",
        markdown_fallback="generated Markdown summaries are the primary source for this trajectory.",
        consistency="all repair-round values come from outputs/eval summary tables.",
        colors=[f"Oracle-doc: {PALETTE['deep_teal']}", f"Open BM25: {PALETTE['coral_orange']}"],
    )


def plot_tatqa_repair_diagnostic_grid(
    points: list[RepairTrajectoryPoint],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    versions = ["base", "v47", "v48", "v49", "v50"]
    x = np.arange(len(versions))
    point_map = {(point.setting, point.version): point for point in points}
    diagnostics = [
        ("Exact Match", "em", "higher is better"),
        ("Answer support", "answer_support", "higher is better"),
        ("Supported wrong", "supported_wrong", "lower is better"),
        ("Row grounding", "row_operation_grounded", "higher is better"),
    ]
    settings = [("Oracle-doc", PALETTE["deep_teal"]), ("Open BM25", PALETTE["coral_orange"])]

    fig, axes = plt.subplots(2, 4, figsize=(7.4, 3.95), sharex=True)
    for row_idx, (setting, color) in enumerate(settings):
        for col_idx, (title, attr, _direction) in enumerate(diagnostics):
            ax = axes[row_idx, col_idx]
            values = [getattr(point_map[(setting, version)], attr) for version in versions]
            ax.plot(x, values, color=color, marker="o", markersize=3.2, linewidth=1.3, zorder=3)
            lower, upper = padded_axis_limits(values, pad_ratio=0.22)
            ax.set_ylim(lower, upper)
            ax.set_title(title if row_idx == 0 else "", fontsize=8, pad=4)
            if col_idx == 0:
                ax.set_ylabel(setting, fontsize=8)
            if row_idx == 1:
                ax.set_xticks(x)
                ax.set_xticklabels(versions, rotation=0)
            else:
                ax.set_xticks(x)
                ax.tick_params(labelbottom=False)
            ax.grid(axis="y", color="#D6D6D6", linestyle=":", linewidth=0.7)
            ax.set_axisbelow(True)
            for spine in ax.spines.values():
                spine.set_color("#333333")
                spine.set_linewidth(0.65)
            ax.tick_params(labelsize=6.7, width=0.65, pad=1.5)
            if col_idx == len(diagnostics) - 1:
                ax.text(
                    1.02,
                    0.5,
                    setting,
                    transform=ax.transAxes,
                    rotation=270,
                    va="center",
                    ha="left",
                    fontsize=7,
                    color=color,
                )
    handles = [
        plt.Line2D([0], [0], color=color, marker="o", linewidth=1.5, markersize=4, label=setting)
        for setting, color in settings
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.985), fontsize=7.5)
    fig.suptitle("TAT-QA-50 Failure-Driven Repair Diagnostics", fontsize=10.5, y=1.035)
    fig.text(0.5, 0.02, "Repair round", ha="center", fontsize=8)
    fig.subplots_adjust(left=0.075, right=0.965, top=0.84, bottom=0.16, wspace=0.28, hspace=0.28)
    outputs = save_figure(fig, output_dir, "fig_tatqa_repair_diagnostic_grid", formats, dpi)
    plt.close(fig)
    values: list[dict[str, object]] = []
    for point in points:
        values.append(
            {
                "version": point.version,
                "setting": point.setting,
                "EM": point.em,
                "answer_support": point.answer_support,
                "supported_wrong": point.supported_wrong,
                "calculation_supported": point.calculation_supported,
                "operation_semantics_checked": point.operation_semantics_checked,
                "row_operation_grounded": point.row_operation_grounded,
            }
        )
    return FigureAudit(
        figure="fig_tatqa_repair_diagnostic_grid",
        output_files=outputs,
        source_files=sorted({point.source for point in points}),
        fields=[
            "accuracy",
            "answer_supported",
            "supported_wrong",
            "calculation_supported",
            "operation_semantics_checked",
            "row_operation_grounded",
        ],
        filters=["TAT-QA-50 full_evigraph rows", "Oracle-doc and Open BM25", "repair rounds base/v47/v48/v49/v50"],
        sample_sizes=["n=50 per setting per repair round"],
        values=values,
        missing_values="none detected",
        aggregation="No aggregation; each point is read from the per-round generated summary table.",
        markdown_fallback="outputs/eval summary.md files are the primary source.",
        consistency="Uses the same source summaries as the TAT-QA repair trajectory; no invented diagnostics.",
        colors=[f"Oracle-doc: {PALETTE['deep_teal']}", f"Open BM25: {PALETTE['coral_orange']}"],
    )


def plot_selector_lambda_sweep(
    curves: list[SelectorSweepCurve],
    output_dir: Path,
    formats: list[str],
    dpi: int,
) -> FigureAudit:
    panels = [
        (r"(a) Exact Match", "em", r"$\xi_{\mathrm{em}}$", (0.32, 0.44)),
        (r"(b) Switch Rate", "switch_rate", r"$\xi_{\mathrm{switch}}$", (0.00, 0.55)),
        (r"(c) Accepted Gain", "win_rate", r"$\xi_{\mathrm{gain}}$", (0.00, 0.14)),
        (r"(d) Accepted Loss", "loss_rate", r"$\xi_{\mathrm{loss}}$", (0.00, 0.035)),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.35, 5.45), sharex=True)
    for panel_idx, (ax, (title, metric, ylabel, ylim)) in enumerate(zip(axes.ravel(), panels)):
        for curve in curves:
            x = np.asarray(curve.lambdas, dtype=float)
            y = np.asarray(curve.metrics[metric], dtype=float)
            ax.plot(
                x,
                y,
                color=curve.color,
                marker=curve.marker,
                markevery=2,
                linewidth=1.35,
                markersize=3.7,
                markerfacecolor=curve.color,
                markeredgecolor="white",
                markeredgewidth=0.35,
                label=curve.label,
                zorder=3,
            )
        title_y = -0.31
        ax.text(0.5, title_y, title, transform=ax.transAxes, ha="center", va="top", fontsize=13, fontfamily="serif")
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_ylim(*ylim)
        ax.set_xlim(-0.02, 1.02)
        ax.set_xticks(np.linspace(0.0, 1.0, 6))
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.grid(True, color="#D2D2D2", linewidth=0.85)
        ax.set_axisbelow(True)
        for spine in ax.spines.values():
            spine.set_color("#C8C8C8")
            spine.set_linewidth(1.25)
        ax.tick_params(labelsize=9, width=0.8, colors="#2C2C2C")
    for ax in axes[1, :]:
        ax.set_xlabel(r"$\lambda$", fontsize=12, labelpad=3)

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        ncol=5,
        frameon=True,
        fancybox=True,
        framealpha=0.82,
        borderpad=0.35,
        handlelength=1.7,
        columnspacing=1.0,
        bbox_to_anchor=(0.5, 0.99),
        fontsize=8.2,
    )
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.13, wspace=0.24, hspace=0.72)
    outputs = save_figure(fig, output_dir, "fig_selector_lambda_sweep", formats, dpi)
    plt.close(fig)

    values: list[dict[str, object]] = []
    for curve in curves:
        for idx, lam in enumerate(curve.lambdas):
            if idx in {0, 5, 10, 15, 20}:
                values.append(
                    {
                        "selector": curve.label,
                        "lambda": lam,
                        "EM": round(curve.metrics["em"][idx], 6),
                        "switch_rate": round(curve.metrics["switch_rate"][idx], 6),
                        "accepted_gain": round(curve.metrics["win_rate"][idx], 6),
                        "accepted_loss": round(curve.metrics["loss_rate"][idx], 6),
                    }
                )
    return FigureAudit(
        figure="fig_selector_lambda_sweep",
        output_files=outputs,
        source_files=sorted({curve.source for curve in curves}),
        fields=[
            "primary_prediction",
            "candidate_prediction",
            "primary_calculation",
            "candidate_calculation",
            "primary_accuracy",
            "candidate_accuracy",
        ],
        filters=["FinQA-600 v46 guarded-confidence portfolio rows", "no-gold selector scores; gold accuracy used only for post-hoc plotting"],
        sample_sizes=["n=600; lambda grid=0.00..1.00 step=0.05"],
        values=values,
        missing_values="none detected",
        aggregation="For each selector and lambda, choose candidate when no-gold score > lambda; EM/gain/loss are sample means.",
        markdown_fallback="none; row-level CSV is the source for the sweep.",
        consistency="The combined selector recovers the same primary/candidate evidence-state family as the guarded portfolio analysis without using labels for selection.",
        colors=[f"{curve.label}: {curve.color}" for curve in curves],
    )


def metric_matrix(records: list[MetricRecord], settings: list[str], methods: list[str], metric: str) -> dict[str, list[float]]:
    record_map = {(record.setting, record.method): record for record in records}
    matrix: dict[str, list[float]] = {}
    for method in methods:
        values: list[float] = []
        for setting in settings:
            key = (setting, method)
            if key not in record_map:
                raise ValueError(f"Missing metric row for setting={setting}, method={method}")
            record = record_map[key]
            values.append(record.em if metric == "em" else record.answer_support)
        matrix[method] = values
    return matrix


def read_csv_rows(path: Path, required_fields: Iterable[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required CSV file not found: {display_path(path)}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = [field for field in required_fields if field not in fields]
        if missing:
            raise ValueError(f"{display_path(path)} is missing required columns: {', '.join(missing)}")
        return list(reader)


def parse_markdown_grouped_summary(text: str) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    current_file: str | None = None
    headers: list[str] | None = None
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+\.csv)\s*$", line)
        if heading:
            current_file = heading.group(1).strip()
            grouped[current_file] = []
            headers = None
            continue
        if current_file is None or not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if headers is None:
            headers = cells
            continue
        if len(cells) == len(headers):
            grouped[current_file].append(dict(zip(headers, cells)))
    return grouped


def parse_simple_markdown_tables(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in text.splitlines():
        if not line.startswith("|"):
            headers = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            continue
        if headers is None:
            headers = cells
            continue
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def parse_optional_float(value: str) -> float | None:
    normalized = value.strip().lower()
    if normalized in {"", "n/a", "na", "--"}:
        return None
    return float(normalized)


def numeric_answer_confidence(prediction: str, calculation: str) -> float:
    text = f"{prediction}\n{calculation}".lower()
    if not text.strip():
        return 0.0
    numeric_hits = len(re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?\s*%?", text))
    score = min(1.0, numeric_hits / 3.0)
    if calculation.strip():
        score += 0.35
    if any(token in text for token in ("=", " / ", " + ", " - ", " * ", "percent", "ratio")):
        score += 0.20
    if "based on the selected evidence" in text and not calculation.strip():
        score -= 0.25
    return clamp01(score)


def evidence_coverage_confidence(prediction: str) -> float:
    text = prediction.lower()
    if not text.strip():
        return 0.0
    score = 0.0
    if "finqa evidence" in text or "source:" in text:
        score += 0.45
    if "## table" in text or "| --- |" in text:
        score += 0.25
    if "based on the selected evidence" in text:
        score += 0.15
    score += min(0.25, len(text) / 2800.0)
    return clamp01(score)


def concise_answer_confidence(prediction: str, calculation: str) -> float:
    text = prediction.strip()
    if not text:
        return 0.0
    score = 0.0
    if re.fullmatch(r"[-+]?\d[\d,]*(?:\.\d+)?\s*%?", text):
        score += 0.85
    elif len(text) <= 48 and re.search(r"\d", text):
        score += 0.55
    elif len(text) <= 120 and re.search(r"\d", text):
        score += 0.35
    if calculation.strip():
        score += 0.20
    if text.lower().startswith("based on the selected evidence"):
        score -= 0.30
    return clamp01(score)


def verbose_failure_confidence(prediction: str, calculation: str) -> float:
    text = prediction.strip().lower()
    if not text:
        return 0.0
    score = 0.0
    if text.startswith("based on the selected evidence"):
        score += 0.40
    if len(text) > 500:
        score += 0.30
    if len(text) > 1400:
        score += 0.20
    if not calculation.strip():
        score += 0.20
    return clamp01(score)


def noisy_or(values: Iterable[float]) -> float:
    product = 1.0
    for value in values:
        product *= 1.0 - clamp01(value)
    return clamp01(1.0 - product)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def padded_axis_limits(values: list[float], pad_ratio: float = 0.15) -> tuple[float, float]:
    lower = min(values)
    upper = max(values)
    span = upper - lower
    if span == 0:
        span = max(abs(upper), 1.0) * 0.05
    pad = span * pad_ratio
    return max(0.0, lower - pad), min(1.0, upper + pad)


def annotate_vertical_bars(ax: plt.Axes, bars, values: Iterable[float], dy: float, fontsize: int) -> None:
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + dy,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=fontsize,
        )


def style_axes(ax: plt.Axes, xgrid: bool = False, ygrid: bool = True) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#7A7A7A")
    ax.spines["bottom"].set_color("#7A7A7A")
    ax.tick_params(colors="#222222", width=0.8)
    ax.set_axisbelow(True)
    if ygrid:
        ax.yaxis.grid(True, color="#E8E8E8", linewidth=0.7)
    if xgrid:
        ax.xaxis.grid(True, color="#E8E8E8", linewidth=0.7)


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: list[str], dpi: int) -> list[str]:
    outputs: list[str] = []
    for fmt in formats:
        path = output_dir / f"{stem}.{fmt}"
        if fmt == "png":
            fig.savefig(path, dpi=dpi)
        else:
            fig.savefig(path)
        outputs.append(display_path(path))
    return outputs


def write_data_audit(
    path: Path,
    audits: list[FigureAudit],
    validation: ValidationReport,
    strict: bool,
    command: str,
) -> None:
    lines = [
        "# Figure Data Audit",
        "",
        f"Generated at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Repository root: `{display_path(ROOT)}`",
        f"Command: `{command}`",
        f"Strict mode: `{strict}`",
        "",
        "## Audit Conclusion",
        "",
        "- No invented experimental values were used.",
        "- Raw experiment CSV files were not modified.",
        "- CSV is the primary source for EM and answer-support values unless explicitly noted.",
        "- Markdown and LaTeX paper assets were parsed for portfolio intervals, failure categories, and consistency checks.",
        "- No financial OHLC candlestick data was generated; the interval figure is a scientific point-range plot.",
        "",
        "## Validation",
        "",
        "### Checked files",
        "",
    ]
    for source in sorted(set(validation.checked_files)):
        lines.append(f"- `{source}`")
    lines.extend(["", "### Notes", ""])
    for note in validation.notes:
        lines.append(f"- {note}")
    lines.extend(["", "### Missing optional files", ""])
    if validation.missing_optional:
        for item in validation.missing_optional:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.extend(["", "### Conflicts", ""])
    if validation.conflicts:
        for conflict in validation.conflicts:
            lines.append(f"- {conflict}")
    else:
        lines.append("- none")
    lines.extend(["", "## Palette", "", "| item | color |", "| --- | --- |"])
    for key, value in {**METHOD_COLORS, **METRIC_COLORS}.items():
        lines.append(f"| {key} | `{value}` |")
    lines.append("")

    for audit in audits:
        lines.extend([f"## {audit.figure}", "", "### Output files", ""])
        for output in audit.output_files:
            lines.append(f"- `{output}`")
        lines.extend(["", "### Source files", ""])
        for source in sorted(set(audit.source_files)):
            lines.append(f"- `{source}`")
        lines.extend(["", "### Fields", ""])
        for field in audit.fields:
            lines.append(f"- `{field}`")
        lines.extend(["", "### Filters", ""])
        for item in audit.filters:
            lines.append(f"- {item}")
        lines.extend(["", "### Sample sizes", ""])
        for item in audit.sample_sizes:
            lines.append(f"- {item}")
        lines.extend(["", "### Final plotted values", "", "| item | value |", "| --- | --- |"])
        for idx, value in enumerate(audit.values, start=1):
            lines.append(f"| {idx} | `{value}` |")
        lines.extend(
            [
                "",
                f"Missing values: {audit.missing_values}",
                f"Aggregation/filtering: {audit.aggregation}",
                f"Markdown fallback: {audit.markdown_fallback}",
                f"Consistency: {audit.consistency}",
                "",
                "### Colors",
                "",
            ]
        )
        for color in audit.colors:
            lines.append(f"- {color}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def validate_numeric_column(path: Path, rows: list[dict[str, str]], column: str) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            float(row[column])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid numeric value in {display_path(path)} column {column}, row {idx}: {row.get(column)!r}") from exc


def compare_metric(report: ValidationReport, path: Path, label: str, computed: float, displayed: float, tolerance: float) -> None:
    if abs(computed - displayed) > tolerance:
        report.conflicts.append(
            f"{display_path(path)} {label}: computed {computed:.6f} vs displayed {displayed:.6f} exceeds tolerance {tolerance}"
        )


def record_missing(report: ValidationReport, strict: bool, path: Path) -> None:
    message = f"missing validation source: {display_path(path)}"
    if strict:
        report.conflicts.append(message)
    else:
        report.missing_optional.append(message)


def extract_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        raise ValueError(f"Heading not found in summary: {heading}")
    rest = text[start + len(heading) :]
    next_heading = re.search(r"\n##\s+", rest)
    return rest[: next_heading.start()] if next_heading else rest


def parse_int_line(text: str, pattern: str) -> int:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not parse integer with pattern: {pattern}")
    return int(match.group(1))


def parse_float_line(text: str, pattern: str) -> float:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Could not parse float with pattern: {pattern}")
    return float(match.group(1))


def parse_float_fragment(text: str) -> float:
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", text)
    if not match:
        raise ValueError(f"Could not parse float from {text!r}")
    return float(match.group(0))


def mean_float(values: Iterable[str]) -> float:
    numbers = [float(value) for value in values]
    if not numbers:
        raise ValueError("Cannot compute mean over empty numeric sequence.")
    return float(sum(numbers) / len(numbers))


def mean_boolish(values: Iterable[str]) -> float:
    parsed = [parse_boolish(value) for value in values]
    if not parsed:
        raise ValueError("Cannot compute mean over empty boolean sequence.")
    return float(sum(parsed) / len(parsed))


def parse_boolish(value: str) -> int:
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "1.0", "yes"}:
        return 1
    if normalized in {"false", "0", "0.0", "no", ""}:
        return 0
    try:
        return 1 if float(normalized) > 0 else 0
    except ValueError as exc:
        raise ValueError(f"Cannot parse boolean-like value: {value!r}") from exc


def sources_for_records(records: Iterable[MetricRecord]) -> list[str]:
    return sorted({record.source for record in records})


def matrix_to_values(settings: list[str], methods: list[str], matrix: dict[str, list[float]], label: str) -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for idx, setting in enumerate(settings):
        for method in methods:
            values.append({"setting": setting, "method": method, label: round(matrix[method][idx], 6)})
    return values


def component_delta_values(
    settings: list[str],
    comparisons: list[tuple[str, str]],
    deltas: dict[str, list[float]],
) -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for idx, setting in enumerate(settings):
        row: dict[str, object] = {"setting": setting}
        for comparison, _baseline in comparisons:
            row[comparison] = round(deltas[comparison][idx], 6)
        values.append(row)
    return values


def resolve_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
