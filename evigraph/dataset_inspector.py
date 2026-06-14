from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from evigraph.dataset_adapter import DatasetAdapter


class DatasetInspector:
    def inspect(
        self,
        questions_path: str | Path,
        corpus_path: str | Path | None = None,
        output_path: str | Path | None = None,
    ) -> dict[str, Any]:
        path = Path(questions_path)
        records = DatasetAdapter()._read_records(path)
        report = self._report(path, records, Path(corpus_path) if corpus_path else None)
        if output_path:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report

    def render_markdown(self, report: dict[str, Any]) -> str:
        lines = [
            "# Dataset Inspection Report",
            "",
            f"- Questions: `{report['questions_path']}`",
            f"- Corpus: `{report.get('corpus_path') or 'n/a'}`",
            f"- Records: {report['records']}",
            f"- Unique ids: {report['unique_ids']}",
            f"- Duplicate ids: {report['duplicate_ids']}",
            f"- Missing query: {report['missing_query']}",
            f"- Missing answer: {report['missing_answer']}",
            f"- Missing source_doc: {report['missing_source_doc']}",
            f"- Corpus source_doc coverage: {report['source_doc_coverage']:.3f}",
            "",
            "## Task Types",
            "",
            self._counter_table(report["task_types"]),
            "",
            "## Missing Corpus Sources",
            "",
            self._list_items(report["missing_corpus_sources"]),
            "",
        ]
        return "\n".join(lines).rstrip() + "\n"

    def write_markdown(self, report: dict[str, Any], output_path: str | Path) -> str:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render_markdown(report), encoding="utf-8")
        return str(output)

    def _report(self, path: Path, records: list[dict[str, Any]], corpus_path: Path | None) -> dict[str, Any]:
        ids = [str(record.get("id", "")) for record in records if record.get("id")]
        id_counts = Counter(ids)
        source_docs = [str(record.get("source_doc", "")) for record in records if record.get("source_doc")]
        corpus_sources = self._corpus_sources(corpus_path)
        matched_sources = [source for source in source_docs if self._source_matches(source, corpus_sources)]
        missing_sources = sorted({source for source in source_docs if not self._source_matches(source, corpus_sources)})
        return {
            "questions_path": str(path),
            "corpus_path": str(corpus_path) if corpus_path else None,
            "records": len(records),
            "unique_ids": len(id_counts),
            "duplicate_ids": sum(count - 1 for count in id_counts.values() if count > 1),
            "missing_query": sum(1 for record in records if not record.get("query")),
            "missing_answer": sum(1 for record in records if not record.get("answer")),
            "missing_source_doc": sum(1 for record in records if not record.get("source_doc")),
            "source_doc_coverage": len(matched_sources) / max(1, len(source_docs)),
            "missing_corpus_sources": missing_sources[:50],
            "task_types": dict(Counter(str(record.get("task_type", "unknown")) for record in records)),
        }

    def _corpus_sources(self, corpus_path: Path | None) -> set[str]:
        if not corpus_path or not corpus_path.exists():
            return set()
        if corpus_path.is_file() and corpus_path.suffix.lower() == ".json":
            return self._index_sources(corpus_path)
        files = [corpus_path] if corpus_path.is_file() else [file for file in corpus_path.rglob("*") if file.is_file()]
        sources = set()
        for file in files:
            sources.add(file.name)
            sources.add(str(file))
            try:
                sources.add(str(file.resolve()))
            except OSError:
                pass
        return sources

    def _index_sources(self, index_path: Path) -> set[str]:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
        sources = set()
        for chunk in payload.get("chunks", []):
            source = str(chunk.get("source_doc", ""))
            if not source:
                continue
            sources.add(source)
            sources.add(Path(source).name)
            try:
                sources.add(str(Path(source).resolve()))
            except OSError:
                pass
        return sources

    def _source_matches(self, source: str, corpus_sources: set[str]) -> bool:
        if not corpus_sources:
            return False
        return source in corpus_sources or Path(source).name in corpus_sources

    def _counter_table(self, counter: dict[str, int]) -> str:
        if not counter:
            return "No task types recorded."
        lines = ["| task_type | count |", "| --- | ---: |"]
        for key, value in sorted(counter.items()):
            lines.append(f"| {key} | {value} |")
        return "\n".join(lines)

    def _list_items(self, items: list[str]) -> str:
        if not items:
            return "None."
        return "\n".join(f"- `{item}`" for item in items)


class BenchmarkGate:
    def evaluate(
        self,
        report: dict[str, Any],
        min_records: int = 1,
        min_source_doc_coverage: float = 1.0,
        allow_missing_source_doc: bool = False,
    ) -> dict[str, Any]:
        checks = [
            self._check("min_records", report["records"] >= min_records, report["records"], min_records),
            self._check("no_duplicate_ids", report["duplicate_ids"] == 0, report["duplicate_ids"], 0),
            self._check("no_missing_query", report["missing_query"] == 0, report["missing_query"], 0),
            self._check("no_missing_answer", report["missing_answer"] == 0, report["missing_answer"], 0),
            self._check(
                "source_doc_present",
                allow_missing_source_doc or report["missing_source_doc"] == 0,
                report["missing_source_doc"],
                0,
            ),
            self._check(
                "source_doc_coverage",
                float(report["source_doc_coverage"]) >= min_source_doc_coverage,
                round(float(report["source_doc_coverage"]), 6),
                min_source_doc_coverage,
            ),
        ]
        return {
            "passed": all(check["passed"] for check in checks),
            "checks": checks,
        }

    def render_markdown(self, gate: dict[str, Any]) -> str:
        lines = [
            "# Benchmark Gate",
            "",
            f"- Passed: `{gate['passed']}`",
            "",
            "| check | passed | actual | expected |",
            "| --- | --- | ---: | ---: |",
        ]
        for check in gate["checks"]:
            lines.append(
                f"| {check['name']} | {check['passed']} | {check['actual']} | {check['expected']} |"
            )
        return "\n".join(lines) + "\n"

    def _check(self, name: str, passed: bool, actual: Any, expected: Any) -> dict[str, Any]:
        return {
            "name": name,
            "passed": bool(passed),
            "actual": actual,
            "expected": expected,
        }
