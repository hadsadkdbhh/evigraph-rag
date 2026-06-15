from __future__ import annotations

import unittest

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Answer, EvidenceNode
from evigraph.verifier import ClaimVerifier


class ClaimVerifierTest(unittest.TestCase):
    def test_row_grounding_accepts_matching_calculation_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "commodities net 2017 47 2016 73 -35.6", source_doc="report.md"))
        answer = Answer(
            text="-35.6%",
            citations=["table"],
            calculations=["percent_change row=commodities net: (47 - 73) / 73 * 100 = -35.6%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage change in net commodities from 2016 to 2017?",
            answer,
            graph,
        )

        self.assertTrue(verification["row_grounded"])
        self.assertTrue(verification["row_operation_grounded"])
        self.assertTrue(verification["semantically_grounded"])
        self.assertTrue(verification["answer_supported"])

    def test_row_grounding_rejects_unmatched_calculation_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "interest rates net 2017 47 2016 73 -35.6", source_doc="report.md"))
        answer = Answer(
            text="-35.6%",
            citations=["table"],
            calculations=["percent_change row=interest rates net: (47 - 73) / 73 * 100 = -35.6%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage change in net commodities from 2016 to 2017?",
            answer,
            graph,
        )

        self.assertFalse(verification["row_grounded"])
        self.assertFalse(verification["row_operation_grounded"])
        self.assertFalse(verification["answer_supported"])
        self.assertIn("Calculation row label does not match query terms.", verification["missing_evidence"])

    def test_calculation_result_supports_numeric_answer(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("text", "text", "interest expense of $914 million increased by $23 million", source_doc="report.md"))
        answer = Answer(
            text="2.6%",
            citations=["text"],
            calculations=["percent_delta row=interest expense: 23 / 891 * 100 = 2.6%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage increase in interest expense?",
            answer,
            graph,
        )

        self.assertTrue(verification["calculation_supported"])
        self.assertTrue(verification["arithmetically_supported"])
        self.assertTrue(verification["semantically_grounded"])
        self.assertTrue(verification["answer_supported"])
        self.assertEqual(verification["context_utilization"], "numeric_calculation_row_and_citation_checked")

    def test_calculation_inputs_do_not_support_wrong_numeric_answer(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("text", "text", "interest expense of $914 million increased by $23 million", source_doc="report.md"))
        answer = Answer(
            text="23%",
            citations=["text"],
            calculations=["percent_delta row=interest expense: 23 / 891 * 100 = 2.6%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage increase in interest expense?",
            answer,
            graph,
        )

        self.assertFalse(verification["calculation_supported"])
        self.assertFalse(verification["arithmetically_supported"])
        self.assertFalse(verification["answer_supported"])


if __name__ == "__main__":
    unittest.main()
