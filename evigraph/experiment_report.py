from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DEFAULT_METRICS = [
    "accuracy",
    "answer_supported",
    "supported_accuracy",
    "unsupported_correct",
    "supported_wrong",
    "answer_support_gap",
    "arithmetically_supported",
    "calculation_supported",
    "operation_semantics_checked",
    "row_operation_grounded",
    "semantically_grounded",
    "citation_correct",
    "misleading_acceptance",
    "input_tokens",
    "tool_calls",
    "latency_ms",
]


class ExperimentReport:
    def render(self, csv_paths: list[str | Path], title: str = "EviGraph Experiment Summary") -> str:
        sections = [f"# {title}", ""]
        for csv_path in csv_paths:
            path = Path(csv_path)
            rows = self._read_rows(path)
            sections.extend(
                [
                    f"## {path.name}",
                    "",
                    f"- Rows: {len(rows)}",
                    f"- Grouping: `{', '.join(self._group_columns(rows)) or 'all'}`",
                    "",
                    self._table(rows),
                    "",
                ]
            )
        return "\n".join(sections).rstrip() + "\n"

    def write(self, csv_paths: list[str | Path], output_path: str | Path, title: str = "EviGraph Experiment Summary") -> str:
        markdown = self.render(csv_paths, title=title)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown, encoding="utf-8")
        return str(output)

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        if not path.exists():
            raise FileNotFoundError(f"Experiment CSV does not exist: {path}")
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _table(self, rows: list[dict[str, str]]) -> str:
        if not rows:
            return "No rows found."
        group_columns = self._group_columns(rows)
        metric_columns = [metric for metric in DEFAULT_METRICS if metric in rows[0]]
        grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            key = tuple(row.get(column, "") for column in group_columns)
            grouped[key].append(row)

        header = [*group_columns, "n", *metric_columns]
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---:" if column in {"n", *metric_columns} else "---" for column in header) + " |",
        ]
        for key, group in sorted(grouped.items(), key=lambda item: item[0]):
            values: list[str] = [*key, str(len(group))]
            for metric in metric_columns:
                values.append(self._format_number(mean(self._to_float(row.get(metric)) for row in group)))
            lines.append("| " + " | ".join(values) + " |")
        return "\n".join(lines)

    def _group_columns(self, rows: list[dict[str, Any]]) -> list[str]:
        if not rows:
            return []
        first = rows[0]
        columns = ["dataset", "method"]
        if "budget_nodes" in first:
            columns.append("budget_nodes")
        return [column for column in columns if column in first]

    def _to_float(self, value: Any) -> float:
        if value in (None, ""):
            return 0.0
        if isinstance(value, str) and value.lower() in {"true", "false"}:
            return float(value.lower() == "true")
        return float(value)

    def _format_number(self, value: float) -> str:
        return f"{value:.3f}".rstrip("0").rstrip(".")
