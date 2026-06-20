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
        self.assertTrue(verification["operation_semantics_checked"])

    def test_row_grounding_accepts_generic_period_row_when_context_names_measure(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "table",
                "text",
                (
                    "The following is a reconciliation of the beginning and ending amounts "
                    "of unrecognized tax benefits.\n"
                    "| december 31, | 2016 | 2015 |\n"
                    "| balance at december 31 | $ 369 | $ 373 |"
                ),
                source_doc="report.md",
            )
        )
        answer = Answer(
            text="-1.1%",
            citations=["table"],
            calculations=["percent_change row=balance at december 31: (369 - 373) / 373 * 100 = -1.1%"],
        )

        verification = ClaimVerifier().verify(
            "what was the percentage change in the unrecognized tax benefits from 2015 to 2016?",
            answer,
            graph,
        )

        self.assertTrue(verification["row_grounded"])
        self.assertTrue(verification["row_operation_grounded"])
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
        self.assertTrue(verification["operation_semantics_checked"])
        self.assertEqual(verification["context_utilization"], "numeric_calculation_row_operation_and_citation_checked")

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

    def test_operation_semantics_rejects_ratio_for_percent_change_query(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "commodities net 2017 47 2016 73 64.4", source_doc="report.md"))
        answer = Answer(
            text="64.4%",
            citations=["table"],
            calculations=["ratio_percent row=commodities net denominator_row=commodities net: 47 / 73 * 100 = 64.4%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage change in net commodities from 2016 to 2017?",
            answer,
            graph,
        )

        self.assertFalse(verification["operation_semantics_checked"])
        self.assertFalse(verification["row_operation_grounded"])
        self.assertFalse(verification["semantically_grounded"])
        self.assertFalse(verification["answer_supported"])
        self.assertIn("Calculation operation type does not match query intent.", verification["missing_evidence"])

    def test_operation_semantics_accepts_ratio_for_portion_query(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "mutual funds 9223 total investments 26410 34.9", source_doc="report.md"))
        answer = Answer(
            text="34.9%",
            citations=["table"],
            calculations=["ratio_percent row=mutual funds denominator_row=total investments: 9223 / 26410 * 100 = 34.9%"],
        )

        verification = ClaimVerifier().verify(
            "what portion of the total investment is allocated to mutual funds in 2011?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])


if __name__ == "__main__":
    unittest.main()
