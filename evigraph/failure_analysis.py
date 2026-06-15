from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class FailureAnalyzer:
    def analyze(self, csv_path: str | Path, method: str = "full_evigraph") -> dict[str, Any]:
        path = Path(csv_path)
        rows = self._read_rows(path)
        scoped = [row for row in rows if row.get("method") == method]
        failures = [row for row in scoped if self._to_float(row.get("accuracy")) < 1.0]
        categories = Counter(self._category(row) for row in failures)
        return {
            "csv_path": str(path),
            "method": method,
            "total": len(scoped),
            "correct": len(scoped) - len(failures),
            "failed": len(failures),
            "accuracy": (len(scoped) - len(failures)) / max(1, len(scoped)),
            "categories": dict(categories),
            "examples": self._examples_by_category(failures),
        }

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        lines = [
            "# Failure Analysis",
            "",
            f"- CSV: `{self._display_path(analysis['csv_path'])}`",
            f"- Method: `{analysis['method']}`",
            f"- Total: {analysis['total']}",
            f"- Correct: {analysis['correct']}",
            f"- Failed: {analysis['failed']}",
            f"- Accuracy: {analysis['accuracy']:.3f}",
            "",
            "## Failure Categories",
            "",
            "| category | count |",
            "| --- | ---: |",
        ]
        for category, count in sorted(analysis["categories"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {category} | {count} |")
        lines.extend(["", "## Examples", ""])
        for category, examples in sorted(analysis["examples"].items()):
            lines.extend([f"### {category}", ""])
            for row in examples:
                lines.append(f"- `{row['id']}`")
                lines.append(f"  - query: {row['query']}")
                lines.append(f"  - gold: `{row['answer']}`")
                lines.append(f"  - prediction: `{self._shorten(row['prediction'])}`")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(self, csv_path: str | Path, output_path: str | Path, method: str = "full_evigraph") -> str:
        analysis = self.analyze(csv_path, method=method)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        return str(output)

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _examples_by_category(self, failures: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in failures:
            category = self._category(row)
            if len(grouped[category]) < 5:
                grouped[category].append(row)
        return dict(grouped)

    def _category(self, row: dict[str, str]) -> str:
        prediction = row.get("prediction", "")
        query = row.get("query", "").lower()
        if prediction.startswith("Based on the selected evidence:"):
            if any(token in query for token in ["percentage", "percent", "rate", "growth"]):
                return "no_numeric_answer_percent"
            if any(token in query for token in ["average", "per"]):
                return "no_numeric_answer_ratio"
            if any(token in query for token in ["sum", "total", "combined", "amount", "portion", "share"]):
                return "no_numeric_answer_additive_or_lookup"
            return "no_numeric_answer_other"
        if self._numbers(prediction) and self._numbers(row.get("answer", "")):
            return "wrong_numeric_operation_or_row"
        return "unsupported_textual_prediction"

    def _numbers(self, text: str) -> list[float]:
        return [float(match) for match in re.findall(r"[-+]?\d+(?:\.\d+)?", text)]

    def _to_float(self, value: Any) -> float:
        if value in (None, ""):
            return 0.0
        return float(value)

    def _shorten(self, text: str, limit: int = 220) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3] + "..."

    def _display_path(self, path_text: str) -> str:
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)
