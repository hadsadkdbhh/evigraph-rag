from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evigraph.retrieval_diagnostics import RetrievalDiagnosticAnalyzer


class FailureSliceAnalyzer:
    """Slice failed examples by retrieval coverage and question intent."""

    def analyze(
        self,
        csv_path: str | Path,
        questions_path: str | Path,
        corpus_path: str | Path | None,
        retrieval_mode: str,
        method: str = "full_evigraph",
        top_k: int = 8,
    ) -> dict[str, Any]:
        path = Path(csv_path)
        rows = [row for row in self._read_rows(path) if row.get("method") == method]
        retrieval = RetrievalDiagnosticAnalyzer().analyze(
            path,
            questions_path=questions_path,
            corpus_path=corpus_path,
            retrieval_mode=retrieval_mode,
            method=method,
            top_k=top_k,
        )
        retrieval_by_id = {row["id"]: row for row in retrieval["diagnostics"]}
        slices = [self._slice_row(row, retrieval_by_id.get(row.get("id", ""), {})) for row in rows if not self._is_correct(row)]
        return {
            "csv_path": str(path),
            "questions_path": str(questions_path),
            "corpus_path": str(corpus_path or ""),
            "retrieval_mode": retrieval_mode,
            "method": method,
            "total": len(rows),
            "failed": len(slices),
            "source_counts": dict(Counter(item["source_slice"] for item in slices)),
            "intent_counts": dict(Counter(item["intent"] for item in slices)),
            "support_counts": dict(Counter(item["support_slice"] for item in slices)),
            "joint_counts": dict(Counter(f"{item['source_slice']}::{item['intent']}" for item in slices)),
            "examples": self._examples(slices),
            "slices": slices,
        }

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        lines = [
            "# Failure Slice Analysis",
            "",
            f"- CSV: `{self._display_path(analysis['csv_path'])}`",
            f"- Questions: `{self._display_path(analysis['questions_path'])}`",
            f"- Retrieval mode: `{analysis['retrieval_mode']}`",
            f"- Method: `{analysis['method']}`",
            f"- Failed rows: {analysis['failed']} / {analysis['total']}",
            "",
            "## Source Slices",
            "",
            "| slice | count |",
            "| --- | ---: |",
        ]
        for key, count in sorted(analysis["source_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {key} | {count} |")
        lines.extend(["", "## Intent Slices", "", "| intent | count |", "| --- | ---: |"])
        for key, count in sorted(analysis["intent_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {key} | {count} |")
        lines.extend(["", "## Support Slices", "", "| slice | count |", "| --- | ---: |"])
        for key, count in sorted(analysis["support_counts"].items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {key} | {count} |")
        lines.extend(["", "## Joint Source x Intent", "", "| source/intent | count |", "| --- | ---: |"])
        for key, count in sorted(analysis["joint_counts"].items(), key=lambda item: (-item[1], item[0]))[:20]:
            lines.append(f"| {key} | {count} |")
        lines.extend(["", "## Examples", ""])
        for group, examples in analysis["examples"].items():
            if not examples:
                continue
            lines.extend([f"### {group}", ""])
            for item in examples:
                lines.append(f"- `{item['id']}`")
                lines.append(f"  - query: {item['query']}")
                lines.append(f"  - gold: `{item['answer']}`")
                lines.append(f"  - prediction: `{self._shorten(item['prediction'], 160)}`")
                lines.append(
                    "  - "
                    f"source={item['source_slice']}, intent={item['intent']}, "
                    f"support={item['support_slice']}, source_rank={item.get('source_rank')}"
                )
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def write(
        self,
        csv_path: str | Path,
        questions_path: str | Path,
        corpus_path: str | Path | None,
        retrieval_mode: str,
        output_path: str | Path,
        method: str = "full_evigraph",
        top_k: int = 8,
    ) -> str:
        analysis = self.analyze(
            csv_path,
            questions_path=questions_path,
            corpus_path=corpus_path,
            retrieval_mode=retrieval_mode,
            method=method,
            top_k=top_k,
        )
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        return str(output)

    def _slice_row(self, row: dict[str, str], retrieval: dict[str, Any]) -> dict[str, Any]:
        source_hit = bool(retrieval.get("source_hit"))
        gold_hit = bool(retrieval.get("gold_answer_number_hit"))
        if not source_hit:
            source_slice = "source_missing"
        elif not gold_hit:
            source_slice = "source_hit_gold_number_missing"
        else:
            source_slice = "source_hit_gold_number_present"
        item = {
            "id": row.get("id", ""),
            "query": row.get("query", ""),
            "answer": row.get("answer", ""),
            "prediction": row.get("prediction", ""),
            "source_slice": source_slice,
            "support_slice": self._support_slice(row),
            "intent": self._intent(row.get("query", "")),
            "source_rank": retrieval.get("source_rank"),
        }
        return item

    def _support_slice(self, row: dict[str, str]) -> str:
        prediction = row.get("prediction", "")
        if prediction.startswith("Based on the selected evidence:") or prediction.startswith("Insufficient evidence"):
            return "textual_or_insufficient"
        if self._truthy(row.get("answer_supported")) and self._numbers(row.get("prediction", "")):
            return "supported_wrong_numeric"
        if self._numbers(row.get("prediction", "")):
            return "unsupported_wrong_numeric"
        return "textual_or_insufficient"

    def _intent(self, query: str) -> str:
        lowered = query.lower()
        if any(token in lowered for token in ("percent", "percentage", "growth", "rate", "increase", "decrease")):
            if any(token in lowered for token in ("percent of", "percentage of", "portion", "represented", "ratio")):
                return "ratio_percent"
            return "percent_change"
        if any(token in lowered for token in ("average", "mean")):
            return "average"
        if any(token in lowered for token in ("total", "sum", "combined")):
            return "sum_or_lookup"
        if any(token in lowered for token in ("difference", "change in", "higher", "lower")):
            return "difference"
        if any(token in lowered for token in ("ratio", "compared to")):
            return "ratio"
        return "lookup_or_other"

    def _examples(self, slices: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in slices:
            for key in (item["source_slice"], item["intent"], item["support_slice"]):
                if len(grouped[key]) < 3:
                    grouped[key].append(item)
        return dict(grouped)

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _numbers(self, text: str) -> list[float]:
        values = []
        for match in re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text or ""):
            try:
                values.append(float(match.replace(",", "")))
            except ValueError:
                continue
        return values

    def _truthy(self, value: Any) -> bool:
        if isinstance(value, str):
            return value.strip().lower() in {"1", "1.0", "true", "yes"}
        return bool(value)

    def _is_correct(self, row: dict[str, str]) -> bool:
        try:
            return float(row.get("accuracy", "0")) >= 1.0
        except ValueError:
            return False

    def _display_path(self, path_text: str) -> str:
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    def _shorten(self, text: str, limit: int) -> str:
        compact = " ".join(str(text).split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."
