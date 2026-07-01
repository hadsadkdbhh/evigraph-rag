from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from evigraph.evidence_graph import EvidenceGraph
from evigraph.methods import MethodRunner
from evigraph.repair import VerifierGuidedRepairer
from evigraph.schema import Answer, EvidenceNode


class FakeGenerator:
    def __init__(self) -> None:
        self.planner_first_calls = 0

    def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
        source_docs = {node.source_doc for node in support_graph.nodes.values()}
        if "right.md" in source_docs:
            return Answer(
                text="16.8%",
                citations=["right"],
                calculations=["percent_change row=interest income: (99 - 119) / 119 * 100 = -16.8%"],
            )
        return Answer(
            text="-5.2%",
            citations=["wrong"],
            calculations=["ratio_percent row=interest rates: 34.7 / 36.6 * 100 = -5.2%"],
        )

    def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
        self.planner_first_calls += 1
        return self.generate(query, support_graph)


class FakeVerifier:
    def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
        supported = "interest income" in " ".join(answer.calculations)
        return {
            "answer_supported": supported,
            "row_grounded": supported,
            "operation_semantics_checked": supported,
            "missing_evidence": [] if supported else ["Calculation operation type does not match query intent."],
        }


class VerifierGuidedRepairerTest(unittest.TestCase):
    def test_repairs_failed_row_operation_answer_from_alternate_source_cluster(self) -> None:
        graph = EvidenceGraph()
        wrong = EvidenceNode(
            "wrong",
            "text",
            "interest rates table 2014 36.6 2015 34.7",
            source_doc="wrong.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.0},
        )
        right = EvidenceNode(
            "right",
            "text",
            "interest income table 2014 119 2015 99",
            source_doc="right.md",
            metadata={"retrieval_rank": 2},
            scores={"final_score": 3.9},
        )
        graph.add_node(wrong)
        graph.add_node(right)
        initial = Answer(
            text="-5.2%",
            citations=["wrong"],
            calculations=["ratio_percent row=interest rates: 34.7 / 36.6 * 100 = -5.2%"],
        )
        failed = {
            "answer_supported": False,
            "row_grounded": False,
            "operation_semantics_checked": False,
        }

        generator = FakeGenerator()

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what percent decrease for interest income occurred between 2014 and 2015?",
            initial,
            failed,
            graph,
            generator,
            FakeVerifier(),
        )

        self.assertEqual(answer.text, "16.8%")
        self.assertGreaterEqual(generator.planner_first_calls, 2)
        self.assertTrue(verification["answer_supported"])
        self.assertTrue(verification["repair_applied"])
        self.assertIsNotNone(action)
        self.assertEqual(action.action_type, "REPAIR_NUMERIC_ANSWER")
        self.assertEqual(action.target_node_ids, ["right"])

    def test_does_not_repair_already_supported_answer(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("node", "text", "value 10", source_doc="right.md"))
        initial = Answer(text="10", citations=["node"], calculations=["planned_lookup row=value: 10 = 10"])
        supported = {"answer_supported": True, "row_grounded": True, "operation_semantics_checked": True}

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what is the value?",
            initial,
            supported,
            graph,
            FakeGenerator(),
            FakeVerifier(),
        )

        self.assertIs(answer, initial)
        self.assertIs(verification, supported)
        self.assertIsNone(action)

    def test_rejects_low_rank_self_consistent_repair_candidate(self) -> None:
        graph = EvidenceGraph()
        wrong = EvidenceNode(
            "wrong",
            "text",
            "interest rates table 2014 36.6 2015 34.7",
            source_doc="wrong.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.0},
        )
        low_rank = EvidenceNode(
            "right",
            "text",
            "interest income table 2014 119 2015 99",
            source_doc="right.md",
            metadata={"retrieval_rank": 3},
            scores={"final_score": 3.0},
        )
        graph.add_node(wrong)
        graph.add_node(low_rank)
        initial = Answer(
            text="-5.2%",
            citations=["wrong"],
            calculations=["ratio_percent row=interest rates: 34.7 / 36.6 * 100 = -5.2%"],
        )
        failed = {
            "answer_supported": False,
            "row_grounded": False,
            "operation_semantics_checked": False,
        }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what percent decrease for interest income occurred between 2014 and 2015?",
            initial,
            failed,
            graph,
            FakeGenerator(),
            FakeVerifier(),
        )

        self.assertIs(answer, initial)
        self.assertFalse(verification["repair_applied"])
        self.assertIsNone(action)

    def test_method_runner_does_not_apply_repair_in_open_retrieval(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "report.md").write_text(
                "interest rates 2014 36.6 2015 34.7\n",
                encoding="utf-8",
            )
            runner = MethodRunner({"run": {"output_dir": str(root / "runs")}})

            class RaisingRepairer:
                def repair(self, *args, **kwargs):
                    raise AssertionError("open retrieval should not invoke verifier-guided repair")

            runner.repairer = RaisingRepairer()

            runner.run(
                "what percent decrease for interest income occurred between 2014 and 2015?",
                "full_evigraph",
                corpus_path=str(corpus),
                retrieval_mode="open",
                log_run=False,
            )

    def test_method_runner_allows_repair_in_source_rerank(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "report.md").write_text(
                "interest rates 2014 36.6 2015 34.7\n",
                encoding="utf-8",
            )
            runner = MethodRunner({"run": {"output_dir": str(root / "runs")}})
            calls = []

            class RecordingRepairer:
                def repair(self, query, answer, verification, graph, generator, verifier):
                    calls.append(query)
                    return answer, verification, None

            runner.repairer = RecordingRepairer()

            runner.run(
                "what percent decrease for interest income occurred between 2014 and 2015?",
                "full_evigraph",
                corpus_path=str(corpus),
                source_doc="report.md",
                retrieval_mode="source_rerank",
                log_run=False,
            )

            self.assertEqual(len(calls), 1)

    def test_verifier_grounded_rejection_ablation_keeps_failed_numeric_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "report.md").write_text(
                "| metric | 2022 | 2023 |\n| --- | ---: | ---: |\n| revenue | 10 | 12 |\n",
                encoding="utf-8",
            )
            runner = MethodRunner({"run": {"output_dir": str(root / "runs")}})

            class FakeGenerator:
                def generate(self, query, support_graph):
                    return Answer(
                        text="20.0%",
                        citations=[next(iter(support_graph.nodes))],
                        calculations=["ratio_percent row=wrong row: 2 / 10 * 100 = 20.0%"],
                    )

            class FakeVerifier:
                def verify(self, query, answer, support_graph):
                    return {
                        "answer_supported": False,
                        "unsupported_claims": [],
                        "contradictions": [],
                        "missing_evidence": [],
                        "citation_correct": True,
                        "confidence": 0.2,
                        "context_utilization": "test",
                        "checked_citations": list(answer.citations),
                        "arithmetically_supported": True,
                        "calculation_supported": True,
                        "operation_semantics_checked": True,
                        "row_operation_grounded": False,
                        "semantically_grounded": False,
                        "row_grounded": False,
                    }

            runner.generator = FakeGenerator()
            runner.verifier = FakeVerifier()

            result = runner.run(
                "what percent did revenue increase?",
                "evigraph_wo_verifier_grounded_rejection",
                corpus_path=str(corpus),
                log_run=False,
            )

            self.assertEqual(result["answer"]["text"], "20.0%")
            self.assertNotEqual(result["answer"]["text"], "Insufficient evidence to answer.")


if __name__ == "__main__":
    unittest.main()
