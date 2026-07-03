from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from evigraph.failure_analysis import FailureAnalyzer
from evigraph.row_operation_diagnostics import DIAGNOSTIC_LABELS, RowOperationDiagnosticAnalyzer


@dataclass(frozen=True)
class ResultSpec:
    label: str
    csv_name: str
    methods: tuple[str, ...]


DEFAULT_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_subset_oracle_doc_ablation.csv",
        ("topk", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_subset_open_bm25_ablation.csv",
        ("topk", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open hybrid",
        "finqa_subset_open_hybrid_ablation.csv",
        ("topk", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_subset_source_rerank_ablation.csv",
        ("topk", "full_context", "utility_only", "full_evigraph"),
    ),
)

FINQA_300_LOCAL_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_300_subset_oracle_doc_full_local_planner.csv",
        ("full_evigraph",),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_300_subset_open_bm25_full_local_planner.csv",
        ("full_evigraph",),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_300_subset_source_rerank_full_local_planner.csv",
        ("full_evigraph",),
    ),
)

FINQA_300_LOCAL_ABLATION_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_300_subset_oracle_doc_ablation.csv",
        (
            "direct_rag",
            "topk",
            "retrieve_then_program",
            "full_context",
            "utility_only",
            "evigraph_wo_risk",
            "evigraph_wo_operation_planner",
            "evigraph_wo_verifier_grounded_rejection",
            "evigraph_wo_verifier",
            "evigraph_wo_support",
            "full_evigraph",
        ),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_300_subset_open_bm25_ablation.csv",
        (
            "direct_rag",
            "topk",
            "retrieve_then_program",
            "full_context",
            "utility_only",
            "evigraph_wo_risk",
            "evigraph_wo_operation_planner",
            "evigraph_wo_verifier_grounded_rejection",
            "evigraph_wo_verifier",
            "evigraph_wo_support",
            "full_evigraph",
        ),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_300_subset_source_rerank_ablation.csv",
        (
            "direct_rag",
            "topk",
            "retrieve_then_program",
            "full_context",
            "utility_only",
            "evigraph_wo_risk",
            "evigraph_wo_operation_planner",
            "evigraph_wo_verifier_grounded_rejection",
            "evigraph_wo_verifier",
            "evigraph_wo_support",
            "full_evigraph",
        ),
    ),
)

FINQA_300_LOCAL_RETRIEVAL_BASELINE_RESULT_SPECS = (
    ResultSpec(
        "Open BM25",
        "finqa_300_subset_open_bm25_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open dense",
        "finqa_300_subset_open_dense_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open hybrid",
        "finqa_300_subset_open_hybrid_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
)

FINQA_300_LOCAL_STRONG_RETRIEVAL_BASELINE_RESULT_SPECS = (
    ResultSpec(
        "Open BM25",
        "finqa_300_subset_open_bm25_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open TF-IDF",
        "finqa_300_subset_open_tfidf_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
    ResultSpec(
        "Open hybrid",
        "finqa_300_subset_open_hybrid_baseline.csv",
        ("direct_rag", "topk", "retrieve_then_program", "full_context", "utility_only", "full_evigraph"),
    ),
)

FINQA_300_LLM_DIRECT_RAG_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_300_subset_oracle_doc_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_300_subset_open_bm25_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_300_subset_source_rerank_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
)

FINQA_600_LOCAL_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_600_subset_oracle_doc_full_local_planner.csv",
        ("full_evigraph",),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_600_subset_open_bm25_full_local_planner.csv",
        ("full_evigraph",),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_600_subset_source_rerank_full_local_planner.csv",
        ("full_evigraph",),
    ),
)

FINQA_600_LLM_DIRECT_RAG_RESULT_SPECS = (
    ResultSpec(
        "Oracle-doc",
        "finqa_600_subset_oracle_doc_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
    ResultSpec(
        "Open BM25",
        "finqa_600_subset_open_bm25_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
    ResultSpec(
        "BM25 + source rerank",
        "finqa_600_subset_source_rerank_llm_direct_rag.csv",
        ("llm_direct_rag",),
    ),
)

RESULT_SPEC_PRESETS = {
    "finqa": DEFAULT_RESULT_SPECS,
    "finqa_300_local": FINQA_300_LOCAL_RESULT_SPECS,
    "finqa_300_local_ablation": FINQA_300_LOCAL_ABLATION_RESULT_SPECS,
    "finqa_300_local_retrieval_baselines": FINQA_300_LOCAL_RETRIEVAL_BASELINE_RESULT_SPECS,
    "finqa_300_local_strong_retrieval_baselines": FINQA_300_LOCAL_STRONG_RETRIEVAL_BASELINE_RESULT_SPECS,
    "finqa_300_llm_direct_rag": FINQA_300_LLM_DIRECT_RAG_RESULT_SPECS,
    "finqa_600_local": FINQA_600_LOCAL_RESULT_SPECS,
    "finqa_600_llm_direct_rag": FINQA_600_LLM_DIRECT_RAG_RESULT_SPECS,
}


class PaperAssetBuilder:
    """Build paper-ready result snippets from manifest CSV outputs."""

    def build(
        self,
        eval_dir: str | Path,
        output_dir: str | Path,
        preset: str = "finqa",
    ) -> dict[str, str]:
        eval_path = Path(eval_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        specs = self._result_specs(preset)

        result_rows = self._result_rows(eval_path, specs)
        contribution_rows = self._contribution_rows(result_rows)
        failure_rows = self._failure_rows(eval_path, specs)
        diagnostic_rows = self._diagnostic_rows(eval_path, specs)
        paths = {
            "latex": str(output_path / "finqa_results_tables.tex"),
            "markdown": str(output_path / "finqa_results_summary.md"),
        }
        Path(paths["latex"]).write_text(
            self.render_latex(result_rows, contribution_rows, failure_rows, diagnostic_rows),
            encoding="utf-8",
        )
        Path(paths["markdown"]).write_text(
            self.render_markdown(
                result_rows,
                contribution_rows,
                failure_rows,
                diagnostic_rows,
                source_label=self._display_path(eval_path),
            ),
            encoding="utf-8",
        )
        return paths

    def render_latex(
        self,
        result_rows: list[dict[str, Any]],
        contribution_rows: list[dict[str, Any]],
        failure_rows: list[dict[str, Any]],
        diagnostic_rows: list[dict[str, Any]],
    ) -> str:
        lines = [
            "% Auto-generated by scripts/build_paper_assets.py.",
            "% Re-run after scripts/run_manifest.py --manifest configs/experiments.finqa.json.",
            "\\begin{table}[t]",
            "\\centering",
            "\\small",
            "\\begin{tabular}{llrrrrrr}",
            "\\toprule",
            "Setting & Method & EM & Ans. & Calc. & OpSem & Row & Tokens \\\\",
            "\\midrule",
        ]
        for row in result_rows:
            lines.append(
                " & ".join(
                    [
                        self._latex_escape(row["setting"]),
                        self._method_label(row["method"]),
                        self._fmt(row["accuracy"]),
                        self._fmt(row["answer_supported"]),
                        self._fmt(row["calculation_supported"]),
                        self._fmt(row["operation_semantics_checked"]),
                        self._fmt(row["row_operation_grounded"]),
                        self._fmt(row["input_tokens"]),
                    ]
                )
                + " \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{FinQA diagnostic results. EM is numeric exact match. Ans., Calc., OpSem, and Row are verifier diagnostics for answer support, calculation-result support, operation-semantics checking, and row grounding. Source rerank uses the provided source document and is an analysis setting rather than a deployable open-retrieval claim.}",
                "\\label{tab:finqa-diagnostic-results}",
                "\\end{table}",
                "",
                "\\begin{table}[t]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{lrrrrrrrr}",
                "\\toprule",
                "Setting & Planner $\\Delta$EM & Reject $\\Delta$EM & Verifier $\\Delta$EM & Support $\\Delta$EM & Risk $\\Delta$EM & Graph vs. Top-k & Graph vs. Utility & Ans. \\\\",
                "\\midrule",
            ]
        )
        for row in contribution_rows:
            lines.append(
                " & ".join(
                    [
                        self._latex_escape(row["setting"]),
                        self._signed_fmt(row["planner_delta_em"]),
                        self._signed_fmt(row["verifier_rejection_delta_em"]),
                        self._signed_fmt(row["verifier_delta_em"]),
                        self._signed_fmt(row["support_delta_em"]),
                        self._signed_fmt(row["risk_delta_em"]),
                        self._signed_fmt(row["graph_vs_topk_em"]),
                        self._signed_fmt(row["graph_vs_utility_em"]),
                        self._fmt(row["verifier_answer_supported"]),
                    ]
                )
                + " \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{Component contribution diagnostics. Component deltas compare full EviGraph with the corresponding ablation. Reject $\\Delta$EM isolates verifier-grounded answer rejection while preserving verifier diagnostics. Graph deltas compare full EviGraph with retrieval-order Top-k and utility-only selection. Ans. is the full model's answer-support rate.}",
                "\\label{tab:finqa-component-contributions}",
                "\\end{table}",
                "",
                "\\begin{table}[t]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{lrrrrrr}",
                "\\toprule",
                "Setting & Wrong row/op & No numeric & No percent & Add./lookup & Ratio & Unsupported \\\\",
                "\\midrule",
            ]
        )
        for row in failure_rows:
            lines.append(
                " & ".join(
                    [
                        self._latex_escape(row["setting"]),
                        str(row["wrong_numeric_operation_or_row"]),
                        str(row["no_numeric_answer_other"]),
                        str(row["no_numeric_answer_percent"]),
                        str(row["no_numeric_answer_additive_or_lookup"]),
                        str(row["no_numeric_answer_ratio"]),
                        str(row["unsupported_textual_prediction"]),
                    ]
                )
                + " \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{Failure categories for full EviGraph on the FinQA diagnostic subset. The categories are generated directly from the manifest CSVs and should be used to drive the next engineering iteration.}",
                "\\label{tab:finqa-failure-categories}",
                "\\end{table}",
                "",
                "\\begin{table}[t]",
                "\\centering",
                "\\small",
                "\\begin{tabular}{lrrrrrr}",
                "\\toprule",
                "Setting & Num. & Den. & Year/period & Row label & Op. type & Ambig. \\\\",
                "\\midrule",
            ]
        )
        for row in diagnostic_rows:
            lines.append(
                " & ".join(
                    [
                        self._latex_escape(row["setting"]),
                        str(row["wrong_numerator"]),
                        str(row["wrong_denominator"]),
                        str(row["wrong_year_or_period"]),
                        str(row["wrong_row_label"]),
                        str(row["wrong_operation_type"]),
                        str(row["ambiguous_supported_wrong_number"]),
                    ]
                )
                + " \\\\"
            )
        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\caption{Row/operation diagnostics for wrong numeric full EviGraph answers. Counts are multi-label: one failed example can expose more than one diagnostic signal.}",
                "\\label{tab:finqa-row-operation-diagnostics}",
                "\\end{table}",
                "",
            ]
        )
        return "\n".join(lines)

    def render_markdown(
        self,
        result_rows: list[dict[str, Any]],
        contribution_rows: list[dict[str, Any]],
        failure_rows: list[dict[str, Any]],
        diagnostic_rows: list[dict[str, Any]],
        source_label: str = "outputs/eval/finqa",
    ) -> str:
        lines = [
            "# FinQA Paper Assets",
            "",
            f"Generated from `{source_label}` after the latest manifest run.",
            "",
            "## Main Diagnostic Table",
            "",
            "| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in result_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["setting"],
                        self._plain_method_label(row["method"]),
                        self._fmt(row["accuracy"]),
                        self._fmt(row["answer_supported"]),
                        self._fmt(row["calculation_supported"]),
                        self._fmt(row["operation_semantics_checked"]),
                        self._fmt(row["row_operation_grounded"]),
                        self._fmt(row["input_tokens"]),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "## Component Contribution Diagnostics",
                "",
                "| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in contribution_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["setting"],
                        self._signed_fmt(row["planner_delta_em"]),
                        self._signed_fmt(row["verifier_rejection_delta_em"]),
                        self._signed_fmt(row["verifier_delta_em"]),
                        self._signed_fmt(row["support_delta_em"]),
                        self._signed_fmt(row["risk_delta_em"]),
                        self._signed_fmt(row["graph_vs_topk_em"]),
                        self._signed_fmt(row["graph_vs_utility_em"]),
                        self._fmt(row["verifier_answer_supported"]),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "## Full EviGraph Failure Categories",
                "",
                "| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in failure_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["setting"],
                        str(row["wrong_numeric_operation_or_row"]),
                        str(row["no_numeric_answer_other"]),
                        str(row["no_numeric_answer_percent"]),
                        str(row["no_numeric_answer_additive_or_lookup"]),
                        str(row["no_numeric_answer_ratio"]),
                        str(row["unsupported_textual_prediction"]),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "## Row/Operation Diagnostics",
                "",
                "| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in diagnostic_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["setting"],
                        str(row["wrong_numerator"]),
                        str(row["wrong_denominator"]),
                        str(row["wrong_year_or_period"]),
                        str(row["wrong_row_label"]),
                        str(row["wrong_operation_type"]),
                        str(row["ambiguous_supported_wrong_number"]),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "## Paper-Safe Claims",
                "",
                "- Treat these as diagnostic smoke-subset results, not final benchmark claims.",
                "- Report open retrieval settings separately from oracle-doc and source-rerank settings.",
                "- Use the failure-category table to justify the next row/operation-selection iteration.",
                "",
            ]
        )
        return "\n".join(lines)

    def _result_specs(self, preset: str) -> tuple[ResultSpec, ...]:
        try:
            return RESULT_SPEC_PRESETS[preset]
        except KeyError as exc:
            allowed = ", ".join(sorted(RESULT_SPEC_PRESETS))
            raise ValueError(f"Unknown paper asset preset {preset!r}. Expected one of: {allowed}") from exc

    def _result_rows(self, eval_dir: Path, specs: tuple[ResultSpec, ...]) -> list[dict[str, Any]]:
        rows = []
        for spec in specs:
            csv_path = self._spec_csv_path(eval_dir, spec)
            grouped = self._group_by_method(self._read_csv(csv_path))
            for method in spec.methods:
                method_rows = grouped.get(method, [])
                if not method_rows:
                    continue
                rows.append(
                    {
                        "setting": spec.label,
                        "method": method,
                        "accuracy": self._mean(method_rows, "accuracy"),
                        "answer_supported": self._mean(method_rows, "answer_supported"),
                        "calculation_supported": self._mean(method_rows, "calculation_supported"),
                        "operation_semantics_checked": self._mean(method_rows, "operation_semantics_checked"),
                        "row_operation_grounded": self._mean(method_rows, "row_operation_grounded"),
                        "input_tokens": self._mean(method_rows, "input_tokens"),
                    }
                )
        return rows

    def _contribution_rows(self, result_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        by_setting_method = {(row["setting"], row["method"]): row for row in result_rows}
        settings = []
        seen = set()
        for row in result_rows:
            if row["setting"] not in seen:
                settings.append(row["setting"])
                seen.add(row["setting"])

        rows = []
        for setting in settings:
            full = by_setting_method.get((setting, "full_evigraph"))
            if not full:
                continue
            no_planner = by_setting_method.get((setting, "evigraph_wo_operation_planner"))
            no_verifier_rejection = by_setting_method.get((setting, "evigraph_wo_verifier_grounded_rejection"))
            no_verifier = by_setting_method.get((setting, "evigraph_wo_verifier"))
            no_support = by_setting_method.get((setting, "evigraph_wo_support"))
            no_risk = by_setting_method.get((setting, "evigraph_wo_risk"))
            topk = by_setting_method.get((setting, "topk"))
            utility = by_setting_method.get((setting, "utility_only"))
            rows.append(
                {
                    "setting": setting,
                    "planner_delta_em": self._delta(full, no_planner, "accuracy"),
                    "verifier_rejection_delta_em": self._delta(full, no_verifier_rejection, "accuracy"),
                    "verifier_delta_em": self._delta(full, no_verifier, "accuracy"),
                    "support_delta_em": self._delta(full, no_support, "accuracy"),
                    "risk_delta_em": self._delta(full, no_risk, "accuracy"),
                    "graph_vs_topk_em": self._delta(full, topk, "accuracy"),
                    "graph_vs_utility_em": self._delta(full, utility, "accuracy"),
                    "verifier_answer_supported": float(full.get("answer_supported", 0.0)),
                }
            )
        return rows

    def _failure_rows(self, eval_dir: Path, specs: tuple[ResultSpec, ...]) -> list[dict[str, Any]]:
        rows = []
        analyzer = FailureAnalyzer()
        for spec in specs:
            analysis = analyzer.analyze(self._spec_csv_path(eval_dir, spec), method=self._diagnostic_method(spec))
            categories = analysis["categories"]
            rows.append(
                {
                    "setting": spec.label,
                    "wrong_numeric_operation_or_row": categories.get("wrong_numeric_operation_or_row", 0),
                    "no_numeric_answer_other": categories.get("no_numeric_answer_other", 0),
                    "no_numeric_answer_percent": categories.get("no_numeric_answer_percent", 0),
                    "no_numeric_answer_additive_or_lookup": categories.get("no_numeric_answer_additive_or_lookup", 0),
                    "no_numeric_answer_ratio": categories.get("no_numeric_answer_ratio", 0),
                    "unsupported_textual_prediction": categories.get("unsupported_textual_prediction", 0),
                }
            )
        return rows

    def _diagnostic_rows(self, eval_dir: Path, specs: tuple[ResultSpec, ...]) -> list[dict[str, Any]]:
        rows = []
        analyzer = RowOperationDiagnosticAnalyzer()
        for spec in specs:
            analysis = analyzer.analyze(self._spec_csv_path(eval_dir, spec), method=self._diagnostic_method(spec))
            label_counts = analysis["label_counts"]
            row = {"setting": spec.label}
            for label in DIAGNOSTIC_LABELS:
                row[label] = label_counts.get(label, 0)
            rows.append(row)
        return rows

    def _spec_csv_path(self, eval_dir: Path, spec: ResultSpec) -> Path:
        exact_path = eval_dir / spec.csv_name
        if exact_path.exists():
            return exact_path
        suffix = spec.csv_name.removeprefix("finqa_subset_")
        matches = sorted(eval_dir.glob(f"*_{suffix}"))
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise FileNotFoundError(f"Required experiment CSV not found: {exact_path}")
        raise ValueError(f"Ambiguous experiment CSVs for {spec.csv_name}: {matches}")

    def _diagnostic_method(self, spec: ResultSpec) -> str:
        return "full_evigraph" if "full_evigraph" in spec.methods else spec.methods[0]

    def _read_csv(self, path: Path) -> list[dict[str, str]]:
        if not path.exists():
            raise FileNotFoundError(f"Required experiment CSV not found: {path}")
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _group_by_method(self, rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row.get("method", ""), []).append(row)
        return grouped

    def _mean(self, rows: list[dict[str, str]], metric: str) -> float:
        return mean(self._to_float(row.get(metric)) for row in rows)

    def _to_float(self, value: Any) -> float:
        if value in (None, ""):
            return 0.0
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            return float(value.lower() == "true")
        return float(value)

    def _fmt(self, value: float) -> str:
        return f"{value:.2f}"

    def _signed_fmt(self, value: float) -> str:
        return f"{value:+.2f}"

    def _delta(self, row: dict[str, Any], baseline: dict[str, Any] | None, metric: str) -> float:
        if baseline is None:
            return 0.0
        return float(row.get(metric, 0.0)) - float(baseline.get(metric, 0.0))

    def _method_label(self, method: str) -> str:
        labels = {
            "llm_direct_rag": "LLM Direct RAG",
            "direct_rag": "Direct RAG",
            "topk": "Top-k Program",
            "retrieve_then_program": "Retrieve-then-program",
            "full_context": "Full context",
            "utility_only": "Utility-only",
            "evigraph_wo_risk": "No risk",
            "evigraph_wo_operation_planner": "No planner",
            "evigraph_wo_verifier_grounded_rejection": "No verifier rejection",
            "evigraph_wo_verifier": "No verifier",
            "evigraph_wo_support": "No support graph",
            "full_evigraph": "Full EviGraph",
        }
        return labels.get(method, self._latex_escape(method))

    def _plain_method_label(self, method: str) -> str:
        return self._method_label(method).replace("\\_", "_").replace("\\&", "&")

    def _latex_escape(self, text: str) -> str:
        return text.replace("&", "\\&").replace("_", "\\_")

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)
