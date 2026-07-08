from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evigraph.failure_slices import FailureSliceAnalyzer


class FailureSliceAnalyzerTest(unittest.TestCase):
    def test_slices_failures_by_source_coverage_and_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            questions = root / "questions.jsonl"
            questions.write_text(
                json.dumps({"id": "q1", "query": "percent change?", "answer": "17%", "source_doc": "a.md"}) + "\n"
                + json.dumps({"id": "q2", "query": "average value?", "answer": "5", "source_doc": "b.md"}) + "\n",
                encoding="utf-8",
            )
            csv_path = root / "results.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["id", "method", "query", "answer", "prediction", "accuracy", "answer_supported"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "id": "q1",
                        "method": "full_evigraph",
                        "query": "percent change?",
                        "answer": "17%",
                        "prediction": "12%",
                        "accuracy": "0",
                        "answer_supported": "True",
                    }
                )
                writer.writerow(
                    {
                        "id": "q2",
                        "method": "full_evigraph",
                        "query": "average value?",
                        "answer": "5",
                        "prediction": "Insufficient evidence to answer.",
                        "accuracy": "0",
                        "answer_supported": "False",
                    }
                )
            fake_retrieval = {
                "diagnostics": [
                    {"id": "q1", "source_hit": True, "source_rank": 1, "gold_answer_number_hit": False},
                    {"id": "q2", "source_hit": False, "source_rank": None, "gold_answer_number_hit": False},
                ]
            }
            with patch("evigraph.failure_slices.RetrievalDiagnosticAnalyzer") as fake_cls:
                fake_cls.return_value.analyze.return_value = fake_retrieval
                analysis = FailureSliceAnalyzer().analyze(
                    csv_path,
                    questions_path=questions,
                    corpus_path=root / "corpus",
                    retrieval_mode="open",
                )
            markdown = FailureSliceAnalyzer().render_markdown(analysis)

        self.assertEqual(analysis["source_counts"]["source_hit_gold_number_missing"], 1)
        self.assertEqual(analysis["source_counts"]["source_missing"], 1)
        self.assertEqual(analysis["intent_counts"]["percent_change"], 1)
        self.assertEqual(analysis["intent_counts"]["average"], 1)
        self.assertIn("supported_wrong_numeric", markdown)


if __name__ == "__main__":
    unittest.main()
