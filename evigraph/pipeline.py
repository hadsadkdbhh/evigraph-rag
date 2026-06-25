from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evigraph.methods import MethodRunner


class EviGraphPipeline:
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.runner = MethodRunner(config)

    def run(self, query: str, corpus_path: str | None = None, top_k: int = 8) -> dict[str, Any]:
        return self.runner.run(query, "full_evigraph", corpus_path, top_k)


@dataclass
class ClosureCheck:
    name: str
    ok: bool
    detail: str


class ExperimentClosureGate:
    """Audit the generated artifacts that make an experiment loop reproducible."""

    REQUIRED_CSV_COLUMNS = {
        "dataset",
        "experiment",
        "id",
        "method",
        "answer",
        "prediction",
        "accuracy",
        "answer_supported",
        "calculation_supported",
        "operation_semantics_checked",
        "row_operation_grounded",
    }

    def evaluate(
        self,
        manifest_path: str | Path,
        eval_dir: str | Path,
        paper_output_dir: str | Path,
        report_dir: str | Path,
    ) -> dict[str, Any]:
        manifest_file = Path(manifest_path)
        root = manifest_file.resolve().parents[1] if manifest_file.parent.name == "configs" else Path.cwd()
        self._display_root = root
        manifest = json.loads(self._resolve(root, manifest_file).read_text(encoding="utf-8"))
        eval_path = self._resolve(root, eval_dir)
        paper_path = self._resolve(root, paper_output_dir)
        report_path = self._resolve(root, report_dir)
        report_path.mkdir(parents=True, exist_ok=True)

        checks: list[ClosureCheck] = []
        metrics: list[dict[str, Any]] = []

        checks.append(self._file_check("manifest", self._resolve(root, manifest_file)))
        checks.append(self._file_check("summary", eval_path / "summary.md"))
        checks.append(self._file_check("experiment_card", eval_path / "experiment_card.md"))
        checks.append(self._file_check("paper_markdown", paper_path / "finqa_results_summary.md"))
        checks.append(self._file_check("paper_latex", paper_path / "finqa_results_tables.tex"))

        for dataset in manifest.get("datasets", []):
            dataset_name = dataset["name"]
            expected_records = self._dataset_records(root, dataset)
            checks.append(self._file_check(f"{dataset_name}_inspection_json", eval_path / f"{dataset_name}_inspection.json"))
            checks.append(self._file_check(f"{dataset_name}_inspection_md", eval_path / f"{dataset_name}_inspection.md"))
            checks.append(self._file_check(f"{dataset_name}_gate", eval_path / f"{dataset_name}_gate.md"))
            if dataset.get("raw_questions"):
                checks.append(self._file_check(f"{dataset_name}_converted_questions", self._resolve(root, dataset["questions"])))
            if dataset.get("build_index"):
                checks.append(self._file_check(f"{dataset_name}_index", self._resolve(root, dataset["index"])))

            for experiment in manifest.get("experiments", []):
                experiment_name = experiment["name"]
                csv_path = eval_path / f"{dataset_name}_{experiment_name}.csv"
                expected_rows = expected_records * self._experiment_multiplier(experiment)
                csv_check, csv_metrics = self._csv_check(
                    f"{dataset_name}_{experiment_name}_csv",
                    csv_path,
                    expected_rows=expected_rows,
                )
                checks.append(csv_check)
                metrics.extend(csv_metrics)
                if experiment.get("type", "batch") != "pareto":
                    checks.append(self._file_check(f"{dataset_name}_{experiment_name}_failures", csv_path.with_name(f"{csv_path.stem}_failures.md")))
                    checks.append(
                        self._file_check(
                            f"{dataset_name}_{experiment_name}_row_operation_diagnostics",
                            csv_path.with_name(f"{csv_path.stem}_row_operation_diagnostics.md"),
                        )
                    )

        result = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "manifest": str(self._resolve(root, manifest_file)),
            "ok": all(check.ok for check in checks),
            "git": self._git_state(root),
            "checks": [check.__dict__ for check in checks],
            "metrics": metrics,
            "artifacts": {
                "eval_dir": str(eval_path),
                "paper_output_dir": str(paper_path),
                "closure_report_json": str(report_path / "experiment_closure_report.json"),
                "closure_report_markdown": str(report_path / "experiment_closure_report.md"),
            },
        }
        (report_path / "experiment_closure_report.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (report_path / "experiment_closure_report.md").write_text(self.render_markdown(result), encoding="utf-8")
        return result

    def render_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Experiment Closure Report",
            "",
            f"- Created UTC: `{result['created_utc']}`",
            f"- Overall status: `{'PASS' if result['ok'] else 'FAIL'}`",
            f"- Git commit: `{result['git']['commit']}`",
            f"- Git dirty: `{result['git']['dirty']}`",
            "",
            "## Result Metrics",
            "",
            "| dataset | experiment | method | rows | accuracy | answer_support | calc_support | op_semantics | row_grounding |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for metric in result["metrics"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        metric["dataset"],
                        metric["experiment"],
                        metric["method"],
                        str(metric["rows"]),
                        self._fmt(metric["accuracy"]),
                        self._fmt(metric["answer_supported"]),
                        self._fmt(metric["calculation_supported"]),
                        self._fmt(metric["operation_semantics_checked"]),
                        self._fmt(metric["row_operation_grounded"]),
                    ]
                )
                + " |"
            )
        lines.extend(
            [
                "",
                "## Artifact Checks",
                "",
                "| check | status | detail |",
                "| --- | --- | --- |",
            ]
        )
        for check in result["checks"]:
            lines.append(f"| {check['name']} | {'PASS' if check['ok'] else 'FAIL'} | {check['detail']} |")
        lines.append("")
        return "\n".join(lines)

    def _csv_check(self, name: str, path: Path, expected_rows: int) -> tuple[ClosureCheck, list[dict[str, Any]]]:
        if not path.exists() or path.stat().st_size == 0:
            return ClosureCheck(name, False, f"missing or empty: {path}"), []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            columns = set(reader.fieldnames or [])
        missing = sorted(self.REQUIRED_CSV_COLUMNS - columns)
        if missing:
            return ClosureCheck(name, False, f"missing columns: {', '.join(missing)}"), []
        if len(rows) != expected_rows:
            return ClosureCheck(name, False, f"expected {expected_rows} rows, found {len(rows)}"), []
        return ClosureCheck(name, True, f"{len(rows)} rows: {self._display(path)}"), self._metrics(rows)

    def _metrics(self, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
        groups: dict[tuple[str, str, str], list[dict[str, str]]] = {}
        for row in rows:
            groups.setdefault((row["dataset"], row["experiment"], row["method"]), []).append(row)
        metrics: list[dict[str, Any]] = []
        for (dataset, experiment, method), group in sorted(groups.items()):
            metrics.append(
                {
                    "dataset": dataset,
                    "experiment": experiment,
                    "method": method,
                    "rows": len(group),
                    "accuracy": self._mean(group, "accuracy"),
                    "answer_supported": self._mean(group, "answer_supported"),
                    "calculation_supported": self._mean(group, "calculation_supported"),
                    "operation_semantics_checked": self._mean(group, "operation_semantics_checked"),
                    "row_operation_grounded": self._mean(group, "row_operation_grounded"),
                }
            )
        return metrics

    def _file_check(self, name: str, path: Path) -> ClosureCheck:
        if not path.exists():
            return ClosureCheck(name, False, f"missing: {path}")
        if path.is_file() and path.stat().st_size == 0:
            return ClosureCheck(name, False, f"empty: {path}")
        return ClosureCheck(name, True, self._display(path))

    def _dataset_records(self, root: Path, dataset: dict[str, Any]) -> int:
        source = dataset.get("raw_questions") or dataset.get("questions")
        if not source:
            return 0
        path = self._resolve(root, source)
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

    def _experiment_multiplier(self, experiment: dict[str, Any]) -> int:
        if experiment.get("type", "batch") == "pareto":
            return len(experiment.get("budgets", [1]))
        return len(experiment.get("methods", ["full_evigraph"]))

    def _mean(self, rows: list[dict[str, str]], column: str) -> float:
        values = [self._numeric(row[column]) for row in rows if row.get(column) not in (None, "")]
        return sum(values) / len(values) if values else 0.0

    def _numeric(self, value: str) -> float:
        lowered = value.strip().lower()
        if lowered == "true":
            return 1.0
        if lowered == "false":
            return 0.0
        return float(value)

    def _fmt(self, value: float) -> str:
        return f"{value:.3f}".rstrip("0").rstrip(".")

    def _resolve(self, root: Path, path: str | Path) -> Path:
        candidate = Path(path)
        return candidate if candidate.is_absolute() else root / candidate

    def _display(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self._display_root.resolve()))
        except ValueError:
            return str(path)

    def _git_state(self, root: Path) -> dict[str, Any]:
        return {
            "commit": self._git(root, ["rev-parse", "HEAD"]),
            "dirty": bool(self._git(root, ["status", "--porcelain"])),
        }

    def _git(self, root: Path, args: list[str]) -> str:
        try:
            result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            return "unknown"
        return result.stdout.strip()
