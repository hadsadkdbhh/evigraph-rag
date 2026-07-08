from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_BASELINES = (
    "direct_rag",
    "retrieve_then_program",
    "utility_only",
    "evigraph_wo_operation_planner",
)


class StatisticalAnalyzer:
    """Build lightweight confidence and paired-comparison reports for manifest CSVs."""

    def analyze(
        self,
        csv_paths: list[str | Path],
        target_method: str = "full_evigraph",
        baselines: tuple[str, ...] = DEFAULT_BASELINES,
    ) -> dict[str, Any]:
        reports = [
            self._analyze_csv(Path(path), target_method=target_method, baselines=baselines)
            for path in csv_paths
        ]
        return {"target_method": target_method, "baselines": list(baselines), "reports": reports}

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        lines = [
            "# Statistical Confidence Report",
            "",
            f"- Target method: `{analysis['target_method']}`",
            f"- Baselines: `{', '.join(analysis['baselines'])}`",
            "",
        ]
        for report in analysis["reports"]:
            lines.extend(
                [
                    f"## {self._display_path(report['csv_path'])}",
                    "",
                    "### Accuracy Intervals",
                    "",
                    "| method | n | correct | accuracy | 95% Wilson CI |",
                    "| --- | ---: | ---: | ---: | --- |",
                ]
            )
            for row in report["intervals"]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            row["method"],
                            str(row["n"]),
                            str(row["correct"]),
                            self._fmt(row["accuracy"]),
                            f"[{self._fmt(row['ci_low'])}, {self._fmt(row['ci_high'])}]",
                        ]
                    )
                    + " |"
                )
            lines.extend(
                [
                    "",
                    "### Paired Comparisons",
                    "",
                    "| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |",
                    "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for row in report["paired"]:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            row["target_method"],
                            row["baseline_method"],
                            self._fmt(row["delta_accuracy"]),
                            str(row["target_only"]),
                            str(row["baseline_only"]),
                            str(row["ties"]),
                            self._fmt(row["mcnemar_p"]),
                        ]
                    )
                    + " |"
                )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(
        self,
        csv_paths: list[str | Path],
        output_path: str | Path,
        target_method: str = "full_evigraph",
        baselines: tuple[str, ...] = DEFAULT_BASELINES,
    ) -> str:
        analysis = self.analyze(csv_paths, target_method=target_method, baselines=baselines)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        return str(output)

    def _analyze_csv(
        self,
        path: Path,
        target_method: str,
        baselines: tuple[str, ...],
    ) -> dict[str, Any]:
        rows = self._read_rows(path)
        by_method: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            by_method[row.get("method", "")].append(row)
        methods = [method for method in (*baselines, target_method) if method in by_method]
        intervals = [self._interval_row(method, by_method[method]) for method in methods]
        paired = [
            self._paired_row(target_method, baseline, by_method[target_method], by_method[baseline])
            for baseline in baselines
            if target_method in by_method and baseline in by_method
        ]
        return {"csv_path": str(path), "intervals": intervals, "paired": paired}

    def _interval_row(self, method: str, rows: list[dict[str, str]]) -> dict[str, Any]:
        n = len(rows)
        correct = sum(int(self._is_correct(row)) for row in rows)
        low, high = self._wilson_interval(correct, n)
        return {
            "method": method,
            "n": n,
            "correct": correct,
            "accuracy": correct / max(1, n),
            "ci_low": low,
            "ci_high": high,
        }

    def _paired_row(
        self,
        target_method: str,
        baseline_method: str,
        target_rows: list[dict[str, str]],
        baseline_rows: list[dict[str, str]],
    ) -> dict[str, Any]:
        target_by_id = {row.get("id", ""): row for row in target_rows}
        baseline_by_id = {row.get("id", ""): row for row in baseline_rows}
        shared_ids = sorted(set(target_by_id) & set(baseline_by_id))
        target_only = 0
        baseline_only = 0
        ties = 0
        for sample_id in shared_ids:
            target_correct = self._is_correct(target_by_id[sample_id])
            baseline_correct = self._is_correct(baseline_by_id[sample_id])
            if target_correct and not baseline_correct:
                target_only += 1
            elif baseline_correct and not target_correct:
                baseline_only += 1
            else:
                ties += 1
        target_acc = sum(int(self._is_correct(target_by_id[sample_id])) for sample_id in shared_ids) / max(1, len(shared_ids))
        baseline_acc = sum(int(self._is_correct(baseline_by_id[sample_id])) for sample_id in shared_ids) / max(1, len(shared_ids))
        return {
            "target_method": target_method,
            "baseline_method": baseline_method,
            "delta_accuracy": target_acc - baseline_acc,
            "target_only": target_only,
            "baseline_only": baseline_only,
            "ties": ties,
            "mcnemar_p": self._mcnemar_exact_p(target_only, baseline_only),
        }

    def _wilson_interval(self, correct: int, n: int, z: float = 1.96) -> tuple[float, float]:
        if n <= 0:
            return 0.0, 0.0
        phat = correct / n
        denom = 1 + z * z / n
        center = (phat + z * z / (2 * n)) / denom
        margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
        return max(0.0, center - margin), min(1.0, center + margin)

    def _mcnemar_exact_p(self, target_only: int, baseline_only: int) -> float:
        discordant = target_only + baseline_only
        if discordant == 0:
            return 1.0
        smaller = min(target_only, baseline_only)
        tail = sum(math.comb(discordant, k) for k in range(smaller + 1)) * (0.5**discordant)
        return min(1.0, 2 * tail)

    def _is_correct(self, row: dict[str, str]) -> bool:
        try:
            return float(row.get("accuracy", "0")) >= 1.0
        except ValueError:
            return False

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _display_path(self, path_text: str) -> str:
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    def _fmt(self, value: float) -> str:
        return f"{value:.3f}"
