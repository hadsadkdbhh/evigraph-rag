from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_tatqa_subset import build_subset


class TatqaSubsetBuilderTest(unittest.TestCase):
    def test_builds_numeric_questions_and_corpus_without_derivations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "tatqa.json"
            raw_output = root / "raw" / "tatqa_2_subset.jsonl"
            corpus_output = root / "corpus"
            input_path.write_text(
                json.dumps(
                    [
                        {
                            "table": {
                                "uid": "doc-alpha",
                                "table": [
                                    ["metric", "2019", "2018"],
                                    ["revenue", "120", "100"],
                                    ["cost", "30", "20"],
                                ],
                            },
                            "paragraphs": [{"order": 1, "text": "Revenue increased in 2019."}],
                            "questions": [
                                {
                                    "uid": "q_span",
                                    "question": "What happened?",
                                    "answer": ["Revenue increased."],
                                    "answer_type": "span",
                                    "answer_from": "text",
                                    "scale": "",
                                    "derivation": "",
                                },
                                {
                                    "uid": "q_arith_percent",
                                    "question": "What was the revenue percentage change?",
                                    "answer": "20",
                                    "answer_type": "arithmetic",
                                    "answer_from": "table",
                                    "scale": "percent",
                                    "derivation": "(120-100)/100",
                                },
                            ],
                        },
                        {
                            "table": {
                                "uid": "doc-beta",
                                "table": [["metric", "value"], ["total", "15"]],
                            },
                            "paragraphs": [{"order": 1, "text": "Total cost was disclosed."}],
                            "questions": [
                                {
                                    "uid": "q_arith_plain",
                                    "question": "What is total plus five?",
                                    "answer": "20",
                                    "answer_type": "arithmetic",
                                    "answer_from": "table-text",
                                    "scale": "",
                                    "derivation": "15+5",
                                }
                            ],
                        },
                    ]
                ),
                encoding="utf-8",
            )

            result = build_subset(input_path, raw_output, corpus_output, sample_size=2, seed=1)
            questions = [json.loads(line) for line in raw_output.read_text(encoding="utf-8").splitlines()]
            corpus_text = "\n".join(path.read_text(encoding="utf-8") for path in corpus_output.glob("*.md"))

            self.assertEqual(result["eligible_questions"], 2)
            self.assertEqual(result["sampled_questions"], 2)
            self.assertEqual({question["id"] for question in questions}, {"q_arith_percent", "q_arith_plain"})
            self.assertIn("20%", {question["answer"] for question in questions})
            self.assertTrue(all(question["source_doc"].endswith(".md") for question in questions))
            self.assertIn("| metric | 2019 | 2018 |", corpus_text)
            self.assertIn("Revenue increased in 2019.", corpus_text)
            self.assertNotIn("(120-100)/100", corpus_text)
            self.assertNotIn("15+5", corpus_text)


if __name__ == "__main__":
    unittest.main()
