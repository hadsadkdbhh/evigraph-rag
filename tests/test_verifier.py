from __future__ import annotations

import unittest

from evigraph.evidence_graph import EvidenceGraph
from evigraph.schema import Answer, EvidenceNode
from evigraph.verifier import ClaimVerifier


class ClaimVerifierTest(unittest.TestCase):
    def test_rejects_explicit_calculation_year_mismatch(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "node",
                "text",
                "recognized tax-related interest and penalties in 2011 was 16 and 2013 interest rate contracts were 2400.",
            )
        )
        answer = Answer(
            text="11.6%",
            citations=["node"],
            calculations=["percent_change row=interest rate contracts years=2012->2013: (2400 - 2150) / 2150 * 100 = 11.6%"],
        )

        verification = ClaimVerifier().verify(
            "what was the percentage change in the company recognized tax-related interest and penalties in 2011?",
            answer,
            graph,
        )

        self.assertFalse(verification["answer_supported"])
        self.assertFalse(verification["period_grounded"])
        self.assertIn("Calculation period or year does not match query terms.", verification["missing_evidence"])

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

    def test_row_grounding_accepts_cash_flow_reconciliation_row_when_table_header_names_measure(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "table",
                "text",
                (
                    "cash flow data\n"
                    "| metric | 2015 | 2014 |\n"
                    "| --- | ---: | ---: |\n"
                    "| net cash used in working capital2 | 505.3 | 457.7 |\n"
                    "| net income adjusted to reconcile net income to net cashprovided by operating activities1 | 848.2 | 831.2 |"
                ),
                source_doc="report.md",
            )
        )
        answer = Answer(
            text="2.0%",
            citations=["table"],
            calculations=[
                "percent_change row=net income adjusted to reconcile net income to net cashprovided by operating activities1 "
                "years=2014->2015: (848.2 - 831.2) / 831.2 * 100 = 2.0%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what is the percentage increase from 2014-2015 in total cash flow data?",
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

    def test_row_grounding_keeps_colon_inside_structured_row_label(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "table",
                "text",
                "plus : four times tower cash flow 558360 adjusted consolidated cash flow 531822 105.0",
                source_doc="report.md",
            )
        )
        answer = Answer(
            text="105%",
            citations=["table"],
            calculations=[
                "ratio_percent row=plus : four times tower cash flow for the three months ended december 31 2005 "
                "denominator_row=adjusted consolidated cash flow for the twelve months ended december 31 2005: "
                "558360 / 531822 * 100 = 105.0%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what portion of the adjusted consolidated cash flow for the twelve months ended december 31 , 2005 is related to tower cash flow?",
            answer,
            graph,
        )

        self.assertTrue(verification["row_grounded"])
        self.assertTrue(verification["answer_supported"])

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

    def test_operation_semantics_accepts_percent_of_the_change_query(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "segment revenue 2008 6197 2009 6305 1.7", source_doc="report.md"))
        answer = Answer(
            text="1.7%",
            citations=["table"],
            calculations=["percent_change row=segment revenue: (6305 - 6197) / 6197 * 100 = 1.7%"],
        )

        verification = ClaimVerifier().verify(
            "what was the percent of the change in the risk and insurance brokerage services segment revenue from 2008 2009",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_percent_of_change_contribution_plan(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "table",
                "text",
                "2007 net revenue 231.0 rider revenue 3.9 2008 net revenue 252.7 18.0",
                source_doc="report.md",
            )
        )
        answer = Answer(
            text="18%",
            citations=["table"],
            calculations=[
                "planned_percent_of_increase numerator=rider revenue/amount denominator=2008 net revenue/amount-2007 net revenue/amount: 3.9 / (252.7 - 231) * 100 = 18.0%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what percent of the change between net revenue in 2007 and 2008 was due to rider revenue?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_planned_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "operating expenses 2017 100 2018 127.5 27.5", source_doc="report.md"))
        answer = Answer(
            text="27.5%",
            citations=["table"],
            calculations=["planned_percent_change target=operating expenses/2018 base=operating expenses/2017: (127.5 - 100) / 100 * 100 = 27.5%"],
        )

        verification = ClaimVerifier().verify(
            "what is the percentual increase in the operating expenses during 2017 and 2018?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_implicit_percent_increase(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "total revenue 2011 11287 2010 8512 32.6", source_doc="report.md"))
        answer = Answer(
            text="32.6%",
            citations=["table"],
            calculations=[
                "implicit_percent_increase row=total revenue years=2010->2011: (11287 - 8512) / 8512 * 100 = 32.6%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what is the increase observed in the total revenue during 2010 and 2011?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

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

    def test_operation_semantics_accepts_next_period_ratio(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "2008 83382 total 249038 33.5", source_doc="report.md"))
        answer = Answer(
            text="33.5%",
            citations=["table"],
            calculations=[
                "future_minimum_payment_next_period_ratio year=2008 denominator=total: 83382 / 249038 = 0.334816 * 100 = 33.5%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what portion of the future minimum operating lease payments is due in the next 12 months?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_cash_flow_result_sum(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "operating activities 2547.2 investing activities -1641.6 financing activities -1359.8", source_doc="report.md"))
        answer = Answer(
            text="-454.2",
            citations=["table"],
            calculations=[
                "cash_flow_result year=2018 rows=operating activities; investing activities; financing activities: 2547.2 + -1641.6 + -1359.8 = -454.2"
            ],
        )

        verification = ClaimVerifier().verify(
            "considering the year 2018 , what is the cash flow result?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_planned_plain_ratio_for_ratio_query(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "2011 453815 thereafter 2996337 0.2", source_doc="report.md"))
        answer = Answer(
            text="0.2",
            citations=["table"],
            calculations=["planned_ratio target=2011/value base=thereafter/value: 453815 / 2.99634e+06 = 0.2"],
        )

        verification = ClaimVerifier().verify(
            "as of december 2007 what was the ratio of the future debt maturities for 2011 to the amounts after 2012",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])

    def test_operation_semantics_accepts_percent_higher_between_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "foreign exchange products 1.8 interest-rate products 1.25 44.0", source_doc="report.md"))
        answer = Answer(
            text="44%",
            citations=["table"],
            calculations=[
                "relative_difference_between_rows row=foreign exchange products denominator_row=interest-rate products: (1.8 - 1.25) / 1.25 * 100 = 44.0%"
            ],
        )

        verification = ClaimVerifier().verify(
            "what percent higher is the average var for foreign exchange products than that of interest rate products?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])

    def test_operation_semantics_accepts_percentage_point_difference(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(EvidenceNode("table", "text", "americas 2003 51.2 2001 47.4 3.8", source_doc="report.md"))
        answer = Answer(
            text="3.8%",
            citations=["table"],
            calculations=["percentage_point_row_difference row=americas: 51.2 - 47.4 = 3.8"],
        )

        verification = ClaimVerifier().verify(
            "what was the difference in operating profit for the americas as a percentage of net sales between 2001 and 2003?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])

    def test_operation_semantics_accepts_planned_absolute_difference(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                "table",
                "text",
                "entergy arkansas payments 2 entergy louisiana payments 6 difference 4",
                source_doc="report.md",
            )
        )
        answer = Answer(
            text="4",
            citations=["table"],
            calculations=[
                "planned_absolute_difference target=entergy arkansas/payments base=entergy louisiana/payments: abs(2 - 6) = 4"
            ],
        )

        verification = ClaimVerifier().verify(
            "what is the difference in payments between entergy arkansas and entergy louisiana?",
            answer,
            graph,
        )

        self.assertTrue(verification["operation_semantics_checked"])
        self.assertTrue(verification["answer_supported"])


if __name__ == "__main__":
    unittest.main()
