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

    def test_does_not_repair_already_supported_answer_without_better_candidate(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("node", "text", "value 10", source_doc="right.md"))
        initial = Answer(text="10", citations=["node"], calculations=["planned_lookup row=value: 10 = 10"])
        supported = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "calculation_supported": True,
            "arithmetically_supported": True,
        }

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

    def test_does_not_repair_pure_source_consistency_failure(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "wrong_source",
                "text",
                "ipr&d 303.4 cash acquired 303.4",
                source_doc="wrong.md",
                metadata={"retrieval_rank": 4},
                scores={"final_score": 4.0},
            )
        )
        graph.add_node(
            EvidenceNode(
                "other_source",
                "text",
                "ipr&d 53.1 total purchase price net of cash acquired 182.2",
                source_doc="other.md",
                metadata={"retrieval_rank": 1},
                scores={"final_score": 4.5},
            )
        )
        initial = Answer(
            text="100%",
            citations=["wrong_source"],
            calculations=["ratio_percent row=ipr&d denominator_row=cash acquired: 303.4 / 303.4 * 100 = 100.0%"],
        )
        source_failed = {
            "answer_supported": False,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "source_consistent": False,
        }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what percentage of the total cash purchase price net of cash acquired was represented by ipr&d?",
            initial,
            source_failed,
            graph,
            FakeGenerator(),
            FakeVerifier(),
        )

        self.assertIs(answer, initial)
        self.assertIs(verification, source_failed)
        self.assertIsNone(action)

    def test_repairs_source_consistency_failure_when_current_percent_is_implausible(self) -> None:
        graph = EvidenceGraph()
        weak = EvidenceNode(
            "weak",
            "text",
            "purchase price 1.6 cash paid 1137.4",
            source_doc="weak.md",
            metadata={"retrieval_rank": 4},
            scores={"final_score": 4.0},
        )
        strong = EvidenceNode(
            "strong",
            "text",
            "purchase price 1139 cash paid 1137.4",
            source_doc="strong.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 3.9},
        )
        graph.add_node(weak)
        graph.add_node(strong)
        initial = Answer(
            text="71087.5%",
            citations=["weak"],
            calculations=["ratio_percent row=cash paid denominator_row=purchase price: 1137.4 / 1.6 * 100 = 71087.5%"],
        )
        source_failed = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "source_consistent": False,
        }

        class StrongerGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "strong.md" in source_docs:
                    return Answer(
                        text="99.9%",
                        citations=["strong"],
                        calculations=["ratio_percent row=cash paid denominator_row=purchase price: 1137.4 / 1139 * 100 = 99.9%"],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class StrongerVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "row_operation_grounded": True,
                    "semantically_grounded": True,
                    "missing_evidence": [],
                    "confidence": 0.92 if answer.text == "99.9%" else 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what portion of the purchase price is paid in cash?",
            initial,
            source_failed,
            graph,
            StrongerGenerator(),
            StrongerVerifier(),
        )

        self.assertEqual(answer.text, "99.9%")
        self.assertTrue(verification["repair_applied"])
        self.assertIn("source_consistency", action.params["issues"])

    def test_repairs_supported_source_consistency_failure_to_higher_rank_source(self) -> None:
        graph = EvidenceGraph()
        current = EvidenceNode(
            "current",
            "text",
            "purchase obligations 2008 1953 lease obligations 2008 168",
            source_doc="finqa_020_ip_2007_page_75_pdf_2.md",
            metadata={"retrieval_rank": 4},
            scores={"final_score": 4.0},
        )
        higher_rank = EvidenceNode(
            "higher_rank",
            "text",
            "purchase obligations for pulpwood logs and wood chips 2006 2400 total purchase obligations 3264",
            source_doc="finqa_002_ip_2005_page_35_pdf_3.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 3.9},
        )
        graph.add_node(current)
        graph.add_node(higher_rank)
        initial = Answer(
            text="8.6%",
            citations=["current"],
            calculations=["ratio_percent row=lease obligations denominator_row=purchase obligations: 168 / 1953 * 100 = 8.6%"],
        )
        source_failed = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "source_consistent": False,
            "confidence": 0.85,
        }

        class HigherRankGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "finqa_002_ip_2005_page_35_pdf_3.md" in source_docs:
                    return Answer(
                        text="73.5%",
                        citations=["higher_rank"],
                        calculations=["ratio_percent row=pulpwood contracts denominator_row=purchase obligations: 2400 / 3264 * 100 = 73.5%"],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class SourceVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "source_consistent": answer.text == "73.5%",
                    "row_operation_grounded": True,
                    "semantically_grounded": True,
                    "missing_evidence": [],
                    "confidence": 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what percent of purchase obligations in 2006 was set aside for pulpwood logs and wood chips?",
            initial,
            source_failed,
            graph,
            HigherRankGenerator(),
            SourceVerifier(),
        )

        self.assertEqual(answer.text, "73.5%")
        self.assertTrue(verification["repair_applied"])
        self.assertIn("source_consistency", action.params["issues"])

    def test_does_not_rescore_supported_answer_from_rank_five_source_candidate(self) -> None:
        graph = EvidenceGraph()
        current = EvidenceNode(
            "current",
            "text",
            "weighted average discount rate service cost 2016 4.1 2017 2.9 2018 3.2",
            source_doc="rank1.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 5.0},
        )
        right = EvidenceNode(
            "right",
            "text",
            "service cost pension plans 2016 81 2017 110 2018 136",
            source_doc="rank5.md",
            metadata={"retrieval_rank": 5},
            scores={"final_score": 3.5},
        )
        graph.add_node(current)
        graph.add_node(right)
        initial = Answer(
            text="3.4",
            citations=["current"],
            calculations=[
                "planned_average values=weighted average discount rate service cost/2016, "
                "weighted average discount rate service cost/2017, weighted average discount rate service cost/2018: "
                "(4.1 + 2.9 + 3.2) / 3 = 3.4"
            ],
        )
        supported_but_weak = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "source_consistent": True,
            "confidence": 0.85,
        }

        class RankFiveGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "rank5.md" in source_docs:
                    return Answer(
                        text="109",
                        citations=["right"],
                        calculations=[
                            "planned_average values=service cost/pension plans 2016, "
                            "service cost/pension plans 2017, service cost/pension plans 2018: "
                            "(81 + 110 + 136) / 3 = 109"
                        ],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class RankFiveVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "source_consistent": True,
                    "row_operation_grounded": answer.text == "109",
                    "semantically_grounded": answer.text == "109",
                    "missing_evidence": [],
                    "confidence": 0.9 if answer.text == "109" else 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what was the average pension service cost from 2016 to 2018 in millions",
            initial,
            supported_but_weak,
            graph,
            RankFiveGenerator(),
            RankFiveVerifier(),
        )

        self.assertIs(answer, initial)
        self.assertIs(verification, supported_but_weak)
        self.assertIsNone(action)

    def test_repairs_source_consistency_failure_from_rank_five_source_candidate(self) -> None:
        graph = EvidenceGraph()
        current = EvidenceNode(
            "current",
            "text",
            "annual minimum rental 2010 59 2011 9",
            source_doc="rank1.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 5.0},
        )
        right = EvidenceNode(
            "right",
            "text",
            "annual minimum rental 2010 3160 2011 3200",
            source_doc="rank5.md",
            metadata={"retrieval_rank": 5},
            scores={"final_score": 3.5},
        )
        graph.add_node(current)
        graph.add_node(right)
        initial = Answer(
            text="-84.7%",
            citations=["current"],
            calculations=["percent_change: (9 - 59) / 59 * 100 = -84.7%"],
        )
        source_failed = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "source_consistent": False,
            "confidence": 0.85,
        }

        class RankFiveSourceGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "rank5.md" in source_docs:
                    return Answer(
                        text="1.3%",
                        citations=["right"],
                        calculations=["planned_percent_change target=2011 base=2010: (3200 - 3160) / 3160 * 100 = 1.3%"],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class RankFiveSourceVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "source_consistent": answer.text == "1.3%",
                    "row_operation_grounded": True,
                    "semantically_grounded": True,
                    "missing_evidence": [],
                    "confidence": 0.9 if answer.text == "1.3%" else 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what is the percent change in minimum annual rental payment between 2010 and 2011?",
            initial,
            source_failed,
            graph,
            RankFiveSourceGenerator(),
            RankFiveSourceVerifier(),
        )

        self.assertEqual(answer.text, "1.3%")
        self.assertTrue(verification["repair_applied"])
        self.assertIsNotNone(action)
        self.assertIn("source_consistency", action.params["issues"])

    def test_repairs_supported_but_weaker_operand_candidate_when_candidate_has_stronger_support(self) -> None:
        graph = EvidenceGraph()
        weak = EvidenceNode(
            "weak",
            "text",
            "purchase price 1.6 cash paid 1137.4",
            source_doc="weak.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.0},
        )
        strong = EvidenceNode(
            "strong",
            "text",
            "purchase price 1139 cash paid 1137.4",
            source_doc="strong.md",
            metadata={"retrieval_rank": 2},
            scores={"final_score": 3.9},
        )
        graph.add_node(weak)
        graph.add_node(strong)
        initial = Answer(
            text="71087.5%",
            citations=["weak"],
            calculations=["ratio_percent row=cash paid denominator_row=purchase price: 1137.4 / 1.6 * 100 = 71087.5%"],
        )
        supported_but_weak = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
        }

        class StrongerGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "strong.md" in source_docs:
                    return Answer(
                        text="99.9%",
                        citations=["strong"],
                        calculations=["ratio_percent row=cash paid denominator_row=purchase price: 1137.4 / 1139 * 100 = 99.9%"],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class StrongerVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                strong = answer.text == "99.9%"
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "row_operation_grounded": True,
                    "semantically_grounded": True,
                    "missing_evidence": [],
                    "confidence": 0.92 if strong else 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what portion of the purchase price is paid in cash?",
            initial,
            supported_but_weak,
            graph,
            StrongerGenerator(),
            StrongerVerifier(),
        )

        self.assertEqual(answer.text, "99.9%")
        self.assertTrue(verification["repair_applied"])
        self.assertEqual(action.action_type, "REPAIR_NUMERIC_ANSWER")

    def test_does_not_replace_supported_source_matched_answer_with_cross_source_rescore(self) -> None:
        graph = EvidenceGraph()
        current = EvidenceNode(
            "current",
            "text",
            "annual long term debt maturities 2016 204079 2017 766451",
            source_doc="finqa_329_etr_2015_page_131_pdf_1.md",
            metadata={"retrieval_rank": 2, "rerank_boost": "source_doc_match"},
            scores={"final_score": 3.8},
        )
        distractor = EvidenceNode(
            "distractor",
            "text",
            "annual long term debt maturities 2016 270852 2017 766801",
            source_doc="finqa_019_etr_2013_page_118_pdf_2.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.5},
        )
        graph.add_node(distractor)
        graph.add_node(current)
        initial = Answer(
            text="275.6%",
            citations=["current"],
            calculations=[
                "percent_change row=annual long term debt maturities: (766451 - 204079) / 204079 * 100 = 275.6%"
            ],
        )
        supported = {
            "answer_supported": True,
            "row_grounded": True,
            "period_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": True,
            "calculation_supported": True,
            "confidence": 0.85,
        }

        class CrossSourceGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "finqa_019_etr_2013_page_118_pdf_2.md" in source_docs:
                    return Answer(
                        text="183.1%",
                        citations=["distractor"],
                        calculations=[
                            "percent_change row=annual long term debt maturities: (766801 - 270852) / 270852 * 100 = 183.1%"
                        ],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class SupportedVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                return {
                    "answer_supported": True,
                    "row_grounded": True,
                    "period_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": True,
                    "calculation_supported": True,
                    "row_operation_grounded": True,
                    "semantically_grounded": True,
                    "missing_evidence": [],
                    "confidence": 0.95 if answer.text == "183.1%" else 0.85,
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what is the percent change in annual long-term debt maturities from 2016 to 2017?",
            initial,
            supported,
            graph,
            CrossSourceGenerator(),
            SupportedVerifier(),
        )

        self.assertIs(answer, initial)
        self.assertIs(verification, supported)
        self.assertIsNone(action)

    def test_repairs_operand_failure_even_when_row_and_operation_pass(self) -> None:
        graph = EvidenceGraph()
        wrong = EvidenceNode(
            "wrong",
            "text",
            "rental expense 2008 100 2009 105",
            source_doc="wrong.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.0},
        )
        right = EvidenceNode(
            "right",
            "text",
            "rental expense 2008 100 2009 117",
            source_doc="right.md",
            metadata={"retrieval_rank": 2},
            scores={"final_score": 3.9},
        )
        graph.add_node(wrong)
        graph.add_node(right)
        initial = Answer(
            text="5.0%",
            citations=["wrong"],
            calculations=["percent_change row=rental expense: (105 - 100) / 100 * 100 = 5.0%"],
        )
        failed_operand = {
            "answer_supported": False,
            "row_grounded": True,
            "operation_semantics_checked": True,
            "arithmetically_supported": False,
            "calculation_supported": True,
        }

        class OperandGenerator:
            def generate_planner_first(self, query: str, support_graph: EvidenceGraph) -> Answer:
                source_docs = {node.source_doc for node in support_graph.nodes.values()}
                if "right.md" in source_docs:
                    return Answer(
                        text="17.0%",
                        citations=["right"],
                        calculations=["percent_change row=rental expense: (117 - 100) / 100 * 100 = 17.0%"],
                    )
                return initial

            def generate(self, query: str, support_graph: EvidenceGraph) -> Answer:
                return self.generate_planner_first(query, support_graph)

        class OperandVerifier:
            def verify(self, query: str, answer: Answer, support_graph: EvidenceGraph) -> dict:
                supported = answer.text == "17.0%"
                return {
                    "answer_supported": supported,
                    "row_grounded": True,
                    "operation_semantics_checked": True,
                    "arithmetically_supported": supported,
                    "calculation_supported": supported,
                    "missing_evidence": [] if supported else ["Answer contains numeric claims not supported by source numbers."],
                }

        answer, verification, action = VerifierGuidedRepairer().repair(
            "what was the percentage change in rental expense from 2008 to 2009?",
            initial,
            failed_operand,
            graph,
            OperandGenerator(),
            OperandVerifier(),
        )

        self.assertEqual(answer.text, "17.0%")
        self.assertTrue(verification["repair_applied"])
        self.assertIn("operand_support", action.params["issues"])
        self.assertEqual(action.target_node_ids, ["right"])

    def test_operand_candidate_graph_prefers_query_aligned_nodes_within_source(self) -> None:
        graph = EvidenceGraph()
        distractor = EvidenceNode(
            "distractor",
            "text",
            "interest rates 2014 36.6 2015 34.7",
            source_doc="report.md",
            metadata={"retrieval_rank": 1},
            scores={"final_score": 4.0},
        )
        aligned = EvidenceNode(
            "aligned",
            "text",
            "interest income 2014 119 2015 99",
            source_doc="report.md",
            metadata={"retrieval_rank": 1, "neighbor_context": True},
            scores={"final_score": 3.8},
        )
        graph.add_node(distractor)
        graph.add_node(aligned)

        support_graph = VerifierGuidedRepairer()._source_cluster_graphs(
            graph,
            "what percent decrease for interest income occurred between 2014 and 2015?",
            Answer("0", [], ["percent_change row=interest rates: (34.7 - 36.6) / 36.6 * 100 = -5.2%"]),
        )[0]

        self.assertEqual(next(iter(support_graph.nodes)), "aligned")

    def test_rejects_repair_candidate_outside_top_eight_window(self) -> None:
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
            metadata={"retrieval_rank": 9},
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

    def test_method_runner_applies_repair_in_open_retrieval(self) -> None:
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
                retrieval_mode="open",
                log_run=False,
            )
            self.assertEqual(len(calls), 1)

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

    def test_method_runner_records_period_ungrounded_numeric_answer_without_row_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "report.md").write_text(
                "recognized tax-related interest and penalties 2011 16 2012 19 2013 22\n",
                encoding="utf-8",
            )
            runner = MethodRunner({"run": {"output_dir": str(root / "runs")}})

            class FakeGenerator:
                def generate(self, query, support_graph):
                    return Answer(
                        text="15.8%",
                        citations=[next(iter(support_graph.nodes))],
                        calculations=["percent_change row=interest and penalties years=2012->2013: (22 - 19) / 19 * 100 = 15.8%"],
                    )

                def generate_planner_first(self, query, support_graph):
                    return self.generate(query, support_graph)

            runner.generator = FakeGenerator()

            result = runner.run(
                "what was the percentage change in recognized tax-related interest and penalties in 2011?",
                "full_evigraph",
                corpus_path=str(corpus),
                source_doc="report.md",
                retrieval_mode="oracle_doc",
                log_run=False,
            )

            self.assertEqual(result["answer"]["text"], "15.8%")
            self.assertFalse(result["verification"]["period_grounded"])
            self.assertIn(
                "Calculation period or year does not match query terms.",
                result["verification"]["missing_evidence"],
            )


if __name__ == "__main__":
    unittest.main()
