from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evigraph.dataset_adapter import DatasetAdapter


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


if __name__ == "__main__":
    unittest.main()
