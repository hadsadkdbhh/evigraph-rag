from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evigraph.case_selection import PaperCaseSelector


class CaseSelectionTest(unittest.TestCase):
    def test_selects_component_and_gpt_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            questions = root / "questions.jsonl"
            questions.write_text(
                json.dumps({"id": "q1", "query": "What was revenue?", "answer": "42", "source_doc": "target.md"})
                + "\n"
                + json.dumps({"id": "q2", "query": "What was margin?", "answer": "7", "source_doc": "target.md"})
                + "\n",
                encoding="utf-8",
            )
            evigraph_csv = root / "evigraph.csv"
            self._write_csv(
                evigraph_csv,
                [
                    {"id": "q1", "method": "full_evigraph", "query": "What was revenue?", "answer": "42", "prediction": "42", "accuracy": "1"},
                    {"id": "q1", "method": "direct_rag", "query": "What was revenue?", "answer": "42", "prediction": "41", "accuracy": "0"},
                    {"id": "q1", "method": "utility_only", "query": "What was revenue?", "answer": "42", "prediction": "40", "accuracy": "0"},
                    {"id": "q1", "method": "evigraph_wo_operation_planner", "query": "What was revenue?", "answer": "42", "prediction": "39", "accuracy": "0"},
                    {"id": "q2", "method": "full_evigraph", "query": "What was margin?", "answer": "7", "prediction": "8", "accuracy": "0"},
                    {"id": "q2", "method": "direct_rag", "query": "What was margin?", "answer": "7", "prediction": "8", "accuracy": "0"},
                    {"id": "q2", "method": "utility_only", "query": "What was margin?", "answer": "7", "prediction": "8", "accuracy": "0"},
                    {"id": "q2", "method": "evigraph_wo_operation_planner", "query": "What was margin?", "answer": "7", "prediction": "8", "accuracy": "0"},
                ],
            )
            gpt_csv = root / "gpt.csv"
            self._write_csv(
                gpt_csv,
                [
                    {
                        "id": "q1",
                        "method": "llm_direct_rag",
                        "query": "What was revenue?",
                        "answer": "42",
                        "prediction": "42",
                        "accuracy": "1",
                        "answer_supported": "False",
                    }
                ],
                extra_fieldnames=["answer_supported"],
            )
            fake_retrieval = {
                "diagnostics": [
                    {"id": "q1", "source_hit": True, "source_rank": 1, "gold_answer_number_hit": True, "query_year_hit": True},
                    {"id": "q2", "source_hit": True, "source_rank": 2, "gold_answer_number_hit": False, "query_year_hit": True},
                ]
            }
            with patch("evigraph.case_selection.RetrievalDiagnosticAnalyzer") as fake_cls:
                fake_cls.return_value.analyze.return_value = fake_retrieval
                selection = PaperCaseSelector().select(
                    evigraph_csv,
                    questions_path=questions,
                    corpus_path=root / "corpus",
                    retrieval_mode="open",
                    gpt_csv=gpt_csv,
                )
            markdown = PaperCaseSelector().render_markdown(selection)

        self.assertEqual(selection["cases"]["evigraph_over_direct"]["id"], "q1")
        self.assertEqual(selection["cases"]["open_retrieval_failure"]["id"], "q2")
        self.assertEqual(selection["cases"]["gpt_correct_but_unsupported"]["id"], "q1")
        self.assertIn("GPT-5.4 Correct But Unsupported", markdown)

    def _write_csv(
        self,
        path: Path,
        rows: list[dict[str, str]],
        extra_fieldnames: list[str] | None = None,
    ) -> None:
        fieldnames = ["id", "method", "query", "answer", "prediction", "accuracy"]
        for fieldname in extra_fieldnames or []:
            if fieldname not in fieldnames:
                fieldnames.append(fieldname)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
