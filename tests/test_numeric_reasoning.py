from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evigraph.evidence_graph import EvidenceGraph
from evigraph.generator import SupportOnlyGenerator
from evigraph.metrics import numeric_exact_match
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
        self.assertEqual(answer.citations, ["retrieved_2_case_0_1", "retrieved_1_case_0_0"])

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
