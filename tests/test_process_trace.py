from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from evigraph.process_trace import EvidenceCritic, ProcessTraceAnalyzer


class ProcessTraceAnalyzerTest(unittest.TestCase):
    def test_evidence_critic_detects_period_row_operand_and_operation(self) -> None:
        critic = EvidenceCritic()

        assessment = critic.assess(
            "What was the percentage change in rental expense from 2008 to 2009?",
            "rental expense | 2008 | 100\nrental expense | 2009 | 117",
            "percent_change row=rental expense: (117 - 100) / 100 * 100 = 17.0%",
        )

        self.assertTrue(assessment["target_period_present"])
        self.assertTrue(assessment["required_row_present"])
        self.assertTrue(assessment["numeric_operands_present"])
        self.assertTrue(assessment["operation_cue_present"])
        self.assertFalse(assessment["noise_risk"])

    def test_process_trace_summarizes_hop_rates_and_first_failed_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            good_run = self._write_run(
                root,
                "percent_change row=rental expense: (117 - 100) / 100 * 100 = 17.0%",
                "rental expense | 2008 | 100\nrental expense | 2009 | 117",
            )
            bad_run = self._write_run(
                root,
                "ratio_percent row=net sales denominator_row=assets: 5 / 100 * 100 = 5.0%",
                "",
            )
            csv_path = self._write_csv(
                root,
                [
                    {
                        "id": "good",
                        "query": "What was the percentage change in rental expense from 2008 to 2009?",
                        "answer": "17%",
                        "prediction": "17.0%",
                        "accuracy": "1.0",
                        "answer_supported": "1",
                        "operation_semantics_checked": "1",
                        "row_operation_grounded": "1",
                        "citation_correct": "1",
                        "run_dir": str(good_run),
                    },
                    {
                        "id": "bad",
                        "query": "What was the percentage change in rental expense from 2008 to 2009?",
                        "answer": "17%",
                        "prediction": "5.0%",
                        "accuracy": "0.0",
                        "answer_supported": "0",
                        "operation_semantics_checked": "0",
                        "row_operation_grounded": "0",
                        "citation_correct": "0",
                        "run_dir": str(bad_run),
                    },
                ],
            )

            analysis = ProcessTraceAnalyzer().analyze(csv_path)
            markdown = ProcessTraceAnalyzer().render_markdown(analysis)

        self.assertEqual(analysis["total"], 2)
        self.assertEqual(analysis["step_counts"]["exact_match"], 1)
        self.assertEqual(analysis["first_failed_step_counts"]["evidence_available"], 1)
        self.assertIn("| operand_hit | 1 | 0.500 |", markdown)
        self.assertIn("first_failed=`evidence_available`", markdown)

    def _write_run(self, root: Path, calculation: str, context: str) -> Path:
        run_dir = root / f"run_{len(list(root.glob('run_*')))}"
        run_dir.mkdir()
        (run_dir / "answer.md").write_text(
            f"# Answer\n\n17.0%\n\n## Calculations\n- {calculation}\n\n## Query\nq\n",
            encoding="utf-8",
        )
        nodes = [{"node_id": "n1", "node_type": "text", "content": context}] if context else []
        (run_dir / "support_graph.json").write_text(json.dumps({"nodes": nodes, "edges": []}), encoding="utf-8")
        return run_dir

    def _write_csv(self, root: Path, rows: list[dict[str, str]]) -> Path:
        path = root / "results.csv"
        fieldnames = [
            "id",
            "method",
            "query",
            "answer",
            "prediction",
            "accuracy",
            "answer_supported",
            "operation_semantics_checked",
            "row_operation_grounded",
            "citation_correct",
            "run_dir",
        ]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({"method": "full_evigraph", **row})
        return path


if __name__ == "__main__":
    unittest.main()
