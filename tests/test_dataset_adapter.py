from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evigraph.dataset_adapter import DatasetAdapter, field_map_for_profile
from evigraph.dataset_inspector import BenchmarkGate, DatasetInspector
from evigraph.subset_builder import BenchmarkSubsetBuilder


ROOT = Path(__file__).resolve().parents[1]


class DatasetAdapterTest(unittest.TestCase):
    def test_converts_jsonl_with_explicit_field_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "raw.jsonl"
            output_path = root / "questions.jsonl"
            input_path.write_text(
                json.dumps(
                    {
                        "qid": "chart_001",
                        "question": "How much higher was 2023 than 2022?",
                        "gold_answer": ["12.5", "twelve point five"],
                        "document": "report.pdf",
                        "category": "chart",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = DatasetAdapter().convert(
                input_path,
                output_path,
                field_map={
                    "id": "qid",
                    "query": "question",
                    "answer": "gold_answer",
                    "source_doc": "document",
                    "task_type": "category",
                },
                dataset_name="chartqa_smoke",
            )

            self.assertEqual(result["records"], 1)
            converted = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(converted["id"], "chart_001")
            self.assertEqual(converted["query"], "How much higher was 2023 than 2022?")
            self.assertEqual(converted["answer"], '["12.5", "twelve point five"]')
            self.assertEqual(converted["source_doc"], "report.pdf")
            self.assertEqual(converted["task_type"], "chart")
            self.assertEqual(converted["dataset"], "chartqa_smoke")

    def test_raises_when_query_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "bad.json"
            output_path = root / "questions.jsonl"
            input_path.write_text(json.dumps([{"answer": "12.5"}]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no query"):
                DatasetAdapter().convert(input_path, output_path)

    def test_inspector_reports_source_doc_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "chart_001.txt").write_text("chart text", encoding="utf-8")
            questions = root / "questions.jsonl"
            questions.write_text(
                "\n".join(
                    [
                        json.dumps({"id": "q1", "query": "Q1", "answer": "A1", "source_doc": "chart_001.txt"}),
                        json.dumps({"id": "q2", "query": "Q2", "answer": "A2", "source_doc": "missing.txt"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            report = DatasetInspector().inspect(questions, corpus)

            self.assertEqual(report["records"], 2)
            self.assertEqual(report["missing_query"], 0)
            self.assertEqual(report["missing_answer"], 0)
            self.assertEqual(report["source_doc_coverage"], 0.5)
            self.assertEqual(report["missing_corpus_sources"], ["missing.txt"])

    def test_inspector_reads_sources_from_index_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index_path = root / "index.json"
            index_path.write_text(
                json.dumps({"chunks": [{"source_doc": str(root / "case_alpha_report.md"), "text": "x"}]}),
                encoding="utf-8",
            )
            questions = root / "questions.jsonl"
            questions.write_text(
                json.dumps(
                    {
                        "id": "q1",
                        "query": "Q1",
                        "answer": "A1",
                        "source_doc": "case_alpha_report.md",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            report = DatasetInspector().inspect(questions, index_path)

            self.assertEqual(report["source_doc_coverage"], 1.0)
            self.assertEqual(report["missing_corpus_sources"], [])

    def test_repository_mock_questions_match_corpus_sources(self) -> None:
        report = DatasetInspector().inspect(ROOT / "data" / "questions.jsonl", ROOT / "data" / "corpus")

        self.assertEqual(report["records"], 1)
        self.assertEqual(report["source_doc_coverage"], 1.0)
        self.assertEqual(report["missing_corpus_sources"], [])

    def test_benchmark_gate_fails_on_low_coverage(self) -> None:
        report = {
            "records": 10,
            "duplicate_ids": 0,
            "missing_query": 0,
            "missing_answer": 0,
            "missing_source_doc": 0,
            "source_doc_coverage": 0.8,
        }

        gate = BenchmarkGate().evaluate(report, min_records=10, min_source_doc_coverage=1.0)

        self.assertFalse(gate["passed"])
        self.assertIn("source_doc_coverage", [check["name"] for check in gate["checks"] if not check["passed"]])

    def test_benchmark_gate_passes_clean_report(self) -> None:
        report = {
            "records": 20,
            "duplicate_ids": 0,
            "missing_query": 0,
            "missing_answer": 0,
            "missing_source_doc": 0,
            "source_doc_coverage": 1.0,
        }

        gate = BenchmarkGate().evaluate(report, min_records=20, min_source_doc_coverage=1.0)

        self.assertTrue(gate["passed"])

    def test_subset_builder_filters_unmatched_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "chart_a.txt").write_text("a", encoding="utf-8")
            (corpus / "chart_b.txt").write_text("b", encoding="utf-8")
            raw = root / "raw.jsonl"
            raw.write_text(
                "\n".join(
                    [
                        json.dumps({"id": "a", "question": "A?", "answer": "1", "image": "chart_a.txt"}),
                        json.dumps({"id": "b", "question": "B?", "answer": "2", "image": "chart_b.txt"}),
                        json.dumps({"id": "c", "question": "C?", "answer": "3", "image": "missing.txt"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output = root / "subset.jsonl"

            result = BenchmarkSubsetBuilder().build(
                raw,
                output,
                field_map={"source_doc": "image"},
                corpus_path=corpus,
                sample_size=2,
                seed=7,
                require_source_doc=True,
            )
            subset = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(result["eligible_records"], 2)
            self.assertEqual(result["sampled_records"], 2)
            self.assertEqual(result["skipped_unmatched_source_doc"], 1)
            self.assertEqual({record["image"] for record in subset}, {"chart_a.txt", "chart_b.txt"})

    def test_chartqa_profile_maps_image_to_source_doc(self) -> None:
        field_map = field_map_for_profile("chartqa")
        record = {
            "id": "chartqa_001",
            "question": "What is the value?",
            "answer": "10",
            "image": "chart_001.png",
            "type": "human",
        }

        converted = DatasetAdapter()._convert_record(1, record, field_map, None, "chartqa")

        self.assertEqual(converted["source_doc"], "chart_001.png")
        self.assertEqual(converted["task_type"], "human")
        self.assertEqual(converted["dataset"], "chartqa")


if __name__ == "__main__":
    unittest.main()
