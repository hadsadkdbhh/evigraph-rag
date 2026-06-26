from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evigraph.evidence_graph import EvidenceGraph
from evigraph.generator import SupportOnlyGenerator
from evigraph.metrics import numeric_exact_match
from evigraph.numeric_planner import HeuristicNumericPlanClient, NumericPlannerFallback
from evigraph.retrieval import CorpusRetriever
from evigraph.schema import EvidenceNode


class NumericReasoningTest(unittest.TestCase):
    def test_numeric_contexts_prefer_retrieval_rank_order(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="rank2_wrong",
                node_type="text",
                content=(
                    "|  | 2016 | 2015 |\n"
                    "| --- | --- | --- |\n"
                    "| total redeemable stock of subsidiaries | $ 100 | $ 100 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 2},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="rank1_correct",
                node_type="text",
                content=(
                    "|  | 2016 | 2015 |\n"
                    "| --- | --- | --- |\n"
                    "| total redeemable stock of subsidiaries | $ 353 | $ 109 |\n"
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 1},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in millions of total redeemable stock of subsidiaries from 2015 to 2016?",
            graph,
        )

        self.assertEqual(answer.text, "244")
        self.assertEqual(answer.citations, ["rank1_correct"])

    def test_row_matching_skips_weak_single_term_overlap(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="rank1_weak",
                node_type="text",
                content=(
                    "|  | 2016 | 2015 |\n"
                    "| --- | --- | --- |\n"
                    "| plus contingently issuable performance stock units | 2014 | 2014 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="rank2_correct",
                node_type="text",
                content=(
                    "|  | 2016 | 2015 |\n"
                    "| --- | --- | --- |\n"
                    "| total redeemable stock of subsidiaries | $ 782 | $ 538 |\n"
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in millions of total redeemable stock of subsidiaries from 2015 to 2016?",
            graph,
        )

        self.assertEqual(answer.text, "244")
        self.assertEqual(answer.citations, ["rank2_correct"])

    def test_numeric_contexts_read_retrieved_chunk_before_neighbor_context(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="neighbor_1_case_0_2",
                node_type="text",
                content="Later allocation values included 27.0 and 36.5 in adjacent discussion.",
                source_doc="case.md",
                metadata={"retrieval_rank": 1, "neighbor_context": True},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_case_0_1",
                node_type="text",
                content=(
                    "The aggregate purchase price was $171.5 million, "
                    "and was subsequently increased to $173.2 million, subject to post-closing adjustments."
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 1},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "for the mtn deal , what was the total post closing adjustments , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "1.7")
        self.assertEqual(answer.citations, ["retrieved_1_case_0_1"])

    def test_percent_change_from_year_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| annual long-term debt maturities | amount ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| 2016 | $ 204079 |\n"
                    "| 2017 | $ 766451 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percent change in annual long-term debt maturities from 2016 to 2017?",
            graph,
        )

        self.assertEqual(answer.text, "275.6%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_year_difference_prefers_ending_or_period_end_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| as of or for the year ended december 31 ( in millions ) | 2018 | 2017 | 2016 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| available-for-sale investment securities ( average ) | 203449 | 219345 | 226892 |\n"
                    "| afs investment securities ( period-end ) | 228681 | 200247 | 236670 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the net change in ending available for sale investment securities from 2017 to 2018?",
            graph,
        )

        self.assertEqual(answer.text, "28434")
        self.assertIn("period-end", answer.calculations[0])

    def test_year_difference_stitches_period_end_continuation_chunk(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_case_0_0",
                node_type="text",
                content=(
                    "| as of or for the year ended december 31 ( in millions ) | 2018 | 2017 | 2016 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| investment securities gains/ ( losses ) | $ -395 | $ -78 | $ 132 |\n"
                    "| available-for-sale investment securities ( average ) | 203449 | 219345 | 226892 |\n"
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_2_case_0_1",
                node_type="text",
                content=(
                    "| available-for-sale investment securities ( average ) | 203449 | 219345 | 226892 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| held-to-maturity investment securities ( average ) | 31747 | 47927 | 51358 |\n"
                    "| afs investment securities ( period-end ) | 228681 | 200247 | 236670 |\n"
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the net change in ending available for sale investment securities from 2017 to 2018?",
            graph,
        )

        self.assertEqual(answer.text, "28434")
        self.assertIn("period-end", answer.calculations[0])
        self.assertEqual(answer.citations, ["retrieved_1_case_0_0", "retrieved_2_case_0_1"])

    def test_percent_change_prefers_specific_table_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| $ in millions | as of december 2017 | as of december 2016 |\n"
                    "| --- | --- | --- |\n"
                    "| interest rates net | $ -410 ( 410 ) | $ -381 ( 381 ) |\n"
                    "| credit net | $ 1505 | $ 2504 |\n"
                    "| commodities net | $ 47 | $ 73 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage change in net comodities from 2016 to 2017?",
            graph,
        )

        self.assertEqual(answer.text, "-35.6%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_higher_averages_matching_metric_columns_between_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| years ended december 31 ( in millions ) | 2008 annual average | 2008 maximum | 2008 minimum | 2007 annual average | 2007 maximum | 2007 minimum |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n"
                    "| foreign exchange products | $ 1.8 | $ 4.7 | $ .3 | $ 1.8 | $ 4.0 | $ .7 |\n"
                    "| interest-rate products | 1.1 | 2.4 | .6 | 1.4 | 3.7 | .1 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percent higher is the average var for foreign exchange products than that of interest rate products?",
            graph,
        )

        self.assertEqual(answer.text, "44%")
        self.assertIn("relative_difference_between_rows", answer.calculations[0])

    def test_difference_in_percentage_row_between_years_returns_percentage_points(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year ended december 31, | 2003 | 2002 | 2001 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| americas | 51.2% ( 51.2 % ) | 48.3% ( 48.3 % ) | 47.4% ( 47.4 % ) |\n"
                    "| europe | 26.3 | 24.4 | 19.5 |\n"
                    "| asia pacific | 45.3 | 46.1 | 45.4 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the difference in operating profit for the americas as a percentage of net sales between 2001 and 2003?",
            graph,
        )

        self.assertEqual(answer.text, "3.8%")
        self.assertIn("percentage_point_row_difference", answer.calculations[0])

    def test_percent_change_prefers_ending_balance_for_unrecognized_tax_benefits(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "The following is a reconciliation of the beginning and ending amounts "
                    "of unrecognized tax benefits for the periods indicated.\n"
                    "| december 31, | 2016 | 2015 | 2014 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| balance at january 1 | $ 373 | $ 394 | $ 392 |\n"
                    "| additions for current year tax positions | 8 | 7 | 7 |\n"
                    "| balance at december 31 | $ 369 | $ 373 | $ 394 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage change in the unrecognized tax benefits from 2015 to 2016?",
            graph,
        )

        self.assertEqual(answer.text, "-1.1%")
        self.assertIn("row=balance at december 31", answer.calculations[0])

    def test_percent_change_promotes_wrapped_year_header(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| $ in millions | level 3 asse |\n"
                    "| --- | --- |\n"
                    "| $ in millions | level 3 assets as of december 2017 | level 3 assets as of december 2016 |\n"
                    "| interest rates net | $ -410 ( 410 ) | $ -381 ( 381 ) |\n"
                    "| commodities net | $ 47 | $ 73 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage change in net comodities from 2016 to 2017?",
            graph,
        )

        self.assertEqual(answer.text, "-35.6%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_change_from_query_aligned_prose_sentence(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "Other obligations were $17.3 million as of May 26, 2019. "
                    "Our accrued trade liabilities were $484 million as of May 26, 2019, "
                    "and $500 million as of May 27, 2018."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage change of our accrued trade liabilities in 2019 compared to 2018",
            graph,
        )

        self.assertEqual(answer.text, "-3.2%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_of_the_change_routes_to_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year | segment revenue |\n"
                    "| --- | ---: |\n"
                    "| 2008 | 6197 |\n"
                    "| 2009 | 6305 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percent of the change in the risk and insurance brokerage services segment revenue from 2008 2009",
            graph,
        )

        self.assertEqual(answer.text, "1.7%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_change_prefers_respectively_prose_when_values_follow_years(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "| as of december 31, | increase in fair market value |\n"
                    "| --- | ---: |\n"
                    "| 2015 | -33.7 |\n"
                    "| 2014 | -35.5 |\n"
                    "During 2015 and 2014, we had interest income of $ 22.8 and $ 27.4, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage change in interest income from 2014 to 2015?",
            graph,
        )

        self.assertEqual(answer.text, "-16.8%")
        self.assertIn("row=interest income", answer.calculations[0])

    def test_what_percent_decrease_reports_positive_magnitude_from_respectively_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content="During 2015 and 2014, we had interest income of $ 22.8 and $ 27.4, respectively.",
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percent decrease for interest income occurred between 2014 and 2015?",
            graph,
        )

        self.assertEqual(answer.text, "16.8%")
        self.assertIn("row=interest income", answer.calculations[0])

    def test_percent_of_change_due_to_contribution_uses_planner(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| metric | amount |\n"
                    "| --- | ---: |\n"
                    "| 2007 net revenue | 231.0 |\n"
                    "| rider revenue | 3.9 |\n"
                    "| 2008 net revenue | 252.7 |\n"
                ),
                source_doc="report.md",
            )
        )
        planner = NumericPlannerFallback(HeuristicNumericPlanClient())

        answer = SupportOnlyGenerator(planner_fallback=planner).generate(
            "what percent of the change between net revenue in 2007 and 2008 was due to rider revenue?",
            graph,
        )

        self.assertEqual(answer.text, "18%")
        self.assertIn("planned_percent_of_increase", answer.calculations[0])

    def test_percentual_increase_routes_to_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| metric | 2017 | 2018 |\n"
                    "| --- | ---: | ---: |\n"
                    "| operating expenses | 100 | 127.5 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentual increase in the operating expenses during 2017 and 2018?",
            graph,
        )

        self.assertEqual(answer.text, "27.5%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_increase_routes_to_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2003 | 2002 |\n"
                    "| --- | --- | --- |\n"
                    "| inventories | $ 180.0 | $ 87.9 |\n"
                    "| raw materials and work in progress | $ 90.8 | $ 44.3 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percent increase did inventories receive between 2002 and 2003?",
            graph,
        )

        self.assertEqual(answer.text, "104.8%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percentage_growth_routes_to_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2018 | 2017 |\n"
                    "| --- | --- | --- |\n"
                    "| operating profit as reported | $ 1211 | $ 1194 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage growth in the operating profit as reported from 2017 to 2018",
            graph,
        )

        self.assertEqual(answer.text, "1.4%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percentage_growth_uses_table_caption_terms_for_row_match(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "Annual net sales for each business segment were as follows.\n"
                    "| ( in millions ) | 2017 | 2016 | 2015 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| cabinets | $ 2467.1 | $ 2397.8 | $ 2173.4 |\n"
                    "| plumbing | 1720.8 | 1534.4 | 1414.5 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage growth in sales of cabinets from 2016 to 2017",
            graph,
        )

        self.assertEqual(answer.text, "2.9%")
        self.assertIn("row=cabinets", answer.calculations[0])

    def test_percentage_reduction_routes_to_percent_change(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2013 | 2014 |\n"
                    "| --- | --- | --- |\n"
                    "| loews common stock | 126.23 | 110.59 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage reduction in the loews common stock from 2013 to 2014",
            graph,
        )

        self.assertEqual(answer.text, "-12.4%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_increase_from_current_value_and_delta_phrase(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content="Interest expense, net, of $914 million increased by $23 million, due primarily to higher average debt levels.",
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage increase in interest expense?",
            graph,
        )

        self.assertEqual(answer.text, "2.6%")
        self.assertIn("percent_delta", answer.calculations[0])

    def test_reverse_stock_split_reduction_from_to_phrase(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "The reverse stock split reduced the number of shares of common stock outstanding "
                    "from approximately 1.3 billion shares to approximately 0.4 billion shares."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "considering the reverse stock split, what was the percentual reduction of the common stock outstanding shares?",
            graph,
        )

        self.assertEqual(answer.text, "69.2%")
        self.assertIn("percent_change_from_to", answer.calculations[0])

    def test_reverse_stock_split_prefers_from_to_phrase_before_unrelated_year_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="wrong_table",
                node_type="text",
                content=(
                    "|  | 2017 | 2016 |\n"
                    "| --- | --- | --- |\n"
                    "| class a common stock issued and outstanding | 339235 | 338240 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="split_phrase",
                node_type="text",
                content=(
                    "The reverse stock split reduced the number of shares of common stock outstanding "
                    "from approximately 1.3 billion shares to approximately 0.4 billion shares."
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "considering the reverse stock split, what was the percentual reduction of the common stock outstanding shares?",
            graph,
        )

        self.assertEqual(answer.text, "69.2%")
        self.assertEqual(answer.citations, ["split_phrase"])

    def test_percent_change_from_respectively_year_sequence(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "Rental expense for operating leases was approximately $66.9 million, "
                    "$57.2 million and $49.0 million during the years ended December 31, "
                    "2010, 2009 and 2008, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage change in rental expense for operating leases from 2008 to 2009?",
            graph,
        )

        self.assertEqual(answer.text, "16.7%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_change_respectively_ignores_preceding_table_years(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "| 2011 | $ 62465 |\n"
                    "| --- | --- |\n"
                    "| 2012 | 54236 |\n"
                    "| 2013 | 47860 |\n"
                    "| 2014 | 37660 |\n"
                    "| 2015 | 28622 |\n"
                    "rental expense for operating leases was approximately $66.9 million, "
                    "$57.2 million and $49.0 million during the years ended December 31, "
                    "2010, 2009 and 2008, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage change in rental expense for operating leases from 2008 to 2009?",
            graph,
        )

        self.assertEqual(answer.text, "16.7%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_change_respectively_prose_beats_distractor_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "| restricted stock units | number of rsus | weighted average grant date fair value |\n"
                    "| --- | ---: | ---: |\n"
                    "| rsus at december 31 2008 | 401375 | $ 29.03 |\n"
                    "| rsus at december 31 2009 | 1683606 | $ 12.23 |\n"
                    "Compensation cost recognized for RSUs totaled $7.3 million, "
                    "$4.9 million and $3.0 million for the years ended December 31, "
                    "2009, 2008 and 2007, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percent of the increase in compensation cost recognized for rsus from 2008 to 2009",
            graph,
        )

        self.assertEqual(answer.text, "49.0%")
        self.assertIn("compensation cost recognized rsus", answer.calculations[0])

    def test_percent_change_year_value_fallback_prefers_query_matching_context(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="wrong_year_values",
                node_type="text",
                content=(
                    "Rental expense for operating leases.\n"
                    "| year | value |\n"
                    "| --- | --- |\n"
                    "| 2010 | 31 |\n"
                    "| 2011 | 62465 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="matching_year_values",
                node_type="text",
                content=(
                    "Minimum annual rental payments under noncancelable leases.\n"
                    "| year | value |\n"
                    "| --- | --- |\n"
                    "| 2010 | 3160 |\n"
                    "| 2011 | 3200 |\n"
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percent change in minimum annual rental payment between 2010 and 2011?",
            graph,
        )

        self.assertEqual(answer.text, "1.3%")
        self.assertEqual(answer.citations, ["matching_year_values"])

    def test_growth_rate_uses_latest_two_table_years_when_query_has_no_years(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( in millions ) | for the years ended december 31 , 2017 | for the years ended december 31 , 2016 | for the years ended december 31 , 2015 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| net earnings attributable to pmi | $ 6035 | $ 6967 | $ 6873 |\n"
                    "| net earnings for basic and diluted eps | $ 6021 | $ 6948 | $ 6849 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the growth rate of the net earnings attributable to pmi?",
            graph,
        )

        self.assertEqual(answer.text, "-13.4%")
        self.assertIn("row=net earnings attributable to pmi", answer.calculations[0])

    def test_growth_rate_ignores_truncated_table_fragment_before_full_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( in millions ) | for the years ended december 31 , 2017 | for the years ended december 31 ,\n"
                    "basic and diluted earnings per share were calculated using the following:\n"
                    "| ( in millions ) | for the years ended december 31 , 2017 | for the years ended december 31 , 2016 | for the years ended december 31 , 2015 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| net earnings attributable to pmi | $ 6035 | $ 6967 | $ 6873 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the growth rate of the net earnings attributable to pmi?",
            graph,
        )

        self.assertEqual(answer.text, "-13.4%")
        self.assertIn("row=net earnings attributable to pmi", answer.calculations[0])

    def test_growth_rate_from_year_labeled_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2002 net revenue | $ 922.9 |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                    "| 2003 net revenue | $ 973.7 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the growth rate in net revenue in 2003 for entergy louisiana , inc.?",
            graph,
        )

        self.assertEqual(answer.text, "5.5%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_percent_change_prefers_nonzero_fiscal_schedule_over_earlier_lookalike(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="lookalike",
                node_type="text",
                content=(
                    "The following table summarizes the estimated aggregate amortization expense.\n"
                    "| year | amortization amount ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2016 | $ 45 |\n"
                    "| 2017 | $ 45 |\n"
                ),
                source_doc="wrong.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="schedule",
                node_type="text",
                content=(
                    "The estimated amortization expense for each of the five succeeding fiscal years was as follows.\n"
                    "| fiscal 2016 | $ 377.0 |\n"
                    "| --- | --- |\n"
                    "| fiscal 2017 | $ 365.6 |\n"
                    "| fiscal 2018 | $ 355.1 |\n"
                ),
                source_doc="correct.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the expected growth rate in amortization expense from 2016 to 2017?",
            graph,
        )

        self.assertEqual(answer.text, "-3.0%")
        self.assertEqual(answer.citations, ["schedule"])

    def test_roi_from_stock_return_table_uses_index_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| | 12/29/2007 | 1/3/2009 | 1/2/2010 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| cadence design systems inc . | 100.00 | 22.55 | 35.17 |\n"
                    "| nasdaq composite | 100.00 | 59.03 | 82.25 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the roi of nasdaq composite from 2008 to 2009?",
            graph,
        )

        self.assertEqual(answer.text, "-41.0%")
        self.assertIn("roi", answer.calculations[0])

    def test_roi_from_sp500_table_handles_compact_query_token(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| company/index | december 30 2006 | january 3 2009 |\n"
                    "| --- | --- | --- |\n"
                    "| advance auto parts | $ 100.00 | $ 97.26 |\n"
                    "| s&p 500 index | 100.00 | 65.70 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the roi of an investment in s&p500 index from 2006 to january 3 , 2009?",
            graph,
        )

        self.assertEqual(answer.text, "-34.3%")
        self.assertIn("row=s&p 500 index", answer.calculations[0])

    def test_roi_from_sp500_table_recovers_truncated_year_header(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="truncated_table",
                node_type="text",
                content=(
                    "| company/index | december 30 2006 | december 29 2007 | january 3 2009 | january 2 2010 |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| advance auto parts | $ 100.00 | $ 108.00 | $ 97.\n"
                    "ary 3 2009 | january 2 2010 |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| advance auto parts | $ 100.00 | $ 108.00 | $ 97.26 | $ 116.01 |\n"
                    "| s&p 500 index | 100.00 | 104.24 | 65.70 | 78.62 |\n"
                    "| s&p retail index | 100.00 | 82.15 | 58.29 | 82.36 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the roi of an investment in s&p500 index from 2006 to january 3 , 2009?",
            graph,
        )

        self.assertEqual(answer.text, "-34.3%")
        self.assertIn("row=s&p 500 index", answer.calculations[0])

    def test_roi_from_sp500_table_combines_same_source_chunks(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_finqa_086_aap_2011_page_28_pdf_2_0_0",
                node_type="text",
                content=(
                    "| company/index | december 30 2006 | december 29 2007 | january 3 2009 | january 2 2010 |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| advance auto parts | $ 100.00 | $ 108.00 | $ 97."
                ),
                source_doc="finqa_086_aap_2011_page_28_pdf_2.md",
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_2_finqa_086_aap_2011_page_28_pdf_2_0_1",
                node_type="text",
                content=(
                    "ary 3 2009 | january 2 2010 |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| advance auto parts | $ 100.00 | $ 108.00 | $ 97.26 | $ 116.01 |\n"
                    "| s&p 500 index | 100.00 | 104.24 | 65.70 | 78.62 |\n"
                    "| s&p retail index | 100.00 | 82.15 | 58.29 | 82.36 |\n"
                ),
                source_doc="finqa_086_aap_2011_page_28_pdf_2.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the roi of an investment in s&p500 index from 2006 to january 3 , 2009?",
            graph,
        )

        self.assertEqual(answer.text, "-34.3%")
        self.assertIn("row=s&p 500 index", answer.calculations[0])
        self.assertEqual(
            set(answer.citations),
            {
                "retrieved_1_finqa_086_aap_2011_page_28_pdf_2_0_0",
                "retrieved_2_finqa_086_aap_2011_page_28_pdf_2_0_1",
            },
        )

    def test_total_debt_percent_change_reports_magnitude(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content="Our total debt was $28.5 billion at December 31, 2015, and $29.5 billion at December 31, 2014.",
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percentage change in total debt from 2014 to 2015?",
            graph,
        )

        self.assertEqual(answer.text, "3.4%")
        self.assertIn("percent_change", answer.calculations[0])

    def test_ratio_percent_from_table_and_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="evidence",
                node_type="text",
                content=(
                    "foodservice net sales declined to $ 396 million in 2006.\n"
                    "|  | 2006 | 2005 |\n"
                    "| --- | --- | --- |\n"
                    "| sales | $ 2455 | $ 2245 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2006 what percentage of consumer packaging sales were represented by foodservice net sales?",
            graph,
        )

        self.assertEqual(answer.text, "16.1%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_represented_by_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| current assets | $ 28.1 |\n"
                    "| --- | --- |\n"
                    "| ipr&d | 190.0 |\n"
                    "| total cash purchase price net of cash acquired | $ 320.1 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total cash purchase price net of cash acquired was represented by ipr&d?",
            graph,
        )

        self.assertEqual(answer.text, "59.4%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_represented_by_prose_amount_with_thousand_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "The total purchase consideration consisted of: ( in thousands ).\n"
                    "|  | ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| cash paid | $ 11001 |\n"
                    "| total purchase price | $ 15704 |\n"
                    "Goodwill, representing the excess of the purchase price over net assets, "
                    "was $3.4 million."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total purchase price is represented by goodwill?",
            graph,
        )

        self.assertEqual(answer.text, "21.7%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_paid_in_cash_uses_cash_row_as_numerator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "The aggregate purchase price for R2 of approximately $220600 consisted of "
                    "cash paid of $6900.\n"
                    "| item | amount |\n"
                    "| --- | ---: |\n"
                    "| cash paid | $ 6900 |\n"
                    "| estimated purchase price | $ 220600 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the estimated purchase price of r2 is paid in cash?",
            graph,
        )

        self.assertEqual(answer.text, "3.1%")
        self.assertIn("row=cash paid", answer.calculations[0])
        self.assertIn("6900 / 220600", answer.calculations[0])

    def test_ratio_percent_paid_in_cash_combines_split_purchase_price_chunks(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_finqa_008_holx_2007_page_128_pdf_2_0_1",
                node_type="text",
                content=(
                    "The aggregate purchase price for R2 of approximately $220600 consisted of "
                    "approximately 4400 shares of Hologic common stock valued at $205500, "
                    "cash paid of $6900, debt assumed of $5700 and approximately $2500 for "
                    "acquisition related fees and expenses."
                ),
                source_doc="finqa_008_holx_2007_page_128_pdf_2.md",
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_2_finqa_008_holx_2007_page_128_pdf_2_0_2",
                node_type="text",
                content=(
                    "| net tangible assets acquired as of july 13 2006 | $ 1200 |\n"
                    "| --- | --- |\n"
                    "| goodwill | 145500 |\n"
                    "| estimated purchase price | $ 220600 |\n"
                ),
                source_doc="finqa_008_holx_2007_page_128_pdf_2.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the estimated purchase price of r2 is paid in cash?",
            graph,
        )

        self.assertEqual(answer.text, "3.1%")
        self.assertIn("row=cash paid", answer.calculations[0])
        self.assertIn("6900 / 220600", answer.calculations[0])

    def test_ratio_percent_rejects_same_row_numerator_and_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2007 |\n"
                    "| --- | --- |\n"
                    "| sales | $ 5245 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of industrial packaging sales where represented by european industrial packaging net sales in 2007?",
            graph,
        )

        self.assertNotEqual(answer.text, "100%")

    def test_ratio_percent_allocated_to_year_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2011 | 2010 |\n"
                    "| --- | --- | --- |\n"
                    "| money market funds | $ 17187 | $ 1840 |\n"
                    "| mutual funds | 9223 | 6850 |\n"
                    "| total deferred compensation plan investments | $ 26410 | $ 8690 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the total investment is allocated to mutual funds in 2011?",
            graph,
        )

        self.assertEqual(answer.text, "34.9%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_is_phrase_uses_suffix_as_numerator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| item | amount |\n"
                    "| --- | ---: |\n"
                    "| total purchase price net of cash acquired | 182.2 |\n"
                    "| ipr&d | 52.84 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total purchase price net of cash acquired is ipr&d ?",
            graph,
        )

        self.assertEqual(answer.text, "29%")
        self.assertIn("row=ipr&d", answer.calculations[0])
        self.assertIn("denominator_row=total purchase price net of cash acquired", answer.calculations[0])

    def test_ratio_percent_prefix_where_phrase_uses_prefix_as_numerator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| segment | 2008 |\n"
                    "| --- | ---: |\n"
                    "| north american consumer packaging net sales | 2492 |\n"
                    "| consumer packaging sales | 3195 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "north american consumer packaging net sales where what percentage of consumer packaging sales in 2008?",
            graph,
        )

        self.assertEqual(answer.text, "78%")
        self.assertIn("north american consumer packaging net sales", answer.calculations[0])
        self.assertIn("denominator_row=consumer packaging sales", answer.calculations[0])

    def test_ratio_percent_uses_query_year_for_prose_numerator_and_scoped_sales_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "consumer packaging in millions 2009 2008 2007 .\n"
                    "| in millions | 2009 | 2008 | 2007 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 3060 | $ 3195 | $ 3015 |\n"
                    "| operating profit | 433 | 17 | 112 |\n"
                    "north american consumer packaging net sales were $ 2.2 billion compared "
                    "with $ 2.5 billion in 2008 and $ 2.4 billion in 2007 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "north american consumer packaging net sales where what percentage of consumer packaging sales in 2008?",
            graph,
        )

        self.assertEqual(answer.text, "78.2%")
        self.assertIn("2500", answer.calculations[0])
        self.assertIn("3195", answer.calculations[0])

    def test_ratio_percent_uses_scoped_sales_denominator_for_foodservice_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "consumer packaging in millions 2006 2005 2004 .\n"
                    "| in millions | 2006 | 2005 | 2004 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 2455 | $ 2245 | $ 2295 |\n"
                    "| operating profit | $ 131 | $ 121 | $ 155 |\n"
                    "foodservice net sales declined to $ 396 million in 2006 , compared "
                    "with $ 437 million in 2005 and $ 480 million in 2004 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2005 what percentage of consumer packaging sales were represented by foodservice net sales?",
            graph,
        )

        self.assertEqual(answer.text, "19.5%")
        self.assertIn("437", answer.calculations[0])
        self.assertIn("2245", answer.calculations[0])

    def test_ratio_percent_prefers_segment_sales_table_denominator_over_prose_subsegment(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "industrial packaging in millions 2007 2006 2005 .\n"
                    "| in millions | 2007 | 2006 | 2005 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 5245 | $ 4925 | $ 4625 |\n"
                    "| operating profit | $ 501 | $ 399 | $ 219 |\n"
                    "north american industrial packaging net sales for 2007 were $ 3.9 billion . "
                    "european industrial packaging net sales for 2007 were $ 1.1 billion , "
                    "up from $ 1.0 billion in 2006 and $ 880 million in 2005 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of industrial packaging sales where represented by european industrial packaging net sales in 2007?",
            graph,
        )

        self.assertEqual(answer.text, "21%")
        self.assertIn("1100", answer.calculations[0])
        self.assertIn("5245", answer.calculations[0])

    def test_ratio_percent_combines_split_sales_table_and_foodservice_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_finqa_046_ip_2006_page_32_pdf_1_0_1",
                node_type="text",
                content=(
                    "consumer packaging in millions 2006 2005 2004 .\n"
                    "| in millions | 2006 | 2005 | 2004 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 2455 | $ 2245 | $ 2295 |\n"
                    "| operating profit | $ 131 | $ 121 | $ 155 |\n"
                ),
                source_doc="report.md",
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_7_finqa_046_ip_2006_page_32_pdf_1_0_2",
                node_type="text",
                content=(
                    "| in millions | 2006 | 2005 | 2004 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 2455 | $ 2245 | $ 2295 |\n"
                    "foodservice net sales declined to $ 396 million in 2006 , compared "
                    "with $ 437 million in 2005 and $ 480 million in 2004 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2005 what percentage of consumer packaging sales were represented by foodservice net sales?",
            graph,
        )

        self.assertEqual(answer.text, "19.5%")
        self.assertIn("437", answer.calculations[0])
        self.assertIn("2245", answer.calculations[0])
        self.assertGreater(len(answer.citations), 1)

    def test_ratio_percent_combines_split_sales_table_and_region_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_finqa_298_ip_2007_page_31_pdf_1_0_0",
                node_type="text",
                content=(
                    "industrial packaging in millions 2007 2006 2005 .\n"
                    "| in millions | 2007 | 2006 | 2005 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| sales | $ 5245 | $ 4925 | $ 4625 |\n"
                    "| operating profit | $ 501 | $ 399 | $ 219 |\n"
                ),
                source_doc="report.md",
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_3_finqa_298_ip_2007_page_31_pdf_1_0_2",
                node_type="text",
                content=(
                    "north american industrial packaging net sales for 2007 were $ 3.9 billion , "
                    "compared with $ 3.7 billion in 2006 and $ 3.6 billion in 2005 . "
                    "european industrial packaging net sales for 2007 were $ 1.1 billion , "
                    "up from $ 1.0 billion in 2006 and $ 880 million in 2005 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of industrial packaging sales where represented by european industrial packaging net sales in 2007?",
            graph,
        )

        self.assertEqual(answer.text, "21%")
        self.assertIn("1100", answer.calculations[0])
        self.assertIn("5245", answer.calculations[0])
        self.assertGreater(len(answer.citations), 1)

    def test_ratio_percent_handles_truncated_year_only_sales_header(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="truncated",
                node_type="text",
                content=(
                    "consumer packaging in millions 2006 2005 2004 .\n"
                    "| 2006 | 2005 | 2004 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| sales | $ 2455 | $ 2245 | $ 2295 |\n"
                    "| operating profit | $ 131 | $ 121 | $ 155 |\n"
                    "foodservice net sales declined to $ 396 million in 2006 , compared "
                    "with $ 437 million in 2005 and $ 480 million in 2004 ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2005 what percentage of consumer packaging sales were represented by foodservice net sales?",
            graph,
        )

        self.assertEqual(answer.text, "19.5%")
        self.assertIn("437", answer.calculations[0])
        self.assertIn("2245", answer.calculations[0])

    def test_ratio_percent_made_up_of_uses_total_row_from_table_context(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "average common equity attribution $ in billions 2017 2016 2015.\n"
                    "| $ in billions | 2017 | 2016 | 2015 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| institutional securities | 40.2 | 43.2 | 34.6 |\n"
                    "| wealth management | 17.2 | 15.3 | 11.2 |\n"
                    "| total | 69.8 | 68.9 | 66.9 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of average common equity attribution in 2017 is made up of institutional securities?",
            graph,
        )

        self.assertEqual(answer.text, "57.6%")
        self.assertIn("row=institutional securities", answer.calculations[0])
        self.assertIn("denominator_row=total", answer.calculations[0])

    def test_ratio_percent_in_named_column_uses_same_row_total_column(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "retail / hnw long-term aum by asset class and client region.\n"
                    "| ( dollar amounts in millions ) | americas | emea | asia-pacific | total |\n"
                    "| --- | ---: | ---: | ---: | ---: |\n"
                    "| equity | 94805 | 53140 | 16803 | 164748 |\n"
                    "| long-term retail/hnw | 298024 | 77699 | 27761 | 403484 |\n"
                    "retail and hnw long-term inflows of $ 9.8 billion were driven by demand.\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the long-term retail/hnw in americas as a percentage of the total long-term retail/hnw?",
            graph,
        )

        self.assertEqual(answer.text, "73.9%")
        self.assertIn("row=long-term retail/hnw", answer.calculations[0])
        self.assertIn("numerator_column=americas", answer.calculations[0])
        self.assertIn("denominator_column=total", answer.calculations[0])
        self.assertIn("298024 / 403484", answer.calculations[0])

    def test_ratio_percent_selects_query_measure_column(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | oil ( mmbbls ) | gas ( bcf ) | ngls ( mmbbls ) | total ( mmboe ) |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| u.s . onshore | 12 | 626 | 23 | 140 |\n"
                    "| canada | 23 | 198 | 4 | 60 |\n"
                    "| total | 66 | 894 | 28 | 243 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total oil and gas mmboe comes from canada?",
            graph,
        )

        self.assertEqual(answer.text, "24.7%")
        self.assertIn("column=total ( mmboe )", answer.calculations[0])

    def test_ratio_percent_prefers_later_complete_measure_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="partial_oil_table",
                node_type="text",
                content=(
                    "|  | oil ( mmbbls ) |\n"
                    "| --- | --- |\n"
                    "| canada | 23 |\n"
                    "| total | 66 |\n"
                ),
                source_doc="partial.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="complete_mmboe_table",
                node_type="text",
                content=(
                    "|  | oil ( mmbbls ) | gas ( bcf ) | ngls ( mmbbls ) | total ( mmboe ) |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| u.s . onshore | 12 | 626 | 23 | 140 |\n"
                    "| canada | 23 | 198 | 4 | 60 |\n"
                    "| total | 66 | 894 | 28 | 243 |\n"
                ),
                source_doc="complete.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of the total oil and gas mmboe comes from canada?",
            graph,
        )

        self.assertEqual(answer.text, "24.7%")
        self.assertEqual(answer.citations, ["complete_mmboe_table"])

    def test_ratio_percent_prefers_context_with_query_year(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_unp_2011",
                node_type="text",
                content=(
                    "# Evidence UNP/2011/page_76.pdf-1\n"
                    "| millions | dec . 31 2011 | dec . 31 2010 |\n"
                    "| --- | ---: | ---: |\n"
                    "| accrued wages and vacation | 363 | 357 |\n"
                    "| total accounts payable and other current liabilities | 3108 | 2713 |\n"
                ),
                source_doc="unp_2011.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_2_unp_2008",
                node_type="text",
                content=(
                    "# Evidence UNP/2008/page_77.pdf-1\n"
                    "| millions of dollars | dec . 31 2008 | dec . 31 2007 |\n"
                    "| --- | ---: | ---: |\n"
                    "| accrued wages and vacation | 367 | 394 |\n"
                    "| total accounts payable and other current liabilities | 2560 | 2902 |\n"
                ),
                source_doc="unp_2008.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "as of december 31 , 2008 what was the percent of the total accounts payable and other liabilities that was accrued wages and vacation",
            graph,
        )

        self.assertEqual(answer.text, "14.3%")
        self.assertEqual(answer.citations, ["retrieved_2_unp_2008"])
        self.assertIn("column=dec . 31 2008", answer.calculations[0])

    def test_ratio_percent_total_denominator_prefers_total_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| contractual obligation | total | less than 1 year | 1 - 3 years |\n"
                    "| --- | --- | --- | --- |\n"
                    "| long-term debt | $ 275.1 | $ 8.6 | $ 13.8 |\n"
                    "| purchase obligations | 177.3 | 176.6 | 0.7 |\n"
                    "| total | $ 521.3 | $ 199.6 | $ 35.2 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of total aggregate contractual obligations is due to purchase obligations?",
            graph,
        )

        self.assertEqual(answer.text, "34%")
        self.assertIn("denominator_row=total", answer.calculations[0])

    def test_ratio_percent_total_denominator_waits_for_total_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="partial",
                node_type="text",
                content=(
                    "| millions of dollars | dec . 31 2008 | dec . 31 2007 |\n"
                    "| --- | --- | --- |\n"
                    "| accounts payable | $ 629 | $ 732 |\n"
                    "| accrued wages and vacation | 367 | 394 |\n"
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="complete",
                node_type="text",
                content=(
                    "| millions of dollars | dec . 31 2008 | dec . 31 2007 |\n"
                    "| --- | --- | --- |\n"
                    "| accounts payable | $ 629 | $ 732 |\n"
                    "| accrued wages and vacation | 367 | 394 |\n"
                    "| total accounts payable and other current liabilities | $ 2560 | $ 2902 |\n"
                ),
                source_doc="report.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "as of december 31 , 2008 what was the percent of the total accounts payable and other liabilities that was accrued wages and vacation",
            graph,
        )

        self.assertEqual(answer.text, "14.3%")
        self.assertEqual(answer.citations, ["complete"])
        self.assertIn("denominator_row=total accounts payable and other current liabilities", answer.calculations[0])

    def test_ratio_percent_major_facilities_owned_uses_total_facilities(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="facilities",
                node_type="text",
                content=(
                    "| ( square feet in millions ) | unitedstates | othercountries | total |\n"
                    "| --- | --- | --- | --- |\n"
                    "| owned facilities1 | 29.9 | 16.7 | 46.6 |\n"
                    "| leased facilities2 | 2.3 | 6.0 | 8.3 |\n"
                    "| total facilities | 32.2 | 22.7 | 54.9 |\n"
                ),
                source_doc="intc.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of major facilities by square footage are owned as of december 28 , 2013?",
            graph,
        )

        self.assertEqual(answer.text, "84.9%")
        self.assertIn("row=owned facilities1", answer.calculations[0])
        self.assertIn("denominator_row=total facilities", answer.calculations[0])

    def test_ratio_percent_major_facilities_leased_uses_total_facilities(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="facilities",
                node_type="text",
                content=(
                    "| ( square feet in millions ) | unitedstates | othercountries | total |\n"
                    "| --- | --- | --- | --- |\n"
                    "| owned facilities1 | 29.9 | 16.7 | 46.6 |\n"
                    "| leased facilities2 | 2.3 | 6.0 | 8.3 |\n"
                    "| total facilities | 32.2 | 22.7 | 54.9 |\n"
                ),
                source_doc="intc.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of major facilities by square footage are leased as of december 28 , 2013?",
            graph,
        )

        self.assertEqual(answer.text, "15.1%")
        self.assertIn("row=leased facilities2", answer.calculations[0])
        self.assertIn("denominator_row=total facilities", answer.calculations[0])

    def test_ratio_percent_not_leased_alpharetta_square_feet_uses_exception_and_table_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="etfc_facilities",
                node_type="text",
                content=(
                    "all facilities are leased , except for 165000 square feet of our office in alpharetta , georgia .\n"
                    "square footage amounts are net of space that has been sublet or part of a facility restructuring .\n"
                    "| location | approximate square footage |\n"
                    "| --- | --- |\n"
                    "| alpharetta georgia | 254000 |\n"
                    "| jersey city new jersey | 107000 |\n"
                ),
                source_doc="etfc.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "at december 31 , 2013 what was the percent of square feet of our office in alpharetta , georgia not leased",
            graph,
        )

        self.assertEqual(answer.text, "65%")
        self.assertEqual(answer.citations, ["etfc_facilities"])
        self.assertIn("165000 / 254000", answer.calculations[0])

    def test_ratio_percent_office_facility_closing_uses_prose_lease_expense_year(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="abmd_leases",
                node_type="text",
                content=(
                    "in december 2005 we closed our office facility in the netherlands , "
                    "recording a charge of approximately $ 58000 for the remaining lease term .\n"
                    "total rent expense under these leases approximated $ 821000 , $ 824000 and $ 1262000 "
                    "for the fiscal years ended march 31 , 2004 , 2005 and 2006 , respectively .\n"
                    "| fiscal year ending march 31, | operating leases |\n"
                    "| --- | --- |\n"
                    "| 2007 | 1703 |\n"
                    "| 2008 | 1371 |\n"
                    "| total future minimum lease payments | $ 4819 |\n"
                ),
                source_doc="abmd.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "the non-recurring charge for the office facility closing was what percent of lease expense in 2006?",
            graph,
        )

        self.assertEqual(answer.text, "4.6%")
        self.assertEqual(answer.citations, ["abmd_leases"])
        self.assertIn("58000 / 1.262e+06", answer.calculations[0])

    def test_ratio_percent_equity_plan_remaining_available_uses_issued_plus_remaining_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="hii_equity_plan",
                node_type="text",
                content=(
                    "| plan category | number of securities to be issued upon exercise of outstanding options warrants and rights ( 1 ) ( a ) ( b ) | "
                    "weighted-average exercise price of outstanding optionswarrants and rights | "
                    "number of securities remaining available for future issuance under equity compensation plans ( excluding securitiesreflected in column ( a ) ) ( c ) |\n"
                    "| --- | --- | --- | --- |\n"
                    "| equity compensation plans approved by security holders | 448859 | $ 0.00 | 4087587 |\n"
                    "| equity compensation plans not approved by security holders ( 2 ) | 2014 | 2014 | 2014 |\n"
                ),
                source_doc="hii.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the equity compensation plan approved by security holders remains available for future issuance?",
            graph,
        )

        self.assertEqual(answer.text, "90.1%")
        self.assertEqual(answer.citations, ["hii_equity_plan"])
        self.assertIn("4087587 / (448859 + 4087587)", answer.calculations[0])

    def test_ratio_percent_total_commitments_less_than_one_year_uses_matching_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="wrong_obligations",
                node_type="text",
                content=(
                    "| contractual obligations | payments due by fiscal year total | payments due by fiscal year less than 1 year |\n"
                    "| --- | --- | --- |\n"
                    "| total obligations | $ 20147 | $ 6932 |\n"
                ),
                source_doc="abmd.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="lmt_commitments",
                node_type="text",
                content=(
                    "| ( in millions ) | commitment expiration by period total commitment | commitment expiration by period less than 1 year ( a ) | commitment expiration by period 1-3 years ( a ) |\n"
                    "| --- | --- | --- | --- |\n"
                    "| standby letters of credit | $ 2630 | $ 2425 | $ 171 |\n"
                    "| surety bonds | 434 | 79 | 352 |\n"
                    "| guarantees | 2 | 1 | 1 |\n"
                    "| total commitments | $ 3066 | $ 2505 | $ 524 |\n"
                ),
                source_doc="lmt.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percent of total commitments expire in less than 1 year?",
            graph,
        )

        self.assertEqual(answer.text, "81.7%")
        self.assertEqual(answer.citations, ["lmt_commitments"])
        self.assertIn("2505 / 3066", answer.calculations[0])

    def test_ratio_percent_commitment_subject_to_renewal_uses_standby_letters_footnote(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="lmt_renewal",
                node_type="text",
                content=(
                    "| ( in millions ) | commitment expiration by period total commitment | commitment expiration by period less than 1 year ( a ) | commitment expiration by period 1-3 years ( a ) |\n"
                    "| --- | --- | --- | --- |\n"
                    "| standby letters of credit | $ 2630 | $ 2425 | $ 171 |\n"
                    "| surety bonds | 434 | 79 | 352 |\n"
                    "| total commitments | $ 3066 | $ 2505 | $ 524 |\n"
                    "( a ) approximately $ 2262 million and $ 49 million of standby letters of credit in the 201cless than 1 year 201d "
                    "and 201c1-3 year 201d periods , respectively , and approximately $ 38 million of surety bonds in the "
                    "201cless than 1 year 201d period are expected to renew for additional periods until completion of the contractual obligation .\n"
                ),
                source_doc="lmt.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percent of the total commitment with an expiration of less that 1 year was subject to renewal",
            graph,
        )

        self.assertEqual(answer.text, "93.3%")
        self.assertEqual(answer.citations, ["lmt_renewal"])
        self.assertIn("2262 / 2425", answer.calculations[0])

    def test_percent_change_quarterly_cash_dividend_december_uses_dividend_column(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="dre_dividends",
                node_type="text",
                content=(
                    "| quarter ended | 2002 high | 2002 low | 2002 dividend | 2002 high | 2002 low | dividend |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n"
                    "| december 31 | $ 25.84 | $ 21.50 | $ .455 | $ 24.80 | $ 22.00 | $ .45 |\n"
                    "| march 31 | 26.50 | 22.92 | .450 | 25.44 | 21.85 | .43 |\n"
                ),
                source_doc="dre.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percent change in quarterly cash dividend for the period ended march 31 2002 to the period ended december 31 2002?",
            graph,
        )

        self.assertEqual(answer.text, "1.1%")
        self.assertEqual(answer.citations, ["dre_dividends"])
        self.assertIn("0.455 - 0.45", answer.calculations[0])

    def test_percent_change_quarterly_cash_dividend_march_2003_uses_declared_dividend(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="dre_dividends",
                node_type="text",
                content=(
                    "on january 29 , 2003 , the company declared a quarterly cash dividend of $ .455 per share .\n"
                    "| quarter ended | 2002 high | 2002 low | 2002 dividend | 2002 high | 2002 low | dividend |\n"
                    "| --- | --- | --- | --- | --- | --- | --- |\n"
                    "| march 31 | 26.50 | 22.92 | .450 | 25.44 | 21.85 | .43 |\n"
                ),
                source_doc="dre.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the percent change in quarterly cash dividend for the period ended march 31 2002 to the period ended march 31 2003?",
            graph,
        )

        self.assertEqual(answer.text, "1.1%")
        self.assertEqual(answer.citations, ["dre_dividends"])
        self.assertIn("0.455 - 0.45", answer.calculations[0])

    def test_ratio_percent_due_after_total(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| 2010 | $ 6951 |\n"
                    "| thereafter | 25048 |\n"
                    "| total | $ 44572 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of total purchase commitments are due after 2014?",
            graph,
        )

        self.assertEqual(answer.text, "56.2%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_due_to_row_for_year(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| in millions | 2008 | 2009 | thereafter |\n"
                    "| --- | --- | --- | --- |\n"
                    "| lease obligations | $ 136 | $ 116 | $ 92 |\n"
                    "| purchase obligations ( a ) | 1953 | 294 | 1480 |\n"
                    "| total | $ 2089 | $ 410 | $ 1572 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of december 31 , 2007 , total future minimum commitments under existing non-cancelable operating leases and purchase obligations were due to purchase obligations for the year of 2008?",
            graph,
        )

        self.assertEqual(answer.text, "93.5%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_as_percentage_of_selects_specific_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | payments ( receipts ) ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| entergy arkansas | $ 2 |\n"
                    "| entergy louisiana | $ 6 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the payments for entergy arkansas as a percentage of payments for entergy louisiana?",
            graph,
        )

        self.assertEqual(answer.text, "33.3%")
        self.assertIn("row=entergy arkansas", answer.calculations[0])
        self.assertIn("denominator_row=entergy louisiana", answer.calculations[0])

    def test_ratio_percent_from_prose_amounts_near_query_terms(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "Operating companies income increased $119 million, due primarily to higher net pricing "
                    "and research savings reflecting cost reduction initiatives ($198 million)."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the cost reduction initiatives as a percentage of the operating companies income increase?",
            graph,
        )

        self.assertEqual(answer.text, "166.4%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_uses_terminal_total_operating_income_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "Operating income increased $54 million or 6% from 2008 to $900 million in 2009. "
                    "These items were partially offset by an increase of $140 million in restructuring costs.\n"
                    "| years ended december 31, | 2009 | 2008 | 2007 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| segment revenue | $ 1267 | $ 1356 | $ 1345 |\n"
                    "| segment operating income | 203 | 208 | 180 |\n"
                    "| segment operating income margin | 16.0% | 15.3% | 13.4% |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "considering the year 2009 , what is the percentage of the segment's operating income among the total operating income?",
            graph,
        )

        self.assertEqual(answer.text, "22.6%")
        self.assertIn("203 / 900", answer.calculations[0])

    def test_ratio_percent_from_that_was_prose_amounts(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "Restricted cash as of December 31, 2009, was $236.6 million, "
                    "of which $93.1 million was proceeds from the issuance of tax-exempt bonds."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "as of december 31 2009 what was the percentage of restricted cash that was proceeds from the issuance of tax-exempt bonds?",
            graph,
        )

        self.assertEqual(answer.text, "39.3%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_ratio_percent_mixes_table_numerator_and_prose_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "Gross operating revenues increased primarily due to an increase of $98.0 million "
                    "in fuel cost recovery revenues due to higher fuel rates.\n"
                    "| | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the deferred fuel cost revisions as a percentage of the increase in fuel cost recovery revenues?",
            graph,
        )

        self.assertEqual(answer.text, "60.3%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_increase_component_as_percentage_of_year_denominator_sums_prose_amounts(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="etr_table",
                node_type="text",
                content=(
                    "Other regulatory credits increased primarily due to: "
                    "the deferral in 2004 of $14.3 million of capacity charges; "
                    "the amortization in 2003 of $11.8 million of deferred capacity charges; "
                    "and the deferral in 2004 of $11.4 million related to severance.\n"
                    "Following is an analysis of the change in net revenue comparing 2003 to 2002.\n"
                    "|  | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2002 net revenue | $ 922.9 |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                    "| 2003 net revenue | $ 973.7 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the increase in other regulatory credits as a percentage of net revenue in 2003?",
            graph,
        )

        self.assertEqual(answer.text, "3.9%")
        self.assertIn("increase_component_ratio_percent", answer.calculations[0])
        self.assertIn("(14.3 + 11.8 + 11.4) / 973.7 * 100", answer.calculations[0])

    def test_increase_component_ratio_combines_same_source_chunks(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_etr_0_0",
                node_type="text",
                content=(
                    "Other regulatory credits increased primarily due to: "
                    "the deferral in 2004 of $14.3 million of capacity charges; "
                    "the amortization in 2003 of $11.8 million of deferred capacity charges; "
                    "and the deferral in 2004 of $11.4 million related to severance."
                ),
                source_doc="etr.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="neighbor_1_etr_0_1",
                node_type="text",
                content=(
                    "Following is an analysis of the change in net revenue comparing 2003 to 2002.\n"
                    "|  | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2002 net revenue | $ 922.9 |\n"
                    "| 2003 net revenue | $ 973.7 |\n"
                ),
                source_doc="etr.md",
                metadata={"retrieval_rank": 1, "neighbor_context": True},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the increase in other regulatory credits as a percentage of net revenue in 2003?",
            graph,
        )

        self.assertEqual(answer.text, "3.9%")
        self.assertEqual(answer.citations, ["retrieved_1_etr_0_0", "neighbor_1_etr_0_1"])

    def test_ratio_percent_prefers_later_mixed_prose_over_partial_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="partial_rows",
                node_type="text",
                content=(
                    "|  | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| deferred fuel cost revisions | 98.0 |\n"
                    "| fuel cost recovery revenues | 98.0 |\n"
                ),
                source_doc="partial.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="complete_mixed",
                node_type="text",
                content=(
                    "Gross operating revenues increased primarily due to an increase of $98.0 million "
                    "in fuel cost recovery revenues due to higher fuel rates.\n"
                    "| | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                ),
                source_doc="complete.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the deferred fuel cost revisions as a percentage of the increase in fuel cost recovery revenues?",
            graph,
        )

        self.assertEqual(answer.text, "60.3%")
        self.assertEqual(answer.citations, ["complete_mixed"])

    def test_ratio_percent_rejects_weak_prose_numerator_overlap(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="partial_prose",
                node_type="text",
                content=(
                    "Gross operating revenues increased primarily due to an increase of $98.0 million "
                    "in fuel cost recovery revenues due to higher fuel rates. "
                    "Fuel and purchased power expenses increased due to deferred fuel costs."
                ),
                source_doc="partial.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="complete_mixed",
                node_type="text",
                content=(
                    "Gross operating revenues increased primarily due to an increase of $98.0 million "
                    "in fuel cost recovery revenues due to higher fuel rates.\n"
                    "| | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                ),
                source_doc="complete.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the deferred fuel cost revisions as a percentage of the increase in fuel cost recovery revenues?",
            graph,
        )

        self.assertEqual(answer.text, "60.3%")
        self.assertEqual(answer.citations, ["complete_mixed"])

    def test_ratio_percent_combines_same_source_adjacent_chunks(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_case_0_0",
                node_type="text",
                content=(
                    "Gross operating revenues increased primarily due to an increase of $98.0 million "
                    "in fuel cost recovery revenues due to higher fuel rates."
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_2_case_0_1",
                node_type="text",
                content=(
                    "| | ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| deferred fuel cost revisions | 59.1 |\n"
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the deferred fuel cost revisions as a percentage of the increase in fuel cost recovery revenues?",
            graph,
        )

        self.assertEqual(answer.text, "60.3%")
        self.assertEqual(set(answer.citations), {"retrieved_2_case_0_1", "retrieved_1_case_0_0"})

    def test_ratio_percent_mixes_prose_numerator_and_year_table_denominator(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "The annual long-term debt maturities and annual cash sinking fund requirements "
                    "are as follows ( in thousands ).\n"
                    "| 2003 | $ 1150786 |\n"
                    "| --- | --- |\n"
                    "| 2007 | $ 475288 |\n"
                    "Not included are other sinking fund requirements of approximately $30.2 million annually."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what are the annual other sinking fund requirements as a percentage of annual long-term debt maturities and annual cash sinking fund requirements for debt outstanding in 2007?",
            graph,
        )

        self.assertEqual(answer.text, "6.4%")
        self.assertIn("ratio_percent", answer.calculations[0])

    def test_prose_ratio_prefers_exact_year_table_denominator_over_prose_subitem(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="mixed",
                node_type="text",
                content=(
                    "Other restructuring charges were $30.0 million. "
                    "The restructuring program included a smaller operating-income item of $100.0 million.\n"
                    "| metric | 2008 | 2009 |\n"
                    "| --- | ---: | ---: |\n"
                    "| total operating income | $ 846.0 | $ 900.0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2009 what percentage of total operating income was represented by other restructuring charges?",
            graph,
        )

        self.assertEqual(answer.text, "3.3%")
        self.assertIn("30 / 900", answer.calculations[0])
        self.assertIn("denominator_row=total operating income", answer.calculations[0])

    def test_ratio_percent_prefers_adjusted_period_component(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| tower cash flow for the three months ended december 31 2005 | $ 139590 |\n"
                    "| --- | --- |\n"
                    "| consolidated cash flow for the twelve months ended december 31 2005 | $ 498266 |\n"
                    "| less : tower cash flow for the twelve months ended december 31 2005 | -524804 ( 524804 ) |\n"
                    "| plus : four times tower cash flow for the three months ended december 31 2005 | 558360 |\n"
                    "| adjusted consolidated cash flow for the twelve months ended december 31 2005 | $ 531822 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what portion of the adjusted consolidated cash flow for the twelve months ended december 31 , 2005 is related to tower cash flow?",
            graph,
        )

        self.assertEqual(answer.text, "105%")
        self.assertIn("plus : four times tower cash flow", answer.calculations[0])

    def test_row_average_from_entity_table(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| company | payments volume ( billions ) | total transactions ( billions ) |\n"
                    "| --- | --- | --- |\n"
                    "| american express | 637 | 5.0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average payment volume per transaction for american express?",
            graph,
        )

        self.assertEqual(answer.text, "127.40")
        self.assertIn("row_average", answer.calculations[0])

    def test_year_range_average_from_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year | amortization amount ( in millions ) |\n"
                    "| --- | --- |\n"
                    "| 2015 | $ 45 |\n"
                    "| 2016 | $ 45 |\n"
                    "| 2017 | $ 45 |\n"
                    "| 2018 | $ 45 |\n"
                    "| 2019 | $ 44 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average amortization amount , in millions , from 2015-2019?",
            graph,
        )

        self.assertEqual(answer.text, "44.8")
        self.assertIn("year_range_average", answer.calculations[0])

    def test_year_range_average_from_respectively_prose(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "For the years ended December 31, 2010, 2009, and 2008, the potential "
                    "anti-dilutive share conversions were 256,868 shares, 1,230,881 shares, "
                    "and 638,401 shares, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the average potential anti-dilutive share conversions from 2008 to 2010",
            graph,
        )

        self.assertEqual(answer.text, "708716.7")
        self.assertIn("year_range_average", answer.calculations[0])

    def test_year_range_average_prefers_inline_exact_row_over_truncated_table_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "selected income statement and balance sheet data as of or for the year ended "
                    "december 31 , ( in millions ) 2018 2017 2016 investment securities gains/ "
                    "( losses ) $ ( 395 ) $ ( 78 ) $ 132 available-for-sale ( afs ) investment "
                    "securities ( average ) 203449 219345 226892 held-to-maturity investment "
                    "securities ( average ) 31747 47927 51358 investment securities portfolio "
                    "( average ) 235197 267272 278250 afs investment securities ( period-end ) "
                    "228681 200247 236670 htm investment securities ( period-end ) 31434 47733 50168 .\n"
                    "## Table\n"
                    "| as of or for the year ended december 31 ( in millions ) | 2018 | 2017 | 2016 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| investment securities gains/ ( losses ) | $ -395 | $ -78 | $ 132 |\n"
                    "| available-for-sale ( afs ) investment securities ( average ) | 203449 | 219345 | 226892 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average of the afs investment securities during the years 2016-2018?",
            graph,
        )

        self.assertEqual(answer.text, "221866.0")
        self.assertIn("afs investment securities ( period-end )", answer.calculations[0])
        self.assertNotIn("gains", answer.calculations[0])

    def test_ratio_between_years_from_respectively_sentence(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "The u.s. pension trust had assets of $1572 million and $1739 million "
                    "as of December 31, 2018 and 2017, respectively."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the ratio of the pension trust assets for 2017 to 2018",
            graph,
        )

        self.assertEqual(answer.text, "1.11")
        self.assertIn("ratio_between_years", answer.calculations[0])

    def test_ratio_between_year_label_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year | gallons hedged |\n"
                    "| --- | --- |\n"
                    "| 2017 | 12000000 |\n"
                    "| 2018 | 3000000 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the ratio of the gallons hedged in 2017 to 2018",
            graph,
        )

        self.assertEqual(answer.text, "4")
        self.assertIn("ratio_between_years", answer.calculations[0])

    def test_same_year_ratio_compared_to_uses_two_table_rows(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| metric | 2018 | 2017 | 2016 |\n"
                    "| --- | ---: | ---: | ---: |\n"
                    "| htm investment securities period-end | 31434 | 47733 | 50168 |\n"
                    "| investment securities portfolio period-end | 260115 | 247980 | 286838 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2017 what was the ratio of the htm investment securities period-end compared to "
            "investment securities portfolio period 2013end",
            graph,
        )

        self.assertEqual(answer.text, "0.19")
        self.assertIn("same_year_row_ratio", answer.calculations[0])

    def test_same_year_ratio_recovers_inline_rows_across_chunks(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="retrieved_1_case_0_0",
                node_type="text",
                content=(
                    "selected balance sheet data as of december 31 , ( in millions ) "
                    "2018 2017 2016 investment securities gains losses 395 78 132 "
                    "htm investment securities period-end 31434 47733 50168"
                ),
                source_doc="case.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="neighbor_1_case_0_1",
                node_type="text",
                content="investment securities portfolio period-end 260115 247980 286838",
                source_doc="case.md",
                metadata={"retrieval_rank": 1, "neighbor_context": True},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2017 what was the ratio of the htm investment securities period-end compared to "
            "investment securities portfolio period 2013end",
            graph,
        )

        self.assertEqual(answer.text, "0.19")
        self.assertIn("same_year_row_ratio", answer.calculations[0])
        self.assertEqual(answer.citations, ["retrieved_1_case_0_0", "neighbor_1_case_0_1"])

    def test_ratio_after_year_to_year_uses_future_range_row(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year | expected future pension benefits |\n"
                    "| --- | --- |\n"
                    "| 2008 | 1490 |\n"
                    "| 2009 | 1540 |\n"
                    "| 2010 | 1600 |\n"
                    "| 2011 | 1660 |\n"
                    "| years 2012 2013 2016 | 9530 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "at december 31 , 2006 what was the ratio of the expected future pension benefits after 2012 compared to 2008",
            graph,
        )

        self.assertEqual(answer.text, "6.4")
        self.assertIn("ratio_between_years", answer.calculations[0])

    def test_ratio_for_year_to_amounts_after_uses_planner_before_year_ratio(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="correct",
                node_type="text",
                content=(
                    "future maturities of corporate debt scheduled principal payments of corporate debt "
                    "as of december 31 , 2007 are as follows ( dollars in thousands ).\n"
                    "| 2008 | $ 2014 |\n"
                    "| --- | ---: |\n"
                    "| 2009 | 2014 |\n"
                    "| 2010 | 2014 |\n"
                    "| 2011 | 453815 |\n"
                    "| 2012 | 2014 |\n"
                    "| thereafter | 2996337 |\n"
                    "| total future principal payments of corporate debt | 3450152 |\n"
                ),
                source_doc="correct.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="distractor",
                node_type="text",
                content=(
                    "| year | long-term debt obligations |\n"
                    "| --- | ---: |\n"
                    "| 2007 | 1340 |\n"
                    "| 2011 | 607 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator(
            planner_fallback=NumericPlannerFallback(HeuristicNumericPlanClient())
        ).generate(
            "as of december 2007 what was the ratio of the future debt maturities for 2011 to the amounts after 2012",
            graph,
        )

        self.assertEqual(answer.text, "0.2")
        self.assertIn("planned_ratio", answer.calculations[0])
        self.assertIn("453815 / 2.99634e+06", answer.calculations[0])
        self.assertEqual(answer.citations, ["correct"])

    def test_acquisition_debts_to_assets_ratio_combines_assumed_liabilities(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="dre_table",
                node_type="text",
                content=(
                    "the assets acquired and liabilities assumed were recorded at their estimated fair value "
                    "at the date of acquisition, as summarized below.\n"
                    "| operating rental properties | $ 602011 |\n"
                    "| --- | --- |\n"
                    "| land held for development | 154300 |\n"
                    "| total real estate investments | 756311 |\n"
                    "| other assets | 10478 |\n"
                    "| lease related intangible assets | 86047 |\n"
                    "| goodwill | 14722 |\n"
                    "| total assets acquired | 867558 |\n"
                    "| debt assumed | -148527 ( 148527 ) |\n"
                    "| other liabilities assumed | -5829 ( 5829 ) |\n"
                    "| purchase price net of assumed liabilities | $ 713202 |\n"
                ),
                source_doc="dre.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the ratio of the debts to the assets in the purchase transaction",
            graph,
        )

        self.assertEqual(answer.text, "17.8%")
        self.assertIn("acquisition_liabilities_to_assets_ratio", answer.calculations[0])
        self.assertIn("(148527 + 5829) / 867558 * 100", answer.calculations[0])
        self.assertEqual(answer.citations, ["dre_table"])

    def test_percent_of_total_due_after_uses_same_row_columns(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( in millions ) | payments due by period ( 1 ) total | payments due by period ( 1 ) 2007 | payments due by period ( 1 ) 2008 | payments due by period ( 1 ) 2009 | payments due by period ( 1 ) 2010 | payments due by period ( 1 ) 2011 | payments due by period ( 1 ) thereafter |\n"
                    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                    "| long-term debt obligations | $ 4134 | $ 1340 | $ 198 | $ 4 | $ 534 | $ 607 | $ 1451 |\n"
                    "| lease obligations | 2328 | 351 | 281 | 209 | 178 | 158 | 1151 |\n"
                    "| purchase obligations | 1035 | 326 | 120 | 26 | 12 | 12 | 539 |\n"
                    "| total contractual obligations | $ 7497 | $ 2017 | $ 599 | $ 239 | $ 724 | $ 777 | $ 3141 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percent of the total long-term debt obligations that was due after 2011",
            graph,
        )

        self.assertEqual(answer.text, "35.1%")
        self.assertIn("numerator_column=payments due by period ( 1 ) thereafter", answer.calculations[0])

    def test_percent_of_total_due_after_uses_vertical_schedule_rows_first(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="correct",
                node_type="text",
                content=(
                    "|  | ( in thousands ) |\n"
                    "| --- | --- |\n"
                    "| 2010 | $ 6951 |\n"
                    "| 2011 | 5942 |\n"
                    "| 2012 | 3659 |\n"
                    "| 2013 | 1486 |\n"
                    "| 2014 | 1486 |\n"
                    "| thereafter | 25048 |\n"
                    "| total | $ 44572 |\n"
                ),
                source_doc="correct.md",
                metadata={"retrieval_rank": 1},
            )
        )
        graph.add_node(
            EvidenceNode(
                node_id="distractor",
                node_type="text",
                content=(
                    "| ( in millions ) | payments due by period ( 1 ) total | payments due by period ( 1 ) thereafter |\n"
                    "| --- | --- | --- |\n"
                    "| purchase obligations | 1035 | 539 |\n"
                ),
                source_doc="distractor.md",
                metadata={"retrieval_rank": 2},
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what percentage of total purchase commitments are due after 2014?",
            graph,
        )

        self.assertEqual(answer.text, "56.2%")
        self.assertEqual(answer.citations, ["correct"])
        self.assertIn("row=thereafter", answer.calculations[0])

    def test_change_from_year_columns(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2013 | 2012 | 2011 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| weighted average common shares outstanding for basic computations | 320.9 | 323.7 | 335.9 |\n"
                    "| weighted average common shares outstanding for diluted computations | 326.5 | 328.4 | 339.9 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in the weighted average common shares outstanding for diluted computations from 2012 to 2013 , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "-1.9")
        self.assertIn("row_year_difference", answer.calculations[0])

    def test_change_between_years_uses_first_minus_second(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2014 | 2012 |\n"
                    "| --- | --- | --- |\n"
                    "| long term debt | $ 28987 | $ 0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in amount of long term debt between 2014 and 2012?",
            graph,
        )

        self.assertEqual(answer.text, "28987")
        self.assertIn("row_year_difference", answer.calculations[0])

    def test_change_between_years_uses_newer_minus_older(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2013 | 2012 |\n"
                    "| --- | --- | --- |\n"
                    "| currency hedges | $ 383 | $ 0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the change in millions between 2012 and 2013 in currency hedges?",
            graph,
        )

        self.assertEqual(answer.text, "383")
        self.assertIn("row_year_difference", answer.calculations[0])

    def test_average_amount_uses_selected_row_values(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| december 31, | 2016 | 2015 | 2014 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| balance at january 1 | $ 373 | $ 394 | $ 392 |\n"
                    "| settlements | -13 ( 13 ) | -19 ( 19 ) | -2 ( 2 ) |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "for the period ending in 2016 , what was the average amount of settlements , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "11.3")
        self.assertIn("row_values_average", answer.calculations[0])

    def test_average_amount_prefers_explicit_row_over_period_end_balance(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| december 31, | 2016 | 2015 | 2014 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| settlements | -13 ( 13 ) | -19 ( 19 ) | -2 ( 2 ) |\n"
                    "| balance at december 31 | $ 369 | $ 373 | $ 394 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "for the period ending in 2016 , what was the average amount of settlements , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "11.3")
        self.assertIn("row=settlements", answer.calculations[0])

    def test_average_row_prefers_year_anchored_label(self) -> None:
        # Regression for IPG/2008: query anchors 2008, but two liability rows
        # differ only by year in the label. The 2006 row must not win.
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2007 program | 2003 program | 2001 program | total |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| liability at december 31 2006 | $ 2014 | $ 12.6 | $ 19.2 | $ 31.8 |\n"
                    "| liability at december 31 2008 | $ 1.2 | $ 5.7 | $ 5.9 | $ 12.8 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average liability for all three programs , as of december 31 , 2008 , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "4.3")
        self.assertIn("row_values_average", answer.calculations[0])
        self.assertIn("december 31 2008", answer.calculations[0])

    def test_average_row_excludes_total_column(self) -> None:
        # The "total" column is a summary of the three program columns and must
        # not be averaged in alongside them.
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2007 program | 2003 program | 2001 program | total |\n"
                    "| --- | --- | --- | --- | --- |\n"
                    "| liability at december 31 2008 | $ 1.2 | $ 5.7 | $ 5.9 | $ 12.8 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the average liability for all three programs , as of december 31 , 2008 , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "4.3")
        self.assertIn("row_values_average", answer.calculations[0])

    def test_percent_change_prefers_period_end_row_over_beginning(self) -> None:
        # Regression for JPM/2007: a change query over a table that carries both
        # "X at beginning of period" and "X at december 31" must use the
        # period-end row. The two rows tie on lexical score, so the change intent
        # must prefer period-end over period-beginning rather than row order.
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| year ended december 31 ( in millions ) | 2007 | 2006 |\n"
                    "| --- | --- | --- |\n"
                    "| fair value at beginning of period | $ 7546 | $ 6682 |\n"
                    "| originations of msrs | 2335 | 1512 |\n"
                    "| fair value at december 31 | $ 8632 | $ 7546 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percentage change in the fair value of msrs in 2007?",
            graph,
        )

        self.assertEqual(answer.text, "14.4%")
        self.assertIn("row=fair value at december 31", answer.calculations[0])

    def test_repeated_increase_projection(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( in millions ) | 2007 | 2006 | 2005 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| development costs incurred during the period | 1654 | 1251 | 1030 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "if current development costs increased in 2008 as much as in 2007 , what would the 2008 total be , in millions?",
            graph,
        )

        self.assertEqual(answer.text, "2057")
        self.assertIn("repeated_increase_projection", answer.calculations[0])

    def test_pretax_aftertax_difference(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "these unrealized losses related to reclassifications totaled $ 303 million , "
                    "or $ 189 million after-tax , as of december 31 , 2011."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "in 2011 what was the amount of tax related to the unrealized losses reclassifications totaled $ 303 million , or $ 189 million after-tax,",
            graph,
        )

        self.assertEqual(answer.text, "114")
        self.assertIn("pretax_aftertax_difference", answer.calculations[0])

    def test_rate_of_return_multiplies_year_anchored_asset_value(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| december 31 ( in millions ) | 2008 | 2007 |\n"
                    "| --- | --- | --- |\n"
                    "| total adjusted average assets | 1966895 | 1473541 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "assuming a 5% ( 5 % ) rate of return , what would the earnings be ( in millions ) on 2008 total adjusted average assets?",
            graph,
        )

        self.assertEqual(answer.text, "98345")
        self.assertIn("rate_of_return_on_table_value", answer.calculations[0])

    def test_return_on_assets_uses_net_earnings_over_total_assets(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( $ in millions ) | year ended december 31 2017 | year ended december 31 2013 |\n"
                    "| --- | --- | --- |\n"
                    "| net earnings ( loss ) | 479 | 261 |\n"
                    "| total assets | 6374 | 6190 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the return on total assets during 2013?",
            graph,
        )

        self.assertEqual(answer.text, "4.2%")
        self.assertIn("return_on_assets", answer.calculations[0])

    def test_cumulative_stock_return_uses_terminal_minus_initial_value(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 12/09 | 12/10 | 12/14 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| e*trade financial corporation | 100.00 | 90.91 | 137.81 |\n"
                    "| s&p 500 index | 100.00 | 115.06 | 205.14 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was the percent of the return on the e*trade financial corporation common stock from 2009 to 2014",
            graph,
        )

        self.assertEqual(answer.text, "37.8%")
        self.assertIn("cumulative_return_percent", answer.calculations[0])

    def test_implied_tier2_capital_ratio_derives_from_total_minus_tier1(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| in billions of dollars at year end | 2008 | 2007 |\n"
                    "| --- | --- | --- |\n"
                    "| tier 1 capital | $ 71.0 | $ 82.0 |\n"
                    "| total capital ( tier 1 and tier 2 ) | 108.4 | 121.6 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "at december 31 , 2008 what was the ratio of the tier 2 capital compared to 2007",
            graph,
        )

        self.assertEqual(answer.text, "0.94")
        self.assertIn("implied_tier2_capital_ratio", answer.calculations[0])

    def test_net_change_uses_respectively_ordered_prose_amounts(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "at december 31 , 2015 and december 31 , 2014 , the alll on total purchased "
                    "impaired loans was $ .3 billion and $ .9 billion , respectively ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "at december 31 , 2015 what was the net change from december 31 , 2014 on alll on total purchased impaired loans in billions?",
            graph,
        )

        self.assertEqual(answer.text, "-0.6")
        self.assertIn("respectively_prose_difference", answer.calculations[0])

    def test_between_years_respectively_difference_uses_newer_minus_older(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="text",
                node_type="text",
                content=(
                    "the estimated sensitivity to a one basis point increase in credit spreads "
                    "on derivatives was a gain of $ 3 million and $ 2 million "
                    "( including hedges ) as of december 2017 and december 2016 , respectively ."
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what was change in millions for the estimated sensitivity to a one basis point increase in credit spreads on derivatives ( including hedges ) between 2017 and 2016?",
            graph,
        )

        self.assertEqual(answer.text, "1")
        self.assertIn("respectively_prose_difference", answer.calculations[0])

    def test_current_ratio_uses_current_assets_over_current_liabilities(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| current assets | $ 513782 |\n"
                    "| --- | --- |\n"
                    "| current liabilities | 310919 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the current ratio of robert mondavi?",
            graph,
        )

        self.assertEqual(answer.text, "1.7")
        self.assertIn("current_ratio", answer.calculations[0])

    def test_vertical_metric_percent_change_uses_metric_column_not_year_row_label(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| ( dollars in millions ) | december 31 , average investments | december 31 , pre-tax investment income |\n"
                    "| --- | --- | --- |\n"
                    "| 2012 | 16220.9 | 600.2 |\n"
                    "| 2011 | 15680.9 | 620.0 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "at december 31 , what was the percentage change in investment income from 2011 to 2012",
            graph,
        )

        self.assertEqual(answer.text, "-3.2%")
        self.assertIn("vertical_metric_percent_change", answer.calculations[0])

    def test_implicit_percent_increase_from_years_prefers_percent_change_for_weighted_average_price(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "|  | 2007 | 2006 | 2005 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| weighted average exercise price per share | $ 60.94 | $ 37.84 | $ 25.14 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "by how much did the weighted average exercise price per share increase from 2005 to 2007?",
            graph,
        )

        self.assertEqual(answer.text, "142.4%")
        self.assertIn("implicit_percent_increase", answer.calculations[0])

    def test_implicit_percent_increase_observed_during_years(self) -> None:
        graph = EvidenceGraph()
        graph.add_node(
            EvidenceNode(
                node_id="table",
                node_type="text",
                content=(
                    "| years ended december 31 | 2011 | 2010 | 2009 |\n"
                    "| --- | --- | --- | --- |\n"
                    "| total revenue | $ 11287 | $ 8512 | $ 7595 |\n"
                ),
                source_doc="report.md",
            )
        )

        answer = SupportOnlyGenerator().generate(
            "what is the increase observed in the total revenue during 2010 and 2011?",
            graph,
        )

        self.assertEqual(answer.text, "32.6%")
        self.assertIn("implicit_percent_increase", answer.calculations[0])

    def test_percentage_exact_match_allows_rounding(self) -> None:
        self.assertEqual(numeric_exact_match("86.8%", "87%"), 1.0)

    def test_numeric_exact_match_allows_one_decimal_rounding(self) -> None:
        self.assertEqual(numeric_exact_match("708716.7", "708716.6"), 1.0)

    def test_source_doc_retrieval_adds_oracle_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            corpus = root / "corpus"
            corpus.mkdir()
            (corpus / "a.md").write_text("alpha table 2016 10\nmore alpha 2017 20", encoding="utf-8")
            (corpus / "b.md").write_text("beta unrelated 2016 100\nbeta unrelated 2017 200", encoding="utf-8")

            nodes = CorpusRetriever().retrieve("alpha 2017", corpus, source_doc="a.md")

        self.assertTrue(nodes)
        self.assertTrue(any(node.metadata.get("loader") == "source_doc_oracle" for node in nodes))
        self.assertTrue(all(Path(str(node.source_doc)).name == "a.md" for node in nodes))


if __name__ == "__main__":
    unittest.main()
