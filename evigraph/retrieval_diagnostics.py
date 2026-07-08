from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from statistics import mean
from typing import Any

from evigraph.retrieval import CorpusRetriever
from evigraph.schema import EvidenceNode


class RetrievalDiagnosticAnalyzer:
    """Measure whether retrieval exposes the source and numeric surface needed downstream."""

    def __init__(self, retriever: CorpusRetriever | None = None) -> None:
        self.retriever = retriever or CorpusRetriever()

    def analyze(
        self,
        csv_path: str | Path,
        questions_path: str | Path,
        corpus_path: str | Path | None,
        retrieval_mode: str,
        method: str = "full_evigraph",
        top_k: int = 8,
        adjacent_window: int = 1,
    ) -> dict[str, Any]:
        path = Path(csv_path)
        rows = [row for row in self._read_rows(path) if row.get("method") == method]
        questions = self._read_questions(questions_path)
        diagnostics = [
            self._diagnose_row(
                row,
                questions.get(row.get("id", ""), {}),
                corpus_path,
                retrieval_mode,
                top_k,
                adjacent_window,
            )
            for row in rows
        ]
        total = len(diagnostics)
        source_ranks = [item["source_rank"] for item in diagnostics if item["source_rank"] is not None]
        return {
            "csv_path": str(path),
            "questions_path": str(questions_path),
            "corpus_path": str(corpus_path or ""),
            "retrieval_mode": retrieval_mode,
            "method": method,
            "top_k": top_k,
            "adjacent_window": adjacent_window,
            "total": total,
            "counts": {
                "source_hit": sum(int(item["source_hit"]) for item in diagnostics),
                "source_top1": sum(int(item["source_top1"]) for item in diagnostics),
                "gold_answer_number_hit": sum(int(item["gold_answer_number_hit"]) for item in diagnostics),
                "prediction_number_hit": sum(int(item["prediction_number_hit"]) for item in diagnostics),
                "query_year_hit": sum(int(item["query_year_hit"]) for item in diagnostics),
                "exact_match": sum(int(item["exact_match"]) for item in diagnostics),
                "exact_match_with_source_hit": sum(
                    int(item["exact_match"] and item["source_hit"]) for item in diagnostics
                ),
                "wrong_with_source_hit": sum(
                    int((not item["exact_match"]) and item["source_hit"]) for item in diagnostics
                ),
                "wrong_without_source_hit": sum(
                    int((not item["exact_match"]) and not item["source_hit"]) for item in diagnostics
                ),
            },
            "rates": {},
            "mean_source_rank": mean(source_ranks) if source_ranks else None,
            "examples": self._examples(diagnostics),
            "diagnostics": diagnostics,
        }

    def render_markdown(self, analysis: dict[str, Any]) -> str:
        counts = analysis["counts"]
        total = max(1, int(analysis["total"]))
        lines = [
            "# Retrieval Diagnostic",
            "",
            f"- CSV: `{self._display_path(analysis['csv_path'])}`",
            f"- Questions: `{self._display_path(analysis['questions_path'])}`",
            f"- Corpus: `{self._display_path(analysis['corpus_path'])}`",
            f"- Retrieval mode: `{analysis['retrieval_mode']}`",
            f"- Method: `{analysis['method']}`",
            f"- Top K: {analysis['top_k']}",
            f"- Adjacent window: {analysis.get('adjacent_window', 1)}",
            f"- Total rows for method: {analysis['total']}",
            "",
            "## Coverage",
            "",
            "| metric | count | rate |",
            "| --- | ---: | ---: |",
        ]
        for key in (
            "source_hit",
            "source_top1",
            "gold_answer_number_hit",
            "prediction_number_hit",
            "query_year_hit",
            "exact_match",
            "exact_match_with_source_hit",
            "wrong_with_source_hit",
            "wrong_without_source_hit",
        ):
            count = counts.get(key, 0)
            lines.append(f"| {key} | {count} | {count / total:.3f} |")
        mean_rank = analysis.get("mean_source_rank")
        lines.extend(["", f"- Mean source rank when hit: `{mean_rank:.2f}`" if mean_rank else "- Mean source rank when hit: `n/a`"])
        lines.extend(["", "## Examples", ""])
        for title, examples in analysis["examples"].items():
            if not examples:
                continue
            lines.extend([f"### {title}", ""])
            for item in examples:
                lines.append(f"- `{item['id']}`")
                lines.append(f"  - query: {self._shorten(item['query'], 180)}")
                lines.append(f"  - source_doc: `{item['source_doc']}`")
                lines.append(f"  - gold: `{item['answer']}`")
                lines.append(f"  - prediction: `{self._shorten(item['prediction'], 120)}`")
                lines.append(
                    "  - "
                    f"source_hit={item['source_hit']}, "
                    f"source_rank={item['source_rank']}, "
                    f"gold_number_hit={item['gold_answer_number_hit']}, "
                    f"query_year_hit={item['query_year_hit']}"
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
        adjacent_window: int = 1,
    ) -> str:
        analysis = self.analyze(
            csv_path,
            questions_path=questions_path,
            corpus_path=corpus_path,
            retrieval_mode=retrieval_mode,
            method=method,
            top_k=top_k,
            adjacent_window=adjacent_window,
        )
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(analysis), encoding="utf-8")
        return str(output)

    def _diagnose_row(
        self,
        row: dict[str, str],
        question: dict[str, Any],
        corpus_path: str | Path | None,
        retrieval_mode: str,
        top_k: int,
        adjacent_window: int,
    ) -> dict[str, Any]:
        query = row.get("query", "") or question.get("query", "")
        source_doc = str(question.get("source_doc", ""))
        nodes = self.retriever.retrieve(
            query,
            str(corpus_path) if corpus_path else None,
            top_k=top_k,
            source_doc=source_doc or None,
            retrieval_mode=retrieval_mode,
            adjacent_window=adjacent_window,
        )
        context = "\n".join(node.text() for node in nodes)
        source_rank = self._source_rank(nodes, source_doc)
        gold_numbers = self._numbers(row.get("answer", ""))
        prediction_numbers = self._numbers(row.get("prediction", ""))
        return {
            "id": row.get("id", ""),
            "query": query,
            "answer": row.get("answer", ""),
            "prediction": row.get("prediction", ""),
            "source_doc": source_doc,
            "source_hit": source_rank is not None,
            "source_top1": source_rank == 1,
            "source_rank": source_rank,
            "gold_answer_number_hit": self._contains_any_number(context, gold_numbers),
            "prediction_number_hit": self._contains_any_number(context, prediction_numbers),
            "query_year_hit": self._query_year_hit(query, context),
            "exact_match": self._to_float(row.get("accuracy")) >= 1.0,
        }

    def _source_rank(self, nodes: list[EvidenceNode], source_doc: str) -> int | None:
        if not source_doc:
            return None
        source_name = Path(source_doc).name
        for index, node in enumerate(nodes, start=1):
            node_source = Path(str(node.source_doc or "")).name
            if node_source == source_name or source_name.lower() in node.text().lower():
                return index
        return None

    def _query_year_hit(self, query: str, context: str) -> bool:
        years = re.findall(r"\b(?:19|20)\d{2}\b", query)
        return all(year in context for year in years) if years else True

    def _contains_any_number(self, text: str, numbers: list[float]) -> bool:
        if not numbers:
            return False
        context_numbers = self._numbers(text)
        return any(any(self._close(needle, value) for value in context_numbers) for needle in numbers)

    def _examples(self, diagnostics: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        return {
            "wrong_without_source_hit": [
                item for item in diagnostics if not item["exact_match"] and not item["source_hit"]
            ][:5],
            "wrong_with_source_hit": [
                item for item in diagnostics if not item["exact_match"] and item["source_hit"]
            ][:5],
            "source_hit_but_gold_number_missing": [
                item for item in diagnostics if item["source_hit"] and not item["gold_answer_number_hit"]
            ][:5],
        }

    def _read_rows(self, path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def _read_questions(self, path: str | Path) -> dict[str, dict[str, Any]]:
        questions: dict[str, dict[str, Any]] = {}
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line)
                questions[str(payload.get("id", ""))] = payload
        return questions

    def _numbers(self, text: str) -> list[float]:
        values: list[float] = []
        for match in re.findall(r"[-+]?\d[\d,]*(?:\.\d+)?", text or ""):
            try:
                values.append(float(match.replace(",", "")))
            except ValueError:
                continue
        return values

    def _close(self, left: float, right: float) -> bool:
        return abs(left - right) <= max(0.1, abs(right) * 0.001)

    def _to_float(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _display_path(self, path_text: str) -> str:
        if not path_text:
            return ""
        path = Path(path_text)
        try:
            return str(path.resolve().relative_to(Path.cwd().resolve()))
        except ValueError:
            return str(path)

    def _shorten(self, text: str, limit: int) -> str:
        normalized = re.sub(r"\s+", " ", text or "").strip()
        if len(normalized) <= limit:
            return normalized
        return normalized[: limit - 3].rstrip() + "..."
