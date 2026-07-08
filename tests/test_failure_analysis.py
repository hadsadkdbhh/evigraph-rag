from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from evigraph.failure_analysis import FailureAnalyzer


class FailureAnalyzerTest(unittest.TestCase):
    def test_supported_wrong_operand_semantic_mismatch_gets_specific_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "eval.csv"
            fieldnames = [
                "id",
                "method",
                "query",
                "answer",
                "prediction",
                "accuracy",
                "answer_supported",
                "operand_semantics_checked",
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "id": "case-1",
                        "method": "full_evigraph",
                        "query": "what percentage of total goodwill is attributable to u.s. brokerage reporting unit?",
                        "answer": "91%",
                        "prediction": "1.6%",
                        "accuracy": "0",
                        "answer_supported": "1",
                        "operand_semantics_checked": "0",
                    }
                )

            analysis = FailureAnalyzer().analyze(csv_path)

            self.assertEqual(analysis["categories"], {"supported_wrong_operand_semantic_mismatch": 1})

    def test_supported_wrong_source_inconsistency_gets_specific_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "eval.csv"
            fieldnames = [
                "id",
                "method",
                "query",
                "answer",
                "prediction",
                "accuracy",
                "answer_supported",
                "operand_semantics_checked",
                "source_consistent",
            ]
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(
                    {
                        "id": "case-2",
                        "method": "full_evigraph",
                        "query": "what percentage of total price was represented by ipr&d?",
                        "answer": "4.4%",
                        "prediction": "100%",
                        "accuracy": "0",
                        "answer_supported": "1",
                        "operand_semantics_checked": "1",
                        "source_consistent": "0",
                    }
                )

            analysis = FailureAnalyzer().analyze(csv_path)

            self.assertEqual(analysis["categories"], {"supported_wrong_source_inconsistency": 1})


if __name__ == "__main__":
    unittest.main()
