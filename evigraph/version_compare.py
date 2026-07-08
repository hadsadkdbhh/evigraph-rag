from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RETRIEVAL_MODES = ("oracle_doc", "open_bm25", "source_rerank")


@dataclass(frozen=True)
class ComparisonPair:
    mode: str
    baseline_csv: Path
    target_csv: Path


class EvalVersionComparator:
    """Compare two manifest output directories over matched retrieval-mode CSVs."""

    def compare_dirs(
        self,
        baseline_dir: str | Path,
        target_dir: str | Path,
        baseline_label: str = "baseline",
        target_label: str = "target",
    ) -> dict[str, Any]:
        baseline = Path(baseline_dir)
        target = Path(target_dir)
        pairs = self._matched_pairs(baseline, target)
        rows = [
            self._compare_pair(pair, baseline_label=baseline_label, target_label=target_label)
            for pair in pairs
        ]
        return {
            "baseline_dir": str(baseline),
            "target_dir": str(target),
            "baseline_label": baseline_label,
            "target_label": target_label,
            "rows": rows,
        }

    def render_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# Eval Version Comparison",
            "",
            f"- Baseline: `{report['baseline_label']}` (`{report['baseline_dir']}`)",
            f"- Target: `{report['target_label']}` (`{report['target_dir']}`)",
            "",
            "| retrieval mode | n | baseline EM | target EM | delta EM | target-only | baseline-only | ties |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in report["rows"]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        row["mode"],
                        str(row["n"]),
                        self._fmt(row["baseline_accuracy"]),
                        self._fmt(row["target_accuracy"]),
                        self._fmt(row["delta_accuracy"]),
                        str(row["target_only"]),
                        str(row["baseline_only"]),
                        str(row["ties"]),
                    ]
                )
                + " |"
            )
        lines.extend(["", "## Target-Only Wins", ""])
        for row in report["rows"]:
            lines.append(f"### {row['mode']}")
            wins = row["target_only_examples"]
            if not wins:
                lines.append("- None")
            for example in wins[:10]:
                lines.append(
                    f"- `{example['id']}`: gold `{example['answer']}`, "
                    f"baseline `{example['baseline_prediction']}`, target `{example['target_prediction']}`"
                )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(
        self,
        baseline_dir: str | Path,
        target_dir: str | Path,
        output_path: str | Path,
        baseline_label: str = "baseline",
        target_label: str = "target",
    ) -> str:
        report = self.compare_dirs(
            baseline_dir,
            target_dir,
            baseline_label=baseline_label,
            target_label=target_label,
        )
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(report), encoding="utf-8")
        return str(output)

    def _matched_pairs(self, baseline_dir: Path, target_dir: Path) -> list[ComparisonPair]:
        baseline_by_mode = self._csvs_by_mode(baseline_dir)
        target_by_mode = self._csvs_by_mode(target_dir)
        pairs = []
        for mode in RETRIEVAL_MODES:
            if mode not in baseline_by_mode or mode not in target_by_mode:
                continue
            pairs.append(
                ComparisonPair(
                    mode=mode,
                    baseline_csv=baseline_by_mode[mode],
                    target_csv=target_by_mode[mode],
                )
            )
        return pairs

    def _csvs_by_mode(self, directory: Path) -> dict[str, Path]:
        results: dict[str, Path] = {}
        if not directory.exists():
            return results
        for csv_path in sorted(directory.glob("*.csv")):
            if csv_path.stat().st_size <= 0:
                continue
            name = csv_path.name.lower()
            for mode in RETRIEVAL_MODES:
                if mode in name:
                    results.setdefault(mode, csv_path)
        return results

    def _compare_pair(
        self,
        pair: ComparisonPair,
        baseline_label: str,
        target_label: str,
    ) -> dict[str, Any]:
        baseline_rows = self._read_by_id(pair.baseline_csv)
        target_rows = self._read_by_id(pair.target_csv)
        shared_ids = sorted(set(baseline_rows) & set(target_rows))
        target_only = []
        baseline_only = []
        ties = 0
        for sample_id in shared_ids:
            baseline = baseline_rows[sample_id]
            target = target_rows[sample_id]
            baseline_correct = self._is_correct(baseline)
            target_correct = self._is_correct(target)
            if target_correct and not baseline_correct:
                target_only.append(self._example(sample_id, baseline, target, baseline_label, target_label))
            elif baseline_correct and not target_correct:
                baseline_only.append(self._example(sample_id, baseline, target, baseline_label, target_label))
            else:
                ties += 1
        baseline_correct_count = sum(int(self._is_correct(baseline_rows[sample_id])) for sample_id in shared_ids)
        target_correct_count = sum(int(self._is_correct(target_rows[sample_id])) for sample_id in shared_ids)
        n = len(shared_ids)
        baseline_accuracy = baseline_correct_count / max(1, n)
        target_accuracy = target_correct_count / max(1, n)
        return {
            "mode": pair.mode,
            "n": n,
            "baseline_csv": str(pair.baseline_csv),
            "target_csv": str(pair.target_csv),
            "baseline_accuracy": baseline_accuracy,
            "target_accuracy": target_accuracy,
            "delta_accuracy": target_accuracy - baseline_accuracy,
            "target_only": len(target_only),
            "baseline_only": len(baseline_only),
            "ties": ties,
            "target_only_examples": target_only,
            "baseline_only_examples": baseline_only,
        }

    def _read_by_id(self, csv_path: Path) -> dict[str, dict[str, str]]:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            return {
                row.get("id", ""): row
                for row in csv.DictReader(handle)
                if row.get("id")
            }

    def _example(
        self,
        sample_id: str,
        baseline: dict[str, str],
        target: dict[str, str],
        baseline_label: str,
        target_label: str,
    ) -> dict[str, str]:
        return {
            "id": sample_id,
            "query": target.get("query", baseline.get("query", "")),
            "answer": target.get("answer", baseline.get("answer", "")),
            f"{baseline_label}_prediction": baseline.get("prediction", ""),
            f"{target_label}_prediction": target.get("prediction", ""),
            "baseline_prediction": baseline.get("prediction", ""),
            "target_prediction": target.get("prediction", ""),
        }

    def _is_correct(self, row: dict[str, str]) -> bool:
        try:
            return float(row.get("accuracy", "0")) >= 1.0
        except ValueError:
            return False

    def _fmt(self, value: float) -> str:
        return f"{value:.3f}"
