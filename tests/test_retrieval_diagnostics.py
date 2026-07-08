from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from evigraph.retrieval_diagnostics import RetrievalDiagnosticAnalyzer
from evigraph.schema import EvidenceNode


class FakeRetriever:
    def retrieve(self, query, corpus_path=None, top_k=8, source_doc=None, retrieval_mode="open", adjacent_window=1):
        if "missing source" in query:
            return [
                EvidenceNode(
                    node_id="n1",
                    node_type="text",
                    content="wrong document says revenue was 41 in 2020",
                    source_doc="wrong.md",
                )
            ]
        return [
            EvidenceNode(
                node_id="n1",
                node_type="text",
                content="target source says revenue was 42 in 2020",
                source_doc=source_doc,
            )
        ]


class RetrievalDiagnosticAnalyzerTest(unittest.TestCase):
    def test_retrieval_diagnostic_splits_source_hit_and_source_miss(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            questions_path = root / "questions.jsonl"
            questions_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "id": "hit",
                                "query": "What was revenue in 2020?",
                                "answer": "42",
                                "source_doc": "target.md",
                            }
                        ),
                        json.dumps(
                            {
                                "id": "miss",
                                "query": "missing source revenue in 2020?",
                                "answer": "42",
                                "source_doc": "target.md",
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            csv_path = root / "results.csv"
            with csv_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["id", "method", "query", "answer", "prediction", "accuracy"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "id": "hit",
                        "method": "full_evigraph",
                        "query": "What was revenue in 2020?",
                        "answer": "42",
                        "prediction": "42",
                        "accuracy": "1",
                    }
                )
                writer.writerow(
                    {
                        "id": "miss",
                        "method": "full_evigraph",
                        "query": "missing source revenue in 2020?",
                        "answer": "42",
                        "prediction": "41",
                        "accuracy": "0",
                    }
                )

            analyzer = RetrievalDiagnosticAnalyzer(retriever=FakeRetriever())
            analysis = analyzer.analyze(
                csv_path,
                questions_path=questions_path,
                corpus_path=root / "corpus",
                retrieval_mode="open",
                top_k=4,
            )
            markdown = analyzer.render_markdown(analysis)

        self.assertEqual(analysis["total"], 2)
        self.assertEqual(analysis["counts"]["source_hit"], 1)
        self.assertEqual(analysis["counts"]["source_top1"], 1)
        self.assertEqual(analysis["counts"]["wrong_without_source_hit"], 1)
        self.assertEqual(analysis["counts"]["gold_answer_number_hit"], 1)
        self.assertIn("| source_hit | 1 | 0.500 |", markdown)
        self.assertIn("wrong_without_source_hit", markdown)


if __name__ == "__main__":
    unittest.main()
